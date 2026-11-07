"""Pruebas propias del paquete: archivado y consulta del archivo histórico en una app temporal (sin el motor, solo librería estándar)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.dont_write_bytecode = True
PAQUETE = Path(__file__).resolve().parents[1]
ID = PAQUETE.name


def correr(script: Path, *args: str, cwd: Path, humano: bool = False) -> subprocess.CompletedProcess:
    entorno = {"PYTHONDONTWRITEBYTECODE": "1", "PATH": os.environ.get("PATH", "")}
    if humano:
        entorno["UXYNGRAPHAR_HUMANO"] = "1"
    return subprocess.run([sys.executable, str(script), *args], cwd=cwd, capture_output=True, text=True,
                          env=entorno, stdin=subprocess.DEVNULL)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = Path(self.tmp.name)
        self.paquete = self.app / "uxyngraphar" / "paquetes" / ID
        shutil.copytree(PAQUETE, self.paquete, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "pruebas"))
        self.archivo = self.paquete / "scripts" / "archivo.py"
        self.trabajo = self.app / "uxyngraphar" / "trabajo" / ID
        self.doc = self.app / "docs" / "especificacion-v1.md"
        self.doc.parent.mkdir(parents=True)
        self.doc.write_text("# Especificación v1\nrecargo del 5 % en Postgres\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()


class TestArchivar(Base):
    def test_sin_humano_falla_y_no_copia(self):
        r = correr(self.archivo, "archivar", str(self.doc), cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("error: archivar es una acción de la persona", r.stderr)
        r = correr(self.archivo, "archivar", str(self.doc), "--humano", cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("solo una persona", r.stderr)
        self.assertFalse(self.trabajo.exists())

    def test_copia_fechada_sin_borrar_el_original(self):
        r = correr(self.archivo, "archivar", "docs/especificacion-v1.md", "--humano", cwd=self.app, humano=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        destino = self.trabajo / "archivo" / date.today().isoformat() / "especificacion-v1.md"
        self.assertEqual(Path(r.stdout.strip()), destino.resolve())
        self.assertEqual(destino.read_bytes(), self.doc.read_bytes())
        self.assertTrue(self.doc.is_file())

    def test_mismo_nombre_el_mismo_dia_falla(self):
        self.assertEqual(correr(self.archivo, "archivar", str(self.doc), "--humano", cwd=self.app, humano=True).returncode, 0)
        r = correr(self.archivo, "archivar", str(self.doc), "--humano", cwd=self.app, humano=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("ya está archivado hoy", r.stderr)

    def test_rechaza_archivos_de_paquetes_y_rutas_inexistentes(self):
        r = correr(self.archivo, "archivar", str(self.paquete / "PAQUETE.md"), "--humano", cwd=self.app, humano=True)
        self.assertIn("no se archivan archivos de paquetes", r.stderr)
        r = correr(self.archivo, "archivar", "no-existe.md", "--humano", cwd=self.app, humano=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("no existe", r.stderr)


class TestBuscar(Base):
    def test_solo_la_persona(self):
        correr(self.archivo, "archivar", str(self.doc), "--humano", cwd=self.app, humano=True)
        self.assertEqual(correr(self.archivo, "buscar", "recargo", cwd=self.app, humano=True).returncode, 1)
        self.assertEqual(correr(self.archivo, "buscar", "recargo", "--humano", cwd=self.app).returncode, 1)

    def test_busca_sin_distinguir_mayusculas(self):
        correr(self.archivo, "archivar", str(self.doc), "--humano", cwd=self.app, humano=True)
        r = correr(self.archivo, "buscar", "POSTGRES", "--humano", cwd=self.app, humano=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, f"archivo/{date.today().isoformat()}/especificacion-v1.md:2: recargo del 5 % en Postgres\n")

    def test_archivo_vacio_no_imprime_nada(self):
        r = correr(self.archivo, "buscar", "x", "--humano", cwd=self.app, humano=True)
        self.assertEqual((r.returncode, r.stdout), (0, ""))


class TestManifiesto(unittest.TestCase):
    def test_archivo_protegido_y_fuera_de_ia(self):
        m = json.loads((PAQUETE / "paquete.json").read_text(encoding="utf-8"))
        self.assertEqual(m["protegidos"], ["archivo/**"])
        self.assertEqual(m["fuera_de_ia"], ["archivo/**"])


if __name__ == "__main__":
    unittest.main()
