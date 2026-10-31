#!/usr/bin/env python3
"""Asistente de instalación de uxyngraphar.

Sin argumentos abre una pantalla en tu navegador (python3 instalar.py en cualquier sistema; en Windows también py -3 instalar.py).
Con --consola, o con cualquier opción (--proyecto, --pack, --si…), funciona en texto:
  python3 instalar.py --proyecto RUTA --pack servidor --si
  python3 instalar.py --proyecto RUTA --pack ambos --mismo-repo --sub-servidor apps/api --sub-cliente apps/web
Requiere Python 3.10+ y git. No borra nada: lo que choque queda como *.uxyngraphar-nuevo.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "instalador"))


def main() -> int:
    if len(sys.argv) == 1:
        try:
            import servidor
            return servidor.servir()
        except OSError as exc:
            print(f"No pude abrir la pantalla ({exc}); sigo en modo texto.\n")
    import consola
    return consola.arrancar()


if __name__ == "__main__":
    try:
        codigo = main()
    except KeyboardInterrupt:
        codigo = 130
    raise SystemExit(codigo)
