#!/usr/bin/env python3
"""Pruebas de estimación, paquete de contexto y medición de tokens."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import estimar  # noqa: E402
import medir  # noqa: E402
import paquete  # noqa: E402

INSTR = """---
id: 20261015-001-demo
status: approved
areas: []
lectura_minima:
  - 25-areas/pagos/CONTEXTO.md#reglas de cobro
  - docs/10-guias/falta.md
anclas_codigo:
  - src/pagos.py:2-3
  - src/grande.py
espejo_actualizar: []
vinculos_salida: []
---
# Demo

Objetivo claro.

## Decisión a tomar

<!-- decision-group: x -->
- [ ] Aprobar
"""
CONTEXTO = "# Contexto\n\nIntro.\n\n## Reglas de cobro\n\nSe cobra al final.\n\n### Detalle\n\nMás.\n\n## Otra cosa\n\nNo debe aparecer.\n"


class TestEstimar(unittest.TestCase):
    def test_tokens_y_slug(self) -> None:
        self.assertEqual(estimar.tokens("a" * 8), 2)
        self.assertEqual(estimar.slug("Reglas de Cobro (v2)"), "reglas-de-cobro-v2")

    def test_extraer_seccion_incluye_subsecciones_y_corta_en_el_siguiente(self) -> None:
        s = estimar.extraer_seccion(CONTEXTO, "reglas de cobro")
        self.assertIn("Se cobra al final", s or "")
        self.assertIn("### Detalle", s or "")
        self.assertNotIn("Otra cosa", s or "")
        self.assertIsNone(estimar.extraer_seccion(CONTEXTO, "inexistente"))

    def test_limpiar_quita_comentarios(self) -> None:
        self.assertEqual(estimar.limpiar("a\n<!-- x -->\n\n\n\nb"), "a\n\nb")


class TestPaquete(unittest.TestCase):
    def setUp(self) -> None:
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.repo = Path(self._t.name)
        self.docs = self.repo / "docs"
        (self.docs / "25-areas/pagos").mkdir(parents=True)
        (self.docs / "25-areas/pagos/CONTEXTO.md").write_text(CONTEXTO, encoding="utf-8")
        self.ficha = self.docs / "05-instrucciones/02-en-progreso/2026-10-15/demo.md"
        self.ficha.parent.mkdir(parents=True)
        self.ficha.write_text(INSTR, encoding="utf-8")
        (self.repo / "src").mkdir()
        (self.repo / "src/pagos.py").write_text("l1\nl2\nl3\nl4\n", encoding="utf-8")
        (self.repo / "src/grande.py").write_text("\n".join(f"x{i}" for i in range(500)), encoding="utf-8")

    def test_localizar_por_id_slug_y_ruta(self) -> None:
        for ref in ("20261015-001-demo", "demo", "001-demo", str(self.ficha)):
            self.assertEqual(paquete.localizar_instruccion(self.docs, ref), self.ficha.resolve() if ref == str(self.ficha) else self.ficha)
        self.assertIsNone(paquete.localizar_instruccion(self.docs, "nada"))

    def test_contenido_del_paquete(self) -> None:
        p = paquete.construir(self.docs, self.ficha, 100000, self.repo)
        texto = p.render()
        self.assertIn("Objetivo claro", texto)
        self.assertNotIn("decision-group", texto)          # se corta en «Decisión a tomar»
        self.assertNotIn("areas: []", texto)               # frontmatter vacío omitido
        self.assertIn("Se cobra al final", texto)
        self.assertNotIn("No debe aparecer", texto)        # solo la sección pedida
        self.assertIn("    2  l2", texto)
        self.assertNotIn("l4", texto)                      # rango 2-3
        self.assertTrue(any("falta.md" in a for a in p.avisos))
        self.assertTrue(any("sin rango" in a for a in p.avisos))
        self.assertIn("primeras 200 de 500", texto)

    def test_presupuesto_omite_lo_ultimo(self) -> None:
        p = paquete.construir(self.docs, self.ficha, 120, self.repo)
        self.assertTrue(p.omitidas)
        self.assertIn("OMITIDO", p.render())
        self.assertEqual(p.partes[0].titulo.split()[0], "INSTRUCCIÓN")

    def test_arranque_mide_agentes_y_estado(self) -> None:
        (self.repo / "AGENTES.md").write_text("x" * 400, encoding="utf-8")
        (self.docs / "ESTADO.md").write_text("y" * 80, encoding="utf-8")
        self.assertEqual(medir.arranque(self.repo), [("AGENTES.md", 100), ("docs/ESTADO.md", 20)])


class TestPackReal(unittest.TestCase):
    def test_arranque_del_pack_dentro_del_limite(self) -> None:
        pack = AQUI.parent.parent
        total = sum(t for _, t in medir.arranque(pack, "."))
        self.assertLessEqual(total, medir.ARRANQUE_MAX)


if __name__ == "__main__":
    unittest.main()
