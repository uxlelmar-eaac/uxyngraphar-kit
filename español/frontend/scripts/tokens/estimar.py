"""Estimación de tokens y extracción de fragmentos (sin dependencias; la estimación es aproximada: ~4 caracteres/token)."""

from __future__ import annotations

import re
import unicodedata
from math import ceil

CARACTERES_POR_TOKEN = 4


def tokens(texto: str) -> int:
    return ceil(len(texto) / CARACTERES_POR_TOKEN)


def slug(titulo: str) -> str:
    """Slug estilo GitHub: minúsculas, sin acentos ni signos, espacios → guiones."""
    s = unicodedata.normalize("NFKD", titulo.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[\s_]+", "-", re.sub(r"[^a-z0-9\s_-]", "", s)).strip("-")


def extraer_seccion(texto: str, ancla: str) -> str | None:
    """Sección cuyo encabezado tiene el slug `ancla`, hasta el siguiente encabezado del mismo nivel o superior."""
    lineas, objetivo = texto.splitlines(), slug(ancla)
    for i, l in enumerate(lineas):
        m = re.match(r"^(#{1,6})\s+(.*\S)\s*$", l)
        if m and slug(m.group(2)) == objetivo:
            nivel, fin = len(m.group(1)), len(lineas)
            for j in range(i + 1, len(lineas)):
                n = re.match(r"^(#{1,6})\s", lineas[j])
                if n and len(n.group(1)) <= nivel:
                    fin = j
                    break
            return "\n".join(lineas[i:fin]).rstrip() + "\n"
    return None


def limpiar(texto: str) -> str:
    """Quita comentarios HTML y líneas en blanco repetidas (no cambian el sentido para un agente)."""
    sin = re.sub(r"<!--.*?-->\n?", "", texto, flags=re.S)
    return re.sub(r"\n{3,}", "\n\n", sin)
