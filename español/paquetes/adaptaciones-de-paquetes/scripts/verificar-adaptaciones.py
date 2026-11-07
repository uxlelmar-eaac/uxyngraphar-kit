#!/usr/bin/env python3
"""Verifica los ajustes locales contra los paquetes instalados. Código 0 = sin errores."""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import adaptaciones_datos as datos  # noqa: E402


def main() -> int:
    errores, avisos = [], []
    for f, fm, _ in datos.ajustes():
        if fm.get("paquete") in datos.VACIO or fm.get("paquete") == "id-del-paquete":
            (errores if f.status == "activo" else avisos).append(f"{f.id}: falta «paquete» (id del paquete instalado)")
            continue
        if f.status == "retirado":
            continue
        estado = datos.estado_ajuste(fm)
        if estado == "sin paquete":
            avisos.append(f"{f.id}: el paquete «{fm.get('paquete')}» o su archivo «{fm.get('aplica_a')}» no está instalado")
        elif f.status == "activo" and estado == "por revisar":
            avisos.append(f"{f.id}: {fm.get('paquete')}/{fm.get('aplica_a')} cambió desde que se aprobó; una persona lo revisa "
                          f"(adaptaciones.py aprobar-ajuste {f.id} --humano) o lo retira")
    for a in avisos:
        print(f"aviso: {a}")
    for e in errores:
        print(f"error: {e}", file=sys.stderr)
    print(f"adaptaciones-de-paquetes: {len(errores)} errores, {len(avisos)} avisos")
    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main())
