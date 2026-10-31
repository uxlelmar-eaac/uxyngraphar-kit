#!/usr/bin/env python3
"""Pruebas de la deriva del espejo."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import verificar_espejo as ve  # noqa: E402

I = ve.Instruccion


class TestAnalizar(unittest.TestCase):
    def test_sin_codigo_sin_hallazgos(self) -> None:
        self.assertEqual(ve.analizar(["docs/a.md", "README.md"], [], "docs"), [])

    def test_codigo_sin_instruccion(self) -> None:
        h = ve.analizar(["src/a.py"], [], "docs")
        self.assertEqual([x.regla for x in h], ["R-03"])

    def test_codigo_fuera_de_anclas(self) -> None:
        ins = I("x", "docs/i.md", "completed", ["src/a.py:1-10"], ["50-sistema-integral/a.md"])
        h = ve.analizar(["src/a.py", "src/b.py", "docs/50-sistema-integral/a.md"], [ins], "docs")
        self.assertEqual([x.regla for x in h], ["anclas"])

    def test_ancla_directorio_cubre_hijos(self) -> None:
        ins = I("x", "docs/i.md", "completed", ["src/"], ["50-sistema-integral/a.md"])
        self.assertEqual(ve.analizar(["src/m/a.py", "docs/50-sistema-integral/a.md"], [ins], "docs"), [])

    def test_r21_mas_archivos_que_el_tope(self) -> None:
        ins = I("x", "docs/i.md", "approved", ["src/"], [])
        h = ve.analizar([f"src/m{n}.py" for n in range(6)], [ins], "docs")
        self.assertIn("R-21", [x.regla for x in h])
        amp = I("x", "docs/i.md", "approved", ["src/"], [], maximo=7)
        self.assertNotIn("R-21", [x.regla for x in ve.analizar([f"src/m{n}.py" for n in range(6)], [amp], "docs")])

    def test_r21_bloqueos_de_la_ficha(self) -> None:
        ins = I("x", "docs/i.md", "approved", ["src/a.py"], [], bloqueos=["sin aprobación humana"])
        self.assertIn("x: sin aprobación humana", [x.mensaje for x in ve.analizar(["src/a.py"], [ins], "docs")])

    def test_espejo_no_cambiado(self) -> None:
        ins = I("x", "docs/i.md", "completed", ["src/a.py"], ["50-sistema-integral/a.md"])
        h = ve.analizar(["src/a.py"], [ins], "docs")
        self.assertEqual([x.regla for x in h], ["espejo"])

    def test_anclas_sin_espejo(self) -> None:
        ins = I("x", "docs/i.md", "completed", ["src/a.py"], [])
        h = ve.analizar(["src/a.py"], [ins], "docs")
        self.assertIn("espejo", [x.regla for x in h])

    def test_ruta_ancla_windows_y_rango(self) -> None:
        self.assertEqual(ve._ruta_ancla("src/a.ts:40-80"), "src/a.ts")
        self.assertEqual(ve._ruta_ancla("src/a.ts"), "src/a.ts")


class TestGit(unittest.TestCase):
    def test_diff_staged_e_instrucciones(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)

            def git(*a: str) -> None:
                subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=repo, check=True, capture_output=True)

            git("init", "-q")
            (repo / "src").mkdir()
            (repo / "src" / "a.py").write_text("x=1\n", encoding="utf-8")
            ins = repo / "docs" / "05-instrucciones" / "02-en-progreso" / "2026-10-15" / "uno.md"
            ins.parent.mkdir(parents=True)
            ins.write_text("---\nid: uno\nstatus: in-progress\nanclas_codigo:\n  - src/a.py\nespejo_actualizar:\n  - 50-sistema-integral/a.md\n---\n# u\n", encoding="utf-8")
            git("add", "-A")
            cambiados = ve.cambiados_git(repo, "origin/main", staged=True)
            self.assertIn("src/a.py", cambiados or [])
            instr = ve.instrucciones_del_cambio(repo, cambiados or [], "docs")
            self.assertEqual([i.id for i in instr], ["uno"])
            self.assertEqual(instr[0].anclas, ["src/a.py"])
            h = ve.analizar(cambiados or [], instr, "docs")
            self.assertEqual([x.regla for x in h], ["espejo"])


if __name__ == "__main__":
    unittest.main()
