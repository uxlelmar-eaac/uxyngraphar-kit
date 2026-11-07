#!/usr/bin/env python3
"""Reglas del proyecto y sus excepciones.

  python3 uxyngraphar/paquetes/reglas-del-proyecto/scripts/reglas.py indice                 reglas activas (lo único que se lee por defecto)
  python3 uxyngraphar/paquetes/reglas-del-proyecto/scripts/reglas.py para <ruta|ancla>…     reglas que tocan esas rutas (anclas de una instrucción)
  python3 uxyngraphar/paquetes/reglas-del-proyecto/scripts/reglas.py comprobar [RUTA…] [--git]   evalúa sin IA las reglas con comprobación
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import reglas_datos as datos  # noqa: E402


def indice() -> None:
    activas = datos.activas()
    if not activas:
        print("(sin reglas del proyecto activas)")
        return
    print("| id | nivel | aplica_a | resumen |\n|----|-------|----------|---------|")
    for f, fm, _ in activas:
        print(f"| {f.id} | {fm.get('nivel')} | {', '.join(datos.lista(fm.get('aplica_a')))} | {fm.get('resumen')} |")


def para(rutas: list[str]) -> None:
    reglas = datos.para_rutas(rutas)
    if not reglas:
        print("(ninguna regla del proyecto toca esas rutas)")
        return
    for f, fm, cuerpo in reglas:
        print(f"- {f.id} [{fm.get('nivel')}] {fm.get('resumen')}")
        if fm.get("nivel") == "bloqueante":
            print("".join(f"  {l}\n" for l in cuerpo.splitlines() if l.strip() and not l.startswith("<!--")), end="")
    print("Si no puedes cumplir una regla: propón una excepción (fichas.py nueva excepcion) y espera a que una persona la apruebe.")


def comprobar(rutas: list[str], git: bool) -> int:
    hallazgos = datos.comprobar(rutas or None, git)
    bloquean = [h for h in hallazgos if h["nivel"] == "bloqueante" and not h["excusado"]]
    for h in hallazgos:
        marca = "excepción aprobada" if h["excusado"] else h["nivel"]
        print(f"{h['archivo']}: {h['regla']} [{marca}] {h['motivo']}")
    print(f"reglas del proyecto: {len(hallazgos)} incumplimientos, {len(bloquean)} bloqueantes")
    return 1 if bloquean else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("indice")
    sub.add_parser("para").add_argument("rutas", nargs="+")
    c = sub.add_parser("comprobar")
    c.add_argument("rutas", nargs="*")
    c.add_argument("--git", action="store_true", help="solo lo cambiado según git")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "indice":
            indice()
        elif args.cmd == "para":
            para(args.rutas)
        else:
            return comprobar(args.rutas, args.git)
    except (ValueError, FileNotFoundError, FileExistsError, PermissionError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
