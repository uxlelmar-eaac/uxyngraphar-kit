#!/usr/bin/env python3
"""Avisa de las fichas que llevan más de «dias_aviso» días esperando una decisión de una persona. Nunca falla por eso."""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import pendientes as pend  # noqa: E402
import uxyn_base as base  # noqa: E402


def main() -> int:
    limite = int(base.leer_ajustes(pend.PAQUETE).get("dias_aviso", 14))
    lista = pend.recoger()
    viejas = [p for p in lista if p.dias > limite]
    for p in viejas:
        print(f"aviso: {p.paquete}/{p.id} lleva {p.dias} días en «{p.status}» esperando a una persona")
    print(f"revision-humana: {len(lista)} pendientes de decisión, {len(viejas)} con más de {limite} días")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
