#!/usr/bin/env python3
"""Fichas del sistema (trabajo en uxyngraphar/trabajo/<id>/).

  python3 scripts/comun/fichas.py tipos
  python3 scripts/comun/fichas.py nueva <tipo> --slug <slug> [--titulo "…"] [--variante <nombre>] [--en <subcarpeta>] [--humano]
  python3 scripts/comun/fichas.py listar [<tipo>] [--status <status>]
  python3 scripts/comun/fichas.py ver <id>
  python3 scripts/comun/fichas.py estado <id> <status> [--humano]

--humano solo vale para una persona: terminal interactiva o UXYNGRAPHAR_HUMANO=1 (un agente no puede usarlo).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el sistema es inmutable: ni cachés dentro
sys.path.insert(0, str(Path(__file__).resolve().parent))

import uxyn_base as base  # noqa: E402
import uxyn_fichas as fichas  # noqa: E402

SISTEMA = base.carpeta_sistema(Path(__file__).resolve().parent)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="fichas.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("tipos")
    n = sub.add_parser("nueva")
    n.add_argument("tipo")
    n.add_argument("--slug", required=True)
    n.add_argument("--titulo", default="")
    n.add_argument("--variante", default="", help="plantilla alternativa del tipo (ver «tipos»)")
    n.add_argument("--en", default="", help="subcarpeta (solo tipos planos)")
    n.add_argument("--humano", action="store_true", help="lo ejecuta una persona (tipos que nacen con status «solo_humano»)")
    ls = sub.add_parser("listar")
    ls.add_argument("tipo", nargs="?")
    ls.add_argument("--status")
    v = sub.add_parser("ver")
    v.add_argument("id")
    e = sub.add_parser("estado")
    e.add_argument("id")
    e.add_argument("status")
    e.add_argument("--humano", action="store_true", help="lo ejecuta una persona (habilita status «solo_humano»)")
    a = p.parse_args(argv)
    try:
        if a.cmd == "tipos":
            for nombre, d in fichas.tipos(SISTEMA).items():
                estados = ", ".join(d.get("estados") or d["status_validos"])
                variantes = f" · variantes {', '.join(d['variantes'])}" if d.get("variantes") else ""
                print(f"{nombre}: carpeta {d['carpeta']}/ · status {estados}{variantes}")
        elif a.cmd == "nueva":
            print(fichas.crear(SISTEMA, a.tipo, a.slug, a.titulo, a.en, por_humano=a.humano, variante=a.variante))
        elif a.cmd == "listar":
            for f in fichas.listar(SISTEMA, a.tipo):
                if not a.status or f.status == a.status:
                    print(f"{f.id}\t{f.status}\t{f.titulo}")
        elif a.cmd == "ver":
            print(fichas.buscar(SISTEMA, a.id).ruta.read_text(encoding="utf-8"))
        elif a.cmd == "estado":
            print(fichas.cambiar_estado(SISTEMA, a.id, a.status, a.humano))
    except (ValueError, FileNotFoundError, FileExistsError, PermissionError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
