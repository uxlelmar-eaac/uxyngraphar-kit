"""Pruebas propias del paquete: recogida de pendientes y hoja de revisión en una app temporal (sin el motor, solo librería estándar).

La app lleva este paquete y un paquete mínimo de prueba con fichas que esperan a una persona. Se ejecutan como un agente
(sin terminal ni UXYNGRAPHAR_HUMANO): comprueban que el agente prepara la hoja pero no puede aplicar decisiones.
"""

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
OTRO = "propuestas-de-prueba"
MANIFIESTO_OTRO = {
    "manifiesto_formato": 2, "id": OTRO, "version": "1.0.0", "titulo": "Propuestas de prueba", "descripcion": "Paquete mínimo para las pruebas.",
    "familia": "proceso", "motor": ">=2.0", "activacion": [OTRO], "entrada": "README.md", "verificaciones": [],
    "piezas": ["plantillas"],
    "fichas": {
        "propuesta": {"carpeta": "propuestas", "prefijo": "PPR", "plantilla": "plantillas/propuesta.md", "inicial": "propuesta",
                      "estados": {"propuesta": "pendientes", "aprobada": "completadas", "rechazada": "canceladas"},
                      "solo_humano": ["aprobada", "rechazada"]},
        "nota": {"carpeta": "notas", "prefijo": "NPR", "plantilla": "plantillas/propuesta.md", "inicial": "propuesta",
                 "status_validos": ["propuesta"]},
    },
}
PLANTILLA = "---\nid: {{id}}\nstatus: {{status}}\nfecha: {{fecha}}\n---\n\n# {{titulo}}\n"


def correr(script: Path, *args: str, cwd: Path) -> subprocess.CompletedProcess:
    entorno = {k: v for k, v in os.environ.items() if k not in ("UXYNGRAPHAR_HUMANO", "CI")}
    entorno["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run([sys.executable, str(script), *args], cwd=cwd, capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, env=entorno)


class TestRevision(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = Path(self.tmp.name)
        paquetes = self.app / "uxyngraphar" / "paquetes"
        shutil.copytree(PAQUETE, paquetes / ID, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "pruebas"))
        otro = paquetes / OTRO
        shutil.copytree(PAQUETE / "scripts" / "comun", otro / "scripts" / "comun", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        (otro / "plantillas").mkdir()
        (otro / "plantillas" / "propuesta.md").write_text(PLANTILLA, encoding="utf-8")
        (otro / "paquete.json").write_text(json.dumps(MANIFIESTO_OTRO), encoding="utf-8")
        (otro / "README.md").write_text("# Propuestas de prueba\n", encoding="utf-8")
        self.s = paquetes / ID / "scripts"
        self.fichas_otro = otro / "scripts" / "comun" / "fichas.py"

    def tearDown(self):
        self.tmp.cleanup()

    def nueva(self, tipo: str, slug: str) -> Path:
        r = correr(self.fichas_otro, "nueva", tipo, "--slug", slug, cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        return Path(r.stdout.strip())

    def test_sin_pendientes(self):
        self.assertIn("(nada espera una decisión)", correr(self.s / "revision.py", "pendientes", cwd=self.app).stdout)

    def test_recoge_solo_lo_que_espera_a_una_persona(self):
        propuesta = self.nueva("propuesta", "usar-cache")
        nota = self.nueva("nota", "apunte")
        r = correr(self.s / "revision.py", "pendientes", cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(propuesta.stem, r.stdout)
        self.assertIn(f"scripts/comun/fichas.py estado {propuesta.stem} <status> --humano", r.stdout)
        self.assertIn("aprobada, rechazada", r.stdout)
        self.assertNotIn(nota.stem, r.stdout, "un tipo sin solo_humano ni espera_humano no espera a nadie")

    def test_preparar_deja_la_decision_vacia(self):
        propuesta = self.nueva("propuesta", "usar-cache")
        self.assertEqual(correr(self.s / "revision.py", "preparar", cwd=self.app).returncode, 0)
        texto = (self.app / "uxyngraphar" / "trabajo" / ID / "REVISION.md").read_text(encoding="utf-8")
        fila = next(linea for linea in texto.splitlines() if propuesta.stem in linea)
        self.assertTrue(fila.endswith("| aprobada, rechazada |  |"), fila)

    def test_el_agente_no_aplica(self):
        propuesta = self.nueva("propuesta", "usar-cache")
        correr(self.s / "revision.py", "preparar", cwd=self.app)
        r = correr(self.s / "revision.py", "aplicar", cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("--humano", r.stderr)
        r = correr(self.s / "revision.py", "aplicar", "--humano", cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("solo una persona", r.stderr)
        self.assertTrue(propuesta.is_file(), "la ficha no se mueve")

    def test_avisa_de_los_pendientes_antiguos(self):
        propuesta = self.nueva("propuesta", "vieja")
        texto = propuesta.read_text(encoding="utf-8")
        propuesta.write_text("\n".join("fecha: 2020-01-01" if l.startswith("fecha:") else l for l in texto.splitlines()) + "\n",
                             encoding="utf-8")
        r = correr(self.s / "verificar-revision.py", cwd=self.app)
        self.assertEqual(r.returncode, 0, "la antigüedad nunca hace fallar la verificación")
        self.assertIn(f"aviso: {OTRO}/{propuesta.stem} lleva", r.stdout)
        self.assertIn("1 con más de 14 días", r.stdout)


if __name__ == "__main__":
    unittest.main()
