"""Validación de rutas de la sesión antes de escribir — revisión de pendientes.

Extraído de `applier.py` (R-19: nomenclatura relacional `<raiz>_<relacion>.py`).
`sesion-activa.json` es un archivo editable: ningún `docs_root`/`path` que provenga
de él se usa sin comprobar que cae dentro de una raíz de documentación configurada.
"""

from __future__ import annotations

from pathlib import Path, PureWindowsPath

from common import resolve_docs_roots


class RutaInsegura(ValueError):
    """La ruta de una decisión sale de las raíces de documentación permitidas."""


def raices_permitidas() -> list[Path]:
    return [root.resolve() for root, _ in resolve_docs_roots()]


def resolver_dentro(docs_root: str, rel: str, permitidas: list[Path]) -> Path:
    """Devuelve `docs_root/rel` resuelto, o lanza `RutaInsegura` si escapa de la raíz."""
    if not docs_root or not rel:
        raise RutaInsegura("docs_root o path vacío en la decisión")
    root = Path(docs_root).resolve()
    if root not in permitidas:
        raise RutaInsegura(f"docs_root fuera de las raíces configuradas: {root}")
    for flavor in (Path(rel), PureWindowsPath(rel)):
        if flavor.is_absolute() or flavor.anchor or ".." in flavor.parts:
            raise RutaInsegura(f"path no relativo o con '..': {rel}")
    target = (root / rel).resolve()
    if not target.is_relative_to(root):
        raise RutaInsegura(f"path escapa de la raíz (¿enlace simbólico?): {rel}")
    return target
