#!/usr/bin/env python3
"""Memorias del proyecto para este sistema (en uxyngraphar/trabajo/<id>/memorias/).

  python3 scripts/comun/memorias.py listar [--vigentes | --status <status>] [--json]
  python3 scripts/comun/memorias.py ver <id>
  python3 scripts/comun/memorias.py nueva --slug <slug> --titulo "…" [--texto "…"] [--motivo "…"] [--fuente "…"]
                                         [--valida-hasta AAAA-MM-DD] [--humano]
  python3 scripts/comun/memorias.py aprobar <id> --humano
  python3 scripts/comun/memorias.py archivar <id> --humano

El agente crea memorias «propuesta»; solo una persona las aprueba («vigente») o archiva. Las que crea una persona con
--humano nacen vigentes. --humano solo vale para una persona: terminal interactiva o UXYNGRAPHAR_HUMANO=1.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el sistema es inmutable: ni cachés dentro
sys.path.insert(0, str(Path(__file__).resolve().parent))

import uxyn_base as base  # noqa: E402
import uxyn_memorias as memorias  # noqa: E402

SISTEMA = base.carpeta_sistema(Path(__file__).resolve().parent)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="memorias.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    ls = sub.add_parser("listar")
    grupo = ls.add_mutually_exclusive_group()
    grupo.add_argument("--vigentes", action="store_true", help="solo las que el agente aplica (vigentes y no caducadas)")
    grupo.add_argument("--status", choices=memorias.STATUS)
    ls.add_argument("--json", action="store_true")
    v = sub.add_parser("ver")
    v.add_argument("id")
    n = sub.add_parser("nueva")
    n.add_argument("--slug", required=True)
    n.add_argument("--titulo", required=True)
    n.add_argument("--texto", default="", help="qué hay que recordar")
    n.add_argument("--motivo", default="", help="por qué importa")
    n.add_argument("--fuente", default="", help="de dónde sale (pedido, ficha, conversación…)")
    n.add_argument("--valida-hasta", default=None)
    n.add_argument("--humano", action="store_true", help="lo ejecuta una persona (la memoria nace vigente)")
    for nombre in ("aprobar", "archivar"):
        c = sub.add_parser(nombre)
        c.add_argument("id")
        c.add_argument("--humano", action="store_true", help="lo ejecuta una persona (obligatorio)")
    a = p.parse_args(argv)
    try:
        if a.cmd == "listar":
            lista = memorias.vigentes(SISTEMA) if a.vigentes else memorias.listar(SISTEMA, a.status)
            if a.json:
                print(json.dumps([{"id": m.id, "status": m.status, "autor": m.autor, "fecha": m.fecha,
                                   "valida_hasta": m.valida_hasta, "titulo": m.titulo} for m in lista],
                                 ensure_ascii=False, indent=2))
            elif not lista:
                print("(sin memorias)")
            for m in [] if a.json else lista:
                print(f"{m.id}\t{m.status}\t{m.autor}\t{m.titulo}")
        elif a.cmd == "ver":
            print(memorias.buscar(SISTEMA, a.id).ruta.read_text(encoding="utf-8"))
        elif a.cmd == "nueva":
            print(memorias.crear(SISTEMA, a.slug, a.titulo, a.texto, a.motivo, a.fuente, a.valida_hasta, a.humano))
        elif a.cmd == "aprobar":
            print(memorias.cambiar_estado(SISTEMA, a.id, "vigente", a.humano))
        elif a.cmd == "archivar":
            print(memorias.cambiar_estado(SISTEMA, a.id, "archivada", a.humano))
    except (ValueError, FileNotFoundError, FileExistsError, PermissionError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
