#!/usr/bin/env python3
"""Tests mínimos — aplicación de decisiones y movimiento de estados (R-19)."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from applier import apply_decision_to_file


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


class TestDecisionesAplicacion(unittest.TestCase):
    def test_apply_scoped_checkbox(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "45-mejoras-propuestas" / "MEJ-test.md"
            p.parent.mkdir(parents=True)
            content = SAMPLE_MEJORA + "\n<!-- decision-group: otro -->\n- [ ] <!-- decision:aprobar --> otro\n"
            p.write_text(content, encoding="utf-8")
            result = apply_decision_to_file(
                p, "mejora", "aprobar", "test-session", group_id="MEJ-20260101-test"
            )
            self.assertIsNotNone(result)
            assert result is not None
            _, new_content, _ = result
            self.assertIn("status: approved", new_content)
            self.assertIn("instruction_derivada", new_content)

    def test_posponer_writes_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "45-mejoras-propuestas" / "MEJ-posponer.md"
            p.parent.mkdir(parents=True)
            p.write_text(SAMPLE_MEJORA, encoding="utf-8")
            result = apply_decision_to_file(
                p, "mejora", "posponer", "test-session", group_id="MEJ-20260101-test"
            )
            self.assertIsNotNone(result)
            assert result is not None
            _, new_content, _ = result
            self.assertIn("posponer", new_content.lower())
            self.assertIn("Notas del humano", new_content)
            self.assertIn("- [x]", new_content)

    def test_rechazar_moves_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "45-mejoras-propuestas" / "01-pendientes" / "2020-01-01" / "MEJ-reject.md"
            p.parent.mkdir(parents=True)
            p.write_text(SAMPLE_MEJORA.replace("MEJ-20260101-test", "MEJ-reject-test"), encoding="utf-8")
            result = apply_decision_to_file(
                p, "mejora", "rechazar", "test-session", group_id="MEJ-reject-test"
            )
            self.assertIsNotNone(result)
            self.assertFalse(p.exists())
            moved = root / "45-mejoras-propuestas" / "05-canceladas" / "2020-01-01" / "MEJ-reject.md"
            self.assertTrue(moved.exists())

    def test_evolucion_aprobar_sets_instruction_derivada(self) -> None:
        sample = """---
id: EVO-20260101-aprobar
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

# EVO aprobar test

## Decisión a tomar

<!-- decision-group: EVO-20260101-aprobar -->
- [ ] <!-- decision:aprobar --> **Aprobar**
- [ ] <!-- decision:rechazar --> **Rechazar**
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "46-evolucion-documentacion" / "01-pendientes" / "2020-01-01" / "EVO-aprobar.md"
            p.parent.mkdir(parents=True)
            p.write_text(sample, encoding="utf-8")
            result = apply_decision_to_file(
                p, "evolucion", "aprobar", "test-session", group_id="EVO-20260101-aprobar"
            )
            self.assertIsNotNone(result)
            moved = root / "46-evolucion-documentacion" / "02-en-progreso" / "2020-01-01" / "EVO-aprobar.md"
            self.assertTrue(moved.exists())
            new_content = moved.read_text(encoding="utf-8")
            self.assertIn("instruction_derivada: PENDIENTE-YYYYMMDD-NNN", new_content)
            self.assertIn("status: approved", new_content)
            self.assertIn("revision-pendientes-nota:", new_content)

    def test_evolucion_rechazar_moves_to_canceladas(self) -> None:
        sample = """---
id: EVO-20260101-reject
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

# EVO reject test

## Decisión a tomar

<!-- decision-group: EVO-20260101-reject -->
- [ ] <!-- decision:aprobar --> **Aprobar**
- [ ] <!-- decision:rechazar --> **Rechazar**
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "46-evolucion-documentacion" / "01-pendientes" / "2020-01-01" / "EVO-reject.md"
            p.parent.mkdir(parents=True)
            p.write_text(sample, encoding="utf-8")
            result = apply_decision_to_file(
                p, "evolucion", "rechazar", "test-session", group_id="EVO-20260101-reject"
            )
            self.assertIsNotNone(result)
            self.assertFalse(p.exists())
            moved = root / "46-evolucion-documentacion" / "05-canceladas" / "2020-01-01" / "EVO-reject.md"
            self.assertTrue(moved.exists())

    def test_instruccion_aprobar_moves_to_en_progreso(self) -> None:
        sample = """---
