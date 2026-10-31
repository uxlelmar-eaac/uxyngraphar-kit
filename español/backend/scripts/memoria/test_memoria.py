#!/usr/bin/env python3
"""Memoria del sistema (R-24): guardar, buscar, recuperar, purgar e integridad; solo personas; fuera del alcance del agente."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SCRIPTS = AQUI.parent
for sub in ("memoria", "nucleo", "control", "tokens", "decisiones"):
    sys.path.insert(0, str(SCRIPTS / sub))

import almacen  # noqa: E402
import paquete  # noqa: E402
import proteccion  # noqa: E402
import puerta  # noqa: E402
from metricas import fichas  # noqa: E402

HOY = date(2026, 10, 29)
LISTA = "45-mejoras-propuestas/06-listas-para-eliminar/2026-02-01/MEJ-20260201-b.md"
ADR = "20-decisiones/04-archivadas/2025-03-01/ADR-0007-cache.md"


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.repo = Path(self._t.name)
        self.docs = self.repo / "docs"
        self.ficha(LISTA, "---\nid: MEJ-20260201-b\nstatus: para-eliminar\n---\n# Cache de tarifas\n\nTexto original.\n")
        self.ficha(ADR, "---\nid: ADR-0007\nstatus: reemplazada\n---\n# Usar caché local\n")

    def ficha(self, rel: str, texto: str) -> Path:
        f = self.docs / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(texto, encoding="utf-8")
        return f


class TestAlmacen(Base):
    def test_guardar_mueve_y_anota(self) -> None:
        m = almacen.guardar(self.docs, LISTA, "descartada por el equipo", HOY)
        self.assertFalse((self.docs / LISTA).exists())
        self.assertEqual(m.ruta, "95-memoria/mejoras/2026/2026-10/MEJ-20260201-b.md")
        texto = (self.docs / m.ruta).read_text(encoding="utf-8")
        self.assertIn("Texto original.", texto)
        self.assertIn(f"memoria_desde: {LISTA}", texto)
        self.assertIn("memoria_estado_previo: 06-listas-para-eliminar", texto)
        self.assertEqual((m.id, m.titulo, m.creada), ("MEJ-20260201-b", "Cache de tarifas", "2026-02-01"))
        self.assertEqual(almacen.verificar(self.docs), [])

    def test_buscar_solo_en_catalogo(self) -> None:
        almacen.guardar(self.docs, LISTA, "descartada", HOY)
        almacen.guardar(self.docs, ADR, "reemplazada por ADR-0009", HOY)
        self.assertEqual([m.id for m in almacen.buscar(self.docs, "tarifas")], ["MEJ-20260201-b"])
        self.assertEqual([m.id for m in almacen.buscar(self.docs, "ADR-0009")], ["ADR-0007"])
        self.assertEqual([m.id for m in almacen.buscar(self.docs, seccion="decisiones")], ["ADR-0007"])
        self.assertEqual(almacen.buscar(self.docs, "Texto original"), [])   # el contenido no se abre al buscar
        self.assertEqual(len(almacen.buscar(self.docs)), 2)

    def test_recuperar_vuelve_a_archivadas(self) -> None:
        almacen.guardar(self.docs, ADR, "x", HOY)
        destino = almacen.recuperar(self.docs, "ADR-0007")
        self.assertEqual(destino, ADR)
        texto = (self.docs / destino).read_text(encoding="utf-8")
        self.assertNotIn("memoria_", texto)
        self.assertIn("status: obsoleta", texto)
        self.assertEqual(almacen.vigentes(self.docs), {})
        self.assertEqual(almacen.verificar(self.docs), [])
        almacen.guardar(self.docs, LISTA, "x", HOY)
        rec = almacen.recuperar(self.docs, "MEJ-20260201-b")
        self.assertEqual(rec, "45-mejoras-propuestas/04-archivadas/2026-02-01/MEJ-20260201-b.md")
        self.assertIn("status: archivada", (self.docs / rec).read_text(encoding="utf-8"))

    def test_purgar_borra_y_no_guarda_contenido(self) -> None:
        m = almacen.guardar(self.docs, LISTA, "x", HOY)
        almacen.purgar(self.docs, m.id, "contenía un token")
        self.assertFalse((self.docs / m.ruta).exists())
        self.assertEqual(almacen.vigentes(self.docs), {})
        catalogo = (self.docs / "95-memoria/catalogo.jsonl").read_text(encoding="utf-8")
        self.assertIn("purgada", catalogo)
        self.assertNotIn("Texto original", catalogo)
        self.assertEqual(almacen.verificar(self.docs), [])
        with self.assertRaises(almacen.ErrorMemoria):
            almacen.purgar(self.docs, m.id, "otra vez")

    def test_rechazos(self) -> None:
        vivo = "45-mejoras-propuestas/01-pendientes/2026-10-01/MEJ-20261001-c.md"
        self.ficha(vivo, "---\nid: MEJ-20261001-c\nstatus: pending\n---\n[b](../../06-listas-para-eliminar/2026-02-01/MEJ-20260201-b.md)\n")
        casos = {LISTA: "la enlazan", vivo: "está viva", "10-guias/memoria.md": "solo se guardan fichas",
                 "45-mejoras-propuestas/03-completadas/2026-01-01/no-existe.md": "no existe"}
        for rel, texto in casos.items():
            with self.assertRaises(almacen.ErrorMemoria) as ctx:
                almacen.guardar(self.docs, rel, "x", HOY)
            self.assertIn(texto, str(ctx.exception), rel)
        with self.assertRaises(almacen.ErrorMemoria):
            almacen.guardar(self.docs, ADR, "  ", HOY)
        self.assertTrue((self.docs / LISTA).exists())

    def test_id_repetido(self) -> None:
        almacen.guardar(self.docs, LISTA, "x", HOY)
        self.ficha(LISTA, "---\nid: MEJ-20260201-b\nstatus: para-eliminar\n---\n# otra\n")
        with self.assertRaises(almacen.ErrorMemoria):
            almacen.guardar(self.docs, LISTA, "x", HOY)

    def test_verificar_detecta_cambios_a_mano(self) -> None:
        m = almacen.guardar(self.docs, LISTA, "x", HOY)
        f = self.docs / m.ruta
        f.write_text(f.read_text(encoding="utf-8") + "editado\n", encoding="utf-8")
        self.assertIn("cambió", almacen.verificar(self.docs)[0])
        f.unlink()
        self.assertIn("se borró", almacen.verificar(self.docs)[0])
        self.ficha("95-memoria/mejoras/2026/2026-10/colada.md", "x")
        self.assertTrue(any("no está en el catálogo" in p for p in almacen.verificar(self.docs)))

    def test_accesos_quedan_registrados(self) -> None:
        almacen.registrar_acceso(self.docs, "ver", "MEJ-1")
        linea = json.loads((self.docs / "95-memoria/registro-accesos.jsonl").read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual((linea["accion"], linea["id"]), ("ver", "MEJ-1"))
        self.assertIn("usuario", linea)


class TestCli(Base):
    def cli(self, *args: str, humano: bool = False) -> subprocess.CompletedProcess:
        env = {k: v for k, v in os.environ.items() if k.upper() != "UXYNGRAPHAR_HUMANO"}
        if humano:
            env["UXYNGRAPHAR_HUMANO"] = "1"
        return subprocess.run([sys.executable, str(SCRIPTS / "memoria.py"), "--repo", str(self.repo), *args], capture_output=True, text=True,
                              encoding="utf-8", stdin=subprocess.DEVNULL, env=env)

    def test_un_agente_no_la_consulta(self) -> None:
        for args in (["buscar", "x"], ["ver", "X"], ["guardar", LISTA, "--motivo", "x"], ["recuperar", "X"], ["purgar", "X", "--confirmar", "X", "--motivo", "x"]):
            r = self.cli(*args)
            self.assertEqual(r.returncode, 2, args)
            self.assertIn("RECHAZADO", r.stderr)
        self.assertTrue((self.docs / LISTA).exists())
        self.assertFalse((self.docs / "95-memoria/registro-accesos.jsonl").exists())

    def test_flujo_de_una_persona(self) -> None:
        self.assertEqual(self.cli("guardar", f"docs/{LISTA}", "--motivo", "descartada", humano=True).returncode, 0)
        r = self.cli("buscar", "tarifas", humano=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("MEJ-20260201-b", r.stdout)
        self.assertIn("Texto original.", self.cli("ver", "MEJ-20260201-b", humano=True).stdout)
        self.assertEqual(self.cli("buscar", "nada-de-esto", humano=True).returncode, 1)
        accesos = (self.docs / "95-memoria/registro-accesos.jsonl").read_text(encoding="utf-8")
        self.assertEqual(accesos.count('"accion"'), 3)
        self.assertEqual(self.cli("verificar").returncode, 0)                  # verificar no exige persona (lo usan puerta y CI)
        r = self.cli("purgar", "MEJ-20260201-b", "--confirmar", "otro", "--motivo", "x", humano=True)
        self.assertEqual(r.returncode, 2)
        self.assertEqual(self.cli("purgar", "MEJ-20260201-b", "--confirmar", "MEJ-20260201-b", "--motivo", "token", humano=True).returncode, 0)

    def test_purgar_desactivado_por_configuracion(self) -> None:
        almacen.guardar(self.docs, LISTA, "x", HOY)
        (self.docs / "uxyngraphar.config.json").write_text(json.dumps({"memoria": {"permitir_purgar": False}}), encoding="utf-8")
        r = self.cli("purgar", "MEJ-20260201-b", "--confirmar", "MEJ-20260201-b", "--motivo", "x", humano=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn("permitir_purgar", r.stderr)
        self.assertIn("MEJ-20260201-b", almacen.vigentes(self.docs))

    def test_error_claro(self) -> None:
        r = self.cli("ver", "NO-EXISTE", humano=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn("no hay ninguna memoria", r.stderr)


class TestFueraDelAgente(Base):
    def test_puerta_bloquea_cambios_a_mano(self) -> None:
        shutil.copytree(SCRIPTS, self.docs / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        m = almacen.guardar(self.docs, LISTA, "x", HOY)
        cfg = {"niveles": {"memoria": "bloqueante"}}
        cambio = [f"docs/{m.ruta}"]
        self.assertEqual(puerta.control_memoria(self.repo, cambio, "docs", cfg), [])
        f = self.docs / m.ruta
        f.write_text("reescrita\n", encoding="utf-8")
        h = puerta.control_memoria(self.repo, cambio, "docs", cfg)
        self.assertEqual([x.nivel for x in h], ["bloqueante"])
        self.assertIn("R-24", h[0].mensaje)
        self.assertEqual(puerta.control_memoria(self.repo, ["src/app.py"], "docs", cfg), [])   # un cambio ajeno no la revisa

    def test_reglas_deny_y_archivos_de_exclusion(self) -> None:
        (self.repo / ".cursorignore").write_text("node_modules/\n", encoding="utf-8")
        for _ in range(2):
            proteccion.exclusiones_agentes(self.repo, "docs")
        for nombre in proteccion.EXCLUSIONES:
            texto = (self.repo / nombre).read_text(encoding="utf-8")
            self.assertIn("docs/95-memoria/", texto)
            self.assertEqual(texto.count(proteccion.EXC_INI), 1, nombre)
        self.assertTrue((self.repo / ".cursorignore").read_text(encoding="utf-8").startswith("node_modules/\n"))
        self.assertEqual(proteccion.exclusiones_agentes(self.repo, "docs"), [])
        deny = json.loads(proteccion.reglas_agente(self.repo, "docs").read_text(encoding="utf-8"))["permissions"]["deny"]
        for herramienta in ("Read", "Edit", "Write"):
            self.assertIn(f"{herramienta}(docs/95-memoria/**)", deny)

    def test_herramientas_la_ignoran(self) -> None:
        almacen.guardar(self.docs, LISTA, "x", HOY)
        self.assertNotIn("MEJ-20260201-b", [f["id"] for f in fichas(self.docs)])
        for cita in ("95-memoria/mejoras/2026/2026-10/MEJ-20260201-b.md", "memoria:MEJ-20260201-b"):
            avisos: list[str] = []
            parte = paquete._documento(self.docs, cita, avisos)
            self.assertNotIn("Texto original", parte.texto)
            self.assertIn("R-24", avisos[0])


if __name__ == "__main__":
    unittest.main()
