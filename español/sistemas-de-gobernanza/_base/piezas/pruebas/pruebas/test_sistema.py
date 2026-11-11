"""Pruebas propias del sistema: se ejecutan desde la carpeta del sistema construido, sin el motor (solo librería estándar).

De serie comprueban el manifiesto, que las verificaciones existen y que cada script propio de `scripts/` compila y, si usa
argparse, responde a `--help` dentro de una app temporal. Añade aquí las pruebas de lo que hace cada script: el caso
correcto, una ficha con error y una carpeta vacía.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SISTEMA = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SISTEMA / "scripts" / "comun"))

import uxyn_base as base  # noqa: E402

PROPIOS = sorted((SISTEMA / "scripts").glob("*.py"))


class TestSistema(unittest.TestCase):
    def test_manifiesto_valido(self):
        self.assertEqual(base.validar_manifiesto(base.leer_manifiesto(SISTEMA)), [])

    def test_verificaciones_existen(self):
        for v in base.leer_manifiesto(SISTEMA)["verificaciones"]:
            self.assertTrue((SISTEMA / v).is_file(), v)

    def test_scripts_propios_compilan_y_responden(self):
        with tempfile.TemporaryDirectory() as t:
            app = Path(t).resolve()
            instalado = app / "uxyngraphar" / "sistemas-de-gobernanza" / SISTEMA.name
            shutil.copytree(SISTEMA, instalado, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "pruebas"))
            entorno = {**{k: v for k, v in os.environ.items() if not k.startswith("UXYNGRAPHAR_")}, "PYTHONDONTWRITEBYTECODE": "1"}
            for script in PROPIOS:
                with self.subTest(script=script.name):
                    compile(script.read_text(encoding="utf-8"), str(script), "exec")   # que compile, sin escribir cachés
                    if "argparse" in script.read_text(encoding="utf-8"):
                        r = subprocess.run([sys.executable, str(instalado / "scripts" / script.name), "--help"], cwd=app,
                                           capture_output=True, text=True, encoding="utf-8", env=entorno, stdin=subprocess.DEVNULL)
                        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
