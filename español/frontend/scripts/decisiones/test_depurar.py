#!/usr/bin/env python3
"""Pruebas de la depuración (diagnóstico, plan, mover con reescritura de enlaces, guardar en la memoria: nada se borra)."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import depurar  # noqa: E402
import depurar_aplicar as da  # noqa: E402

HOY = date(2026, 10, 15)
FICHA = "---\nid: {id}\nstatus: {status}\ntipo: refactor\nseveridad: baja\nproposed_at: {fecha}\n---\n# {id}\n{extra}"


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.repo = Path(self._t.name)
        self.docs = self.repo / "docs"
        self.docs.mkdir()

    def ficha(self, seccion: str, estado: str, fecha: str, ident: str, status: str, extra: str = "") -> Path:
        p = self.docs / seccion / estado / fecha / f"{ident}.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(FICHA.format(id=ident, status=status, fecha=fecha, extra=extra), encoding="utf-8")
        return p


class TestDiagnostico(Base):
    def test_candidatas_vencidas_y_enlaces(self) -> None:
        self.ficha("45-mejoras-propuestas", "03-completadas", "2026-01-01", "MEJ-20260101-a", "done")
        self.ficha("45-mejoras-propuestas", "06-listas-para-eliminar", "2026-02-01", "MEJ-20260201-b", "para-eliminar")
        otra = self.ficha("45-mejoras-propuestas", "01-pendientes", "2026-10-01", "MEJ-20261001-c", "pending",
                          "[a](../../03-completadas/2026-01-01/MEJ-20260101-a.md)\n")
        d = depurar.diagnosticar(self.docs, HOY)
        self.assertEqual([m["id"] for m in d["mover"]], ["MEJ-20260101-a"])
        self.assertEqual([v["id"] for v in d["vencidas"]], ["MEJ-20260201-b"])
        self.assertEqual(list(d["enlaces_entrantes"].values()), [[otra.relative_to(self.docs).as_posix()]])
        self.assertIn("MEJ-20260101-a", depurar.informe_md(d))
        self.assertTrue(all(i["aprobado"] is False for i in depurar.plan_desde(d)))

    def test_evo_sin_exportar_no_se_propone_eliminar(self) -> None:
        self.ficha("46-evolucion-documentacion", "06-listas-para-eliminar", "2026-02-01", "EVO-20260201-a", "para-eliminar")
        self.ficha("46-evolucion-documentacion", "06-listas-para-eliminar", "2026-02-01", "EVO-20260201-b", "para-eliminar", "")
        exportada = self.docs / "46-evolucion-documentacion/06-listas-para-eliminar/2026-02-01/EVO-20260201-b.md"
        exportada.write_text(exportada.read_text(encoding="utf-8").replace("---\n# ", "exportada_al_pack: 2026-03-01\n---\n# ", 1), encoding="utf-8")
        d = depurar.diagnosticar(self.docs, HOY)
        self.assertEqual([v["id"] for v in d["vencidas"]], ["EVO-20260201-b"])
        self.assertEqual(len(d["evo_sin_exportar"]), 1)
        self.assertIn("EVO retenidas", depurar.informe_md(d))

    def test_anclas_y_espejo_huerfanos(self) -> None:
        (self.repo / "src" / "a").mkdir(parents=True)
        (self.repo / "src" / "a" / "vivo.ts").write_text("x", encoding="utf-8")
        esp = self.docs / "50-sistema-integral" / "src" / "a"
        esp.mkdir(parents=True)
        for n in ("vivo.md", "muerto.md", "README.md"):
            (esp / n).write_text("# e\n", encoding="utf-8")
        i = self.docs / "05-instrucciones" / "03-completadas" / "2026-10-01"
        i.mkdir(parents=True)
        (i / "uno.md").write_text("---\nid: uno\nstatus: done\nanclas_codigo:\n  - src/a/vivo.ts:1-5\n  - src/a/borrado.ts\n  - ruta/archivo.ts\n---\n", encoding="utf-8")
        self.assertEqual(depurar.espejo_huerfano(self.docs), ["50-sistema-integral/src/a/muerto.md"])
        self.assertEqual([a["ancla"] for a in depurar.anclas_huerfanas(self.docs)], ["src/a/borrado.ts"])


class TestAplicar(Base):
    def test_sin_aprobar_no_hace_nada(self) -> None:
        p = self.ficha("45-mejoras-propuestas", "03-completadas", "2026-01-01", "MEJ-20260101-a", "done")
        plan = depurar.plan_desde(depurar.diagnosticar(self.docs, HOY))
        self.assertIn("nada que hacer", da.aplicar_plan(self.docs, plan, dry_run=False)[0])
        self.assertTrue(p.exists())

    def test_archivar_reescribe_enlaces(self) -> None:
        p = self.ficha("45-mejoras-propuestas", "03-completadas", "2026-01-01", "MEJ-20260101-a", "done")
        otra = self.ficha("45-mejoras-propuestas", "01-pendientes", "2026-10-01", "MEJ-20261001-c", "pending",
                          "[a](../../03-completadas/2026-01-01/MEJ-20260101-a.md)\n")
        plan = depurar.plan_desde(depurar.diagnosticar(self.docs, HOY))
        plan[0]["aprobado"] = True
        da.aplicar_plan(self.docs, plan, dry_run=False)
        nuevo = self.docs / "45-mejoras-propuestas/04-archivadas/2026-01-01/MEJ-20260101-a.md"
        self.assertTrue(nuevo.is_file() and not p.exists())
        enlace = otra.read_text(encoding="utf-8").split("](")[1].split(")")[0]
        self.assertTrue((otra.parent / enlace).resolve() == nuevo.resolve())

    def _plan_memoria(self) -> list[dict]:
        self.ficha("45-mejoras-propuestas", "06-listas-para-eliminar", "2026-02-01", "MEJ-20260201-b", "para-eliminar")
        plan = depurar.plan_desde(depurar.diagnosticar(self.docs, HOY))
        plan[0]["aprobado"] = True
        return plan

    def _humano(self) -> None:
        os.environ["UXYNGRAPHAR_HUMANO"] = "1"
        self.addCleanup(os.environ.pop, "UXYNGRAPHAR_HUMANO", None)

    LISTA = "45-mejoras-propuestas/06-listas-para-eliminar/2026-02-01/MEJ-20260201-b.md"

    def test_plan_propone_memoria_con_motivo(self) -> None:
        plan = self._plan_memoria()
        self.assertEqual((plan[0]["accion"], plan[0]["path"]), ("memoria", self.LISTA))
        self.assertIn("06-listas-para-eliminar durante", plan[0]["motivo"])

    def test_archivadas_antiguas_tambien_van_a_memoria(self) -> None:
        self.ficha("45-mejoras-propuestas", "04-archivadas", "2025-01-01", "MEJ-20250101-v", "archivada")
        self.ficha("45-mejoras-propuestas", "04-archivadas", "2026-09-01", "MEJ-20260901-n", "archivada")
        d = depurar.diagnosticar(self.docs, HOY, dias_memoria=180)
        self.assertEqual([v["id"] for v in d["vencidas"]], ["MEJ-20250101-v"])
        self.assertEqual(depurar.diagnosticar(self.docs, HOY, dias_memoria=9999)["vencidas"], [])

    def test_guarda_en_memoria_y_no_borra(self) -> None:
        self._humano()
        plan = self._plan_memoria()
        f = self.docs / self.LISTA
        self.assertIn("[dry-run]", da.aplicar_plan(self.docs, plan, dry_run=True)[0])
        self.assertTrue(f.exists())
        salida = da.aplicar_plan(self.docs, plan, dry_run=False)[0]
        self.assertIn("A MEMORIA", salida)
        self.assertFalse(f.exists())
        guardadas = list((self.docs / "95-memoria/mejoras").rglob("MEJ-20260201-b.md"))
        self.assertEqual(len(guardadas), 1)
        self.assertIn("memoria_desde: " + self.LISTA, guardadas[0].read_text(encoding="utf-8"))
        self.assertFalse((self.docs / "90-archivo/registro-eliminaciones.md").exists())

    def test_accion_eliminar_tambien_va_a_memoria(self) -> None:
        self._humano()
        plan = self._plan_memoria()
        plan[0].update(accion="eliminar", confirmar="MEJ-20260201-b", motivo="descartada")
        self.assertIn("A MEMORIA", da.aplicar_plan(self.docs, plan, dry_run=False)[0])

    def test_sin_motivo_se_rechaza(self) -> None:
        self._humano()
        plan = self._plan_memoria()
        plan[0]["motivo"] = " "
        self.assertIn("falta `motivo`", da.aplicar_plan(self.docs, plan, dry_run=False)[0])
        self.assertTrue((self.docs / self.LISTA).exists())

    def test_bloqueado_si_hay_enlace_vivo(self) -> None:
        self._humano()
        plan = self._plan_memoria()
        self.ficha("45-mejoras-propuestas", "01-pendientes", "2026-10-01", "MEJ-20261001-c", "pending",
                   "[b](../../06-listas-para-eliminar/2026-02-01/MEJ-20260201-b.md)\n")
        self.assertIn("la enlazan", da.aplicar_plan(self.docs, plan, dry_run=False)[0])
        self.assertTrue((self.docs / self.LISTA).exists())

    def test_sin_humano_se_rechaza(self) -> None:
        os.environ.pop("UXYNGRAPHAR_HUMANO", None)
        os.environ.pop("uxyngraphar_HUMANO", None)
        if sys.stdin.isatty():
            self.skipTest("stdin interactivo")
        plan = self._plan_memoria()
        self.assertIn("exige una persona", da.aplicar_plan(self.docs, plan, dry_run=False)[0])
        self.assertTrue((self.docs / self.LISTA).exists())

    def test_fichas_vivas_no_se_guardan(self) -> None:
        self._humano()
        self.ficha("45-mejoras-propuestas", "01-pendientes", "2026-01-01", "MEJ-20260101-a", "pending")
        plan = [{"accion": "memoria", "id": "MEJ-20260101-a", "path": "45-mejoras-propuestas/01-pendientes/2026-01-01/MEJ-20260101-a.md",
                 "aprobado": True, "motivo": "x"}]
        self.assertIn("está viva", da.aplicar_plan(self.docs, plan, dry_run=False)[0])

    def test_mover_no_reescribe_la_memoria(self) -> None:
        self._humano()
        da.aplicar_plan(self.docs, self._plan_memoria(), dry_run=False)
        guardada = next((self.docs / "95-memoria").rglob("MEJ-20260201-b.md"))
        guardada.write_text(guardada.read_text(encoding="utf-8") + "[a](../../../../45-mejoras-propuestas/03-completadas/2026-01-01/MEJ-20260101-a.md)\n", encoding="utf-8")
        antes = guardada.read_bytes()
        self.ficha("45-mejoras-propuestas", "03-completadas", "2026-01-01", "MEJ-20260101-a", "done")
        plan = depurar.plan_desde(depurar.diagnosticar(self.docs, HOY))
        plan[0]["aprobado"] = True
        da.aplicar_plan(self.docs, plan, dry_run=False)
        self.assertEqual(guardada.read_bytes(), antes)


if __name__ == "__main__":
    unittest.main()
