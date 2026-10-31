#!/usr/bin/env python3
"""Comprueba que un PR/commit que toca código declare instrucción, anclas y espejo actualizado.

Uso:  python3 docs/scripts/verificar-espejo.py [--base origin/main | --staged] [--docs docs] [--strict]
Salida: 0 (avisos incluidos) · 1 con --strict o STRICT_ESPEJO=1 si hay hallazgos.
Documentado en 10-guias/ci-validacion-documentacion.md.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "espejo"))

from verificar_espejo import IGNORAR_POR_DEFECTO, analizar, cambiados_git, instrucciones_del_cambio, raiz_repo  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent / "control"))
from uxyngraphar_config import normalizar  # noqa: E402



def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", default=os.environ.get("ESPEJO_BASE", "origin/main"), help="rama base del PR (default origin/main)")
    ap.add_argument("--staged", action="store_true", help="analizar lo preparado para commit (gancho pre-commit)")
    ap.add_argument("--docs", default=os.environ.get("DOCS_DIR", "docs"), help="carpeta del pack relativa a la raíz del repo")
    ap.add_argument("--ignorar", action="append", default=[], help="glob adicional de archivos que no son código (repetible)")
    ap.add_argument("--strict", action="store_true", help="salir con 1 si hay hallazgos")
    a = ap.parse_args(argv)
    estricto = a.strict or os.environ.get("STRICT_ESPEJO", "0") == "1"

    repo = raiz_repo(Path.cwd())
    if repo is not None:
        repo, a.docs = normalizar(Path.cwd(), a.docs)
    if repo is None:
        print("AVISO: no es un repositorio git; nada que verificar.", file=sys.stderr)
        return 0
    cambiados = cambiados_git(repo, a.base, a.staged)
    if cambiados is None:
        print(f"AVISO: no se pudo calcular el diff contra «{a.base}» (¿falta fetch?); se omite la verificación.", file=sys.stderr)
        return 0
    docs = a.docs.strip("/").replace("\\", "/")
    ignorar = tuple(IGNORAR_POR_DEFECTO) + tuple(a.ignorar)
    hallazgos = analizar(cambiados, instrucciones_del_cambio(repo, cambiados, docs), docs, ignorar)
    for h in hallazgos:
        print(f"WARN [{h.regla}]: {h.mensaje}", file=sys.stderr)
    if not hallazgos:
        print("OK: espejo y anclas consistentes con el cambio.")
        return 0
    print(f"{len(hallazgos)} hallazgo(s) de deriva del espejo.")
    return 1 if estricto else 0


if __name__ == "__main__":
    raise SystemExit(main())
