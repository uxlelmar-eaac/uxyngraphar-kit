"""Validación de acciones de decisión — revisión de pendientes.

Extraído de `session.py` (R-19: nomenclatura relacional `<raiz>_<relacion>.py`).
Evita que una errata (`aprovar`) o una acción ajena al tipo quede «aplicada».
"""

from __future__ import annotations

from typing import Any

from common import DEFAULT_OPTIONS, STATUS_MAP

ACCIONES_GLOBALES = frozenset({"posponer", "eliminar"})


def acciones_validas(tipo: str, extra: list[str] | None = None) -> set[str]:
    base = {a for a, _ in DEFAULT_OPTIONS.get(tipo, [])}
    base |= set(STATUS_MAP.get(tipo, {}))
    base |= ACCIONES_GLOBALES
    base |= set(extra or [])
    return base


def error_de_accion(tipo: str, action: str, opciones: list[str] | None = None) -> str | None:
    """Mensaje de error si `action` no es válida para `tipo`; `None` si lo es."""
    if not tipo:
        return "tipo de ficha desconocido"
    validas = acciones_validas(tipo, opciones)
    if action not in validas:
        return f"acción '{action}' no válida para {tipo}; válidas: {', '.join(sorted(validas))}"
    return None


def opciones_de_item(item: dict[str, Any] | None) -> list[str]:
    return [str(o.get("action")) for o in (item or {}).get("options", []) if o.get("action")]
