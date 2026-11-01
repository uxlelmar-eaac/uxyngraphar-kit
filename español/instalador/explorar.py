"""Explorador de carpetas para las páginas locales: solo lee nombres de carpetas, nunca escribe ni abre archivos.

Lo usa el botón «Examinar…» de cada página en lugar del selector del sistema, que no existe en todos los equipos.
"""

from __future__ import annotations

import os
import string
import sys
from pathlib import Path

import sistema

MAX_CARPETAS = 500


def _es_dir(p: Path) -> bool:
    try:
        return p.is_dir()
    except OSError:
        return False


def _tiene_uxyngraphar(p: Path) -> bool:
    """uxyngraphar/.uxyngraphar.lock, docs/.uxyngraphar.lock o cualquier */.uxyngraphar.lock un nivel abajo (sin bajar más: debe ser barato)."""
    try:
        return any((h / ".uxyngraphar.lock").is_file() for h in p.iterdir() if not h.is_symlink() and _es_dir(h))
    except OSError:
        return False


def atajos() -> list[dict]:
    casa = Path.home()
    lista = [{"nombre": "Carpeta personal", "ruta": str(casa)}]
    for nombre, opciones in (("Escritorio", ("Escritorio", "Desktop")), ("Documentos", ("Documentos", "Documents"))):
        hallada = next((casa / o for o in opciones if _es_dir(casa / o)), None)
        if hallada:
            lista.append({"nombre": nombre, "ruta": str(hallada)})
    for proyecto in sistema.leer_proyectos():
        if _es_dir(Path(proyecto)):
            lista.append({"nombre": Path(proyecto).name or proyecto, "ruta": proyecto, "proyecto": True})
    if sys.platform.startswith("win"):
        lista += [{"nombre": f"Unidad {l}:", "ruta": f"{l}:\\"} for l in string.ascii_uppercase if os.path.exists(f"{l}:\\")]
    return lista


def listar(ruta: str = "", ocultas: bool = False) -> dict:
    texto = str(ruta or "").strip()
    try:
        base = Path(os.path.expanduser(texto)).resolve() if texto else Path.home().resolve()
    except (OSError, RuntimeError, ValueError):
        return {"ok": False, "error": "Esa ruta no es válida."}
    if not _es_dir(base):
        return {"ok": False, "error": f"No existe la carpeta «{texto}»." if not base.exists() else "Esa ruta es un archivo, no una carpeta."}
    try:
        entradas = list(os.scandir(base))
    except PermissionError:
        return {"ok": False, "error": "No tengo permiso para ver el contenido de esa carpeta."}
    except OSError as exc:
        return {"ok": False, "error": f"No pude leer esa carpeta: {exc.strerror or exc}"}
    carpetas = []
    for e in entradas:
        if not ocultas and e.name.startswith("."):
            continue
        try:
            if not e.is_dir():
                continue
        except OSError:
            continue
        carpetas.append(e)
    carpetas.sort(key=lambda e: e.name.casefold())
    truncada = len(carpetas) > MAX_CARPETAS
    salida = []
    for e in carpetas[:MAX_CARPETAS]:
        p = Path(e.path)
        try:
            salida.append({"nombre": e.name, "ruta": str(p), "git": (p / ".git").exists(), "uxyngraphar": _tiene_uxyngraphar(p)})
        except PermissionError:
            continue
    padre = base.parent
    return {"ok": True, "ruta": str(base), "padre": None if padre == base else str(padre),
            "carpetas": salida, "truncada": truncada, "atajos": atajos()}
