"""Resumen vivo del trabajo (ESTADO.md autogenerado): se lee una vez en lugar de recorrer colas e índices."""

from __future__ import annotations

import argparse
import re
from datetime import date, datetime, timezone
from pathlib import Path

from common import resolve_docs_roots
from metricas import fichas

INI, FIN = "<!-- uxyngraphar:estado:inicio -->", "<!-- uxyngraphar:estado:fin -->"
MAX = 10


def _titulo(docs: Path, f: dict) -> str:
    m = re.search(r"^#\s+(.+)$", (docs / f["path"]).read_text(encoding="utf-8", errors="replace"), re.M)
    t = (m.group(1) if m else f["id"]).strip()
    return t if len(t) <= 70 else t[:67] + "…"


def _bloque(docs: Path, titulo: str, items: list[dict]) -> list[str]:
    l = [f"**{titulo} ({len(items)}):**"]
    l += [f"- `{f['id']}` — {_titulo(docs, f)} ({f['fecha']})" for f in items[:MAX]] or ["- —"]
    if len(items) > MAX:
        l.append(f"- … y {len(items) - MAX} más")
    return l + [""]


def generar(docs: Path, hoy: date | None = None) -> str:
    hoy = hoy or datetime.now(timezone.utc).date()
    fs = fichas(docs)
    ins = [f for f in fs if f["tipo"] == "instruccion"]
    curso = sorted((f for f in ins if f["estado"] == "02-en-progreso"), key=lambda f: f["fecha"])
    esperan = sorted((f for f in ins if f["estado"] == "01-pendientes" and f["status"] == "awaiting_approval"), key=lambda f: f["fecha"])
    cerradas = sorted((f for f in ins if f["estado"] == "03-completadas"), key=lambda f: f["fecha"], reverse=True)
    colas = {"45 mejoras": "45-mejoras-propuestas", "46 evolución": "46-evolucion-documentacion", "35 propuestas": "35-herramientas/propuestas"}
    pend = " · ".join(f"{n}: {sum(1 for f in fs if f['estado'] == '01-pendientes' and f['path'].startswith(r + '/'))}" for n, r in colas.items())
    l = [INI, f"_Generado por `decisiones.py estado` el {hoy.isoformat()}; no editar entre las marcas._", ""]
    l += _bloque(docs, "En curso", curso) + _bloque(docs, "Esperan aprobación", esperan) + [f"**Pendientes por cola:** {pend}", ""]
    l += _bloque(docs, "Cerradas recientes", cerradas[:5])
    return "\n".join(l).rstrip() + "\n" + FIN


def escribir(docs: Path, bloque: str) -> Path:
    f = docs / "ESTADO.md"
    texto = f.read_text(encoding="utf-8") if f.is_file() else "# Estado del proyecto\n\n"
    if INI in texto and FIN in texto:
        nuevo = texto[: texto.index(INI)] + bloque + texto[texto.index(FIN) + len(FIN):]
    else:
        nuevo = texto.rstrip("\n") + "\n\n" + bloque + "\n"
    f.write_text(nuevo, encoding="utf-8", newline="\n")
    return f


def cmd_estado(args: argparse.Namespace) -> int:
    docs = Path(args.docs).resolve() if args.docs else resolve_docs_roots()[0][0]
    bloque = generar(docs)
    if args.escribir:
        print(f"ESTADO.md actualizado: {escribir(docs, bloque)}")
    else:
        print(bloque)
    return 0
