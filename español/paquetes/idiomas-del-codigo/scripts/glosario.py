#!/usr/bin/env python3
"""Glosario de dominio del proyecto (uxyngraphar/trabajo/idiomas-del-codigo/GLOSARIO.md).

  python3 uxyngraphar/paquetes/idiomas-del-codigo/scripts/glosario.py terminos     términos permitidos (primera columna)
  python3 uxyngraphar/paquetes/idiomas-del-codigo/scripts/glosario.py iniciar      crea el glosario vacío si falta (lo rellena la persona)
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import uxyn_base as base  # noqa: E402

PAQUETE = base.carpeta_paquete(AQUI)
GLOSARIO = "GLOSARIO.md"


def terminos(ruta: Path) -> list[str]:
    salida = []
    for linea in ruta.read_text(encoding="utf-8").splitlines() if ruta.is_file() else []:
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if linea.lstrip().startswith("|") and len(celdas) > 1 and celdas[0] not in ("Término", "") and not set(celdas[0]) <= set("-: "):
            salida.append(celdas[0].strip("`"))
    return salida


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["terminos", "iniciar"])
    a = ap.parse_args(argv)
    ruta = base.carpeta_trabajo(PAQUETE) / GLOSARIO
    if a.cmd == "iniciar":
        if not ruta.exists():
            shutil.copy2(PAQUETE / "plantillas" / GLOSARIO, ruta)
            ruta.chmod(0o644)
        print(ruta)
        return 0
    lista = terminos(ruta)
    print("\n".join(lista) if lista else "(glosario vacío o inexistente: todo término va en inglés)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
