"""Pruebas propias del paquete: verificación de herramientas autorizadas y propuestas en una app temporal (sin el motor, solo librería estándar).

Se ejecutan como un agente (sin terminal ni UXYNGRAPHAR_HUMANO). Las fichas autorizadas se escriben como datos de partida,
igual que las dejaría una persona.
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
PAQUETE = Path(__file__).resolve().parents[1]
ID = PAQUETE.name


def correr(script: Path, *args: str, cwd: Path) -> subprocess.CompletedProcess:
    entorno = {k: v for k, v in os.environ.items() if k not in ("UXYNGRAPHAR_HUMANO", "CI")}
    entorno["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run([sys.executable, str(script), *args], cwd=cwd, capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, env=entorno)


class TestHerramientas(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = Path(self.tmp.name)
        destino = self.app / "uxyngraphar" / "paquetes" / ID
        shutil.copytree(PAQUETE, destino, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "pruebas"))
        self.s = destino / "scripts"
        self.autorizadas = self.app / "uxyngraphar" / "trabajo" / ID / "autorizadas"
        self.autorizadas.mkdir(parents=True)
        (self.app / "scripts").mkdir()
        (self.app / "scripts" / "generar-cliente.sh").write_text("#!/bin/sh\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def autorizada(self, slug: str, status: str = "authorized", por: str = "Ana (equipo API)", source: str = "human",
                   anclas: tuple[str, ...] = ("scripts/generar-cliente.sh",)) -> str:
        fid = f"HER-20261001-{slug}"
        lineas = ["---", f"id: {fid}", f"status: {status}", f"source: {source}", f'authorized_by: "{por}"',
                  "authorized_at: 2026-10-01", "scope: []", "anclas_codigo:", *(f"  - {a}" for a in anclas), "---", "",
                  f"# {slug}", ""]
        (self.autorizadas / f"{fid}.md").write_text("\n".join(lineas), encoding="utf-8")
        return fid

    def verificar(self) -> subprocess.CompletedProcess:
        return correr(self.s / "verificar-herramientas.py", cwd=self.app)

    def test_autorizada_completa(self):
        self.autorizada("generar-cliente-api")
        r = self.verificar()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("herramientas: 0 errores, 0 avisos", r.stdout)

    def test_sin_responsable_o_creada_por_el_agente(self):
        self.autorizada("sin-firma", por="<persona o equipo>")
        self.autorizada("de-la-ia", source="ai")
        r = self.verificar()
        self.assertEqual(r.returncode, 1)
        self.assertIn("authorized sin authorized_by", r.stderr)
        self.assertIn("debe tener source: human", r.stderr)

    def test_revocada_no_se_revisa(self):
        self.autorizada("antigua", status="revoked", por="<persona o equipo>")
        self.assertEqual(self.verificar().returncode, 0)

    def test_ancla_inexistente_es_aviso(self):
        self.autorizada("con-ancla-rota", anclas=("scripts/no-existe.sh",))
        r = self.verificar()
        self.assertEqual(r.returncode, 0)
        self.assertIn("ancla inexistente scripts/no-existe.sh", r.stdout)

    def test_el_agente_propone_pero_no_autoriza(self):
        fichas = self.s / "comun" / "fichas.py"
        r = correr(fichas, "nueva", "autorizada", "--slug", "atajo", cwd=self.app)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(list(self.autorizadas.rglob("*.md")), [])
        r = correr(fichas, "nueva", "propuesta", "--slug", "regenerar-traducciones", cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        propuesta = Path(r.stdout.strip())
        self.assertEqual(propuesta.parent.name, "pendientes")
        self.assertIn("source: ai", propuesta.read_text(encoding="utf-8"))
        r = correr(fichas, "estado", propuesta.stem, "promovida", cwd=self.app)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("solo lo asigna una persona", r.stderr)


if __name__ == "__main__":
    unittest.main()
