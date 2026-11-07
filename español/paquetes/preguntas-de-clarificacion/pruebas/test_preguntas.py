"""Pruebas propias del paquete: reglas de la ficha pregunta y verificación en una app temporal (sin el motor, solo librería estándar)."""

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

sys.dont_write_bytecode = True
PAQUETE = Path(__file__).resolve().parents[1]
ID = PAQUETE.name
sys.path.insert(0, str(PAQUETE / "scripts"))

import preguntas_reglas as reglas  # noqa: E402

RESPONDIDA = """
## Impacto
Dónde vive el filtro y qué estados se ofrecen.

## Decisiones
| # | Pregunta | Opciones | Elegida | Efecto |
|---|----------|----------|---------|--------|
| 1 | ¿Filtro en la URL o en memoria? | URL (recomendada) · memoria | URL | se lee de `?estado=` |
| 2 | ¿Qué estados? | todos · pendiente, pagado, enviado | los tres | lista fija |

## Síntesis
- Filtro en la URL; estados pendiente, pagado y enviado.
"""


def correr(script: Path, *args: str, cwd: Path) -> subprocess.CompletedProcess:
    entorno = {k: v for k, v in os.environ.items() if k not in ("UXYNGRAPHAR_HUMANO", "CI")}
    entorno["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run([sys.executable, str(script), *args], cwd=cwd, capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, env=entorno)


class TestReglas(unittest.TestCase):
    def test_respondida_no_tiene_problemas(self):
        self.assertEqual(reglas.problemas_completada(RESPONDIDA), [])
        self.assertEqual(len(reglas.filas_decisiones(reglas.secciones(RESPONDIDA)["Decisiones"])), 2)

    def test_plantilla_sin_rellenar(self):
        plantilla = (PAQUETE / "plantillas" / "pregunta.md").read_text(encoding="utf-8").split("\n---", 1)[1]
        problemas = reglas.problemas_completada(plantilla)
        self.assertIn("decisión 1 sin pregunta", problemas)
        self.assertIn("síntesis vacía", problemas)

    def test_elegida_vacia_es_decision_supuesta(self):
        texto = RESPONDIDA.replace("| URL | se lee", "| … | se lee")
        self.assertEqual(reglas.problemas_completada(texto), ["decisión 1 sin «Elegida» de la persona"])

    def test_sin_tabla(self):
        self.assertIn("sin decisiones en la tabla", reglas.problemas_completada("## Decisiones\n\n## Síntesis\n- x\n"))

    def test_dias_desde(self):
        self.assertEqual(reglas.dias_desde("2026-11-01", date(2026, 11, 6)), 5)
        self.assertIsNone(reglas.dias_desde(None))

    def test_instruccion_solo_si_existe_su_trabajo(self):
        with tempfile.TemporaryDirectory() as tmp:
            trabajo = Path(tmp) / reglas.INSTRUCCIONES
            self.assertIsNone(reglas.aviso_instruccion(trabajo, "INS-20261106-x"))
            (trabajo / "instrucciones" / "pendientes").mkdir(parents=True)
            self.assertIn("no está en", reglas.aviso_instruccion(trabajo, "INS-20261106-x"))
            (trabajo / "instrucciones" / "pendientes" / "INS-20261106-x.md").write_text("---\n---\n", encoding="utf-8")
            self.assertIsNone(reglas.aviso_instruccion(trabajo, "INS-20261106-x"))
            self.assertIsNone(reglas.aviso_instruccion(trabajo, None))


class TestVerificacion(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = Path(self.tmp.name)
        destino = self.app / "uxyngraphar" / "paquetes" / ID
        shutil.copytree(PAQUETE, destino, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "pruebas"))
        self.s = destino / "scripts"
        self.trabajo = self.app / "uxyngraphar" / "trabajo"

    def tearDown(self):
        self.tmp.cleanup()

    def nueva(self, slug: str, cuerpo: str | None = None) -> str:
        r = correr(self.s / "comun" / "fichas.py", "nueva", "pregunta", "--slug", slug, cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        ruta = Path(r.stdout.strip())
        self.assertEqual(ruta.parent.relative_to(self.trabajo).as_posix(), f"{ID}/preguntas/en-curso")
        if cuerpo is not None:
            texto = ruta.read_text(encoding="utf-8")
            ruta.write_text(texto.split("\n## Impacto", 1)[0] + cuerpo, encoding="utf-8")
        return ruta.stem

    def campo(self, fid: str, clave: str, valor: str) -> None:
        ruta = next((self.trabajo / ID).rglob(f"{fid}.md"))
        texto = ruta.read_text(encoding="utf-8")
        inicio = texto.index(f"\n{clave}:") + 1
        fin = texto.index("\n", inicio)
        ruta.write_text(texto[:inicio] + f"{clave}: {valor}" + texto[fin:], encoding="utf-8")

    def verificar(self) -> subprocess.CompletedProcess:
        return correr(self.s / "verificar-preguntas.py", cwd=self.app)

    def test_completada_con_decisiones_pasa(self):
        fid = self.nueva("filtro", RESPONDIDA)
        self.assertEqual(correr(self.s / "comun" / "fichas.py", "estado", fid, "completada", cwd=self.app).returncode, 0)
        r = self.verificar()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("0 errores, 0 avisos", r.stdout)

    def test_completada_sin_responder_falla(self):
        fid = self.nueva("sin-responder")
        self.assertEqual(self.verificar().returncode, 0, "en curso puede estar a medias")
        correr(self.s / "comun" / "fichas.py", "estado", fid, "completada", cwd=self.app)
        r = self.verificar()
        self.assertEqual(r.returncode, 1)
        self.assertIn("decisión 1 sin pregunta", r.stderr)

    def test_en_curso_estancada_avisa(self):
        fid = self.nueva("vieja", RESPONDIDA)
        self.campo(fid, "created", "2020-01-01")
        r = self.verificar()
        self.assertEqual(r.returncode, 0)
        self.assertIn("en-curso desde hace", r.stdout)
        (self.trabajo / ID / "ajustes.json").write_text(json.dumps({"dias_en_curso": 100000}), encoding="utf-8")
        self.assertNotIn("en-curso desde hace", self.verificar().stdout)

    def test_instruccion_enlazada_sin_instrucciones_aprobadas(self):
        fid = self.nueva("enlazada", RESPONDIDA)
        self.campo(fid, "instruccion_id", "INS-20261106-filtro")
        self.assertIn("0 avisos", self.verificar().stdout, "sin el trabajo de instrucciones-aprobadas no se consulta")
        pendientes = self.trabajo / reglas.INSTRUCCIONES / "instrucciones" / "pendientes"
        pendientes.mkdir(parents=True)
        self.assertIn("instruccion_id INS-20261106-filtro no está en", self.verificar().stdout)
        (pendientes / "INS-20261106-filtro.md").write_text("---\nid: INS-20261106-filtro\n---\n", encoding="utf-8")
        self.assertIn("0 avisos", self.verificar().stdout)


if __name__ == "__main__":
    unittest.main()
