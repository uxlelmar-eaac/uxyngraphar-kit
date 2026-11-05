#!/usr/bin/env python3
"""Verifica el espejo: sin espejos huérfanos y cobertura ≥ «cobertura_minima» (%). Código 0 = sin errores."""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
sys.path.insert(0, str(Path(__file__).resolve().parent))

import espejo_mapa as mapa  # noqa: E402
import uxyn_base as base  # noqa: E402

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)


def main() -> int:
    ajustes = base.leer_ajustes(PAQUETE)
    archivos, carpetas = mapa.codigo(PAQUETE, ajustes)
    elementos = [(c, True) for c in carpetas] + [(f, False) for f in archivos]
    cubiertos = sum(mapa.ruta_espejo(PAQUETE, rel, carpeta).is_file() for rel, carpeta in elementos)
    porcentaje = 100.0 * cubiertos / len(elementos) if elementos else 100.0
    errores = [f"espejo huérfano (su código ya no existe): {h}" for h in mapa.huerfanos(PAQUETE, ajustes)]
    minimo = float(ajustes.get("cobertura_minima", 0))
    if porcentaje < minimo:
        errores.append(f"cobertura {porcentaje:.0f}% < mínimo {minimo:.0f}%")
    for e in errores:
        print(f"error: {e}", file=sys.stderr)
    print(f"espejo: cobertura {cubiertos}/{len(elementos)} ({porcentaje:.0f}%), {len(errores)} errores")
    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main())
