#!/usr/bin/env python3
"""Instala (opt-in) los ganchos git del pack: pre-commit, commit-msg (R-22) y, opcionalmente, pre-push.

Uso:  python3 docs/scripts/instalar-ganchos.py [--docs docs] [--pre-push] [--base origin/main] [--force]
      python3 docs/scripts/instalar-ganchos.py --quitar
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "ganchos"))

from instalar_ganchos import instalar, quitar  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent / "espejo"))
from verificar_espejo import raiz_repo  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent / "control"))
from uxyngraphar_config import normalizar  # noqa: E402



def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--docs", default="docs", help="carpeta del pack relativa a la raíz del repo (default docs)")
    ap.add_argument("--pre-push", action="store_true", help="instalar también pre-push (verifica el espejo contra --base)")
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--force", action="store_true", help="sobrescribir un gancho ajeno")
    ap.add_argument("--quitar", action="store_true", help="eliminar los ganchos de uxyngraphar")
    a = ap.parse_args(argv)
    repo = raiz_repo(Path.cwd())
    if repo is not None:
        repo, a.docs = normalizar(Path.cwd(), a.docs)
    if repo is None:
        print("ERROR: ejecútalo dentro de un repositorio git.", file=sys.stderr)
        return 2
    try:
        mensajes = quitar(repo) if a.quitar else instalar(repo, a.docs.strip("/"), a.pre_push, a.base, a.force)
    except (FileExistsError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print("\n".join(mensajes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
