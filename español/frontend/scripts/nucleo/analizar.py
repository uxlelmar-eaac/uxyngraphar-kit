"""Análisis de adopción: dónde encajaría la documentación que un proyecto ya tiene en la taxonomía de uxyngraphar."""

from __future__ import annotations

import re
from pathlib import Path

# (patrón sobre la ruta/nombre en minúsculas, destino sugerido). Heurística: orientativa, siempre la confirma un humano.
REGLAS = [
    (r"adr|decision|decisión", "20-decisiones/ (ADR)"),
    (r"runbook|despliegue|deploy|incidente|operacion|operación|ops", "30-manuales/"),
    (r"api|endpoint|ruta|route|openapi|swagger", "15-rutas/ (fichas de endpoints)"),
    (r"arquitectura|architecture|diseno|diseño|design", "00-nucleo/arquitectura.md (plantilla P) o 25-areas/"),
    (r"modulo|módulo|module|dominio|domain|area|área", "25-areas/<id>/CONTEXTO.md"),
    (r"auditoria|auditoría|audit|informe|report", "40-auditorias/"),
    (r"todo|roadmap|backlog|mejora|deuda|debt|idea", "45-mejoras-propuestas/"),
    (r"readme|changelog|licen|contribut", "(se queda donde está: no es documentación del sistema)"),
]
IGNORAR = ("node_modules", ".git", "dist", "build", "vendor")


def analizar(repo: Path, docs: str = "docs") -> dict[str, list[str]]:
    """Agrupa los .md existentes (fuera de node_modules, etc.) por destino sugerido; 'sin-sugerencia' si nada encaja."""
    res: dict[str, list[str]] = {}
    for md in sorted(repo.rglob("*.md")):
        rel = md.relative_to(repo)
        if any(p in IGNORAR for p in rel.parts) or rel.parts[0] == ".claude":
            continue
        clave = "sin-sugerencia"
        for patron, destino in REGLAS:
            if re.search(patron, rel.as_posix().lower()):
                clave = destino
                break
        res.setdefault(clave, []).append(rel.as_posix())
    return res


def formatear(res: dict[str, list[str]]) -> str:
    if not res:
        return "No hay documentación .md previa: instala sin --adoptar."
    l = ["Documentación existente y dónde encajaría (sugerencias; no se movió nada):", ""]
    for destino, archivos in sorted(res.items(), key=lambda kv: (kv[0] == "sin-sugerencia", kv[0])):
        l.append(f"{destino}  ({len(archivos)})")
        l += [f"  - {a}" for a in archivos[:8]] + ([f"  … y {len(archivos) - 8} más"] if len(archivos) > 8 else [])
    l += ["", "Siguiente paso: instalar con --adoptar y crear una instrucción `adoptar` que migre lo que apruebes."]
    return "\n".join(l)
