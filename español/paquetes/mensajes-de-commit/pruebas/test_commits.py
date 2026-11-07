"""Pruebas propias del paquete: formato del asunto, mensajes propuestos y commits de un repositorio temporal (sin el motor)."""

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
                          env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1",
                               "HOME": str(cwd)})


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = Path(self.tmp.name)
        self.paquete = self.app / "uxyngraphar" / "paquetes" / ID
        shutil.copytree(PAQUETE, self.paquete, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "pruebas"))

    def tearDown(self):
        self.tmp.cleanup()

    def commits(self, *args: str) -> subprocess.CompletedProcess:
        return correr(sys.executable, str(self.paquete / "scripts" / "commits.py"), *args, cwd=self.app)

    def git(self, *args: str) -> None:
        correr("git", *args, cwd=self.app)

    def repo(self, *asuntos: str) -> None:
        if not shutil.which("git"):
            self.skipTest("sin git")
        for args in (("init", "-q"), ("config", "user.email", "a@example.com"), ("config", "user.name", "a")):
            self.git(*args)
        for i, asunto in enumerate(asuntos):
            (self.app / f"f{i}.txt").write_text(str(i), encoding="utf-8")
            self.git("add", f"f{i}.txt")
            self.git("commit", "-qm", asunto)


class TestMensaje(Base):
    def test_validos(self):
        for asunto in ("feat(orders): add coupon discount", "fix: reject expired tokens", "feat(api/v2)!: drop legacy field",
                       "refactor(order_service.pricing): split totals"):
            r = self.commits("--mensaje", asunto)
            self.assertEqual(r.returncode, 0, asunto)
            self.assertIn("mensaje válido", r.stdout)

    def test_invalidos(self):
        for asunto in ("añadir cupones", "Fix: login", "feat(Orders): add coupons", "feature: add coupons",
                       "feat(orders):add coupons", "feat(orders): añade cupón", "", "feat: " + "a" * 67):
            r = self.commits("--mensaje", asunto)
            self.assertEqual(r.returncode, 1, asunto)
            self.assertIn("no cumple Conventional Commits", r.stdout)

    def test_maximo_72_en_total(self):
        self.assertEqual(self.commits("--mensaje", "feat: " + "a" * 67).returncode, 1)
        self.assertEqual(self.commits("--mensaje", "feat: " + "a" * 66).returncode, 0)

    def test_solo_cuenta_el_asunto(self):
        self.assertEqual(self.commits("--mensaje", "fix(orders): round tax\n\nCuerpo con ñ y muy largo " + "x" * 100).returncode, 0)


class TestHistorial(Base):
    def test_ultimo_commit_y_amend(self):
        self.repo("añadir cupones")
        r = self.commits("1")
        self.assertEqual(r.returncode, 1)
        self.assertIn("«añadir cupones» no cumple Conventional Commits", r.stdout)
        self.git("commit", "-q", "--amend", "-m", "feat(orders): add coupon discount")
        r = self.commits("1")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1 commits revisados, 0 problemas", r.stdout)

    def test_commits_revisar_de_la_persona(self):
        self.repo("wip", "feat: add a", "feat: add b")
        self.assertEqual(self.commits().returncode, 1)
        trabajo = self.app / "uxyngraphar" / "trabajo" / ID
        trabajo.mkdir(parents=True)
        (trabajo / "ajustes.json").write_text(json.dumps({"commits_revisar": 2}), encoding="utf-8")
        r = self.commits()
        self.assertEqual(r.returncode, 0)
        self.assertIn("2 commits revisados", r.stdout)

    def test_fuera_de_git(self):
        r = self.commits("5")
        self.assertEqual(r.returncode, 0)
        self.assertIn("nada que revisar", r.stdout)


if __name__ == "__main__":
    unittest.main()
