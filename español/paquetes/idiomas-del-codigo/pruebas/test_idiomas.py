"""Pruebas propias del paquete: nombres de archivo ASCII y glosario en una app temporal (sin el motor)."""

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
        self.trabajo = self.app / "uxyngraphar" / "trabajo" / ID
        (self.app / "src").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def idiomas(self, *args: str) -> subprocess.CompletedProcess:
        return correr(sys.executable, str(self.s / "idiomas.py"), *args, cwd=self.app)

    def glosario(self, *args: str) -> subprocess.CompletedProcess:
        return correr(sys.executable, str(self.s / "glosario.py"), *args, cwd=self.app)


class TestNombres(Base):
    def test_nombre_no_ascii(self):
        (self.app / "src" / "cupón.ts").write_text("x\n", encoding="utf-8")
        r = self.idiomas()
        self.assertEqual(r.returncode, 1)
        self.assertIn("src/cupón.ts: nombre de archivo no ASCII", r.stdout)
        self.assertTrue((self.paquete / "referencia" / "idioma.md").is_file())

    def test_carpeta_no_ascii(self):
        (self.app / "src" / "facturación").mkdir()
        (self.app / "src" / "facturación" / "invoice.ts").write_text("x\n", encoding="utf-8")
        self.assertEqual(self.idiomas().returncode, 1)

    def test_archivos_explicitos_y_ascii(self):
        (self.app / "src" / "coupon.ts").write_text("x\n", encoding="utf-8")
        r = self.idiomas("src/coupon.ts")
        self.assertEqual(r.returncode, 0)
        self.assertIn("idiomas-del-codigo: 1 archivos revisados, 0 problemas", r.stdout)

    def test_excluir_de_la_persona(self):
        (self.app / "src" / "vendor").mkdir()
        (self.app / "src" / "vendor" / "librería.js").write_text("x\n", encoding="utf-8")
        self.trabajo.mkdir(parents=True)
        (self.trabajo / "ajustes.json").write_text(json.dumps({"excluir": ["**/vendor/**"]}), encoding="utf-8")
        self.assertEqual(self.idiomas().returncode, 0)


class TestGlosario(Base):
    def test_iniciar_y_terminos(self):
        self.assertIn("glosario vacío", self.glosario("terminos").stdout)
        ruta = Path(self.glosario("iniciar").stdout.strip())
        self.assertEqual(ruta, self.trabajo / "GLOSARIO.md")
        self.assertTrue(ruta.is_file())
        with ruta.open("a", encoding="utf-8") as f:
            f.write("| `expediente` | case file | Expediente administrativo | dominio | Ley 39/2015 | equipo |\n")
        self.assertEqual(self.glosario("terminos").stdout.split(), ["expediente"])

    def test_iniciar_no_sobrescribe(self):
        self.trabajo.mkdir(parents=True)
        (self.trabajo / "GLOSARIO.md").write_text("| Término | Glosa (en) |\n|---|---|\n| `nomina` | payroll |\n", encoding="utf-8")
        self.glosario("iniciar")
        self.assertEqual(self.glosario("terminos").stdout.split(), ["nomina"])

    def test_glosario_protegido(self):
        manifiesto = json.loads((PAQUETE / "paquete.json").read_text(encoding="utf-8"))
        self.assertIn("GLOSARIO.md", manifiesto["protegidos"])


if __name__ == "__main__":
    unittest.main()
