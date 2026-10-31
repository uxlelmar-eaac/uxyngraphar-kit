#!/usr/bin/env python3
"""Mide el costo en tokens (estimado: ~4 caracteres por token) de lo que lee un agente.

Uso:  python3 docs/scripts/presupuesto.py arranque [--repo .]     # AGENTES.md + ESTADO.md (límite 1500)
      python3 docs/scripts/presupuesto.py instruccion <id>        # paquete de contexto de una instrucción
      python3 docs/scripts/presupuesto.py pack [--top 15]         # los documentos más pesados
Salida: 1 si se supera el límite (arranque: 1500; instrucción: --max-tokens / UXYNGRAPHAR_MAX_TOKENS, 12000)
o si la instrucción incumple R-21 (alcance de código).
Variable de entorno: UXYNGRAPHAR_MAX_TOKENS (se acepta uxyngraphar_MAX_TOKENS como alias de respaldo).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "tokens"))

import medir  # noqa: E402
from paquete import construir, localizar_instruccion  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("modo", choices=("arranque", "instruccion", "pack"))
    ap.add_argument("ref", nargs="?", default="")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--max-tokens", type=int, default=int(os.environ.get("UXYNGRAPHAR_MAX_TOKENS") or os.environ.get("uxyngraphar_MAX_TOKENS") or "12000"))
    ap.add_argument("--top", type=int, default=15)
    a = ap.parse_args(argv)
    repo = Path(a.repo).resolve()
    if a.modo == "arranque":
        filas = medir.arranque(repo, a.docs)
        for rel, t in filas:
            print(f"{t:>6}  {rel}")
        total = sum(t for _, t in filas)
        print(f"{total:>6}  TOTAL arranque (límite {medir.ARRANQUE_MAX})")
        return 1 if total > medir.ARRANQUE_MAX else 0
    if a.modo == "pack":
        for rel, t in medir.pesados(repo / a.docs if (repo / a.docs).is_dir() else repo, a.top):
            print(f"{t:>6}  {rel}")
        return 0
    ficha = localizar_instruccion(repo / a.docs, a.ref)
    if ficha is None:
        print(f"ERROR: no se encontró la instrucción «{a.ref}»", file=sys.stderr)
        return 2
    paq = construir(repo / a.docs, ficha, a.max_tokens, repo)
    for p in paq.partes:
        print(f"{p.tokens:>6}  {p.titulo}")
    print(f"{paq.total:>6}  TOTAL (presupuesto {a.max_tokens})" + (f" · {len(paq.omitidas)} omitida(s)" if paq.omitidas else ""))
    for b in paq.bloqueos:
        print(f"BLOQUEADO (R-21): {b}")
    return 1 if paq.omitidas or paq.bloqueos else 0


if __name__ == "__main__":
    raise SystemExit(main())
