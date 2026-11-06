#!/usr/bin/env python3
"""Reglas del proyecto y ajustes locales.

  python3 uxyngraphar/paquetes/reglas-del-proyecto/scripts/reglas.py indice                 reglas activas (lo único que se lee por defecto)
  python3 uxyngraphar/paquetes/reglas-del-proyecto/scripts/reglas.py para <ruta|ancla>…     reglas que tocan esas rutas (anclas de una instrucción)
  python3 uxyngraphar/paquetes/reglas-del-proyecto/scripts/reglas.py comprobar [RUTA…] [--git]   evalúa sin IA las reglas con comprobación
  python3 uxyngraphar/paquetes/reglas-del-proyecto/scripts/reglas.py ajustes <id-paquete>   ajustes locales activos de ese paquete
  python3 uxyngraphar/paquetes/reglas-del-proyecto/scripts/reglas.py aprobar-ajuste <AJL-…> --humano   activa o revisa un ajuste (persona)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import reglas_datos as datos  # noqa: E402
import uxyn_base as base  # noqa: E402
import uxyn_fichas as fichas  # noqa: E402


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


def ajustes(pid: str) -> None:
    activos = [(f, fm, c) for f, fm, c in datos.fichas_de("ajuste") if f.status == "activo" and fm.get("paquete") == pid]
    for f, fm, cuerpo in activos:
        estado = datos.estado_ajuste(fm)
        print(f"## {f.id} → manda sobre {pid}/{fm.get('aplica_a')}" + ("" if estado == "vigente" else
              f" (POR REVISAR: {estado}; síguelo y avisa a la persona)"))
        print(cuerpo.strip() + "\n")
    reglas = len(datos.activas())
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
    sub.add_parser("indice")
    sub.add_parser("para").add_argument("rutas", nargs="+")
    c = sub.add_parser("comprobar")
    c.add_argument("rutas", nargs="*")
    c.add_argument("--git", action="store_true", help="solo lo cambiado según git")
    sub.add_parser("ajustes").add_argument("paquete")
    a = sub.add_parser("aprobar-ajuste")
    a.add_argument("id")
    a.add_argument("--humano", action="store_true")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "indice":
            indice()
        elif args.cmd == "para":
            para(args.rutas)
        elif args.cmd == "comprobar":
            return comprobar(args.rutas, args.git)
        elif args.cmd == "ajustes":
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
