"""Exporta las fichas EVO de un proyecto (la cola 46 = buzón hacia el pack fuente) a un único informe para quien mantiene uxyngraphar."""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "decisiones"))

from common_frontmatter import split_frontmatter_parts, update_frontmatter_raw, rebuild_content  # noqa: E402

CAMPO = "exportada_al_pack"
POR_DEFECTO = ("pending", "approved")


def fichas(docs: Path, estados: tuple[str, ...] = POR_DEFECTO, incluir_exportadas: bool = False) -> list[tuple[Path, dict, str]]:
    raiz = docs / "46-evolucion-documentacion"
    salida = []
    for md in sorted(raiz.glob("0[1-6]-*/*/EVO-*.md")):
        raw, fm, cuerpo = split_frontmatter_parts(md.read_text(encoding="utf-8", errors="replace"))
        if raw is None or str(fm.get("status", "")) not in estados:
            continue
        if fm.get(CAMPO) and not incluir_exportadas:
            continue
        salida.append((md, fm, cuerpo))
    return salida


def _lista(valor: object) -> str:
    if isinstance(valor, list):
        return ", ".join(f"`{v}`" for v in valor) or "—"
    return f"`{valor}`" if valor else "—"


def informe(docs: Path, items: list[tuple[Path, dict, str]], proyecto: str, version: str) -> str:
    hoy = date.today().isoformat()
    l = [f"# Propuestas EVO de {proyecto} para uxyngraphar", "",
         f"Exportado el {hoy} · pack instalado {version} · {len(items)} ficha(s).", "",
         "| id | estado | tipo | impacto | prioridad | cambia en el pack |", "|----|--------|------|---------|-----------|-------------------|"]
    for _md, fm, _c in items:
        l.append(f"| {fm.get('id', '?')} | {fm.get('status', '?')} | {fm.get('tipo', '—')} | {fm.get('impacto', '—')} | "
                 f"{fm.get('prioridad', '—')} | {_lista(fm.get('propuesta_cambio'))} |")
    for md, fm, cuerpo in items:
        l += ["", f"## {fm.get('id', md.stem)}", "", f"Origen: `{md.relative_to(docs).as_posix()}`", "", re.sub(r"^# .*\n", "", cuerpo.strip() + "\n", count=1).strip()]
    return "\n".join(l) + "\n"


def marcar(items: list[tuple[Path, dict, str]], fecha: str | None = None) -> int:
    fecha = fecha or date.today().isoformat()
    for md, _fm, _c in items:
        raw, _f, cuerpo = split_frontmatter_parts(md.read_text(encoding="utf-8"))
        md.write_text(rebuild_content(update_frontmatter_raw(raw or "", {CAMPO: fecha}), cuerpo), encoding="utf-8", newline="\n")
    return len(items)
