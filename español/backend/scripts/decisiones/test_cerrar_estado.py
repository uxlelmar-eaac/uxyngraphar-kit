#!/usr/bin/env python3
"""Pruebas de cerrar y estado."""

from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import cerrar  # noqa: E402
import estado  # noqa: E402

INSTR = "---\nid: {id}\nstatus: {status}\nsource: human\ncreated: 2026-10-01T00:00:00Z\nexecuted_at: null\nacto: crear\nespejo_actualizar: [{esp}]\nvinculos_salida: [{sal}]\n---\n# Título {id}\n{extra}"


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.docs = Path(self._t.name) / "docs"

    def ficha(self, estado_dir: str, ident: str, status: str, esp: str = "", sal: str = "", extra: str = "") -> Path:
        p = self.docs / "05-instrucciones" / estado_dir / "2026-10-01" / f"{ident.split('-', 2)[-1]}.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(INSTR.format(id=ident, status=status, esp=esp, sal=sal, extra=extra), encoding="utf-8")
        return p


class TestCerrar(Base):
    def test_cierra_mueve_y_marca(self) -> None:
        p = self.ficha("02-en-progreso", "20261001-001-uno", "approved", esp="50-sistema-integral/a.md", sal="x")
        lineas = cerrar.cerrar(self.docs, "uno")
        destino = self.docs / "05-instrucciones/03-completadas/2026-10-01/uno.md"
        self.assertTrue(destino.is_file() and not p.exists())
        texto = destino.read_text(encoding="utf-8")
        self.assertIn("status: done\n", texto)
        self.assertNotIn("executed_at: null", texto)
        self.assertTrue(any("espejo_actualizar sin escribir" in l for l in lineas))

    def test_reescribe_enlaces_entrantes(self) -> None:
        self.ficha("02-en-progreso", "20261001-001-uno", "approved", sal="x")
        otra = self.docs / "25-areas/a/CONTEXTO.md"
        otra.parent.mkdir(parents=True)
        otra.write_text("[i](../../05-instrucciones/02-en-progreso/2026-10-01/uno.md)\n", encoding="utf-8")
        cerrar.cerrar(self.docs, "20261001-001-uno")
        self.assertIn("03-completadas/2026-10-01/uno.md", otra.read_text(encoding="utf-8"))

    def test_solo_cierra_las_en_progreso(self) -> None:
        self.ficha("01-pendientes", "20261001-002-dos", "awaiting_approval")
        with self.assertRaises(cerrar.ErrorCierre):
            cerrar.cerrar(self.docs, "dos")
        with self.assertRaises(cerrar.ErrorCierre):
            cerrar.cerrar(self.docs, "no-existe")

    def test_dry_run(self) -> None:
        p = self.ficha("02-en-progreso", "20261001-001-uno", "approved", sal="x")
        self.assertIn("[dry-run]", cerrar.cerrar(self.docs, "uno", dry_run=True)[-1])
        self.assertTrue(p.exists())


class TestEstado(Base):
    def test_genera_y_escribe_sin_pisar_el_resto(self) -> None:
        self.ficha("02-en-progreso", "20261001-001-uno", "approved")
        self.ficha("01-pendientes", "20261001-002-dos", "awaiting_approval")
        self.ficha("03-completadas", "20261001-003-tres", "done")
        b = estado.generar(self.docs, date(2026, 10, 15))
        self.assertIn("En curso (1)", b)
        self.assertIn("Esperan aprobación (1)", b)
        self.assertIn("Cerradas recientes (1)", b)
        (self.docs / "ESTADO.md").write_text("# Mi estado\n\nnotas mías\n", encoding="utf-8")
        estado.escribir(self.docs, b)
        estado.escribir(self.docs, b)
        t = (self.docs / "ESTADO.md").read_text(encoding="utf-8")
        self.assertIn("notas mías", t)
        self.assertEqual(t.count(estado.INI), 1)


if __name__ == "__main__":
    unittest.main()
