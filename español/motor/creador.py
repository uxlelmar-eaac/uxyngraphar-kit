"""Creador: el mismo motor del catálogo aplicado a un borrador suelto, y su sincronización con el Creador web.

Dos usos:
- Puente para el servidor (ADR 0013): el backend escribe un borrador en una carpeta temporal y llama a
  `uxyngraphar creador validar|nuevo|desde-spec|empaquetar --dir D --json`. Así la web valida, crea y empaqueta con las
  mismas reglas que el kit (`especificacion.py`, `generador.py`, `artefacto.py`) sin duplicarlas.
- `creador borradores|bajar|subir`: lleva un borrador de la web al catálogo local y vuelve. Cada borrador tiene una
  `revision` en el servidor; si las dos partes cambiaron desde la última sincronización hay conflicto: se muestran las
  diferencias y se elige qué versión conservar («web» o «local»). Nunca se pisa nada en silencio.

Los borradores no llevan `scripts/comun/` ni `INTEGRIDAD.json`: los añade la construcción desde `_base`.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

import artefacto
import casa
import catalogo
import especificacion as esp
import generador
import remoto

base = esp.base
ARCHIVO_ESTADO = "creador.json"
RESERVADOS = ("scripts/comun/",)
MAX_ARCHIVOS = 400
MAX_BYTES_ARCHIVO = 256 * 1024
MAX_BYTES_TOTAL = 5 * 1024 * 1024
MAX_LINEAS_DIFERENCIA = 400


class Conflicto(RuntimeError):
    """La web y el equipo cambiaron el mismo borrador desde la última sincronización."""

    def __init__(self, slug: str, revision_web: int, diferencias: list[dict]):
        super().__init__(f"«{slug}» cambió en la web (revisión {revision_web}) y en este equipo: elige qué conservar "
                         f"con --conservar web|local")
        self.slug, self.revision_web, self.diferencias = slug, revision_web, diferencias


def reservado(rel: str) -> bool:
    return rel == base.INTEGRIDAD or rel.startswith(RESERVADOS) or bool(base.IGNORAR.search(rel))


def huella(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


# ── puente con el servidor: un único sistema en una carpeta ──────────────────

def _unico(carpeta: Path) -> str:
    ids = list(catalogo._sistemas(carpeta))
    if len(ids) != 1:
        raise ValueError(f"{carpeta}: debe contener exactamente un sistema (hay {len(ids)})")
    return ids[0]


def validar(carpeta: Path) -> dict:
    """Errores, avisos y pendientes del único sistema de `carpeta` (lo que la web muestra en «Validación»)."""
    carpeta = Path(carpeta)
    pid = _unico(carpeta)
    m = catalogo.listar(carpeta)[0]
    p = generador.pendientes(pid, carpeta)
    return {"id": pid, "version": m.get("version", ""), "titulo": m.get("titulo", ""), "valido": not m["errores"],
            "listo": p["listo"], "errores": m["errores"], "avisos": m.get("avisos", []), "marcadores": p["marcadores"],
            "faltan_recomendadas": p["faltan_recomendadas"], "siguiente": p["siguiente"]}


def leer(carpeta: Path, pid: str) -> dict[str, str]:
    """Archivos de texto del sistema (sin los reservados): {ruta: contenido}."""
    c = catalogo.carpeta(pid, carpeta)
    salida = {}
    for rel in base.archivos_del_sistema(c):
        if reservado(rel):
            continue
        try:
            salida[rel] = (c / rel).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raise ValueError(f"{rel}: el Creador solo admite archivos de texto UTF-8") from None
    return salida


def escribir(carpeta: Path, pid: str, archivos: dict[str, str]) -> Path:
    """Vuelca `archivos` en `carpeta/<pid>/` (reemplaza lo que hubiera, salvo `scripts/comun/`)."""
    if not base.ID_VALIDO.match(pid):
        raise ValueError(f"id inválido «{pid}»")
    if len(archivos) > MAX_ARCHIVOS:
        raise ValueError(f"demasiados archivos (máximo {MAX_ARCHIVOS})")
    destino = (Path(carpeta) / pid).resolve()
    for rel in archivos:
        _comprobar_ruta(rel)
    if destino.exists():
        for p in sorted(destino.rglob("*"), reverse=True):
            rel = p.relative_to(destino).as_posix()
            if p.is_file() and not rel.startswith(RESERVADOS):
                p.unlink()
            elif p.is_dir() and not any(p.iterdir()):
                p.rmdir()
    for rel, contenido in archivos.items():
        f = destino / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(contenido, encoding="utf-8")
    return destino


def _comprobar_ruta(rel: str) -> None:
    partes = rel.split("/")
    if (not rel or not rel.isascii() or " " in rel or "\\" in rel or ":" in rel or rel.startswith("/")
            or any(x in ("", ".", "..") for x in partes) or reservado(rel)):
        raise ValueError(f"ruta no aceptada: {rel!r}")


def nuevo(carpeta: Path, pid: str, titulo: str, familia: str = "proceso", descripcion: str = "") -> dict:
    """Sistema nuevo desde `_base` (con sus marcadores {{…}} por rellenar)."""
    catalogo.crear(pid, titulo, descripcion, raiz=Path(carpeta), familia=familia)
    return {"id": pid, "archivos": leer(Path(carpeta), pid)}


def desde_spec(carpeta: Path, spec: dict) -> dict:
    """Sistema completo desde una especificación (la que rellena la IA a partir de una descripción)."""
    r = generador.desde_spec(spec, aplicar=True, raiz=Path(carpeta))
    if r["errores"]:
        return {"errores": r["errores"], "avisos": r.get("avisos", [])}
    return {"id": r["id"], "errores": [], "avisos": r.get("avisos", []), "archivos": leer(Path(carpeta), r["id"])}


def empaquetar(carpeta: Path, destino: Path) -> dict:
    """Construye y empaqueta el único sistema de `carpeta`: el zip que se publica."""
    pid = _unico(Path(carpeta))
    z = artefacto.empaquetar(pid, Path(destino), Path(carpeta))
    return {"id": pid, "zip": str(z), "sha256": artefacto.sha256_de(z), "tamano": z.stat().st_size}


# ── sincronización con el Creador web ────────────────────────────────────────

def _estado() -> dict:
    datos = casa.leer_json(ARCHIVO_ESTADO, {})
    return datos if isinstance(datos, dict) else {}


def _guardar_estado(slug: str, revision: int, archivos: dict[str, str]) -> None:
    estado = _estado()
    por_servidor = estado.setdefault(remoto.servidor() or "", {})
    por_servidor[slug] = {"revision": revision, "huellas": {r: huella(t) for r, t in archivos.items()}}
    casa.escribir_json(ARCHIVO_ESTADO, estado)


def _recordado(slug: str) -> dict:
    return _estado().get(remoto.servidor() or "", {}).get(slug) or {}


def diferencias(antes: dict[str, str], despues: dict[str, str]) -> list[dict]:
    """Por archivo: añadido, borrado o cambiado, con su diff unificado (recortado)."""
    salida = []
    for rel in sorted(set(antes) | set(despues)):
        a, d = antes.get(rel), despues.get(rel)
        if a == d:
            continue
        lineas = list(difflib.unified_diff((a or "").splitlines(), (d or "").splitlines(), f"web/{rel}", f"local/{rel}",
                                           lineterm=""))
        salida.append({"ruta": rel, "cambio": "nuevo" if a is None else "borrado" if d is None else "cambiado",
                       "diff": "\n".join(lineas[:MAX_LINEAS_DIFERENCIA])})
    return salida


def _carpeta_local(slug: str, cat: Path | None = None) -> Path:
    return catalogo.catalogo(cat) / slug


def _local(slug: str, cat: Path | None = None) -> dict[str, str]:
    return leer(catalogo.catalogo(cat), slug) if (_carpeta_local(slug, cat) / base.MANIFIESTO).is_file() else {}


def _cambiado_en_local(slug: str, local: dict[str, str]) -> bool:
    huellas = _recordado(slug).get("huellas")
    if huellas is None:
        return bool(local)
    return {r: huella(t) for r, t in local.items()} != huellas


def borradores(cat: Path | None = None) -> list[dict]:
    """Borradores del Creador web de la cuenta conectada, con su estado en este equipo."""
    codigo, cuerpo = remoto._pedir_json("/me/creador/borradores", metodo="GET", con_sesion=True)
    _error(codigo, cuerpo)
    filas = cuerpo.get("borradores", []) if isinstance(cuerpo, dict) else []
    for f in filas:
        r = _recordado(f.get("slug", ""))
        f["en_equipo"] = (_carpeta_local(f.get("slug", ""), cat) / base.MANIFIESTO).is_file()
        f["revision_equipo"] = r.get("revision")
    return filas


def _error(codigo: int, cuerpo: dict) -> None:
    if codigo == 401:
        raise PermissionError(remoto._mensaje(cuerpo, "sin sesión o caducada: uxyngraphar iniciar-sesion"))
    if codigo == 404:
        raise remoto.NoEncontrado(remoto._mensaje(cuerpo, "ese borrador no existe en tu cuenta"))
    if codigo >= 400 and codigo != 409:
        raise remoto.SinServidor(remoto._mensaje(cuerpo, f"el servidor respondió HTTP {codigo}"))


def _web(slug: str) -> tuple[int, dict[str, str]]:
    codigo, cuerpo = remoto._pedir_json(f"/me/creador/borradores/{slug}", metodo="GET", con_sesion=True)
    _error(codigo, cuerpo)
    archivos = {a["ruta"]: a["contenido"] for a in cuerpo.get("archivos", [])
                if isinstance(a, dict) and isinstance(a.get("ruta"), str) and isinstance(a.get("contenido"), str)}
    return int(cuerpo.get("revision") or 0), archivos


def bajar(slug: str, conservar: str | None = None, cat: Path | None = None) -> dict:
    """Trae el borrador `slug` al catálogo local. Si también cambió aquí, lanza `Conflicto` salvo que se elija."""
    if not base.ID_VALIDO.match(slug):
        raise ValueError(f"borrador inválido «{slug}»")
    revision, web = _web(slug)
    local = _local(slug, cat)
    recordada = _recordado(slug).get("revision")
    if local == web:
        _guardar_estado(slug, revision, web)
        return {"slug": slug, "revision": revision, "accion": "al_dia", "ruta": str(_carpeta_local(slug, cat))}
    if _cambiado_en_local(slug, local) and local and conservar != "web":
        if conservar == "local":
            _guardar_estado(slug, revision, local)
            return {"slug": slug, "revision": revision, "accion": "conservado_local", "ruta": str(_carpeta_local(slug, cat))}
        raise Conflicto(slug, revision, diferencias(web, local))
    escribir(catalogo.catalogo(cat), slug, web)
    _guardar_estado(slug, revision, web)
    return {"slug": slug, "revision": revision, "accion": "bajado" if recordada is not None or local else "nuevo",
            "ruta": str(_carpeta_local(slug, cat)), "archivos": len(web)}


def subir(slug: str, conservar: str | None = None, cat: Path | None = None) -> dict:
    """Sube el sistema `slug` del catálogo local a su borrador web (lo crea si no existe)."""
    local = _local(slug, cat)
    if not local:
        raise FileNotFoundError(f"el catálogo local no tiene el sistema «{slug}»")
    total = sum(len(t.encode("utf-8")) for t in local.values())
    if total > MAX_BYTES_TOTAL or any(len(t.encode("utf-8")) > MAX_BYTES_ARCHIVO for t in local.values()):
        raise ValueError(f"«{slug}» es demasiado grande para el Creador web (máximo {MAX_BYTES_ARCHIVO // 1024} KB "
                         f"por archivo y {MAX_BYTES_TOTAL // (1024 * 1024)} MB en total)")
    base_rev = _recordado(slug).get("revision") or 0
    cuerpo = {"revision": base_rev, "archivos": [{"ruta": r, "contenido": t} for r, t in sorted(local.items())]}
    codigo, respuesta = remoto._pedir_json(f"/me/creador/borradores/{slug}", cuerpo, metodo="PUT", con_sesion=True)
    if codigo == 409:
        revision = int(respuesta.get("revision") or 0)
        if conservar == "local":
            cuerpo["revision"] = revision
            codigo, respuesta = remoto._pedir_json(f"/me/creador/borradores/{slug}", cuerpo, metodo="PUT", con_sesion=True)
        elif conservar == "web":
            return bajar(slug, conservar="web", cat=cat)
        else:
            _, web = _web(slug)
            raise Conflicto(slug, revision, diferencias(web, local))
    _error(codigo, respuesta)
    revision = int(respuesta.get("revision") or 0)
    _guardar_estado(slug, revision, local)
    return {"slug": slug, "revision": revision, "accion": "subido", "archivos": len(local)}


def con_carpeta_temporal(funcion, *args):
    """Ejecuta `funcion(carpeta, *args)` sobre una carpeta temporal que se borra al terminar."""
    tmp = Path(tempfile.mkdtemp(prefix="uxy-creador-"))
    try:
        return funcion(tmp, *args)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def json_de_entrada(texto: str) -> dict:
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON inválido: {e}") from e
    if not isinstance(datos, dict):
        raise ValueError("se esperaba un objeto JSON")
    return datos
