#!/usr/bin/env python3
"""Reglas del proyecto (96-reglas-proyecto/): listar, validar y regenerar INDICE.md.

Uso:  python3 docs/scripts/reglas.py listar              # reglas activas (id, nivel, aplica_a, resumen)
      python3 docs/scripts/reglas.py validar             # frontmatter de todas las reglas e índice al día
      python3 docs/scripts/reglas.py indice              # regenera la tabla de INDICE.md desde las reglas activas
Crear, editar o retirar una regla exige aprobación humana explícita (instrucción aprobada que la ancle). Guía: 96-reglas-proyecto/_PROTOCOLO.md.
Salida: 0 · 1 si validar encuentra problemas.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "reglas"))

import reglas_proyecto as rp  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("orden", choices=("listar", "validar", "indice"))
    ap.add_argument("--repo", default=".")
    ap.add_argument("--docs", default="docs")
    a = ap.parse_args(argv)
    docs = Path(a.repo).resolve() / a.docs
    if a.orden == "listar":
        activas = rp.activas(docs)
        print("\n".join(rp.filas_indice(activas)) if activas else "Sin reglas activas.")
        return 0
    if a.orden == "indice":
        print("INDICE.md actualizado." if rp.regenerar_indice(docs) else "INDICE.md ya estaba al día.")
        return 0
    problemas = [f"{r.ruta.name}: {p}" for r in rp.todas(docs) for p in r.problemas]
    if not rp.indice_al_dia(docs):
        problemas.append("INDICE.md no cuadra con las reglas activas: python3 docs/scripts/reglas.py indice")
    print("\n".join(f"ERROR: {p}" for p in problemas) if problemas else "OK: reglas del proyecto válidas.")
    return 1 if problemas else 0


if __name__ == "__main__":
    raise SystemExit(main())
