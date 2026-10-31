#!/usr/bin/env python3
"""Pruebas de empaquetado .zip, análisis de adopción y CLAUDE.md."""

from __future__ import annotations

import subprocess
import sys
import unittest
import warnings
import zipfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import analizar  # noqa: E402
import empaquetar  # noqa: E402
import lock  # noqa: E402
from test_nucleo import Base  # noqa: E402


class TestZip(Base):
    def test_zip_solo_lleva_n_p_m_y_se_instala(self) -> None:
        z = empaquetar.empaquetar(self.pack, self.tmp / "dist")
        with zipfile.ZipFile(z) as f:
            nombres = f.namelist()
        self.assertIn(empaquetar.MANIFIESTO, nombres)
        self.assertIn("REGLAS.md", nombres)
        self.assertFalse([n for n in nombres if "03-completadas/2026" in n and n.endswith(".md") and "README" not in n])
        with empaquetar.abrir_pack(z) as p:
            self.assertEqual(lock.version_de(p), lock.version_de(self.pack))
            self.assertTrue((p / "REGLAS.md").is_file())

    def test_zip_alterado_o_sin_manifiesto_se_rechaza(self) -> None:
        z = empaquetar.empaquetar(self.pack, self.tmp / "dist")
        mal = self.tmp / "mal.zip"
        mal.write_bytes(z.read_bytes())
        with zipfile.ZipFile(mal, "a") as f, warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)   # el nombre repetido es justo la alteración que se prueba
            f.writestr("10-guias/pruebas.md", "alterado")
        with self.assertRaises(ValueError), empaquetar.abrir_pack(mal):
            pass
        sin = self.tmp / "sin.zip"
        with zipfile.ZipFile(sin, "w") as f:
            f.writestr("a.txt", "x")
        with self.assertRaises(ValueError), empaquetar.abrir_pack(sin):
            pass

    def test_zip_con_ruta_insegura(self) -> None:
        mal = self.tmp / "trav.zip"
        with zipfile.ZipFile(mal, "w") as f:
            f.writestr("../fuera.txt", "x")
        with self.assertRaises(ValueError), empaquetar.abrir_pack(mal):
            pass

    def test_cli_instala_desde_zip_con_claude_md(self) -> None:
        z = empaquetar.empaquetar(self.pack, self.tmp / "dist")
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(AQUI.parent / "instalar-pack.py"), str(z), "--repo", str(self.repo), "--claude-md"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("AGENTES.md", (self.repo / "CLAUDE.md").read_text(encoding="utf-8"))
        self.assertTrue((self.repo / "docs/.uxyngraphar.lock").is_file())


class TestAnalizar(Base):
    def test_sugiere_destinos_sin_escribir(self) -> None:
        for n, c in (("docs/adr-001-db.md", "x"), ("docs/despliegue.md", "x"), ("README.md", "x"), ("notas/otra-cosa.md", "x"), ("node_modules/a/readme.md", "x")):
            f = self.repo / n
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(c, encoding="utf-8")
        r = analizar.analizar(self.repo)
        self.assertEqual(r["20-decisiones/ (ADR)"], ["docs/adr-001-db.md"])
        self.assertEqual(r["30-manuales/"], ["docs/despliegue.md"])
        self.assertEqual(r["sin-sugerencia"], ["notas/otra-cosa.md"])
        self.assertFalse(any("node_modules" in a for v in r.values() for a in v))
        self.assertIn("sugerencias", analizar.formatear(r))


if __name__ == "__main__":
    unittest.main()
