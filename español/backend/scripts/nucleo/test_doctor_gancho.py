"""El doctor encuentra el gancho donde git realmente lo busca (core.hooksPath, subcarpetas) y avisa si no vigila el pack."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "ganchos"))
sys.path.insert(0, str(AQUI.parent / "decisiones"))
sys.path.insert(0, str(AQUI.parent / "tokens"))

import doctor  # noqa: E402
import instalar_ganchos  # noqa: E402


def gancho(repo: Path, docs: str = "docs"):
    return [c for c in doctor.proteccion_activa(repo, docs) if c.id == "gancho"][0]


class TestDoctorGancho(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_sin_gancho_avisa_con_el_comando_exacto(self):
        c = gancho(self.repo)
        self.assertEqual(c.nivel, "WARN")
        self.assertIn("instalar-ganchos.py", c.arreglo)

    def test_gancho_instalado_ok(self):
        instalar_ganchos.instalar(self.repo, "docs")
        self.assertEqual(gancho(self.repo).nivel, "OK")

    def test_hookspath_personalizado(self):
        (self.repo / ".husky").mkdir()
        subprocess.run(["git", "config", "core.hooksPath", ".husky"], cwd=self.repo, check=True)
        instalar_ganchos.instalar(self.repo, "docs")
        self.assertTrue((self.repo / ".husky" / "pre-commit").is_file())
        self.assertEqual(gancho(self.repo).nivel, "OK")      # antes: falso aviso, buscaba solo en .git/hooks

    def test_gancho_que_no_vigila_este_pack(self):
        instalar_ganchos.instalar(self.repo, "apps/api/docs")
        c = gancho(self.repo, "apps/web/docs")
        self.assertEqual(c.nivel, "WARN")
        self.assertIn("no vigila", c.mensaje)


if __name__ == "__main__":
    unittest.main()
