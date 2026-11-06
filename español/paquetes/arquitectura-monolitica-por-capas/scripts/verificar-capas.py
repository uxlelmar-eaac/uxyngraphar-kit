#!/usr/bin/env python3
"""Verifica los imports contra las capas del perfil. Con «nivel: aviso» (por defecto) solo avisa; con «bloqueante», falla."""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import capas_datos as datos  # noqa: E402


def main() -> int:
    ajustes = datos.ajustes()
    errores = []
    if not ajustes["capas"]:
        errores.append(f"perfil «{ajustes.get('perfil')}» sin capas en «perfiles»")
    infracciones = [f"{i.archivo}:{i.linea}: {i.motivo}" for i in datos.revisar()]
    bloquea = ajustes.get("nivel") == "bloqueante"
    for i in infracciones if not bloquea else []:
        print(f"aviso: {i}")
    for e in errores + (infracciones if bloquea else []):
        print(f"error: {e}", file=sys.stderr)
    total = len(errores) + (len(infracciones) if bloquea else 0)
    print(f"arquitectura-monolitica-por-capas: {total} errores, {0 if bloquea else len(infracciones)} avisos")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
