"""Clasificación por archivo de lo que contiene un pack (fuente única de la frontera núcleo/proyecto).

Clases:
  N  núcleo: reglas, plantillas, guías y scripts; el proyecto no los edita (se reemplazan al actualizar).
  P  plantilla a rellenar: se instala una vez; nunca se sobrescribe (el proyecto la completa).
  M  mixto: índices con filas del proyecto; se instalan una vez; nunca se sobrescriben.
  C  contenido del proyecto: fichas, instrucciones, rutas, espejo…; jamás se instala ni se toca.
  X  fuera de instalación: artefactos locales (cachés, sesiones, lock, copias .uxyngraphar-nuevo) y PARIDAD-PACKS.md (solo sirve en el repo fuente).
"""

from __future__ import annotations

import re

CLASES = ("N", "P", "M", "C", "X")
ESTADO = r"0[1-6]-[a-z-]+"
FECHA = r"\d{4}-\d{2}-\d{2}"
SECCIONES_ESTADO = r"(?:05-instrucciones|20-decisiones|35-herramientas/propuestas|40-auditorias|45-mejoras-propuestas|46-evolucion-documentacion)"

# El orden importa: gana la primera regla que coincide.
REGLAS: list[tuple[str, str]] = [
    (r"(?:.*/)?__pycache__/.*|PARIDAD-PACKS\.md|uxyngraphar-manifiesto\.json|\.uxyngraphar\.lock|.*\.uxyngraphar-nuevo|\.depuracion/.*|.*\.pyc|\.decisiones/.*|\.gitignore", "X"),
    # README de cada carpeta de estado: esqueleto del pack.
    (rf"{SECCIONES_ESTADO}/{ESTADO}/(?:{FECHA}/)?README\.md", "N"),
    # Fichas vivas dentro de las colas.
    (rf"{SECCIONES_ESTADO}/{ESTADO}/{FECHA}/.+", "C"),
    (r"(?:.*/)?_(?:PLANTILLA|PROTOCOLO)[^/]*", "N"),
    (r"(?:00-nucleo|10-guias)/INDICE\.md|00-nucleo/frontmatter/INDICE\.md", "N"),
    (r"00-nucleo/(?:configuracion-proyecto|arquitectura|restricciones|registro-ids-compartidos|mapa-dependencias|glosario-dominio)\.md", "P"),
    (r"46-evolucion-documentacion/matriz-cobertura-proyectos\.md|50-sistema-integral/registro-cobertura-espejo\.md|uxyngraphar\.config\.json|ESTADO\.md|30-manuales/(?!INDICE).+|40-auditorias/activas\.md", "P"),
    (r"(?:.*/)?INDICE\.md|README\.md|35-herramientas/(?:autorizadas|propuestas)/README\.md", "M"),
    (r"35-herramientas/autorizadas/decisiones-pendientes\.md", "N"),
    (r"(?:AGENTES|AGENTS|REGLAS|PROTOCOLO|VERSION|CHANGELOG)\.md|!00_.*\.html|90-archivo/capacitacion/README\.md|(?:00-nucleo|10-guias|55-automatizaciones|scripts)/.+|50-sistema-integral/(?:mapa-capas|vision-espejo)\.md", "N"),
    (r"(?:15-rutas|25-areas|35-herramientas/(?:autorizadas|propuestas)|40-auditorias|45-mejoras-propuestas|46-evolucion-documentacion|50-sistema-integral|90-archivo|95-memoria|96-reglas-proyecto|97-ajustes-locales|20-decisiones|05-instrucciones)/.+", "C"),
]
_COMPILADAS = [(re.compile(p), c) for p, c in REGLAS]
# Archivos que se instalan fuera de docs/ (raíz del repo del proyecto).
EN_RAIZ = ("AGENTES.md", "AGENTS.md")


def clasificar(rel: str) -> str | None:
    """Clase del archivo (ruta relativa al pack, con «/»). None si ninguna regla lo cubre."""
    rel = rel.replace("\\", "/")
    if rel.startswith("./"):
        rel = rel[2:]
    for patron, clase in _COMPILADAS:
        if patron.fullmatch(rel):
            return clase
    return None


def padre(docs: str) -> str:
    """Carpeta que contiene a `docs/` (la «raíz de la app»): "" en un repo normal, «apps/api» si docs=«apps/api/docs»."""
    d = docs.strip("/")
    return d.rpartition("/")[0]


def destino(rel: str, docs: str = "docs") -> str:
    """Ruta destino en el repo del proyecto. AGENTES.md/AGENTS.md van junto a `docs/` (en la raíz del repo, o en la carpeta de la app)."""
    if rel in EN_RAIZ:
        p = padre(docs)
        return f"{p}/{rel}" if p else rel
    return f"{docs.strip('/')}/{rel}"


def origen(ruta_repo: str, docs: str = "docs") -> str | None:
    """Inversa de `destino`: ruta del repo → ruta relativa al pack (None si no pertenece al pack)."""
    p = padre(docs)
    docs = docs.strip("/") + "/"
    if ruta_repo in [f"{p}/{n}" if p else n for n in EN_RAIZ]:
        return ruta_repo.rpartition("/")[2]
    return ruta_repo[len(docs):] if ruta_repo.startswith(docs) else None
