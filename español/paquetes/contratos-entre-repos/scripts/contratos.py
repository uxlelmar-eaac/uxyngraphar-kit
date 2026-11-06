#!/usr/bin/env python3
"""Contratos entre repositorios.

  python3 uxyngraphar/paquetes/contratos-entre-repos/scripts/contratos.py registro           regenera trabajo/…/REGISTRO.md
  python3 uxyngraphar/paquetes/contratos-entre-repos/scripts/contratos.py comparar [RUTA…]   compara con los repos hermanos
      (por defecto, «otros_repos» de ajustes.json; rutas relativas a la raíz de esta app)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import contratos_datos as datos  # noqa: E402
import uxyn_base as base  # noqa: E402


def registro() -> Path:
    filas = [f"| `{fm.get('id_compartido')}` | {fm.get('rol')} | {fm.get('method')} {fm.get('path')} | {fm.get('version')} | "
             f"{fm.get('proveedor')} | {fm.get('ficha_proveedor') or '—'} | {f.status} | {f.id} |"
             for f, fm in sorted(datos.propios(), key=lambda x: str(x[1].get("id_compartido")))]
    texto = "\n".join(["# Registro de ids compartidos", "",
                       "Generado por `contratos.py registro`; no editar. Fuente: las fichas CON-* de esta carpeta.", "",
                       "| id compartido | rol | ruta | versión | proveedor | ficha del proveedor | estado | ficha |",
                       "|---|---|---|---|---|---|---|---|", *(filas or ["| — | — | — | — | — | — | — | (sin contratos) |"]), ""])
    destino = base.carpeta_trabajo(datos.PAQUETE) / "REGISTRO.md"
    destino.write_text(texto, encoding="utf-8")
    return destino


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("registro")
    sub.add_parser("comparar").add_argument("rutas", nargs="*")
    a = ap.parse_args(argv)
    if a.cmd == "registro":
        print(registro())
        return 0
    divergencias, avisos = datos.comparar(a.rutas or None)
    for x in avisos:
        print(f"aviso: {x}")
    for x in divergencias:
        print(f"divergencia: {x}")
    print(f"contratos: {len(divergencias)} divergencias, {len(avisos)} avisos")
    return 1 if divergencias else 0


if __name__ == "__main__":
    raise SystemExit(main())
