"""Pruebas propias del paquete: notas de memoria y su búsqueda en una app temporal (sin el motor, solo librería estándar)."""

from __future__ import annotations

import json
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
sys.path.insert(0, str(PAQUETE / "scripts" / "comun"))

import uxyn_base as base  # noqa: E402


def correr(script: Path, *args: str, cwd: Path) -> subprocess.CompletedProcess:
    entorno = {"PYTHONDONTWRITEBYTECODE": "1", "PATH": os.environ.get("PATH", "")}
    return subprocess.run([sys.executable, str(script), *args], cwd=cwd, capture_output=True, text=True,
                          env=entorno, stdin=subprocess.DEVNULL)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = Path(self.tmp.name)
        self.paquete = self.app / "uxyngraphar" / "paquetes" / ID
        shutil.copytree(PAQUETE, self.paquete, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "pruebas"))
        self.s = self.paquete / "scripts"
        self.trabajo = self.app / "uxyngraphar" / "trabajo" / ID

    def tearDown(self):
        self.tmp.cleanup()

    def nueva(self, slug: str, titulo: str) -> Path:
        r = correr(self.s / "comun" / "fichas.py", "nueva", "nota", "--slug", slug, "--titulo", titulo, cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        (nota,) = self.trabajo.rglob(f"MEM-*-{slug}.md")
        return nota


class TestFicha(Base):
    def test_nota_nace_vigente_en_memoria(self):
        nota = self.nueva("acme", "Acme factura a 30 días")
        self.assertEqual(nota.parent, self.trabajo / "memoria")
        texto = nota.read_text(encoding="utf-8")
        self.assertIn("status: vigente\n", texto)
        self.assertIn("valida_hasta: null", texto)
        self.assertIn("## Qué hay que recordar", texto)

    def test_archivar_nota_es_cambiar_status(self):
        nota = self.nueva("acme", "Acme factura a 30 días")
        r = correr(self.s / "comun" / "fichas.py", "estado", nota.stem, "archivada", cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(nota.is_file())
        self.assertIn("status: archivada\n", nota.read_text(encoding="utf-8"))
        self.assertEqual(correr(self.s / "comun" / "fichas.py", "estado", nota.stem, "borrada", cwd=self.app).returncode, 1)


class TestBuscar(Base):
    def test_sin_memoria_no_imprime_nada(self):
        r = correr(self.s / "notas.py", "buscar", "acme", cwd=self.app)
        self.assertEqual((r.returncode, r.stdout), (0, ""))
        self.assertFalse(self.trabajo.exists())

    def test_busca_sin_distinguir_mayusculas(self):
        nota = self.nueva("acme", "Acme factura a 30 días")
        r = correr(self.s / "notas.py", "buscar", "ACME", cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"memoria/{nota.name}:", r.stdout)
        self.assertIn(": # Acme factura a 30 días", r.stdout)

    def test_no_busca_fuera_de_memoria(self):
        otro = self.trabajo / "archivo" / "2026-01-01" / "viejo.md"
        otro.parent.mkdir(parents=True)
        otro.write_text("acme antiguo\n", encoding="utf-8")
        self.assertEqual(correr(self.s / "notas.py", "buscar", "acme", cwd=self.app).stdout, "")

    def test_no_acepta_opciones_del_archivo(self):
        self.assertNotEqual(correr(self.s / "notas.py", "buscar", "acme", "--archivo", cwd=self.app).returncode, 0)


class TestVerificar(Base):
    def setUp(self):
        super().setUp()
        integridad = base.calcular_integridad(self.paquete)
        (self.paquete / base.INTEGRIDAD).write_text(json.dumps(integridad), encoding="utf-8")

    def test_verificacion_generica_pasa(self):
        self.nueva("acme", "Acme factura a 30 días")
        r = correr(self.s / "comun" / "verificar.py", cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_status_fuera_de_los_validos_avisa(self):
        nota = self.nueva("acme", "Acme factura a 30 días")
        nota.write_text(nota.read_text(encoding="utf-8").replace("status: vigente", "status: caducada"), encoding="utf-8")
        r = correr(self.s / "comun" / "verificar.py", cwd=self.app)
        self.assertIn("status «caducada» fuera de vigente, archivada", r.stdout)


if __name__ == "__main__":
    unittest.main()
