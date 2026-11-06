#!/usr/bin/env python3
"""Verifica los contratos (id compartido, rol, ruta) y los compara con los repos hermanos presentes. Código 0 = sin errores."""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import contratos_datos as datos  # noqa: E402


def main() -> int:
    errores, avisos = datos.problemas_propios()
    divergencias, mas = datos.comparar()
    errores += divergencias
    avisos += mas
    for a in avisos:
        print(f"aviso: {a}")
    for e in errores:
        print(f"error: {e}", file=sys.stderr)
    print(f"contratos-entre-repositorios: {len(errores)} errores, {len(avisos)} avisos")
    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main())
