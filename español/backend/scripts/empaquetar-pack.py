#!/usr/bin/env python3
"""Genera el .zip de distribución de un pack (núcleo + plantillas + índices, con manifiesto y hashes).

Uso:  python3 scripts/empaquetar-pack.py RUTA_PACK [--salida dist]
El .zip se puede pasar directamente a instalar-pack.py / actualizar-pack.py.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "nucleo"))

from empaquetar import empaquetar  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pack")
    ap.add_argument("--salida", default="dist")
    a = ap.parse_args(argv)
    try:
        print(empaquetar(Path(a.pack).resolve(), Path(a.salida).resolve()))
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
