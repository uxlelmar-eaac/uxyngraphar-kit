"""Instalar desde una subcarpeta de un repo git: todo se expresa desde la raíz del repo y los commits funcionan."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PACKS = AQUI.parents[2]
sys.path.insert(0, str(AQUI))

if not (PACKS / "backend" / "AGENTES.md").is_file():   # instalado en un proyecto: faltan los packs fuente hermanos
    raise unittest.SkipTest("requiere el repo fuente de uxyngraphar (español/backend y español/frontend); se omite en un proyecto instalado")
sys.path.insert(0, str(AQUI.parent / "ganchos"))
sys.path.insert(0, str(AQUI.parent / "control"))

import instalar_ganchos  # noqa: E402
import uxyngraphar_config as cfg  # noqa: E402


def git(repo: Path, *a: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=repo, capture_output=True, text=True)


class TestSubcarpeta(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.raiz = Path(cls.tmp.name)
        git(cls.raiz, "init", "-q")
        cls.app = cls.raiz / "backend"
        cls.app.mkdir()
        pack = PACKS / "backend"
        cls.r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(pack / "scripts" / "instalar-pack.py"), str(pack), "--repo", str(cls.app), "--proteger"], capture_output=True, text=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_se_instala_como_app_del_monorepo_con_aviso(self):
        self.assertEqual(self.r.returncode, 0, self.r.stdout + self.r.stderr)
        self.assertIn("dentro del repositorio git", self.r.stdout)
        for f in ("backend/AGENTES.md", "backend/docs/.uxyngraphar.lock", "backend/docs/uxyngraphar.config.json", ".github/CODEOWNERS", ".claude/settings.json"):
            self.assertTrue((self.raiz / f).is_file(), f)
        self.assertFalse((self.app / ".github").exists())          # CODEOWNERS en la raíz del repo, no en la subcarpeta
        self.assertFalse((self.raiz / "docs").exists())

    def test_gancho_con_ruta_desde_la_raiz_y_commit_funciona(self):
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(self.app / "docs/scripts/instalar-ganchos.py")], cwd=self.app, capture_output=True, text=True)   # sin --docs, desde la subcarpeta
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('DOCS_LIST="backend/docs"', (self.raiz / ".git/hooks/pre-commit").read_text())
        git(self.raiz, "add", "-A")
        c = git(self.raiz, "commit", "-qm", "x")
        self.assertEqual(c.returncode, 0, c.stdout + c.stderr)

    def test_gancho_con_ruta_vieja_se_repara_y_el_mensaje_es_claro(self):
        hook = self.raiz / ".git/hooks/pre-commit"
        hook.write_text(hook.read_text().replace('DOCS_LIST="backend/docs"', 'DOCS_LIST="docs backend/docs"'))
        (self.raiz / "otra.txt").write_text("x")
        git(self.raiz, "add", "-A")
        c = git(self.raiz, "commit", "-qm", "y")
        self.assertNotEqual(c.returncode, 0)
        self.assertIn("no encuentro docs/scripts", c.stderr)
        instalar_ganchos.instalar(self.raiz, "backend/docs")          # reinstalar descarta «docs», que ya no existe
        self.assertIn('DOCS_LIST="backend/docs"', hook.read_text())
        self.assertEqual(git(self.raiz, "commit", "-qm", "y").returncode, 0)

    def test_scripts_resuelven_docs_desde_la_subcarpeta(self):
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(self.app / "docs/scripts/verificar-nucleo.py")], cwd=self.app, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        raiz, docs = cfg.normalizar(self.app, "docs")
        self.assertEqual((raiz, docs), (self.raiz.resolve(), "backend/docs"))


if __name__ == "__main__":
    unittest.main()
