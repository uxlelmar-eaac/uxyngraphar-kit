#!/usr/bin/env python3
"""Busca credenciales en el proyecto (R-12). Los valores se muestran enmascarados.

Uso:  python3 docs/scripts/escanear-secretos.py [--historia [N]]
  (sin flags)  archivos versionados y nuevos no ignorados
  --historia   además, todo el historial de todas las ramas (líneas añadidas alguna vez); N = últimos N commits
Salida: 0 sin hallazgos · 1 con hallazgos. Si algo ya se subió: rota la credencial (borrar el commit no basta).
Exención para fixtures de pruebas: la marca «uxyngraphar:permitir-secreto» en la misma línea.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "control"))

import escaneo  # noqa: E402
from uxyngraphar_config import cargar  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--historia", nargs="?", const=0, type=int, metavar="N")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--permitir", action="append", default=[], metavar="GLOB", help="ruta que se omite (repetible); también config secretos_permitir")
    a = ap.parse_args(argv)
    repo = Path(a.repo).resolve()
    total = 0
    permitir = list(a.permitir) + list(cargar(repo, a.docs)[0].get("secretos_permitir", []))
    for h in escaneo.arbol(repo, permitir):
        total += 1
        print(f"ARBOL     {h.ruta}:{h.linea} {h.tipo} {h.muestra}")
    if a.historia is not None:
        for commit, h in escaneo.historia(repo, a.historia, permitir):
            total += 1
            print(f"HISTORIA  {commit} {h.ruta} {h.tipo} {h.muestra}")
    print(f"escanear-secretos: {total} hallazgo(s)" + ("" if not total else " — rota las credenciales expuestas y limpia el historial si ya se publicaron"))
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
