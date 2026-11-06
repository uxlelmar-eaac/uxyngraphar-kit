#!/usr/bin/env python3
"""Arquitectura por capas.

  python3 uxyngraphar/paquetes/arquitectura-por-capas/scripts/capas.py mapa                 módulos y capas encontrados
  python3 uxyngraphar/paquetes/arquitectura-por-capas/scripts/capas.py revisar [RUTA…]      imports que rompen las capas
  python3 uxyngraphar/paquetes/arquitectura-por-capas/scripts/capas.py iniciar             crea ARQUITECTURA.md del proyecto si falta
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import capas_datos as datos  # noqa: E402
import uxyn_base as base  # noqa: E402

DOC = "ARQUITECTURA.md"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("mapa")
    sub.add_parser("revisar").add_argument("rutas", nargs="*")
    sub.add_parser("iniciar")
    a = ap.parse_args(argv)
    if a.cmd == "mapa":
        ajustes = datos.ajustes()
        print(f"perfil {ajustes.get('perfil')} · capas: {', '.join(ajustes['capas'])}")
        for modulo, capas in sorted(datos.mapa().items()):
            faltan = [c for c in ajustes["capas"] if c not in capas]
            print(f"{modulo}: {', '.join(sorted(capas)) or '(sin capas reconocidas)'}" + (f"  · sin: {', '.join(faltan)}" if faltan else ""))
        return 0
    if a.cmd == "iniciar":
        destino = base.carpeta_trabajo(datos.PAQUETE) / DOC
        if not destino.exists():
            shutil.copy2(datos.PAQUETE / "plantillas" / DOC, destino)
            destino.chmod(0o644)
        print(destino)
        return 0
    infracciones = datos.revisar(a.rutas or None)
    for i in infracciones:
        print(f"{i.archivo}:{i.linea}: {i.motivo} (importa {i.destino})")
    print(f"capas: {len(infracciones)} imports fuera de las reglas")
    return 1 if infracciones else 0


if __name__ == "__main__":
    raise SystemExit(main())