id: 20260101-001-test
status: awaiting_approval
source: human
created: 2020-01-01T00:00:00Z
approved_at: null
areas: [auth]
acto: crear
vinculos_entrada: []
lectura_minima: []
anclas_codigo: []
espejo_actualizar: []
espejo_leer: []
---

# Test instrucción

## Decisión a tomar

<!-- decision-group: 20260101-001-test -->
- [ ] <!-- decision:aprobar --> **Aprobar**
- [ ] <!-- decision:cancelar --> **Cancelar**
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "05-instrucciones" / "01-pendientes" / "2020-01-01" / "test.md"
            p.parent.mkdir(parents=True)
            p.write_text(sample, encoding="utf-8")
            result = apply_decision_to_file(
                p, "instruccion", "aprobar", "test-session", group_id="20260101-001-test"
            )
            self.assertIsNotNone(result)
            self.assertFalse(p.exists())
            moved = root / "05-instrucciones" / "02-en-progreso" / "2020-01-01" / "test.md"
            self.assertTrue(moved.exists())
            self.assertIn("status: approved", moved.read_text(encoding="utf-8"))

    def test_eliminar_moves_to_listas_para_eliminar(self) -> None:
        sample = """---
id: MEJ-20260101-eliminar
status: pending
source: ai
tipo: docs
severidad: baja
proposed_at: 2020-01-01
related_instruction: 20260101-001
areas: []
evidencia: []
---

# Eliminar test

## Decisión a tomar

<!-- decision-group: MEJ-20260101-eliminar -->
- [ ] <!-- decision:rechazar --> **Rechazar**
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "45-mejoras-propuestas" / "01-pendientes" / "2020-01-01" / "MEJ-eliminar.md"
            p.parent.mkdir(parents=True)
            p.write_text(sample, encoding="utf-8")
            result = apply_decision_to_file(
                p, "mejora", "eliminar", "test-session", group_id="MEJ-20260101-eliminar"
            )
            self.assertIsNotNone(result)
            self.assertFalse(p.exists())
            moved = root / "45-mejoras-propuestas" / "06-listas-para-eliminar" / "2020-01-01" / "MEJ-eliminar.md"
            self.assertTrue(moved.exists())
            self.assertIn("status: para-eliminar", moved.read_text(encoding="utf-8"))

    def test_promover_herramienta_crea_autorizada_y_mueve(self) -> None:
        sample = """---
id: mi-script
status: pending
source: ai
proposed_at: 2020-01-01
related_instruction: 20260101-001
motivo: test
---

# Propuesta mi script

## Decisión a tomar

<!-- decision-group: mi-script -->
- [ ] <!-- decision:promover --> **Promover**
- [ ] <!-- decision:rechazar --> **Rechazar**
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "35-herramientas" / "propuestas" / "01-pendientes" / "2020-01-01" / "mi-script.md"
            p.parent.mkdir(parents=True)
            p.write_text(sample, encoding="utf-8")
            result = apply_decision_to_file(
                p, "herramienta", "promover", "test-session", group_id="mi-script"
            )
            self.assertIsNotNone(result)
            draft = root / "35-herramientas" / "autorizadas" / "mi-script.md"
            self.assertTrue(draft.exists())
            moved = root / "35-herramientas" / "propuestas" / "03-completadas" / "2020-01-01" / "mi-script.md"
            self.assertTrue(moved.exists())


if __name__ == "__main__":
    unittest.main()
