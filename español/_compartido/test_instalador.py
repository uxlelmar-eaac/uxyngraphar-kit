"""Prueba extremo a extremo del asistente de la raíz (instalar.py) en modo no interactivo."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]   # español/ (donde vive instalar.py)


class TestInstalador(unittest.TestCase):
    def test_instala_y_luego_ofrece_actualizar(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            (repo / "go.mod").write_text("module x\n")
            r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(RAIZ / "instalar.py"), "--proyecto", str(repo), "--si"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            for f in ("AGENTES.md", "docs/.uxyngraphar.lock", "docs/uxyngraphar.config.json", ".claude/settings.json", "CLAUDE.md"):
                self.assertTrue((repo / f).is_file(), f)
            self.assertIn('"go"', (repo / "docs/uxyngraphar.config.json").read_text())
            r2 = subprocess.run([sys.executable, "-X", "utf8", "-I", str(RAIZ / "instalar.py"), "--proyecto", str(repo), "--si"], capture_output=True, text=True)
            self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
            self.assertIn("al día", r2.stdout)
            self.assertIn("Sin cambios aplicados", r2.stdout)   # --si no aplica actualizaciones por sí solo

    def _repo(self, base: Path, nombre: str) -> Path:
        r = base / nombre
        r.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=r, check=True)
        return r

    def test_ambos_en_el_mismo_repo(self):
        with tempfile.TemporaryDirectory() as t:
            repo = self._repo(Path(t), "mono")
            r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(RAIZ / "instalar.py"), "--proyecto", str(repo), "--pack", "ambos", "--mismo-repo",
                                "--sub-servidor", "apps/api", "--sub-cliente", "apps/web", "--si"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            for f in ("apps/api/AGENTES.md", "apps/api/docs/.uxyngraphar.lock", "apps/web/AGENTES.md", "apps/web/docs/.uxyngraphar.lock"):
                self.assertTrue((repo / f).is_file(), f)
            self.assertFalse((repo / "AGENTES.md").exists())
            self.assertIn("apps/api/docs apps/web/docs", (repo / ".git/hooks/pre-commit").read_text())

    def test_ambos_en_repos_distintos(self):
        with tempfile.TemporaryDirectory() as t:
            a, b = self._repo(Path(t), "api"), self._repo(Path(t), "web")
            r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(RAIZ / "instalar.py"), "--proyecto", str(a), "--proyecto2", str(b), "--pack", "ambos", "--si"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("servidor", (a / "AGENTES.md").read_text().splitlines()[0])
            self.assertIn("cliente", (b / "AGENTES.md").read_text().splitlines()[0])

    def test_rechaza_misma_subcarpeta(self):
        with tempfile.TemporaryDirectory() as t:
            repo = self._repo(Path(t), "mono")
            r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(RAIZ / "instalar.py"), "--proyecto", str(repo), "--pack", "ambos", "--mismo-repo", "--sub-servidor", "app", "--sub-cliente", "app", "--si"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 2)

    def test_carpeta_inexistente(self):
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(RAIZ / "instalar.py"), "--proyecto", "/no/existe/xyz", "--si"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
