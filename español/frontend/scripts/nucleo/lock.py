"""Archivo de bloqueo del proyecto (`<docs>/.uxyngraphar.lock`): línea base de lo que el pack entregó."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

import clasificacion as cl

LOCK_NOMBRE = ".uxyngraphar.lock"
FORMATO = 1
VERSION_RE = re.compile(r"^version:\s*(\S+)", re.M)
# Perfil «minimo»: sin espejo, automatizaciones, auditorías, manuales ni archivo (el resto del núcleo se mantiene).
EXCLUIDO_MINIMO = ("50-sistema-integral/", "55-automatizaciones/", "40-auditorias/", "30-manuales/", "90-archivo/")


RUTA_LOCAL_RE = re.compile(r"^(?:[A-Za-z]:[\\/]|\\\\|/|~|\.\.?[\\/])")


def etiqueta_fuente(fuente: str, version: str) -> str:
    """Origen del pack para el lock. Nunca guarda rutas del equipo de quien instala (privacidad y reproducibilidad)."""
    f = (fuente or "").strip()
    if re.match(r"^(?:https?://|ssh://|git@)", f):
        return re.sub(r"//[^/@]+@", "//", f)   # sin usuario/token incrustado
    return f"uxyngraphar@{version} (copia local)"


def es_ruta_local(fuente: str) -> bool:
    return bool(RUTA_LOCAL_RE.match((fuente or "").strip()))


def sha(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def version_de(raiz: Path) -> str:
    f = raiz / "VERSION.md"
    m = VERSION_RE.search(f.read_text(encoding="utf-8")) if f.is_file() else None
    return m.group(1) if m else "desconocida"


def tipo_pack(raiz: Path) -> str:
    """servidor | cliente (según la primera línea de AGENTES.md)."""
    f = raiz / "AGENTES.md"
    primera = f.read_text(encoding="utf-8").splitlines()[0].lower() if f.is_file() else ""
    return "cliente" if "cliente" in primera else "servidor"


def en_perfil(rel: str, perfil: str) -> bool:
    return perfil != "minimo" or not rel.startswith(EXCLUIDO_MINIMO)


def inventario(raiz: Path, perfil: str = "completo") -> dict[str, dict[str, str]]:
    """Archivos instalables del pack (clases N, P, M) con su hash. Error si hay archivos sin clasificar."""
    res: dict[str, dict[str, str]] = {}
    sin_clase: list[str] = []
    for p in sorted(raiz.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(raiz).as_posix()
        clase = cl.clasificar(rel)
        if clase is None:
            sin_clase.append(rel)
        elif clase in ("N", "P", "M") and en_perfil(rel, perfil):
            res[rel] = {"clase": clase, "sha256": sha(p)}
    if sin_clase:
        raise ValueError("archivos del pack sin clasificar (añadir regla en nucleo/clasificacion.py): " + ", ".join(sin_clase[:8]))
    return res


def ruta_lock(repo: Path, docs: str) -> Path:
    return repo / docs / LOCK_NOMBRE


def _valido(datos: Any) -> bool:
    return isinstance(datos, dict) and isinstance(datos.get("archivos", {}), dict)


def leer(repo: Path, docs: str) -> dict[str, Any] | None:
    """El lock del proyecto; None si no hay. Nunca falla: si está dañado usa la copia más reciente de los respaldos de
    actualización y, si no hay ninguna, uno vacío (sin línea base: toda diferencia es conflicto y no se pisa nada).
    En esos casos lleva la clave «danado» con la explicación; `escribir` la quita al guardar uno sano."""
    f = ruta_lock(repo, docs)
    if not f.is_file():
        return None
    try:
        datos = json.loads(f.read_text(encoding="utf-8"))
        if _valido(datos):
            return datos
    except (ValueError, UnicodeDecodeError):
        pass
    rel = f.relative_to(repo).as_posix()
    raiz = repo / ".uxyngraphar-respaldo"
    for copia in sorted(raiz.glob("*/" + rel), reverse=True) if raiz.is_dir() else []:
        try:
            datos = json.loads(copia.read_text(encoding="utf-8"))
        except (ValueError, UnicodeDecodeError, OSError):
            continue
        if _valido(datos):
            datos["danado"] = f"{rel} estaba dañado; se usa la copia del respaldo {copia.parents[len(Path(rel).parts) - 1].name}"
            return datos
    return {"formato": FORMATO, "pack": tipo_pack(repo / cl.padre(docs)), "perfil": "completo", "docs": docs.strip("/"),
            "version": "desconocida", "archivos": {}, "danado": f"{rel} estaba dañado y no hay copia: sin línea base, nada se sobrescribe"}


def sello(archivos: dict[str, Any]) -> str:
    """Huella del mapa de archivos: detecta ediciones manuales del lock (no es una firma criptográfica)."""
    return hashlib.sha256(("uxyngraphar|" + json.dumps(archivos, sort_keys=True, ensure_ascii=False)).encode("utf-8")).hexdigest()


def sello_valido(datos: dict[str, Any]) -> bool:
    return datos.get("sello") == sello(datos.get("archivos", {}))


def escribir(repo: Path, docs: str, datos: dict[str, Any]) -> None:
    datos.pop("danado", None)
    datos["sello"] = sello(datos.get("archivos", {}))
    f = ruta_lock(repo, docs)
    f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(datos, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    os.replace(tmp, f)


def mayor(version: str) -> str:
    return version.split(".")[0]


def _tupla(version: str) -> tuple[int, ...]:
    partes = []
    for p in version.strip().split("."):
        num = "".join(c for c in p if c.isdigit())
        partes.append(int(num) if num else 0)
    return tuple(partes)


def es_degradacion(adoptada: str, nueva: str) -> bool:
    """True si el proyecto tiene una versión MÁS NUEVA que el pack con el que se intenta actualizar."""
    if not adoptada or not nueva:
        return False
    return _tupla(adoptada) > _tupla(nueva)
