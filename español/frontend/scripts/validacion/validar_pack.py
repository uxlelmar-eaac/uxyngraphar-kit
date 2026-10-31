"""Comprobaciones propias de cada variante del pack (cliente / servidor) y de decisiones pendientes."""

from __future__ import annotations

import re
from pathlib import Path

from validar_comun import Opciones, Pack, Reporte, iter_md

ENLACE_SERVIDOR_RE = re.compile(r"\.\./\.\./servidor/")
PROSA_SERVIDOR_RE = re.compile(r"igual que (el )?servidor|checklist servidor|plantilla completa en servidor", re.IGNORECASE)


def validar_cliente_autocontenido(pack: Pack, rep: Reporte, op: Opciones) -> None:
    """El pack cliente desplegado no debe depender del pack servidor."""
    if pack.tipo != "cliente":
        return
    enlaces: list[str] = []
    prosa: list[str] = []
    for md in iter_md(pack.docs):
        if md.name == "CHANGELOG.md":
            continue
        for n, linea in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            ref = f"{md.relative_to(pack.docs).as_posix()}:{n}"
            if ENLACE_SERVIDOR_RE.search(linea):
                enlaces.append(ref)
            if PROSA_SERVIDOR_RE.search(linea):
                prosa.append(ref)
    if enlaces:
        rep.segun(op.cliente, f"Enlaces ../../servidor/ en docs (el pack cliente debe ser autocontenido; STRICT_CLIENTE_STANDALONE=1 en CI): {', '.join(enlaces[:5])}")
    if prosa:
        rep.warn(f"Referencias en prosa al pack servidor — el pack cliente debe ser autocontenido: {', '.join(prosa[:5])}")


def validar_decisiones_antiguas(pack: Pack, rep: Reporte, op: Opciones) -> None:
    """Pendientes de revisión con más de N días (WARN; ERROR con STRICT_DECISIONES=1)."""
    decisiones = pack.docs / "scripts" / "decisiones"
    if not (decisiones / "scanner.py").is_file():
        return
    import sys

    if str(decisiones) not in sys.path:
        sys.path.insert(0, str(decisiones))
    from scanner import filter_stale, scan_all  # type: ignore[import-not-found]

    antiguas = filter_stale(scan_all([(Path(pack.docs), pack.docs.name)]), op.max_dias_decisiones)
    if antiguas:
        ids = ", ".join(i.id for i in antiguas[:5]) + ("…" if len(antiguas) > 5 else "")
        rep.segun(
            op.decisiones,
            f"{len(antiguas)} decisión(es) pendiente(s) con más de {op.max_dias_decisiones} días ({ids}) — revisar con: python3 scripts/decisiones/decisiones.py scan --max-days {op.max_dias_decisiones}",
        )
