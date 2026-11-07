"""Pruebas propias del paquete: se ejecutan desde la carpeta del paquete, sin el motor (solo librería estándar)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
PAQUETE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PAQUETE / "scripts" / "comun"))

import uxyn_base as base  # noqa: E402


class TestPaquete(unittest.TestCase):
    def test_manifiesto_valido(self):
        self.assertEqual(base.validar_manifiesto(base.leer_manifiesto(PAQUETE)), [])

    def test_verificaciones_existen(self):
        for v in base.leer_manifiesto(PAQUETE)["verificaciones"]:
            self.assertTrue((PAQUETE / v).is_file(), v)


if __name__ == "__main__":
    unittest.main()
