#!/usr/bin/env python3
"""Verifica que el núcleo instalado no fue editado, borrado ni ampliado (R-14 / R-20).

Uso:  python3 verificar-nucleo.py [--repo .] [--docs docs] [--contra RUTA_PACK] [--warn]
  --contra  compara además cada archivo del núcleo con el pack fuente (independiente del lock; úsalo en CI).
Salida: 0 íntegro · 1 hay hallazgos (con --warn siempre 0).
No existe forma de «aceptar» una edición local: el núcleo solo cambia en uxyngraphar y llega con actualizar-pack.py.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "nucleo"))

from verificar import AYUDA, contra_pack, verificar  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent / "control"))
from uxyngraphar_config import normalizar  # noqa: E402



def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--contra", default="", help="carpeta del pack fuente contra la que contrastar")
    ap.add_argument("--warn", action="store_true", help="informar sin fallar")
    a = ap.parse_args(argv)
    repo, a.docs = normalizar(Path(a.repo), a.docs)
    hallazgos = verificar(repo, a.docs)
    if a.contra:
        hallazgos += contra_pack(repo, a.docs, Path(a.contra).resolve())
    for h in hallazgos:
        print(f"{'WARN' if a.warn else 'ERROR'} [{h.codigo}] {h.ruta}: {h.mensaje}", file=sys.stderr)
    if not hallazgos:
        print("OK: núcleo íntegro.")
        return 0
    print(AYUDA, file=sys.stderr)
    return 0 if a.warn else 1


if __name__ == "__main__":
    raise SystemExit(main())
