"""`uxyngraphar andamiar`: crea en el proyecto la estructura del andamiaje de un sistema instalado. Nunca sobrescribe.

Usa la misma lógica que el script portable del sistema (`scripts/comun/andamiar.py`), así que da igual lanzarlo desde
el motor o desde el sistema.
"""

from __future__ import annotations

from pathlib import Path

import especificacion as esp
import andamiar  # noqa: E402,I001  scripts/comun/ de sistemas-de-gobernanza/_base: lo pone en sys.path especificacion

base = esp.base


def sistema_instalado(raiz_app: Path, pid: str) -> Path:
    carpeta = Path(raiz_app).resolve() / base.CARPETA_SISTEMAS_DE_GOBERNANZA / pid
    if not (carpeta / base.MANIFIESTO).is_file():
        raise FileNotFoundError(f"«{pid}» no está instalado en {raiz_app}")
    return carpeta


def variantes(raiz_app: Path, pid: str) -> dict:
    return andamiar.variantes(sistema_instalado(raiz_app, pid))


def simular(raiz_app: Path, pid: str, variante: str, nombre: str) -> list[tuple[str, bool]]:
    raiz = Path(raiz_app).resolve()
    return [(final.relative_to(raiz).as_posix(), existe)
            for final, _, existe in andamiar.plan(sistema_instalado(raiz, pid), variante, nombre, raiz)]


def aplicar(raiz_app: Path, pid: str, variante: str, nombre: str) -> tuple[list[str], list[str]]:
    raiz = Path(raiz_app).resolve()
    creados, omitidos = andamiar.aplicar(sistema_instalado(raiz, pid), variante, nombre, raiz)
    return [f.relative_to(raiz).as_posix() for f in creados], [f.relative_to(raiz).as_posix() for f in omitidos]
