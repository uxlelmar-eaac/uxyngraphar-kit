#!/usr/bin/env python3
"""Notas de memoria.

  python3 uxyngraphar/paquetes/notas-de-memoria/scripts/notas.py buscar <texto>   en la memoria (solo si el pedido lo pide)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import uxyn_base as base  # noqa: E402

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)


def buscar(texto: str) -> list[str]:
    trabajo = base.carpeta_trabajo(PAQUETE, crear=False)
    memoria = trabajo / "memoria"
    aguja = texto.lower()
    hallazgos = []
    for p in sorted(memoria.rglob("*.md")) if memoria.is_dir() else []:
        for n, linea in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if aguja in linea.lower():
                hallazgos.append(f"{p.relative_to(trabajo).as_posix()}:{n}: {linea.strip()[:160]}")
    return hallazgos


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    bu = sub.add_parser("buscar")
    bu.add_argument("texto")
    a = ap.parse_args(argv)
    try:
        for h in buscar(a.texto):
            print(h)
    except (ValueError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
