#!/usr/bin/env python3
"""Pruebas del costo en tokens por fases: transcripciones reales simuladas, manual, estimado, tabla y ciclo new → contexto → cerrar."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SCRIPTS = AQUI.parent
PACK = SCRIPTS.parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(SCRIPTS / "decisiones"))

import costo  # noqa: E402

FICHA = "---\nid: 20261026-001-x\nstatus: approved\n---\n# x\n\n## Costo en tokens\n\n<!-- tokens:inicio -->\nPendiente.\n<!-- tokens:fin -->\n"


def linea(ts: str, cwd: str, mid: str, entrada: int, salida: int, lectura: int = 0, sesion: str = "s1") -> str:
    return json.dumps({"type": "assistant", "timestamp": ts, "cwd": cwd, "sessionId": sesion,
                       "message": {"id": mid, "usage": {"input_tokens": entrada, "output_tokens": salida, "cache_read_input_tokens": lectura,
                                                        "cache_creation_input_tokens": 0}}})


class TestMedir(unittest.TestCase):
    def setUp(self) -> None:
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.repo = Path(self._t.name) / "repo"
        self.docs = self.repo / "docs"
        (self.docs / "05-instrucciones/02-en-progreso/2026-10-26").mkdir(parents=True)
        self.ficha = self.docs / "05-instrucciones/02-en-progreso/2026-10-26/x.md"
        self.ficha.write_text(FICHA, encoding="utf-8")
        self.tr = Path(self._t.name) / "transcripciones" / "proyecto"
        self.tr.mkdir(parents=True)
        cwd = str(self.repo.resolve())
        filas = [linea("2026-10-26T10:00:00Z", cwd, "m1", 100, 10, 1000),        # análisis (inicio de sesión)
                 linea("2026-10-26T10:05:00Z", cwd, "m2", 50, 200),              # instrucción
                 linea("2026-10-26T10:05:00Z", cwd, "m2", 50, 250),              # mismo mensaje (streaming): cuenta una vez, el máximo
                 linea("2026-10-26T10:20:00Z", cwd, "m3", 300, 400, 5000),       # implementación
                 linea("2026-10-26T10:40:00Z", cwd, "m4", 20, 30),               # verificación
                 linea("2026-10-26T10:41:00Z", "/otro/repo", "m5", 9999, 9999),  # otro proyecto: no cuenta
                 linea("2026-10-26T10:50:00Z", cwd, "m6", 5, 5),                 # cierre
                 linea("2026-10-26T11:30:00Z", cwd, "m7", 7777, 7777)]           # después de cerrar: no cuenta
        (self.tr / "s1.jsonl").write_text("\n".join(filas) + "\n", encoding="utf-8")
        for fase, ts in (("instruccion", "2026-10-26T10:04:00Z"), ("implementacion", "2026-10-26T10:15:00Z"),
                         ("verificacion", "2026-10-26T10:35:00Z"), ("cierre", "2026-10-26T10:45:00Z")):
            costo.marcar(self.docs, "20261026-001-x", fase, ts)
        costo.terminar(self.docs, "20261026-001-x", "2026-10-26T11:00:00Z")

    def test_reparte_por_fases_y_escribe(self) -> None:
        m = costo.medir(self.repo, self.docs, "20261026-001-x", self.ficha, str(self.tr.parent))
        f = m["fases"]
        self.assertEqual(f["analisis"], {"entrada": 100, "cache_lectura": 1000, "cache_escritura": 0, "salida": 10})
        self.assertEqual(f["instruccion"]["salida"], 250)
        self.assertEqual(costo.total(f["implementacion"]), 5700)
        self.assertEqual(costo.total(f["verificacion"]), 50)
        self.assertEqual(costo.total(f["cierre"]), 10)
        self.assertIn("medido en 1 sesión", m["fuente"])
        costo.escribir(self.ficha, m)
        texto = self.ficha.read_text(encoding="utf-8")
        self.assertNotIn("Pendiente.", texto)
        self.assertIn("| **Total** |", texto)
        self.assertIn("Tokens nuevos (sin caché leída): **1 170**", texto)
        self.assertEqual(sum(costo.total(v) for v in costo.leer_datos(self.ficha)["fases"].values()), 7170)

    def test_manual_y_estimado(self) -> None:
        costo.registrar(self.docs, "20261026-001-x", "verificacion", entrada=10, salida=5)
        m = costo.medir(self.repo, self.docs, "20261026-001-x", self.ficha, str(Path(self._t.name) / "vacia"))
        self.assertEqual(costo.total(m["fases"]["verificacion"]), 15)
        self.assertEqual(m["fuente"], "1 registro(s) manual(es)")
        otra = costo.medir(self.repo, self.docs, "sin-marcas", self.ficha, str(Path(self._t.name) / "vacia"))
        self.assertTrue(otra["fuente"].startswith("estimado"))
        self.assertGreater(otra["fases"]["instruccion"]["salida"], 0)

    def test_cli_resumen(self) -> None:
        costo.escribir(self.ficha, costo.medir(self.repo, self.docs, "20261026-001-x", self.ficha, str(self.tr.parent)))
        r = subprocess.run([sys.executable, str(SCRIPTS / "costo-tokens.py"), "resumen", "--repo", str(self.repo)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("7 170", r.stdout)
        self.assertIn("Media por fase", r.stdout)


class TestCiclo(unittest.TestCase):
    """new marca «instrucción», contexto marca «implementación» y cerrar escribe la tabla."""

    def test_new_contexto_cerrar(self) -> None:
        if not (PACK / "05-instrucciones" / "_PLANTILLA.md").is_file():
            self.skipTest("requiere el pack fuente")
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            docs = repo / "docs"
            shutil.copytree(PACK, docs, ignore=shutil.ignore_patterns("__pycache__", ".decisiones"))
            env = {**os.environ, "UXYNGRAPHAR_TRANSCRIPCIONES": str(repo / "no-hay")}
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            dec = [sys.executable, str(docs / "scripts/decisiones/decisiones.py")]
            r = subprocess.run(dec + ["new", "instruccion", "--slug", "prueba-costo", "--docs", str(docs)], capture_output=True, text=True, env=env)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            ficha = next((docs / "05-instrucciones/01-pendientes").rglob("prueba-costo.md"))
            ident = next(l.split(":", 1)[1].strip() for l in ficha.read_text(encoding="utf-8").splitlines() if l.startswith("id:"))
            self.assertEqual([m["fase"] for m in costo.leer_marcas(docs, ident)["marcas"]], ["instruccion"])
            destino = docs / "05-instrucciones/02-en-progreso" / ficha.parent.name / ficha.name
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(ficha.read_text(encoding="utf-8").replace("status: draft", "status: approved").replace("status: awaiting_approval", "status: approved"), encoding="utf-8")
            ficha.unlink()
            subprocess.run([sys.executable, str(docs / "scripts/contexto.py"), ident, "--repo", str(repo)], capture_output=True, text=True, env=env)
            self.assertIn("implementacion", [m["fase"] for m in costo.leer_marcas(docs, ident)["marcas"]])
            r = subprocess.run(dec + ["cerrar", ident, "--docs", str(docs)], capture_output=True, text=True, env=env)
            self.assertIn("Costo en tokens", r.stdout, r.stdout + r.stderr)
            cerrada = next((docs / "05-instrucciones/03-completadas").rglob("prueba-costo.md"))
            self.assertIsNotNone(costo.leer_datos(cerrada))


if __name__ == "__main__":
    unittest.main()
