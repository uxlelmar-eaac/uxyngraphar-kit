#!/usr/bin/env python3
"""Tests mínimos — escaneo, frontmatter y sesiones (R-19: división relacional)."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import parse_simple_yaml, update_frontmatter_raw, validate_group_id
from scanner import scan_file, scan_file_items
from session import close_session, list_session_history, load_active_session


SAMPLE_MEJORA = """---
id: MEJ-20260101-test
status: pending
source: ai
tipo: deuda-tecnica
severidad: baja
prioridad: despues
proposed_at: 2020-01-01
related_instruction: 20260101-001
areas: [auth]
evidencia: []
motivo: test
---

# MEJ test

Contexto de prueba.

## Decisión a tomar

<!-- decision-group: MEJ-20260101-test -->
- [ ] <!-- decision:aprobar --> **Aprobar** → instrucción
- [ ] <!-- decision:posponer --> **Posponer**
- [ ] <!-- decision:rechazar --> **Rechazar**

### Notas del humano

"""

SAMPLE_ALIAS = """---
id: MEJ-alias-test
status: pending
source: ai
tipo: docs
severidad: baja
prioridad: despues
proposed_at: 2020-01-01
related_instruction: 20260101-001
areas: []
evidencia: []
motivo: test alias
---

# Alias test

## Decisión humana

- [ ] <!-- decision:posponer --> **Posponer** revisión
- [ ] <!-- decision:rechazar --> **Rechazar**
"""


class TestDecisiones(unittest.TestCase):
    def test_skip_plantilla(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "45-mejoras-propuestas" / "_PLANTILLA-x.md"
            p.parent.mkdir(parents=True)
            p.write_text(
                "---\nid: x\nstatus: pending\n---\n\n## Decisión a tomar\n",
                encoding="utf-8",
            )
            self.assertIsNone(scan_file(root, "test", p))

    def test_detect_pending_mejora(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "45-mejoras-propuestas" / "MEJ-test.md"
            p.parent.mkdir(parents=True)
            p.write_text(SAMPLE_MEJORA, encoding="utf-8")
            item = scan_file(root, "test", p)
            self.assertIsNotNone(item)
            assert item is not None
            self.assertEqual(item.id, "MEJ-20260101-test")
            self.assertEqual(item.tipo, "mejora")
            self.assertFalse(item.group_id_mismatch)

    def test_alias_decision_humana(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "45-mejoras-propuestas" / "MEJ-alias.md"
            p.parent.mkdir(parents=True)
            p.write_text(SAMPLE_ALIAS, encoding="utf-8")
            item = scan_file(root, "test", p)
            self.assertIsNotNone(item)
            assert item is not None
            self.assertEqual(item.id, "MEJ-alias-test")
            self.assertEqual(len(item.options), 2)

    def test_group_id_suffix_ok(self) -> None:
        _, ok = validate_group_id("<!-- decision-group: AUD-001-promo-1 -->", "AUD-001")
        self.assertTrue(ok)

    def test_group_id_mismatch_flag(self) -> None:
        _, ok = validate_group_id("<!-- decision-group: otro-id -->", "MEJ-real")
        self.assertFalse(ok)

    def test_parse_inline_yaml_list(self) -> None:
        fm = parse_simple_yaml("areas: [auth, billing]\nstatus: pending\n")
        self.assertEqual(fm["areas"], ["auth", "billing"])

    def test_preserve_frontmatter_comments(self) -> None:
        raw = "id: MEJ-x\nstatus: pending  # comentario inline\nareas:\n  - auth\n"
        updated = update_frontmatter_raw(raw, {"status": "approved"})
        self.assertIn("# comentario inline", updated)
        self.assertIn("status: approved", updated)
        self.assertIn("  - auth", updated)

    def test_auditoria_multiple_blocks(self) -> None:
        sample = """---
id: AUD-20260101-test
status: active
investigator: ai
severity: medium
date: 2020-01-01
area: auth
modules: []
endpoints: []
questions: []
findings_count: 1
promociones: []
related_instrucciones: []
---

# Auditoría test

## Decisiones a tomar (promociones)

<!-- decision-group: AUD-20260101-test-promo-1 -->
- [ ] <!-- decision:aprobar --> **Promover** a canon
- [ ] <!-- decision:rechazar --> **Rechazar**

<!-- decision-group: AUD-20260101-test-promo-2 -->
- [ ] <!-- decision:aprobar --> **Promover** ADR
- [ ] <!-- decision:rechazar --> **Rechazar**
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "40-auditorias" / "02-en-progreso" / "2026-01-01" / "AUD-test.md"
            p.parent.mkdir(parents=True)
            p.write_text(sample, encoding="utf-8")
            items = scan_file_items(root, "test", p)
            self.assertEqual(len(items), 2)
            self.assertEqual(items[0].tipo, "auditoria")

    def test_detect_evolucion(self) -> None:
        sample = """---
id: EVO-20260101-test
status: pending
source: ai
tipo: cobertura
impacto: general
prioridad: despues
detected_in: test
areas: []
propuesta_cambio: []
proposed_at: 2020-01-01
instruction_derivada: null
---

# EVO test

## Decisión a tomar

<!-- decision-group: EVO-20260101-test -->
- [ ] <!-- decision:aprobar --> **Aprobar**
- [ ] <!-- decision:rechazar --> **Rechazar**
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "46-evolucion-documentacion" / "EVO-test.md"
            p.parent.mkdir(parents=True)
            p.write_text(sample, encoding="utf-8")
            item = scan_file(root, "test", p)
            self.assertIsNotNone(item)
            assert item is not None
            self.assertEqual(item.tipo, "evolucion")

    def test_session_history_after_close(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "PROTOCOLO.md").write_text("# proto\n", encoding="utf-8")
            import os

            old_dirs = os.environ.get("DOCS_DIRS")
            os.environ["DOCS_DIRS"] = str(root)
            try:
                from session import save_active_session

                session = load_active_session()
                session["decisions"] = [{"id": "x", "action": "posponer", "applied": True}]
                save_active_session(session)
                closed = close_session()
                self.assertIsNotNone(closed.get("closed_at"))
                history = list_session_history()
                self.assertGreaterEqual(len(history), 1)
            finally:
                if old_dirs:
                    os.environ["DOCS_DIRS"] = old_dirs
                else:
                    os.environ.pop("DOCS_DIRS", None)


if __name__ == "__main__":
    unittest.main()
