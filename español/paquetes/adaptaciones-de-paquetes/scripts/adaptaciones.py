#!/usr/bin/env python3
"""Ajustes locales que adaptan los paquetes instalados a este proyecto.

  python3 uxyngraphar/paquetes/adaptaciones-de-paquetes/scripts/adaptaciones.py ajustes <id-paquete>   ajustes locales activos de ese paquete
  python3 uxyngraphar/paquetes/adaptaciones-de-paquetes/scripts/adaptaciones.py aprobar-ajuste <AJL-…> --humano   activa o revisa un ajuste (persona)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import adaptaciones_datos as datos  # noqa: E402
import uxyn_base as base  # noqa: E402
import uxyn_fichas as fichas  # noqa: E402


def ajustes(pid: str) -> None:
    activos = datos.activos_de(pid)
    for f, fm, cuerpo in activos:
        estado = datos.estado_ajuste(fm)
        print(f"## {f.id} → manda sobre {pid}/{fm.get('aplica_a')}" + ("" if estado == "vigente" else
              f" (POR REVISAR: {estado}; síguelo y avisa a la persona)"))
        print(cuerpo.strip() + "\n")
    reglas = datos.reglas_activas()
    print(f"{pid}: {len(activos)} ajustes locales activos" + (f" · {reglas} reglas del proyecto activas: "
          "antes de tocar código, `reglas.py para <rutas>`" if reglas else ""))


def aprobar_ajuste(fid: str) -> Path:
    base.exigir_humano("aprobar un ajuste local")
    f = fichas.buscar(datos.PAQUETE, fid)
    fm, _ = base.leer_frontmatter(f.ruta.read_text(encoding="utf-8"))
    objetivo = datos.objetivo_ajuste(fm)
    if f.tipo != "ajuste" or not objetivo.is_file():
        raise ValueError(f"{fid}: no es un ajuste o no existe {objetivo.relative_to(datos.raiz())}")
    if f.status != "activo":
        f = fichas.buscar(datos.PAQUETE, fichas.cambiar_estado(datos.PAQUETE, fid, "activo", True).stem)
    texto = base.escribir_campo(f.ruta.read_text(encoding="utf-8"), "huella", base.sha256(objetivo))
    f.ruta.write_text(texto, encoding="utf-8")
    return f.ruta


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ajustes").add_argument("paquete")
    a = sub.add_parser("aprobar-ajuste")
    a.add_argument("id")
    a.add_argument("--humano", action="store_true")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "ajustes":
            ajustes(args.paquete)
        else:
            if not args.humano:
                raise PermissionError("aprobar un ajuste es una acción de la persona (--humano)")
            print(aprobar_ajuste(args.id))
    except (ValueError, FileNotFoundError, FileExistsError, PermissionError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
