#!/usr/bin/env python3
"""Pruebas del instalador de ganchos."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import instalar_ganchos as ig  # noqa: E402


class TestGanchos(unittest.TestCase):
    def setUp(self) -> None:
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.repo = Path(self._t.name)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        self.hook = ig.dir_ganchos(self.repo) / "pre-commit"

    def test_instala_idempotente_y_ejecutable(self) -> None:
        ig.instalar(self.repo, "docs")
        ig.instalar(self.repo, "docs")
        txt = self.hook.read_text(encoding="utf-8")
        self.assertEqual(txt.count(ig.MARCA), 1)
        self.assertIn("controlar.py", txt)
        self.assertIn("verificar-nucleo.py", txt)
        if os.name != "nt":   # en Windows no hay bit de ejecución: Git ejecuta el gancho con su sh igualmente
            self.assertTrue(self.hook.stat().st_mode & 0o100)

    def test_no_pisa_gancho_ajeno(self) -> None:
        self.hook.parent.mkdir(parents=True, exist_ok=True)
        self.hook.write_text("#!/bin/sh\necho ajeno\n", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            ig.instalar(self.repo, "docs")
        self.assertIn("ajeno", self.hook.read_text(encoding="utf-8"))
        ig.instalar(self.repo, "docs", force=True)
        self.assertIn(ig.MARCA, self.hook.read_text(encoding="utf-8"))

    def test_quitar_solo_los_propios(self) -> None:
        ig.instalar(self.repo, "docs", con_pre_push=True)
        self.assertEqual(len(ig.quitar(self.repo)), 3)   # pre-commit, commit-msg (R-22) y pre-push
        self.assertFalse(self.hook.exists())
        self.hook.write_text("#!/bin/sh\necho ajeno\n", encoding="utf-8")
        ig.quitar(self.repo)
        self.assertTrue(self.hook.exists())

    def test_commit_msg_revisa_el_mensaje(self) -> None:
        ig.instalar(self.repo, "docs")
        txt = (ig.dir_ganchos(self.repo) / "commit-msg").read_text(encoding="utf-8")
        self.assertIn("\"--mensaje\", \"$1\"", txt)

    def test_pre_push_usa_base(self) -> None:
        self.assertIn("origin/develop", ig.contenido("pre-push", "docs", "origin/develop"))


if __name__ == "__main__":
    unittest.main()
