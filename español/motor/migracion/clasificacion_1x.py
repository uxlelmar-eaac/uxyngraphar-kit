"""Clasificación de archivos de un pack 1.x (copia congelada de la regla 1.2.x; solo la usa la migración).

Clases:
  N  núcleo 1.x: lo sustituyen los paquetes 2.0.
  P  plantilla rellenada por el proyecto.
  M  índice mixto con filas del proyecto.
  C  contenido del proyecto (fichas, rutas, espejo…).
  X  artefacto local (lock, sesiones, tokens de aprobación, cachés).
"""

from __future__ import annotations

import re

ESTADO = r"0[1-6]-[a-z-]+"
FECHA = r"\d{4}-\d{2}-\d{2}"
SECCIONES_ESTADO = r"(?:03-preguntas|05-instrucciones|20-decisiones|35-herramientas/propuestas|40-auditorias|45-mejoras-propuestas|46-evolucion-documentacion)"
EN_RAIZ = ("AGENTES.md", "AGENTS.md")

# El orden importa: gana la primera regla que coincide.
REGLAS: list[tuple[str, str]] = [
    (r"(?:.*/)?__pycache__/.*|PARIDAD-PACKS\.md|uxyngraphar-manifiesto\.json|\.uxyngraphar\.lock|.*\.uxyngraphar-nuevo|\.depuracion/.*|.*\.pyc|\.decisiones/.*|\.gitignore", "X"),
    (rf"{SECCIONES_ESTADO}/{ESTADO}/(?:{FECHA}/)?README\.md", "N"),
    (rf"{SECCIONES_ESTADO}/{ESTADO}/{FECHA}/.+", "C"),
    (r"(?:.*/)?_(?:PLANTILLA|PROTOCOLO)[^/]*", "N"),
    (r"(?:00-nucleo|10-guias)/INDICE\.md|00-nucleo/frontmatter/INDICE\.md", "N"),
    (r"00-nucleo/(?:configuracion-proyecto|arquitectura|restricciones|registro-ids-compartidos|mapa-dependencias|glosario-dominio)\.md", "P"),
    (r"46-evolucion-documentacion/matriz-cobertura-proyectos\.md|50-sistema-integral/registro-cobertura-espejo\.md|uxyngraphar\.config\.json|ESTADO\.md|30-manuales/(?!INDICE).+|40-auditorias/activas\.md", "P"),
    (r"(?:.*/)?INDICE\.md|README\.md|35-herramientas/(?:autorizadas|propuestas)/README\.md", "M"),
    (r"35-herramientas/autorizadas/decisiones-pendientes\.md", "N"),
    (r"(?:AGENTES|AGENTS|REGLAS|PROTOCOLO|VERSION|CHANGELOG)\.md|!00_.*\.html|90-archivo/capacitacion/README\.md|(?:00-nucleo|10-guias|55-automatizaciones|scripts)/.+|50-sistema-integral/(?:mapa-capas|vision-espejo)\.md", "N"),
    (r"(?:15-rutas|25-areas|35-herramientas/(?:autorizadas|propuestas)|40-auditorias|45-mejoras-propuestas|46-evolucion-documentacion|50-sistema-integral|90-archivo|95-memoria|96-reglas-proyecto|97-ajustes-locales|20-decisiones|05-instrucciones|03-preguntas)/.+", "C"),
]
_COMPILADAS = [(re.compile(p), c) for p, c in REGLAS]


def clasificar(rel: str) -> str | None:
    """Clase del archivo (ruta relativa al pack, con «/»). None si ninguna regla lo cubre."""
    rel = rel.replace("\\", "/").removeprefix("./")
    return next((c for patron, c in _COMPILADAS if patron.fullmatch(rel)), None)
