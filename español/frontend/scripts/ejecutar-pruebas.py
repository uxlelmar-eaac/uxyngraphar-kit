#!/usr/bin/env python3
"""Ejecuta todas las pruebas del pack (tooling `decisiones`, validador y demás) con un solo comando.

Uso: python3 docs/scripts/ejecutar-pruebas.py [-v]
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


def es_fuente_compartida(raiz: Path) -> bool:
    """¿Se ejecuta desde `_compartido/base/scripts` del kit? Es solo la parte común de los packs, no un pack completo."""
    pack = raiz.parent
    return pack.name == "base" and pack.parent.name == "_compartido" and not (pack / "PROTOCOLO.md").is_file()


def main() -> int:
    raiz = Path(__file__).resolve().parent
    if es_fuente_compartida(raiz):
        print("Omitido: _compartido/base es la fuente parcial común de los packs (le faltan PROTOCOLO.md, REGLAS.md y lo propio de "
              "cada stack), así que sus pruebas no tienen sentido aquí. Ejecuta `python3 _compartido/construir-packs.py` y luego "
              "`python3 backend/scripts/ejecutar-pruebas.py` y `python3 frontend/scripts/ejecutar-pruebas.py`.")
        return 0
    suite = unittest.TestSuite()
    for carpeta in sorted(p for p in raiz.iterdir() if p.is_dir() and any(p.glob("test_*.py"))):
        sys.path.insert(0, str(carpeta))
        suite.addTests(unittest.defaultTestLoader.discover(str(carpeta), pattern="test_*.py", top_level_dir=str(carpeta)))
    resultado = unittest.TextTestRunner(verbosity=2 if "-v" in sys.argv else 1).run(suite)
    return 0 if resultado.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
