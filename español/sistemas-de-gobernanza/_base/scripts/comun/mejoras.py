#!/usr/bin/env python3
"""Propuestas de mejora de este sistema (en uxyngraphar/trabajo/<id>/propuestas-de-mejora/).

  python3 scripts/comun/mejoras.py listar [--json]
  python3 scripts/comun/mejoras.py ver <id>
  python3 scripts/comun/mejoras.py nueva --slug <slug> --titulo "…" --que "…" [--porque "…"] [--evidencia "…"]
                                         [--archivo <archivo del sistema>] [--diff <archivo .diff> | --diff -]

El sistema instalado no se edita nunca (ni la IA ni la persona). Si se queda corto o falla, el agente escribe aquí una
propuesta; la persona la envía al autor con «uxyngraphar reportar <id> --mejora <PMS-…>» (vista previa obligatoria).
El diff, si lo hay, solo puede tocar archivos del sistema: nunca código del proyecto.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el sistema es inmutable: ni cachés dentro
sys.path.insert(0, str(Path(__file__).resolve().parent))

import uxyn_base as base  # noqa: E402
import uxyn_mejoras as mejoras  # noqa: E402

SISTEMA = base.carpeta_sistema(Path(__file__).resolve().parent)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="mejoras.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("listar").add_argument("--json", action="store_true")
    sub.add_parser("ver").add_argument("id")
    n = sub.add_parser("nueva")
    n.add_argument("--slug", required=True)
    n.add_argument("--titulo", required=True)
    n.add_argument("--que", required=True, help="qué falla o qué falta en el sistema")
    n.add_argument("--porque", default="", help="por qué importa")
    n.add_argument("--evidencia", default="", help="qué pasó (sin código del proyecto ni datos privados)")
    n.add_argument("--archivo", default="", help="archivo del sistema afectado (p. ej. LIMITES.md)")
    n.add_argument("--diff", default="", help="archivo con un diff de archivos del sistema, o «-» para leerlo de la entrada")
    a = p.parse_args(argv)
    try:
        if a.cmd == "listar":
            lista = mejoras.listar(SISTEMA)
            if a.json:
                print(json.dumps([{"id": m.id, "status": m.status, "titulo": m.titulo} for m in lista], ensure_ascii=False, indent=2))
            elif not lista:
                print("(sin propuestas de mejora)")
            for m in [] if a.json else lista:
                print(f"{m.id}\t{m.status}\t{m.titulo}")
        elif a.cmd == "ver":
            print(mejoras.buscar(SISTEMA, a.id).ruta.read_text(encoding="utf-8"))
        elif a.cmd == "nueva":
            diff = sys.stdin.read() if a.diff == "-" else (Path(a.diff).read_text(encoding="utf-8") if a.diff else "")
            ruta = mejoras.crear(SISTEMA, a.slug, a.titulo, a.que, a.porque, a.evidencia, a.archivo, diff)
            print(ruta)
            print(f"La persona la envía al autor con: uxyngraphar reportar {SISTEMA.name} --mejora {ruta.stem}")
    except (ValueError, FileNotFoundError, FileExistsError, OSError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
