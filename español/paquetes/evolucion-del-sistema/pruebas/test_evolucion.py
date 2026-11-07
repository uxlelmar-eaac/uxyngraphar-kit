"""Pruebas propias del paquete: matriz, exportación humana y anónima, y verificar-evolucion.py (sin el motor)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
PAQUETE = Path(__file__).resolve().parents[1]
ID = PAQUETE.name


def correr(script: Path, *args: str, cwd: Path, humano: bool = False) -> subprocess.CompletedProcess:
    env = {"PYTHONDONTWRITEBYTECODE": "1", "PATH": os.environ.get("PATH", "")}
    if humano:
        env["UXYNGRAPHAR_HUMANO"] = "1"
    return subprocess.run([sys.executable, str(script), *args], cwd=cwd, capture_output=True, text=True, env=env,
                          stdin=subprocess.DEVNULL)


class TestEvolucion(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = Path(self.tmp.name)
        paquete = self.app / "uxyngraphar" / "paquetes" / ID
        shutil.copytree(PAQUETE, paquete, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "pruebas"))
        self.s = paquete / "scripts"
        self.trabajo = self.app / "uxyngraphar" / "trabajo" / ID

    def tearDown(self):
        self.tmp.cleanup()

    def nueva(self, slug: str) -> Path:
        r = correr(self.s / "comun" / "fichas.py", "nueva", "evo", "--slug", slug, "--titulo", slug, cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        return next(self.trabajo.rglob(f"*{slug}*.md"))

    def rellenar(self, ruta: Path) -> None:
        texto = ruta.read_text(encoding="utf-8")
        texto = texto.replace("Dónde se notó: tarea, instrucción, archivo (`ruta:línea`) o pasos.",
                              f"Al registrar una decisión en {self.app}/src/x.ts:3")
        texto = texto.replace("Qué cambiaría en el paquete (archivo y sentido del cambio), sin aplicarlo.",
                              "plantillas/adr.md: añadir «Alternativas descartadas».")
        ruta.write_text(texto, encoding="utf-8")

    def test_matriz_se_crea_una_vez(self):
        r = correr(self.s / "evolucion.py", "matriz", cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Matriz de cobertura", r.stdout)
        matriz = self.trabajo / "MATRIZ-COBERTURA.md"
        matriz.write_text("# editada\n", encoding="utf-8")
        correr(self.s / "evolucion.py", "matriz", cwd=self.app)
        self.assertEqual(matriz.read_text(encoding="utf-8"), "# editada\n")

    def test_exportar_es_humano_y_anonimo(self):
        ruta = self.nueva("adr-sin-alternativas")
        self.rellenar(ruta)
        self.assertNotEqual(correr(self.s / "evolucion.py", "exportar", cwd=self.app).returncode, 0)
        self.assertNotEqual(correr(self.s / "evolucion.py", "exportar", "--humano", cwd=self.app).returncode, 0)
        r = correr(self.s / "evolucion.py", "exportar", "--humano", "--todas", cwd=self.app, humano=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        (informe,) = (self.trabajo / "exportaciones").glob("EXPORTACION-*.md")
        texto = informe.read_text(encoding="utf-8")
        self.assertIn(ruta.stem, texto)
        self.assertIn("src/x.ts:3", texto)
        self.assertNotIn(str(self.app), texto)
        self.assertRegex(ruta.read_text(encoding="utf-8"), r"exportada: \d{4}-\d{2}-\d{2}")

    def test_verificar_tipo_secciones_y_paquete(self):
        ruta = self.nueva("plantilla-corta")
        r = correr(self.s / "verificar-evolucion.py", cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("sección «evidencia» sin rellenar", r.stdout)
        ruta.write_text(ruta.read_text(encoding="utf-8").replace("tipo: proceso", "tipo: producto")
                        .replace("paquete: null", "paquete: rutas-de-api"), encoding="utf-8")
        r = correr(self.s / "verificar-evolucion.py", cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("tipo «producto»", r.stderr)
        self.assertIn("«rutas-de-api», que no está instalado", r.stdout)


if __name__ == "__main__":
    unittest.main()
