"""El artefacto de un sistema de gobernanza: el zip que se sube al servidor, se guarda en él y se descarga.

Un artefacto es la construcción del sistema (fuente + `scripts/comun/` de `_base` + INTEGRIDAD.json) dentro de una carpeta
raíz `<id>/`, en un zip reproducible: mismo contenido, misma huella (fecha fija, orden fijo, permisos fijos). El servidor
guarda el zip tal cual y publica su sha256; el motor lo comprueba al traerlo.
"""

from __future__ import annotations

import hashlib
import io
import shutil
import stat
import tempfile
import zipfile
from pathlib import Path

import catalogo
import especificacion as esp

base = esp.base

FECHA_FIJA = (1980, 1, 1, 0, 0, 0)
MAX_ARCHIVOS = 2000
MAX_DESCOMPRIMIDO = 50 * 1024 * 1024       # 50 MB en total
MAX_RATIO = 200                            # un archivo que crece más de 200 veces al descomprimir es sospechoso
EDITOR_POR_DEFECTO = "uxyngraphar"


class ArtefactoInvalido(ValueError):
    """El zip no es un artefacto de sistema aceptable."""


def nombre(pid: str, version: str) -> str:
    return f"{pid}-{version}.zip"


def sha256_de(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 16), b""):
            h.update(bloque)
    return h.hexdigest()


def empaquetar_carpeta(construido: Path, destino: Path) -> Path:
    """Zip reproducible de un sistema ya construido (`construido` es la carpeta `<id>/` con INTEGRIDAD.json)."""
    construido = Path(construido)
    errores = esp.validar_sistema(construido, construido=True)
    if errores:
        raise ArtefactoInvalido(f"{construido.name}: la construcción no valida: {'; '.join(errores)}")
    m = base.leer_manifiesto(construido)
    Path(destino).mkdir(parents=True, exist_ok=True)
    salida = Path(destino) / nombre(m["id"], m["version"])
    with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(x for x in construido.rglob("*") if x.is_file()):
            rel = p.relative_to(construido).as_posix()
            if base.IGNORAR.search(rel):
                continue
            info = zipfile.ZipInfo(f"{m['id']}/{rel}", FECHA_FIJA)
            info.external_attr = (0o755 if p.suffix == ".py" else 0o644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, p.read_bytes())
    return salida


def empaquetar(pid: str, destino: Path, cat: Path | None = None) -> Path:
    """Construye `pid` desde el catálogo local y deja `<id>-<version>.zip` en `destino`."""
    with tempfile.TemporaryDirectory(prefix="uxy-artefacto-") as tmp:
        return empaquetar_carpeta(catalogo.construir(pid, Path(tmp), cat), destino)


def _revisar_entradas(z: zipfile.ZipFile) -> str:
    """Comprueba las entradas del zip y devuelve la carpeta raíz (el id)."""
    entradas = z.infolist()
    if not entradas:
        raise ArtefactoInvalido("zip vacío")
    if len(entradas) > MAX_ARCHIVOS:
        raise ArtefactoInvalido(f"demasiados archivos ({len(entradas)} > {MAX_ARCHIVOS})")
    raices, total = set(), 0
    for e in entradas:
        n = e.filename
        if not n.isascii() or " " in n or "\\" in n or n.startswith("/") or ":" in n:
            raise ArtefactoInvalido(f"nombre no aceptado: {n!r}")
        partes = n.rstrip("/").split("/")
        if any(p in ("", ".", "..") for p in partes):
            raise ArtefactoInvalido(f"ruta no aceptada: {n!r}")
        if stat.S_ISLNK(e.external_attr >> 16):
            raise ArtefactoInvalido(f"enlace simbólico no aceptado: {n!r}")
        if e.flag_bits & 0x1:
            raise ArtefactoInvalido(f"archivo cifrado: {n!r}")
        total += e.file_size
        if e.compress_size and e.file_size / e.compress_size > MAX_RATIO and e.file_size > 1024 * 1024:
            raise ArtefactoInvalido(f"compresión sospechosa: {n!r}")
        raices.add(partes[0])
    if total > MAX_DESCOMPRIMIDO:
        raise ArtefactoInvalido(f"demasiado grande al descomprimir ({total} bytes)")
    if len(raices) != 1:
        raise ArtefactoInvalido(f"debe tener una sola carpeta raíz <id>/ (tiene {', '.join(sorted(raices))})")
    (raiz,) = raices
    if not base.ID_VALIDO.match(raiz) or all(e.filename == raiz + "/" for e in entradas):
        raise ArtefactoInvalido(f"carpeta raíz inválida «{raiz}»")
    return raiz


def leer(datos: bytes | Path) -> tuple[str, dict]:
    """(id, manifiesto) de un artefacto sin descomprimirlo en disco (revisa las entradas)."""
    origen = io.BytesIO(datos) if isinstance(datos, (bytes, bytearray)) else datos
    try:
        with zipfile.ZipFile(origen) as z:
            raiz = _revisar_entradas(z)
            import json
            try:
                m = json.loads(z.read(f"{raiz}/{base.MANIFIESTO}").decode("utf-8"))
            except KeyError:
                raise ArtefactoInvalido(f"falta {raiz}/{base.MANIFIESTO}") from None
    except zipfile.BadZipFile as e:
        raise ArtefactoInvalido(f"no es un zip: {e}") from None
    if not isinstance(m, dict) or m.get("id") != raiz:
        raise ArtefactoInvalido(f"el id del manifiesto no coincide con la carpeta raíz «{raiz}»")
    return raiz, m


def desempaquetar(zip_: Path, destino: Path) -> Path:
    """Descomprime el artefacto en `destino/<id>/` (que no debe existir) y lo valida como sistema construido."""
    pid, _ = leer(Path(zip_))
    salida = Path(destino) / pid
    if salida.exists():
        raise FileExistsError(f"ya existe {salida}")
    Path(destino).mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destino, prefix=".desempaquetando-") as tmp:
        with zipfile.ZipFile(zip_) as z:
            for e in z.infolist():
                if e.is_dir():
                    continue
                ruta = Path(tmp) / e.filename
                ruta.parent.mkdir(parents=True, exist_ok=True)
                with z.open(e) as fuente, open(ruta, "wb") as f:
                    shutil.copyfileobj(fuente, f)
        errores = esp.validar_sistema(Path(tmp) / pid, construido=True)
        if errores:
            raise ArtefactoInvalido(f"{pid}: el artefacto no valida: {'; '.join(errores)}")
        (Path(tmp) / pid).rename(salida)
    return salida


def ficha(carpeta: Path, sha256: str = "", tamano: int = 0) -> dict:
    """Los datos que el servidor indexa de un sistema construido (lo que muestra la búsqueda)."""
    m = base.leer_manifiesto(carpeta)
    return {"editor": m.get("editor", EDITOR_POR_DEFECTO), "id": m["id"], "version": m["version"],
            "titulo": m.get("titulo", ""), "descripcion": m.get("descripcion", ""), "familia": m.get("familia", ""),
            "motor": m.get("motor", ""), "idioma": m.get("idioma", "es"), "licencia": m.get("licencia", "CC-BY-4.0"),
            "etiquetas": m.get("etiquetas", []), "problemas": sorted(base.ids_problemas(m)),
            "piezas": m.get("piezas", []), "protocolo": m.get("manifiesto_formato"), "sha256": sha256, "tamano": tamano}
