"""Pruebas de las restricciones de credenciales: .gitignore, reglas deny de agentes y chequeo del doctor."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "control"))
sys.path.insert(0, str(AQUI.parent / "ganchos"))
sys.path.insert(0, str(AQUI.parent / "decisiones"))
sys.path.insert(0, str(AQUI.parent / "tokens"))

import doctor  # noqa: E402
import instalar as ins  # noqa: E402
import proteccion  # noqa: E402


class TestSecretosProyecto(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        (self.repo / "docs").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_gitignore_incluye_credenciales_y_excepcion_example(self):
        ins.asegurar_gitignore(self.repo, "docs", False)
        lineas = (self.repo / ".gitignore").read_text().splitlines()
        for esperado in (".env", ".env.*", "!.env.example", "*.pem", "*.key", "credentials.json"):
            self.assertIn(esperado, lineas)
        (self.repo / ".env").write_text("A=1\n")
        (self.repo / ".env.example").write_text("A=<VALOR>\n")
        ignorados = subprocess.run(["git", "check-ignore", ".env", ".env.example"], cwd=self.repo, capture_output=True, text=True).stdout.split()
        self.assertEqual(ignorados, [".env"])

    def test_reglas_deny_bloquean_lectura_y_escritura_de_llaves(self):
        proteccion.reglas_agente(self.repo, "docs")
        deny = json.loads((self.repo / ".claude" / "settings.json").read_text())["permissions"]["deny"]
        for regla in ("Read(.env)", "Read(**/*.pem)", "Write(**/*.key)", "Read(~/.ssh/**)", "Read(~/.aws/**)"):
            self.assertIn(regla, deny)
        self.assertNotIn("Read(.env.example)", deny)
        antes = list(deny)
        proteccion.reglas_agente(self.repo, "docs")
        self.assertEqual(json.loads((self.repo / ".claude" / "settings.json").read_text())["permissions"]["deny"], antes)   # idempotente

    def test_doctor_reporta_credencial_en_el_arbol(self):
        r = doctor.secretos(self.repo, "docs")
        self.assertEqual(r[0].nivel, "WARN")                       # limpio, pero sin reglas deny
        proteccion.reglas_agente(self.repo, "docs")
        self.assertEqual(doctor.secretos(self.repo, "docs")[0].nivel, "OK")
        (self.repo / "app.py").write_text('K = "' + "AKIA" + 'ABCDEFGHIJKLMNOP"\n')
        r = doctor.secretos(self.repo, "docs")
        self.assertEqual(r[0].nivel, "ERROR")
        self.assertNotIn("AKIA" + "ABCDEFGHIJKLMNOP", r[0].mensaje)


if __name__ == "__main__":
    unittest.main()
