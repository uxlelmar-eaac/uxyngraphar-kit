#!/usr/bin/env python3
"""Verificación genérica del paquete: integridad + fichas del trabajo. Código 0 = sin errores.

Los avisos no hacen fallar. Las verificaciones propias del tema van en otros scripts listados en «verificaciones».
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
sys.path.insert(0, str(Path(__file__).resolve().parent))

import uxyn_base as base  # noqa: E402
import uxyn_fichas as fichas  # noqa: E402


def main() -> int:
    paquete = base.carpeta_paquete(Path(__file__).resolve().parent)
    informe = base.comprobar_integridad(paquete)
    errores = [f"integridad {k}: {v}" for k, vs in informe.items() for v in vs]
    e, avisos = fichas.validar(paquete)
    errores += e
    for a in avisos:
        print(f"aviso: {a}")
    for err in errores:
        print(f"error: {err}", file=sys.stderr)
    nombre = base.leer_manifiesto(paquete)["id"]
    print(f"{nombre}: {len(errores)} errores, {len(avisos)} avisos")
    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main())
