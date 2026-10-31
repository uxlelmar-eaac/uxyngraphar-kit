#!/usr/bin/env python3
"""Pruebas de los ajustes locales (R-25): crear desde una EVO aprobada, sobrevivir a una actualización y retirar."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SCRIPTS = AQUI.parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(SCRIPTS / "nucleo"))
sys.path.insert(0, str(SCRIPTS / "tokens"))

import ajustes_locales as almacen  # noqa: E402
import clasificacion as cl  # noqa: E402

EVO = "---\nid: {id}\nstatus: {st}\ntipo: proceso\nimpacto: ambos\npropuesta_cambio:\n  - 10-guias/guia.md\n---\n# {id}\n\nFalta un paso.\n"
INDICE = (SCRIPTS.parent / "97-ajustes-locales" / "INDICE.md")
HOY = date(2026, 10, 30)


class TestAjustes(unittest.TestCase):
    def setUp(self) -> None:
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.docs = Path(self._t.name) / "docs"
        (self.docs / "10-guias").mkdir(parents=True)
        (self.docs / "10-guias" / "guia.md").write_text("# Guía\n\nPaso 1.\n", encoding="utf-8")
        (self.docs / "97-ajustes-locales").mkdir()
        (self.docs / "97-ajustes-locales" / "INDICE.md").write_text(INDICE.read_text(encoding="utf-8"), encoding="utf-8")
        for st, carpeta, ident in (("approved", "02-en-progreso", "EVO-20261030-paso"), ("pending", "01-pendientes", "EVO-20261030-otra")):
            d = self.docs / "46-evolucion-documentacion" / carpeta / "2026-10-30"
            d.mkdir(parents=True)
            (d / f"{ident}.md").write_text(EVO.format(id=ident, st=st), encoding="utf-8")

    def _crear(self) -> Path:
        return almacen.crear(self.docs, "EVO-20261030-paso", ["docs/10-guias/guia.md"], "Añade el paso 2 tras el paso 1.", por="ana", hoy=HOY)

    def test_crear_marca_la_evo_y_la_lista(self) -> None:
        ruta = self._crear()
        self.assertEqual(ruta.name, "AJ-20261030-paso.md")
        aj = almacen.leer(ruta)
        self.assertEqual((aj.status, aj.evo, aj.aplica_a), ("activo", "EVO-20261030-paso", ["10-guias/guia.md"]))
        self.assertEqual(aj.huellas["10-guias/guia.md"], almacen.huella(self.docs / "10-guias" / "guia.md"))
        evo = next(self.docs.glob("46-*/02-*/*/EVO-20261030-paso.md")).read_text(encoding="utf-8")
        self.assertIn("ajuste_local: AJ-20261030-paso", evo)
        indice = (self.docs / "97-ajustes-locales" / "INDICE.md").read_text(encoding="utf-8")
        self.assertIn("[AJ-20261030-paso](AJ-20261030-paso.md)", indice)
        self.assertIn("<!-- uxyngraphar:inicio -->", indice)   # la zona del pack queda intacta
        self.assertEqual((self.docs / "10-guias" / "guia.md").read_text(encoding="utf-8"), "# Guía\n\nPaso 1.\n")   # el núcleo no cambia

    def test_solo_desde_evo_aprobada_y_destinos_del_pack(self) -> None:
        with self.assertRaises(almacen.ErrorAjuste):
            almacen.crear(self.docs, "EVO-20261030-otra", ["10-guias/guia.md"], "x", hoy=HOY)   # pending
        for malo in ("../fuera.md", "95-memoria/x.md", "10-guias/no-existe.md"):
            with self.assertRaises(almacen.ErrorAjuste):
                almacen.crear(self.docs, "EVO-20261030-paso", [malo], "x", hoy=HOY)
        with self.assertRaises(almacen.ErrorAjuste):
            almacen.crear(self.docs, "EVO-20261030-paso", ["10-guias/guia.md"], "   ", hoy=HOY)

    def test_actualizacion_del_nucleo_pide_revision_y_revisado_la_cierra(self) -> None:
        self._crear()
        self.assertEqual([a.problemas for a in almacen.revisar(self.docs)], [[]])
        (self.docs / "10-guias" / "guia.md").write_text("# Guía\n\nPaso 1 (v2).\n", encoding="utf-8")   # llega una versión nueva
        problemas = almacen.revisar(self.docs)[0].problemas
        self.assertTrue(any("cambió" in p for p in problemas), problemas)
        almacen.confirmar_revision(self.docs, "AJ-20261030-paso")
        self.assertEqual(almacen.revisar(self.docs)[0].problemas, [])

    def test_evo_citada_en_changelog_sugiere_retirar_y_retirar_la_quita(self) -> None:
        self._crear()
        (self.docs / "CHANGELOG.md").write_text("## [9.9.9]\n- Paso 2 (EVO-20261030-paso).\n", encoding="utf-8")
        self.assertTrue(any("llegó al pack" in p for p in almacen.revisar(self.docs)[0].problemas))
        almacen.retirar(self.docs, "AJ-20261030-paso", "ya está en el pack", hoy=HOY)
        self.assertEqual(almacen.activos_para(self.docs, "10-guias/guia.md"), [])
        self.assertEqual(almacen.revisar(self.docs)[0].problemas, [])
        self.assertIn("_Ningún ajuste activo._", (self.docs / "97-ajustes-locales" / "INDICE.md").read_text(encoding="utf-8"))

    def test_contexto_incluye_el_ajuste_tras_el_archivo(self) -> None:
        import paquete
        self._crear()
        inst = self.docs / "05-instrucciones" / "02-en-progreso" / "2026-10-30" / "INS-1.md"
        inst.parent.mkdir(parents=True)
        inst.write_text("---\nid: INS-1\nstatus: approved\nlectura_minima:\n  - 10-guias/guia.md\n---\n# INS-1\n", encoding="utf-8")
        titulos = [p.titulo for p in paquete.construir(self.docs, inst).partes]
        self.assertEqual(titulos[1:3], ["10-guias/guia.md", "97-ajustes-locales/AJ-20261030-paso.md"])

    def test_clasificacion_ajustes_son_del_proyecto(self) -> None:
        self.assertEqual(cl.clasificar("97-ajustes-locales/AJ-20261030-paso.md"), "C")
        self.assertEqual(cl.clasificar("97-ajustes-locales/INDICE.md"), "M")
        self.assertEqual(cl.clasificar("97-ajustes-locales/_PROTOCOLO.md"), "N")

    def test_cli(self) -> None:
        regla = Path(self._t.name) / "regla.md"
        regla.write_text("Haz el paso 2.\n", encoding="utf-8")
        cli = [sys.executable, str(SCRIPTS / "ajustes.py"), "--repo", self._t.name, "--docs", "docs"]
        r = subprocess.run([*cli, "crear", "--evo", "EVO-20261030-paso", "--a", "10-guias/guia.md", "--texto", str(regla)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(subprocess.run([*cli, "verificar"], capture_output=True).returncode, 0)
        (self.docs / "10-guias" / "guia.md").write_text("cambiada\n", encoding="utf-8")
        r = subprocess.run([*cli, "verificar"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("REVISAR", r.stdout)


if __name__ == "__main__":
    unittest.main()
