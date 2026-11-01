#!/usr/bin/env python3
"""Pruebas de mover la carpeta del pack (docs/ → uxyngraphar/)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import doctor as dr  # noqa: E402
import flujo  # noqa: E402
import lock  # noqa: E402
import mover  # noqa: E402
import transaccion  # noqa: E402
from test_nucleo import Base  # noqa: E402

ENV = ("-c", "user.name=t", "-c", "user.email=t@t")


class TestMover(Base):
    def setUp(self) -> None:
        super().setUp()
        (self.repo / "go.mod").write_text("module x\n", encoding="utf-8")
        (self.repo / "README.md").write_text("Guía: [docs](docs/10-guias/actualizar-nucleo.md)\n", encoding="utf-8")
        r = flujo.instalar_completo(self.pack, self.repo, "docs", proteger=True, propietario="@equipo", ganchos=True, claude_md=True)
        self.assertTrue(r.ok, [p.__dict__ for p in r.pasos])
        self.commit("instalado en docs/")

    def git(self, *a: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *ENV, *a], cwd=self.repo, capture_output=True, text=True)

    def commit(self, mensaje: str) -> None:
        self.git("add", "-A")
        c = self.git("commit", "-qm", f"chore: {mensaje}")
        self.assertEqual(c.returncode, 0, c.stdout + c.stderr)

    def leer(self, rel: str) -> str:
        return (self.repo / rel).read_text(encoding="utf-8")

    def test_ver_que_cambia_no_escribe(self) -> None:
        antes = {r: self.leer(r) for r in (".claude/settings.json", ".github/CODEOWNERS", ".gitignore", "CLAUDE.md")}
        p = mover.planificar(self.repo, "docs")
        self.assertEqual((p.desde, p.hacia, p.git), ("docs", "uxyngraphar", True))
        texto = mover.formatear(p)
        for parte in ("git mv", "Gancho de git pre-commit", ".claude/settings.json", ".cursorignore", "CODEOWNERS", ".gitignore",
                      ".gitattributes", "CLAUDE.md", "workflows/uxyngraphar.yml"):
            self.assertIn(parte, texto)
        self.assertTrue(any(r.startswith("README.md:1:") for r in p.revisar), p.revisar)
        self.assertTrue((self.repo / "docs").is_dir() and not (self.repo / "uxyngraphar").exists())
        self.assertEqual(antes, {r: self.leer(r) for r in antes})

    def test_mover_deja_todo_funcionando(self) -> None:
        reglas_usuario = json.loads(self.leer(".claude/settings.json"))
        reglas_usuario["permissions"]["deny"].append("Read(secretos-propios/**)")
        (self.repo / ".claude/settings.json").write_text(json.dumps(reglas_usuario, indent=2), encoding="utf-8")
        self.commit("regla propia")
        carpeta = mover.aplicar(mover.planificar(self.repo, "docs"))
        self.assertTrue((carpeta / "_respaldo.json").is_file())
        self.assertFalse((self.repo / "docs").exists())
        self.assertEqual(lock.leer(self.repo, "uxyngraphar")["docs"], "uxyngraphar")
        deny = json.loads(self.leer(".claude/settings.json"))["permissions"]["deny"]
        self.assertFalse([r for r in deny if "(docs/" in r])
        self.assertIn("Edit(uxyngraphar/scripts/**)", deny)
        self.assertIn("Read(secretos-propios/**)", deny)                      # lo de la persona no se toca
        self.assertIn('DOCS_LIST="uxyngraphar"', self.leer(".git/hooks/pre-commit"))
        for gancho in ("pre-commit", "commit-msg"):
            self.assertTrue(os.access(self.repo / ".git/hooks" / gancho, os.X_OK), gancho)   # git ignora un gancho no ejecutable
        for rel in (".cursorignore", ".github/CODEOWNERS", ".gitignore", ".gitattributes", "CLAUDE.md", ".github/workflows/uxyngraphar.yml"):
            self.assertNotIn("docs/", self.leer(rel).replace("README", ""), rel)
            self.assertIn("uxyngraphar/", self.leer(rel), rel)
        self.assertIn("docs/10-guias", self.leer("README.md"))                 # contenido propio: solo se avisa
        self.assertFalse([c for c in dr.diagnosticar(self.repo) if c.nivel == "ERROR"], [c for c in dr.diagnosticar(self.repo) if c.nivel == "ERROR"])
        estado = self.git("status", "--porcelain").stdout
        self.assertIn("R  docs/REGLAS.md -> uxyngraphar/REGLAS.md", estado)
        self.commit("mover la carpeta del pack")                                # los ganchos pasan con la ruta nueva
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(self.repo / "uxyngraphar/scripts/verificar-nucleo.py")], cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)                  # sin --docs: la deduce

    def test_y_de_vuelta(self) -> None:
        mover.aplicar(mover.planificar(self.repo, "docs"))
        self.commit("a uxyngraphar")
        mover.aplicar(mover.planificar(self.repo, "uxyngraphar", "docs"))
        self.assertTrue((self.repo / "docs/.uxyngraphar.lock").is_file())
        self.assertIn('DOCS_LIST="docs"', self.leer(".git/hooks/pre-commit"))

    def test_rechazos(self) -> None:
        with self.assertRaisesRegex(mover.ErrorMover, "no hay nada que mover"):
            mover.planificar(self.repo, "docs", "docs")
        with self.assertRaisesRegex(mover.ErrorMover, "debe llamarse"):
            mover.planificar(self.repo, "docs", "documentacion")
        with self.assertRaisesRegex(mover.ErrorMover, "no hay un pack"):
            mover.planificar(self.repo, "otra")
        (self.repo / "uxyngraphar").mkdir()
        with self.assertRaisesRegex(mover.ErrorMover, "ya existe"):
            mover.planificar(self.repo, "docs")
        (self.repo / "uxyngraphar").rmdir()
        (self.repo / "docs/25-areas/nota.md").parent.mkdir(parents=True, exist_ok=True)
        (self.repo / "docs/25-areas/nota.md").write_text("x\n", encoding="utf-8")
        with self.assertRaisesRegex(mover.ErrorMover, "sin commit"):
            mover.planificar(self.repo, "docs")
        self.commit("nota")
        (self.repo / "docs/scripts/carpeta_pack.py").unlink()   # como un pack 1.0.x (sus ganchos no lo necesitan; estos sí)
        self.git("add", "-A")
        self.git("commit", "-qm", "chore: pack antiguo", "--no-verify")
        with self.assertRaisesRegex(mover.ErrorMover, "anteriores a la 1.1.0"):
            mover.planificar(self.repo, "docs")

    def test_claude_md_propio_no_se_toca(self) -> None:
        (self.repo / "CLAUDE.md").write_text("# Mío\n\nUsa docs/scripts/contexto.py\n", encoding="utf-8")
        self.commit("claude propio")
        p = mover.planificar(self.repo, "docs")
        self.assertTrue(any("CLAUDE.md lo cambiaste tú" in a for a in p.avisos))
        mover.aplicar(p)
        self.assertIn("docs/scripts", self.leer("CLAUDE.md"))

    def test_fallo_a_mitad_vuelve_atras(self) -> None:
        antes = {r: self.leer(r) for r in (".claude/settings.json", ".github/CODEOWNERS", ".gitignore", ".git/hooks/pre-commit")}
        with mock.patch.object(lock, "escribir", side_effect=OSError("disco lleno")), self.assertRaises(OSError):
            mover.aplicar(mover.planificar(self.repo, "docs"))
        self.assertTrue((self.repo / "docs/.uxyngraphar.lock").is_file())
        self.assertFalse((self.repo / "uxyngraphar").exists())
        self.assertEqual(antes, {r: self.leer(r) for r in antes})
        self.assertEqual(self.git("status", "--porcelain", "--", "docs", ".claude", ".github", ".gitignore", ".gitattributes", "CLAUDE.md").stdout, "")

    def test_corte_brusco_se_recupera(self) -> None:
        p = mover.planificar(self.repo, "docs")
        with mock.patch.object(transaccion.Transaccion, "deshacer", lambda self, motivo="": None), \
             mock.patch.object(transaccion.Transaccion, "escribir", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                mover.aplicar(p)
        self.assertTrue((self.repo / "uxyngraphar").exists())                  # quedó a medias…
        self.assertTrue(transaccion.recuperar(self.repo))                       # …y la siguiente ejecución lo deshace
        self.assertTrue((self.repo / "docs/.uxyngraphar.lock").is_file())
        self.assertFalse((self.repo / "uxyngraphar").exists())
        self.assertEqual(lock.leer(self.repo, "docs")["docs"], "docs")


if __name__ == "__main__":
    unittest.main()
