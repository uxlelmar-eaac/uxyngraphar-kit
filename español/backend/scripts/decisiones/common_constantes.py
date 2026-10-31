"""Constantes y expresiones regulares compartidas — revisión de pendientes.

Extraído de `common.py` (R-19: nomenclatura relacional `<raiz>_<relacion>.py`).
No importa ningún otro módulo del paquete para evitar ciclos.
"""

from __future__ import annotations

import re

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
DECISION_GROUP_RE = re.compile(r"<!--\s*decision-group:\s*([^>]+?)\s*-->")
DECISION_OPTION_RE = re.compile(
    r"^-\s*\[([ xX])\]\s*(?:<!--\s*decision:([a-zA-Z0-9_-]+)\s*-->\s*)?(.*)$"
)
TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
FM_KEY_RE = re.compile(r"^([a-zA-Z0-9_]+):\s*(.*)$")

DECISION_SECTION_RE = re.compile(
    r"^##\s+(Decisión a tomar|Decisión humana|Decisiones a tomar)\s*$",
    re.MULTILINE,
)

DEFAULT_OPTIONS: dict[str, list[tuple[str, str]]] = {
    "instruccion": [("aprobar", "Aprobar"), ("cancelar", "Cancelar")],
    "herramienta": [("promover", "Promover"), ("rechazar", "Rechazar")],
    "mejora": [("aprobar", "Aprobar"), ("posponer", "Posponer"), ("rechazar", "Rechazar")],
    "adr": [("aceptar", "Aceptar"), ("obsoleta", "Obsoleta"), ("rechazar", "Rechazar")],
    "auditoria": [("aprobar", "Promover"), ("posponer", "Posponer"), ("rechazar", "Rechazar")],
    "evolucion": [("aprobar", "Aprobar"), ("posponer", "Posponer"), ("rechazar", "Rechazar")],
}

STATUS_MAP: dict[str, dict[str, str]] = {
    "instruccion": {"aprobar": "approved", "cancelar": "cancelled", "eliminar": "para-eliminar"},
    "herramienta": {"promover": "promovida", "rechazar": "rejected", "eliminar": "para-eliminar"},
    "mejora": {"aprobar": "approved", "rechazar": "rejected", "eliminar": "para-eliminar"},
    "adr": {"aceptar": "aceptada", "obsoleta": "obsoleta", "rechazar": "rechazada", "eliminar": "para-eliminar"},
    "auditoria": {"aprobar": "cerrada", "rechazar": "cancelada", "eliminar": "para-eliminar"},
    "evolucion": {"aprobar": "approved", "rechazar": "rejected", "eliminar": "para-eliminar"},
}

# Organización por estados y fechas (R-17) — ver 10-guias/organizacion-estados-fechas.md
ESTADOS: list[str] = [
    "01-pendientes",
    "02-en-progreso",
    "03-completadas",
    "04-archivadas",
    "05-canceladas",
    "06-listas-para-eliminar",
]
ESTADO_RE = re.compile(
    r"^(01-pendientes|02-en-progreso|03-completadas|04-archivadas|05-canceladas|06-listas-para-eliminar)$"
)
DATE_FOLDER_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Acción → carpeta de estado destino (sin estado = no mover)
MOVE_ACTIONS: dict[tuple[str, str], str] = {
    ("instruccion", "aprobar"): "02-en-progreso",
    ("instruccion", "cancelar"): "05-canceladas",
    ("mejora", "aprobar"): "02-en-progreso",
    ("mejora", "rechazar"): "05-canceladas",
    ("evolucion", "aprobar"): "02-en-progreso",
    ("evolucion", "rechazar"): "05-canceladas",
    ("herramienta", "promover"): "03-completadas",
    ("herramienta", "rechazar"): "05-canceladas",
    ("adr", "aceptar"): "03-completadas",
    ("adr", "obsoleta"): "04-archivadas",
    ("adr", "rechazar"): "05-canceladas",
    ("auditoria", "aprobar"): "03-completadas",
    ("auditoria", "rechazar"): "05-canceladas",
}
ELIMINAR_ESTADO = "06-listas-para-eliminar"

# Enums de frontmatter (fuente: 00-nucleo/frontmatter/<tipo>.md). Los usan el validador y el andamiaje.
_PRIORIDAD = frozenset({"ahora", "despues", "algun-dia"})
ENUMS_FICHA: dict[str, dict[str, frozenset[str]]] = {
    "mejora": {
        "tipo": frozenset({"deuda-tecnica", "refactor", "diseno", "tests", "docs", "perf", "seguridad", "bug"}),
        "severidad": frozenset({"baja", "media", "alta"}),
        "prioridad": _PRIORIDAD,
    },
    "evolucion": {
        "tipo": frozenset({"cobertura", "proceso", "taxonomia", "plantilla", "herramienta-pack"}),
        "impacto": frozenset({"general", "servidor", "cliente", "ambos"}),
        "prioridad": _PRIORIDAD,
    },
    "instruccion": {
        "acto": frozenset({"crear", "editar", "corregir", "mejorar-docs", "auditar", "adoptar", "operar", "revisar-pendientes"}),
    },
    "auditoria": {"severidad": frozenset({"baja", "media", "alta", "critica"})},
}
