#!/usr/bin/env python3
"""Pruebas de metricas, archivado y andamiaje (plantillas)."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PACK = AQUI.parent.parent
sys.path.insert(0, str(AQUI))

import archivado  # noqa: E402
import metricas  # noqa: E402
import plantillas  # noqa: E402

FICHA = "---\nid: {id}\nstatus: {status}\ntipo: refactor\nseveridad: baja\nproposed_at: {fecha}\n---\n# {id}\n"


def ficha(docs: Path, seccion: str, estado: str, fecha: str, ident: str, status: str = "completed") -> Path:
    p = docs / seccion / estado / fecha / f"{ident}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(FICHA.format(id=ident, status=status, fecha=fecha), encoding="utf-8")
    return p


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.docs = Path(self._t.name) / "docs"
        self.docs.mkdir()


class TestMetricasArchivado(Base):
    def test_fichas_ignora_readme_y_plantillas(self) -> None:
        ficha(self.docs, "45-mejoras-propuestas", "01-pendientes", "2026-01-01", "MEJ-20260101-a", "pending")
        (self.docs / "45-mejoras-propuestas" / "README.md").write_text("# r\n", encoding="utf-8")
        (self.docs / "45-mejoras-propuestas" / "_PLANTILLA.md").write_text("---\nid: x\n---\n", encoding="utf-8")
        fs = metricas.fichas(self.docs)
        self.assertEqual([f["id"] for f in fs], ["MEJ-20260101-a"])
        self.assertEqual(fs[0]["estado"], "01-pendientes")

    def test_calcular_y_formatear(self) -> None:
        ficha(self.docs, "45-mejoras-propuestas", "01-pendientes", "2026-01-01", "MEJ-20260101-a", "pending")
        m = metricas.calcular([(self.docs, "x")], hoy=date(2026, 10, 15), max_dias=30)
        self.assertIsInstance(m, dict)
        self.assertIn("MEJ-20260101-a", metricas.formatear(m) + str(m))

    def test_archivar_dry_run_no_mueve(self) -> None:
        p = ficha(self.docs, "45-mejoras-propuestas", "03-completadas", "2026-01-01", "MEJ-20260101-a")
        c = archivado.candidatos("archivar", [(self.docs, "x")], 90, date(2026, 10, 15))
        self.assertEqual(len(c), 1)
        self.assertIn("[dry-run]", archivado.aplicar(c)[0])
        self.assertTrue(p.exists())

    def test_archivar_mueve_y_cambia_status_sin_borrar(self) -> None:
        p = ficha(self.docs, "45-mejoras-propuestas", "03-completadas", "2026-01-01", "MEJ-20260101-a")
        c = archivado.candidatos("archivar", [(self.docs, "x")], 90, date(2026, 10, 15))
        archivado.aplicar(c, dry_run=False)
        destino = self.docs / "45-mejoras-propuestas" / "04-archivadas" / "2026-01-01" / "MEJ-20260101-a.md"
        self.assertFalse(p.exists())
        self.assertTrue(destino.is_file())
        self.assertIn("status: archivada\n", destino.read_text(encoding="utf-8"))

    def test_recientes_no_se_archivan(self) -> None:
        ficha(self.docs, "45-mejoras-propuestas", "03-completadas", "2026-10-01", "MEJ-20261001-a")
        self.assertEqual(archivado.candidatos("archivar", [(self.docs, "x")], 90, date(2026, 10, 15)), [])

    def test_adr_aceptada_no_se_archiva(self) -> None:
        ficha(self.docs, "20-decisiones", "03-completadas", "2026-01-01", "ADR-001-x")
        self.assertEqual(archivado.candidatos("archivar", [(self.docs, "x")], 90, date(2026, 10, 15)), [])

    def test_limpiar_va_a_listas_para_eliminar(self) -> None:
        ficha(self.docs, "45-mejoras-propuestas", "05-canceladas", "2026-01-01", "MEJ-20260101-a", "cancelled")
        c = archivado.candidatos("limpiar", [(self.docs, "x")], 180, date(2026, 10, 15))
        archivado.aplicar(c, dry_run=False)
        self.assertTrue((self.docs / "45-mejoras-propuestas" / "06-listas-para-eliminar" / "2026-01-01" / "MEJ-20260101-a.md").is_file())

    def test_destino_existente_se_omite(self) -> None:
        ficha(self.docs, "45-mejoras-propuestas", "03-completadas", "2026-01-01", "MEJ-20260101-a")
        ficha(self.docs, "45-mejoras-propuestas", "04-archivadas", "2026-01-01", "MEJ-20260101-a", "archivada")
        c = archivado.candidatos("archivar", [(self.docs, "x")], 90, date(2026, 10, 15))
        self.assertTrue(archivado.aplicar(c, dry_run=False)[0].startswith("OMITIDO"))


class TestAndamiaje(Base):
    def setUp(self) -> None:
        super().setUp()
        self.docs = Path(self._t.name) / "pack"
        shutil.copytree(PACK, self.docs, ignore=shutil.ignore_patterns("__pycache__", ".git"))
        self.hoy = date(2026, 10, 15)

    def test_slug_invalido(self) -> None:
        with self.assertRaises(plantillas.ErrorAndamiaje):
            plantillas.crear(self.docs, "mejora", "Mal Slug", self.hoy)

    def test_tipo_desconocido(self) -> None:
        with self.assertRaises(plantillas.ErrorAndamiaje):
            plantillas.crear(self.docs, "otro", "x", self.hoy)

    def test_enum_invalido(self) -> None:
        with self.assertRaises(plantillas.ErrorAndamiaje):
            plantillas.crear(self.docs, "mejora", "x", self.hoy, campos={"tipo": "inventado"})

    def test_instruccion_incrementa_y_no_sobrescribe(self) -> None:
        a = plantillas.crear(self.docs, "instruccion", "uno", self.hoy)
        b = plantillas.crear(self.docs, "instruccion", "dos", self.hoy)
        self.assertIn("20261015-001-uno", a.read_text(encoding="utf-8"))
        self.assertIn("20261015-002-dos", b.read_text(encoding="utf-8"))
        with self.assertRaises(plantillas.ErrorAndamiaje):
            plantillas.crear(self.docs, "instruccion", "uno", self.hoy)

    def test_instruccion_compacta_es_valida_y_ligera(self) -> None:
        import subprocess
        d = plantillas.crear(self.docs, "instruccion", "ligera", self.hoy, plantilla="compacta")
        texto = d.read_text(encoding="utf-8")
        self.assertIn("20261015-001-ligera", texto)
        self.assertLess(len(texto.splitlines()), 50)
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(self.docs / "scripts/validar-documentacion.py"), str(self.docs)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("ERROR", r.stdout + r.stderr)

    def test_cli_new_desde_decisiones_py(self) -> None:
        import subprocess
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(self.docs / "scripts/decisiones/decisiones.py"), "new", "mejora", "--slug", "por-cli", "--docs", str(self.docs)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Creada:", r.stdout)
        self.assertTrue(list((self.docs / "45-mejoras-propuestas/01-pendientes").rglob("MEJ-*-por-cli.md")))

    def test_adr_numera(self) -> None:
        a = plantillas.crear(self.docs, "adr", "demo", self.hoy)
        self.assertRegex(a.name, r"^ADR-\d{3}-demo\.md$")

    def test_dry_run_no_escribe(self) -> None:
        d = plantillas.crear(self.docs, "mejora", "seco", self.hoy, dry_run=True)
        self.assertFalse(d.exists())

    def test_enlaces_relativos_reubicados_existen(self) -> None:
        import re
        d = plantillas.crear(self.docs, "mejora", "enlaces", self.hoy)
        for m in re.finditer(r"\]\(([^)\s#:]+)\)", d.read_text(encoding="utf-8")):
            self.assertTrue((d.parent / m.group(1)).exists(), m.group(1))


if __name__ == "__main__":
    unittest.main()
