#!/usr/bin/env python3
"""Doctor de uxyngraphar: diagnostica de punta a punta si el protocolo está sano en este proyecto.

Revisa entorno, lock, integridad del núcleo, protección contra agentes (deny, CODEOWNERS, gancho), .gitignore,
validación documental, configuración, conflictos de actualización, pendientes antiguos y depuración sugerida.

Uso:  python3 docs/scripts/doctor.py [--repo .] [--docs docs] [--pack RUTA_PACK] [--json] [--strict] [--fix]
  --pack    contrasta el núcleo con el pack fuente y avisa si hay versión nueva
  --fix     correcciones seguras: .gitignore, .gitattributes, reglas deny, CODEOWNERS, CI, lock y gancho pre-commit (nunca toca núcleo ni contenido)
  --strict  los avisos también hacen fallar
Salida: 0 sano · 1 hay errores (o avisos con --strict).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "nucleo"))

from doctor import a_json, arreglar, diagnosticar, formatear  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent / "control"))
from uxyngraphar_config import normalizar  # noqa: E402



def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--pack", default="")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--fix", action="store_true")
    a = ap.parse_args(argv)
    repo, a.docs = normalizar(Path(a.repo), a.docs)
    if a.fix:
        for linea in arreglar(repo, a.docs):
            print(f"fix: {linea}", file=sys.stderr)
    chequeos = diagnosticar(repo, a.docs, Path(a.pack).resolve() if a.pack else None)
    print(a_json(chequeos) if a.json else formatear(chequeos))
    return 1 if any(c.nivel == "ERROR" or (a.strict and c.nivel == "WARN") for c in chequeos) else 0


if __name__ == "__main__":
    raise SystemExit(main())
