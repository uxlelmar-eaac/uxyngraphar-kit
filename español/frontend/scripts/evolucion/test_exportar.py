#!/usr/bin/env python3
"""Pruebas de exportar-evo: selección por estado, informe y marcado."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import exportar  # noqa: E402

EVO = "---\nid: {id}\nstatus: {st}\ntipo: proceso\nimpacto: ambos\npropuesta_cambio:\n  - REGLAS.md\n---\n# {id}\n\nFalta un paso.\n"


class TestExportar(unittest.TestCase):
    def setUp(self) -> None:
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.docs = Path(self._t.name) / "docs"
        for est, carpeta, i in (("pending", "01-pendientes", "EVO-20261026-a"), ("done", "03-completadas", "EVO-20261026-b")):
            d = self.docs / "46-evolucion-documentacion" / carpeta / "2026-10-26"
            d.mkdir(parents=True)
            (d / f"{i}.md").write_text(EVO.format(id=i, st=est), encoding="utf-8")

    def test_selecciona_informa_y_marca(self) -> None:
        items = exportar.fichas(self.docs)
        self.assertEqual([fm["id"] for _m, fm, _c in items], ["EVO-20261026-a"])
        texto = exportar.informe(self.docs, items, "proy", "1.0.0")
        self.assertIn("| EVO-20261026-a | pending | proceso | ambos |", texto)
        self.assertIn("`REGLAS.md`", texto)
        self.assertIn("Falta un paso.", texto)
        self.assertEqual(exportar.marcar(items, "2026-10-26"), 1)
        self.assertEqual(exportar.fichas(self.docs), [])
        self.assertEqual(len(exportar.fichas(self.docs, incluir_exportadas=True)), 1)

    def test_cli(self) -> None:
        r = subprocess.run([sys.executable, str(AQUI.parent / "exportar-evo.py"), "--repo", str(self.docs.parent)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("EVO-20261026-a", r.stdout)
        self.assertNotIn("EVO-20261026-b", r.stdout)


if __name__ == "__main__":
    unittest.main()
