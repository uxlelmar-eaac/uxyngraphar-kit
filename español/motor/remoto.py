"""Cliente del servidor de sistemas de gobernanza (`/v1/sistemas`): índice, búsqueda, descarga y publicación.

Servidor: `UXYNGRAPHAR_SERVIDOR`, si no la clave «servidor» de `casa.json`, si no SERVIDOR_POR_DEFECTO.
`UXYNGRAPHAR_SIN_RED=1` lo apaga (las pruebas y los equipos sin red trabajan solo con el catálogo local).

Caché en la casa (`~/.uxyngraphar/sistemas-de-gobernanza/`):
  indice.json                                   último índice recibido (+ etag y hora), sirve sin red
  <editor>/<id>/<version>/<id>/                 sistemas traídos, ya construidos y en solo lectura
Solo la biblioteca estándar (ADR 0001): urllib, json, hashlib.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import artefacto
import casa
import especificacion as esp

base = esp.base

SERVIDOR_POR_DEFECTO = "https://api.uxyngraphar.com/v1"
CARPETA_CACHE = "sistemas-de-gobernanza"
ARCHIVO_INDICE = "indice.json"
ARCHIVO_SESION = "sesion.json"
VIGENCIA_INDICE = 600          # segundos antes de volver a preguntar por el índice
SEGUNDOS_RED = 15
SEGUNDOS_INDICE = 5            # el índice se consulta al listar proyectos: sin red no debe frenar
PAUSA_TRAS_FALLO = 60          # tras un fallo de red no se vuelve a intentar en este proceso durante este tiempo
_caido_hasta = 0.0
MARCA_COMPLETO = ".completo"
REFERENCIA = re.compile(r"^(?:(?P<editor>[a-z0-9]+(?:-[a-z0-9]+)*)/)?(?P<id>[a-z0-9]+(?:-[a-z0-9]+)*)(?:@(?P<version>\d+\.\d+\.\d+))?$")


class SinServidor(RuntimeError):
    """No hay servidor configurado o no responde (y no hay caché que sirva)."""


class NoEncontrado(LookupError):
    """El servidor no tiene ese sistema o esa versión."""


def servidor() -> str | None:
    if os.environ.get("UXYNGRAPHAR_SIN_RED"):
        return None
    ajustes = casa.leer_json(casa.ARCHIVO_FORMATO, {})
    url = os.environ.get("UXYNGRAPHAR_SERVIDOR") or (ajustes.get("servidor") if isinstance(ajustes, dict) else None)
    url = (url or SERVIDOR_POR_DEFECTO).rstrip("/")
    if not url.startswith(("https://", "http://127.0.0.1", "http://localhost")):
        raise SinServidor(f"servidor «{url}»: solo https (o http en 127.0.0.1/localhost para pruebas)")
    return url


def cache() -> Path:
    return casa.carpeta() / CARPETA_CACHE


def _pedir(ruta: str, datos: bytes | None = None, cabeceras: dict | None = None, metodo: str | None = None,
           segundos: float = SEGUNDOS_RED):
    global _caido_hasta
    url = servidor()
    if not url:
        raise SinServidor("sin red (UXYNGRAPHAR_SIN_RED)")
    if time.time() < _caido_hasta and datos is None:
        raise SinServidor(f"{url}: no respondió hace poco")
    pedido = urllib.request.Request(url + ruta, data=datos, method=metodo,  # noqa: S310 - servidor https configurado
                                    headers={"User-Agent": f"uxyngraphar/{esp.VERSION_MOTOR}", "Accept": "application/json",
                                             **(cabeceras or {})})
    try:
        return urllib.request.urlopen(pedido, timeout=segundos)  # noqa: S310 - servidor https configurado
    except urllib.error.HTTPError as e:
        if e.code == 304:
            return e
        detalle = ""
        try:
            cuerpo = json.loads(e.read().decode("utf-8"))
            detalle = cuerpo.get("message") or cuerpo.get("error") or ""
            detalle = "; ".join(detalle) if isinstance(detalle, list) else str(detalle)
        except (ValueError, AttributeError, OSError):
            pass
        if e.code == 404:
            raise NoEncontrado(detalle or f"no existe: {ruta}") from None
        raise SinServidor(f"{url}{ruta}: HTTP {e.code} {detalle}".strip()) from None
    except (urllib.error.URLError, OSError) as e:
        _caido_hasta = time.time() + PAUSA_TRAS_FALLO
        raise SinServidor(f"{url}: no responde ({getattr(e, 'reason', e)})") from None


def _json(ruta: str) -> dict:
    with _pedir(ruta) as r:
        return json.loads(r.read().decode("utf-8"))


# ── índice ────────────────────────────────────────────────────────────────────

def _indice_guardado() -> dict:
    try:
        return json.loads((cache() / ARCHIVO_INDICE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def indice(refrescar: bool = False) -> dict:
    """{"formato": 1, "sistemas": [{editor, id, titulo, descripcion, familia, etiquetas, problemas,
    versiones: [{version, sha256, tamano, motor, retirada}]}]}. Sin red usa el último guardado (o lanza SinServidor)."""
    guardado = _indice_guardado()
    fresco = guardado and time.time() - guardado.get("_recibido", 0) < VIGENCIA_INDICE
    if fresco and not refrescar and guardado.get("_servidor") == servidor():
        return guardado
    try:
        cabeceras = {"If-None-Match": guardado["_etag"]} if guardado.get("_etag") and guardado.get("_servidor") == servidor() else {}
        with _pedir("/sistemas/indice", cabeceras=cabeceras, segundos=SEGUNDOS_INDICE) as r:
            if getattr(r, "code", 200) == 304:
                datos = guardado
            else:
                datos = json.loads(r.read().decode("utf-8"))
                if not isinstance(datos, dict) or not isinstance(datos.get("sistemas"), list):
                    raise SinServidor("el servidor devolvió un índice inválido")
                datos["_etag"] = r.headers.get("ETag", "")
        datos.update(_recibido=time.time(), _servidor=servidor())
        cache().mkdir(parents=True, exist_ok=True)
        (cache() / ARCHIVO_INDICE).write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
        return datos
    except SinServidor:
        if guardado.get("sistemas") is not None:
            return guardado
        raise


def _compatibles(s: dict) -> list[dict]:
    vs = [v for v in s.get("versiones", []) if not v.get("retirada") and esp.motor_compatible(v.get("motor") or ">=0.0")]
    return sorted(vs, key=lambda v: esp.version_tupla(v["version"]), reverse=True)


def versiones_disponibles(refrescar: bool = False) -> dict[str, dict]:
    """Por id: la última versión compatible con este motor ({editor, version, sha256, …}). Si dos editores usan el
    mismo id, gana «uxyngraphar» (los demás se traen con editor/id)."""
    salida: dict[str, dict] = {}
    for s in indice(refrescar).get("sistemas", []):
        vs = _compatibles(s)
        if not vs:
            continue
        actual = salida.get(s["id"])
        if actual and actual["editor"] == artefacto.EDITOR_POR_DEFECTO:
            continue
        if actual and s.get("editor") != artefacto.EDITOR_POR_DEFECTO:
            continue
        salida[s["id"]] = {**vs[0], "editor": s.get("editor", artefacto.EDITOR_POR_DEFECTO), "titulo": s.get("titulo", "")}
    return salida


def resolver(ref: str) -> dict:
    """`[editor/]id[@version]` → {editor, id, version, sha256, tamano, motor} según el índice."""
    m = REFERENCIA.match(ref.strip())
    if not m:
        raise ValueError(f"referencia «{ref}»: usa id, editor/id o editor/id@X.Y.Z")
    candidatos = [s for s in indice().get("sistemas", []) if s.get("id") == m["id"]
                  and (not m["editor"] or s.get("editor") == m["editor"])]
    if not candidatos:
        raise NoEncontrado(f"el servidor no tiene «{ref}»")
    if len(candidatos) > 1:
        propios = [s for s in candidatos if s.get("editor") == artefacto.EDITOR_POR_DEFECTO]
        if not propios:
            raise ValueError(f"«{m['id']}» existe con varios editores ({', '.join(s['editor'] for s in candidatos)}): usa editor/id")
        candidatos = propios
    (s,) = candidatos
    if m["version"]:
        vs = [v for v in s.get("versiones", []) if v["version"] == m["version"]]
        if not vs:
            raise NoEncontrado(f"«{s['editor']}/{s['id']}» no tiene la versión {m['version']}")
        if not esp.motor_compatible(vs[0].get("motor") or ">=0.0"):
            raise ValueError(f"{s['id']}@{m['version']} requiere motor {vs[0]['motor']} (este es {esp.VERSION_MOTOR})")
    else:
        vs = _compatibles(s)
        if not vs:
            raise NoEncontrado(f"«{s['editor']}/{s['id']}» no tiene versiones para el motor {esp.VERSION_MOTOR}")
    return {"editor": s["editor"], "id": s["id"], **vs[0]}


def buscar(texto: str = "", familia: str = "") -> list[dict]:
    """Busca en el servidor; sin red, en el índice guardado (título, descripción, id, etiquetas y problemas)."""
    try:
        q = urllib.parse.urlencode({k: v for k, v in (("q", texto), ("familia", familia)) if v})
        datos = _json("/sistemas" + (f"?{q}" if q else ""))
        return datos.get("sistemas", datos.get("items", [])) if isinstance(datos, dict) else datos
    except SinServidor as fallo:
        try:
            guardados = indice().get("sistemas", [])
        except SinServidor:
            raise fallo from None
        palabras = [p for p in texto.lower().split() if p]
        salida = []
        for s in guardados:
            pajar = " ".join([s.get("id", ""), s.get("titulo", ""), s.get("descripcion", ""),
                              *s.get("etiquetas", []), *s.get("problemas", [])]).lower()
            if all(p in pajar for p in palabras) and (not familia or s.get("familia") == familia):
                salida.append(s)
        return salida


def ficha(ref: str) -> dict:
    r = resolver(ref)
    try:
        return {**_json(f"/sistemas/{r['editor']}/{r['id']}"), "resuelta": r}
    except SinServidor:
        return {**next(s for s in indice()["sistemas"] if s["id"] == r["id"] and s["editor"] == r["editor"]), "resuelta": r}


# ── traer ─────────────────────────────────────────────────────────────────────

def en_cache(editor: str, pid: str, version: str) -> Path | None:
    c = cache() / editor / pid / version
    return c / pid if (c / MARCA_COMPLETO).is_file() and (c / pid).is_dir() else None


def traer(ref: str) -> Path:
    """Descarga (si no está en la caché) la versión resuelta, comprueba su sha256, la valida y devuelve la carpeta
    construida `<cache>/<editor>/<id>/<version>/<id>/`."""
    r = resolver(ref)
    hecho = en_cache(r["editor"], r["id"], r["version"])
    if hecho and base.integro(base.comprobar_integridad(hecho)):
        return hecho
    destino = cache() / r["editor"] / r["id"] / r["version"]
    if destino.exists():
        import repo
        repo.borrar_arbol(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destino.parent, prefix=".descargando-") as tmp:
        zip_ = Path(tmp) / artefacto.nombre(r["id"], r["version"])
        with _pedir(f"/sistemas/{r['editor']}/{r['id']}/versiones/{r['version']}/descarga",
                    cabeceras={"Accept": "application/zip"}) as resp, open(zip_, "wb") as f:
            shutil.copyfileobj(resp, f)
        huella = artefacto.sha256_de(zip_)
        if r.get("sha256") and huella != r["sha256"]:
            raise artefacto.ArtefactoInvalido(f"{r['id']}@{r['version']}: sha256 distinto al del índice ({huella} ≠ {r['sha256']})")
        pid, m = artefacto.leer(zip_)
        if pid != r["id"] or m.get("version") != r["version"]:
            raise artefacto.ArtefactoInvalido(f"el artefacto trae {pid}@{m.get('version')} y se pidió {r['id']}@{r['version']}")
        carpeta = artefacto.desempaquetar(zip_, Path(tmp) / "x")
        final = Path(tmp) / "final"
        final.mkdir()
        carpeta.rename(final / pid)
        (final / MARCA_COMPLETO).write_text(json.dumps({"sha256": huella, "editor": r["editor"]}) + "\n", encoding="utf-8")
        final.rename(destino)
    import repo
    repo.solo_lectura(destino / r["id"])
    return destino / r["id"]


def limpiar_cache() -> int:
    """Borra los sistemas traídos y el índice guardado; devuelve cuántas versiones había."""
    c = cache()
    if not c.is_dir():
        return 0
    n = len(list(c.glob(f"*/*/*/{MARCA_COMPLETO}")))
    import repo
    repo.borrar_arbol(c)
    return n


# ── sesión y publicación ──────────────────────────────────────────────────────

def token() -> str | None:
    return os.environ.get("UXYNGRAPHAR_TOKEN") or casa.leer_json(ARCHIVO_SESION, {}).get("token")


def guardar_token(valor: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9._~+/=-]{16,512}", valor or ""):
        raise ValueError("token de publicación con formato inválido")
    return casa.escribir_json(ARCHIVO_SESION, {"token": valor, "servidor": servidor()}, privado=True)


def borrar_token() -> bool:
    ruta = casa.carpeta() / ARCHIVO_SESION
    if ruta.is_file():
        ruta.unlink()
        return True
    return False


def publicar(zip_: Path, token_: str | None = None) -> dict:
    """Sube un artefacto (POST /sistemas/publicar, cuerpo application/zip). Devuelve la versión creada."""
    clave = token_ or token()
    if not clave:
        raise PermissionError("falta el token de publicación: uxyngraphar sesion guardar <token> (o UXYNGRAPHAR_TOKEN)")
    artefacto.leer(Path(zip_))
    datos = Path(zip_).read_bytes()
    with _pedir("/sistemas/publicar", datos=datos, metodo="POST",
                cabeceras={"Content-Type": "application/zip", "Authorization": f"Bearer {clave}",
                           "X-Uxyn-Sha256": artefacto.sha256_de(Path(zip_))}) as r:
        return json.loads(r.read().decode("utf-8"))
