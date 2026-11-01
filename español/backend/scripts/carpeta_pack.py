"""Nombre de la carpeta del pack en un proyecto: «uxyngraphar/» en las instalaciones nuevas, «docs/» en las anteriores a 1.1.0.

Las herramientas reciben la carpeta con `--docs`; si no se indica, se deduce (sin preguntar) en este orden:
  1. la carpeta del pack donde vive el propio script (lo normal: `python3 uxyngraphar/scripts/doctor.py`);
  2. una carpeta conocida del proyecto que tenga `.uxyngraphar.lock` (primero «uxyngraphar», luego «docs»);
  3. una carpeta conocida que exista;
  4. «uxyngraphar».
"""

from __future__ import annotations

import os
from pathlib import Path

CARPETA = "uxyngraphar"            # la de las instalaciones nuevas
CARPETAS = (CARPETA, "docs")       # las que se aceptan como último tramo de la ruta (docs = instalaciones antiguas)
LOCK = ".uxyngraphar.lock"


def nombre_valido(docs: str) -> bool:
    return docs.strip("/").rpartition("/")[2] in CARPETAS


def _propia(script: str | Path | None) -> Path | None:
    if not script:
        return None
    p = Path(script).resolve().parent
    while p.name and p.name != "scripts":
        p = p.parent
    return p.parent if p.name == "scripts" else None


def resolver(repo: str | Path = ".", script: str | Path | None = None) -> str:
    """Carpeta del pack relativa a `repo` (con «/»)."""
    repo = Path(repo).resolve()
    propia = _propia(script)
    if propia is not None and nombre_valido(propia.name):
        try:
            return propia.relative_to(repo).as_posix()
        except ValueError:
            pass
    for prueba in (lambda c: (repo / c / LOCK).is_file(), lambda c: (repo / c).is_dir()):
        for c in CARPETAS:
            if prueba(c):
                return c
    return CARPETA


def desde_argumento(valor: str | None, repo: str | Path = ".", script: str | Path | None = None, entorno: str | None = None) -> str:
    """Lo que vale `--docs`: el indicado, o el de la variable de entorno (si se nombra), o el deducido."""
    return (valor or (os.environ.get(entorno, "") if entorno else "") or resolver(repo, script)).strip("/")


def relativa(ruta: str, carpeta: str | Path | None = None) -> str:
    """Ruta escrita en una ficha («docs/10-guias/x.md», «uxyngraphar/10-guias/x.md» o «10-guias/x.md») → relativa a la carpeta del pack."""
    r = ruta.strip().strip("`").replace("\\", "/")
    nombres = {*CARPETAS, *([Path(str(carpeta)).as_posix().strip("/"), Path(str(carpeta)).name] if carpeta else [])}
    for n in sorted(nombres, key=len, reverse=True):
        if n and r.startswith(n + "/"):
            return r[len(n) + 1:]
    return r
