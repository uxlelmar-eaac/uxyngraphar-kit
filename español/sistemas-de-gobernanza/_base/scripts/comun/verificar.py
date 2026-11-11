#!/usr/bin/env python3
"""Verificación genérica del sistema: integridad, fichas y memorias del trabajo, límites y permisos. Código 0 = sin errores.

Los avisos no hacen fallar. Las verificaciones propias del tema van en otros scripts listados en «verificaciones».
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el sistema es inmutable: ni cachés dentro
sys.path.insert(0, str(Path(__file__).resolve().parent))

import uxyn_base as base  # noqa: E402
import uxyn_fichas as fichas  # noqa: E402
import uxyn_memorias as memorias  # noqa: E402
import uxyn_permisos as permisos  # noqa: E402


def main() -> int:
    sistema = base.carpeta_sistema(Path(__file__).resolve().parent)
    informe = base.comprobar_integridad(sistema)
    errores = [f"integridad {k}: {v}" for k, vs in informe.items() for v in vs]
    e, avisos = fichas.validar(sistema)
    errores += e
    for modulo in (memorias, permisos):
        e, a = modulo.validar(sistema)
        errores += e
        avisos += a
    for a in avisos:
        print(f"aviso: {a}")
    for err in errores:
        print(f"error: {err}", file=sys.stderr)
    nombre = base.leer_manifiesto(sistema)["id"]
    print(f"{nombre}: {len(errores)} errores, {len(avisos)} avisos")
    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main())
