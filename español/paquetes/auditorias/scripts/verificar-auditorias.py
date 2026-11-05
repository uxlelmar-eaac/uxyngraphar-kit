#!/usr/bin/env python3
"""Verifica hallazgos de auditorías: severidad válida, evidencia presente y findings_count correcto. Código 0 = sin errores."""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
sys.path.insert(0, str(Path(__file__).resolve().parent))

import uxyn_base as base  # noqa: E402
import uxyn_fichas as fichas  # noqa: E402

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)


def filas_hallazgos(cuerpo: str) -> list[list[str]]:
    dentro, filas = False, []
    for linea in cuerpo.splitlines():
        if linea.startswith("## "):
            dentro = linea.strip().lower() == "## hallazgos"
            continue
        if dentro and linea.startswith("|"):
            celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
            if celdas and celdas[0] not in ("#", "") and not set(celdas[0]) <= set("-: "):
                filas.append(celdas)
    return filas


def main() -> int:
    severidades = set(base.leer_ajustes(PAQUETE).get("severidades", []))
    trabajo = base.carpeta_trabajo(PAQUETE, crear=False)
    errores, avisos = [], []
    for f in fichas.listar(PAQUETE, "auditoria"):
        fm, cuerpo = base.leer_frontmatter(f.ruta.read_text(encoding="utf-8"))
        rel = f.ruta.relative_to(trabajo).as_posix()
        filas = filas_hallazgos(cuerpo)
        for celdas in filas:
            if len(celdas) < 4 or celdas[1].lower() not in severidades:
                errores.append(f"{rel}: hallazgo {celdas[0]} sin severidad válida ({', '.join(sorted(severidades))})")
            elif not celdas[3]:
                errores.append(f"{rel}: hallazgo {celdas[0]} sin evidencia")
        declarado = str(fm.get("findings_count", "0"))
        if declarado.isdigit() and int(declarado) != len(filas):
            (errores if f.status == "cerrada" else avisos).append(f"{rel}: findings_count={declarado} pero hay {len(filas)} hallazgos")
    for a in avisos:
        print(f"aviso: {a}")
    for e in errores:
        print(f"error: {e}", file=sys.stderr)
    print(f"auditorias: {len(errores)} errores, {len(avisos)} avisos")
    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main())
