#!/usr/bin/env python3
"""Pruebas del mapa del espejo y de código sin espejo."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import mapa  # noqa: E402


class TestMapa(unittest.TestCase):
    def setUp(self) -> None:
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.repo = Path(self._t.name)
        self.docs = self.repo / "docs"
        e = self.docs / "50-sistema-integral/src/pagos"
        e.mkdir(parents=True)
        (e / "cobro.md").write_text("---\nresumen: Calcula el cobro final\n---\n# cobro\n\nOtro texto\n", encoding="utf-8")
        (e / "README.md").write_text("# pagos\n\n> cita\n\nCarpeta de pagos | con barra.\n", encoding="utf-8")
        (self.docs / "50-sistema-integral/_PLANTILLA-archivo.md").write_text("# plantilla\n", encoding="utf-8")
        c = self.repo / "src/pagos"
        c.mkdir(parents=True)
        (c / "cobro.py").write_text("x", encoding="utf-8")
        (c / "nuevo.py").write_text("x", encoding="utf-8")
        (self.repo / "src/node_modules").mkdir()
        (self.repo / "src/node_modules/x.js").write_text("x", encoding="utf-8")

    def test_mapa_usa_resumen_o_primera_prosa(self) -> None:
        t = mapa.mapa(self.docs)
        self.assertIn("| `src/pagos/cobro` | Calcula el cobro final |", t)
        self.assertIn("| `src/pagos/` | Carpeta de pagos / con barra. |", t)
        self.assertNotIn("PLANTILLA", t)

    def test_faltantes_excluye_dependencias(self) -> None:
        self.assertEqual(mapa.faltantes(self.docs, self.repo, ["src"]), ["src/pagos/nuevo.py"])

    def test_resumen_largo_se_trunca(self) -> None:
        f = self.docs / "50-sistema-integral/src/pagos/largo.md"
        f.write_text("# l\n\n" + "palabra " * 60, encoding="utf-8")
        self.assertLessEqual(len(mapa.resumen_de(f)), mapa.RESUMEN_MAX)


if __name__ == "__main__":
    unittest.main()
