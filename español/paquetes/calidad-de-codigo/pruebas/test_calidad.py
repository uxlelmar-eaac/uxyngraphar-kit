"""Pruebas propias del paquete: límite de líneas, exenciones, exclusiones y nombres con espacios en una app temporal (sin el motor)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
PAQUETE = Path(__file__).resolve().parents[1]
ID = PAQUETE.name


def correr(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run([*args], cwd=cwd, capture_output=True, text=True,
                          env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin", "HOME": str(cwd)})


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = Path(self.tmp.name)
        self.paquete = self.app / "uxyngraphar" / "paquetes" / ID
        shutil.copytree(PAQUETE, self.paquete, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "pruebas"))
        self.s = self.paquete / "scripts"
        (self.app / "src").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def calidad(self, *args: str) -> subprocess.CompletedProcess:
        return correr(sys.executable, str(self.s / "calidad.py"), *args, cwd=self.app)

    def ajustes(self, valores: dict) -> None:
        trabajo = self.app / "uxyngraphar" / "trabajo" / ID
        trabajo.mkdir(parents=True, exist_ok=True)
        (trabajo / "ajustes.json").write_text(json.dumps(valores), encoding="utf-8")


class TestLineas(Base):
    def test_limite_y_mensaje_con_la_guia(self):
        largo = self.app / "src" / "order-service.ts"
        largo.write_text("export const line = 1;\n" * 351, encoding="utf-8")
        r = self.calidad("src/order-service.ts")
        self.assertEqual(r.returncode, 1)
        self.assertIn("351 líneas (límite 350)", r.stdout)
        self.assertTrue((self.paquete / "referencia" / "limite-lineas.md").is_file())
        self.assertIn("referencia/limite-lineas.md", r.stdout)

    def test_exencion_de_la_persona(self):
        (self.app / "src" / "big.ts").write_text("x\n" * 400, encoding="utf-8")
        self.ajustes({"exenciones_lineas": ["src/big.ts"]})
        self.assertEqual(self.calidad().returncode, 0)

    def test_limite_de_la_persona(self):
        (self.app / "src" / "mid.ts").write_text("x\n" * 120, encoding="utf-8")
        self.ajustes({"limite_lineas": 100})
        self.assertIn("120 líneas (límite 100)", self.calidad().stdout)

    def test_excluidos_y_extensiones_ajenas(self):
        (self.app / "src" / "generated").mkdir()
        (self.app / "src" / "generated" / "api.ts").write_text("x\n" * 400, encoding="utf-8")
        (self.app / "src" / "notes.txt").write_text("x\n" * 400, encoding="utf-8")
        r = self.calidad()
        self.assertEqual(r.returncode, 0)
        self.assertIn("0 archivos revisados", r.stdout)


class TestNombres(Base):
    def test_nombre_con_espacios(self):
        (self.app / "src" / "order service.ts").write_text("x\n", encoding="utf-8")
        r = self.calidad()
        self.assertEqual(r.returncode, 1)
        self.assertIn("nombre de archivo con espacios", r.stdout)

    def test_no_ascii_no_es_de_este_paquete(self):
        (self.app / "src" / "cupón.ts").write_text("x\n", encoding="utf-8")
        self.assertEqual(self.calidad().returncode, 0)

    def test_sin_opcion_de_commits(self):
        self.assertNotEqual(self.calidad("--commits").returncode, 0)


if __name__ == "__main__":
    unittest.main()
