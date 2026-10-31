"""Promoción de propuestas a herramientas autorizadas — revisión de pendientes.

Extraído de `applier.py` (R-19: nomenclatura relacional `<raiz>_<relacion>.py`).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from common import find_section_root, utc_now_iso


def session_suffix() -> str:
    return utc_now_iso().replace(":", "").replace("-", "")[:15]


def _promote_herramienta(file_path: Path, fm: dict[str, Any], dry_run: bool) -> Path | None:
    section = find_section_root(file_path, "35-herramientas")
    if section is None:
        return None
    docs_root = section.parent
    autorizadas = section / "autorizadas"
    slug = str(fm.get("id", file_path.stem))
    dest = autorizadas / f"{slug}.md"
    if dest.exists():
        return dest

    title = slug.replace("-", " ").title()
    draft = f"""---
id: {slug}
status: draft
source: human
authorized_by: "(completar tras revisión)"
authorized_at: {utc_now_iso()[:10]}
scope: [ops]
anclas_codigo: []
presupuesto_max_docs: 2
promoted_from: {file_path.relative_to(docs_root).as_posix()}
---

# {title}

> Borrador generado por decisiones-pendientes desde propuesta. Completar alcance y cambiar `status: authorized`.

## Qué hace

(Copiar desde propuesta origen y adaptar.)

## Cuándo usar

- …

## Alcance permitido (excepción sin instrucción)

(Completar.)

## Anclas

| Recurso | Path |
|---------|------|
| Origen propuesta | `{file_path.name}` |
"""
    if dry_run:
        return dest
    autorizadas.mkdir(parents=True, exist_ok=True)
    dest.write_text(draft, encoding="utf-8")
    return dest
