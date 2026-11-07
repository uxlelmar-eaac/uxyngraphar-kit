"""Pruebas propias del paquete: reglas de alcance y ciclo de una instrucción en una app temporal (sin el motor, solo librería estándar).

Se ejecutan como un agente (sin terminal ni UXYNGRAPHAR_HUMANO): comprueban que nada avanza sin la aprobación de una persona.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
PAQUETE = Path(__file__).resolve().parents[1]
ID = PAQUETE.name
sys.path.insert(0, str(PAQUETE / "scripts"))

import ciclo_reglas as reglas  # noqa: E402


def correr(script: Path, *args: str, cwd: Path) -> subprocess.CompletedProcess:
    entorno = {k: v for k, v in os.environ.items() if k not in ("UXYNGRAPHAR_HUMANO", "CI")}
    entorno["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run([sys.executable, str(script), *args], cwd=cwd, capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, env=entorno)


class TestReglas(unittest.TestCase):
    def test_separar_ancla(self):
        self.assertEqual(reglas.separar_ancla("src/a.ts:10-12"), ("src/a.ts", 10, 12))
        self.assertEqual(reglas.separar_ancla("src/a.ts:7"), ("src/a.ts", 7, 7))
        self.assertEqual(reglas.separar_ancla("`src/a.ts`"), ("src/a.ts", None, None))

    def test_cuenta_solo_archivos_de_codigo_distintos(self):
        fm = {"anclas_codigo": ["src/a.ts:1-5", "src/a.ts:20-30", "README.md", "src/b.py"]}
        self.assertEqual(reglas.archivos_codigo(fm), ["src/a.ts", "src/b.py"])

    def test_alcance_y_ampliacion(self):
        fm = {"anclas_codigo": [f"src/m{i}.ts" for i in range(7)]}
        self.assertIn("7 archivos de código en anclas (máximo 5)", reglas.problemas_alcance(fm, {})[0])
        fm.update(ampliacion_factor="1.5", ampliacion_justificacion="renombrar un tipo usado en 7 archivos")
        self.assertEqual(reglas.problemas_alcance(fm, {}), [])
        fm["ampliacion_justificacion"] = ""
        self.assertIn("ampliacion_factor sin ampliacion_justificacion", reglas.problemas_alcance(fm, {}))
        self.assertIn("fuera de 1.5–2.0", reglas.problemas_alcance({"ampliacion_factor": "3", "ampliacion_justificacion": "x"}, {})[0])

    def test_maximo_de_documentos(self):
        fm = {"lectura_minima": [f"doc{i}.md" for i in range(3)]}
        self.assertEqual(reglas.problemas_alcance(fm, {"max_docs": 3}), [])
        self.assertTrue(reglas.problemas_alcance(fm, {"max_docs": 2}))


class TestCiclo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = Path(self.tmp.name)
        destino = self.app / "uxyngraphar" / "paquetes" / ID
        shutil.copytree(PAQUETE, destino, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "pruebas"))
        self.s = destino / "scripts"
        (self.app / "src").mkdir()
        (self.app / "src" / "a.ts").write_text("\n".join(f"line{i}" for i in range(1, 31)), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def nueva(self, slug: str, anclas: list[str]) -> str:
        r = correr(self.s / "comun" / "fichas.py", "nueva", "instruccion", "--slug", slug, cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        ruta = Path(r.stdout.strip())
        bloque = "anclas_codigo:\n" + "".join(f"  - {a}\n" for a in anclas)
        ruta.write_text(ruta.read_text(encoding="utf-8").replace("anclas_codigo: []\n", bloque), encoding="utf-8")
        return ruta.stem

    def test_sin_aprobacion_no_hay_contexto(self):
        fid = self.nueva("cambiar-a", ["src/a.ts:10-12"])
        r = correr(self.s / "ciclo.py", "contexto", fid, cwd=self.app)
        self.assertEqual(r.returncode, 3)
        self.assertIn("BLOQUEADO", r.stdout)
        self.assertNotIn("line10", r.stdout)

    def test_el_agente_no_aprueba(self):
        fid = self.nueva("cambiar-a", ["src/a.ts:10-12"])
        r = correr(self.s / "ciclo.py", "aprobar", fid, cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("solo lo asigna una persona", r.stderr)
        r = correr(self.s / "ciclo.py", "aprobar", fid, "--humano", cwd=self.app)
        self.assertEqual(r.returncode, 1, "sin terminal ni UXYNGRAPHAR_HUMANO, --humano no basta")
        self.assertIn(fid, correr(self.s / "ciclo.py", "pendientes", cwd=self.app).stdout)

    def test_no_se_cierra_sin_aprobar(self):
        fid = self.nueva("cambiar-a", ["src/a.ts"])
        r = correr(self.s / "ciclo.py", "cerrar", fid, cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("solo se cierra una instrucción approved", r.stderr)

    def test_verificacion_detecta_alcance_excesivo(self):
        self.nueva("pequena", ["src/a.ts"])
        self.assertEqual(correr(self.s / "verificar-ciclo.py", cwd=self.app).returncode, 0)
        self.nueva("demasiado", [f"src/m{i}.ts" for i in range(7)])
        r = correr(self.s / "verificar-ciclo.py", cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("7 archivos de código", r.stderr)

    def test_pregunta_citada_sin_preguntas_de_clarificacion(self):
        fid = self.nueva("con-pregunta", ["src/a.ts"])
        ruta = next((self.app / "uxyngraphar" / "trabajo" / ID).rglob(f"{fid}.md"))
        ruta.write_text(ruta.read_text(encoding="utf-8").replace("preguntas_id: null", "preguntas_id: PRE-20261106-x"),
                        encoding="utf-8")
        r = correr(self.s / "verificar-ciclo.py", cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("preguntas_id", r.stdout, "sin el trabajo de preguntas-de-clarificacion no se consulta")
        preguntas = self.app / "uxyngraphar" / "trabajo" / reglas.PREGUNTAS / "preguntas"
        preguntas.mkdir(parents=True)
        self.assertIn("PRE-20261106-x no está en", correr(self.s / "verificar-ciclo.py", cwd=self.app).stdout)
        (preguntas / "en-curso").mkdir()
        (preguntas / "en-curso" / "PRE-20261106-x.md").write_text("---\nid: PRE-20261106-x\nstatus: en-curso\n---\n",
                                                                  encoding="utf-8")
        self.assertIn("sigue en-curso", correr(self.s / "verificar-ciclo.py", cwd=self.app).stdout)
        (preguntas / "en-curso" / "PRE-20261106-x.md").unlink()
        (preguntas / "completadas").mkdir()
        (preguntas / "completadas" / "PRE-20261106-x.md").write_text("---\nid: PRE-20261106-x\nstatus: completada\n---\n",
                                                                     encoding="utf-8")
        r = correr(self.s / "verificar-ciclo.py", cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("preguntas_id", r.stdout)

    def test_estado_conserva_las_notas(self):
        self.nueva("cambiar-a", ["src/a.ts"])
        estado = self.app / "uxyngraphar" / "trabajo" / ID / "ESTADO.md"
        self.assertEqual(correr(self.s / "ciclo.py", "estado", cwd=self.app).returncode, 0)
        estado.write_text(estado.read_text(encoding="utf-8") + "- nota de la persona\n", encoding="utf-8")
        self.assertEqual(correr(self.s / "ciclo.py", "estado", cwd=self.app).returncode, 0)
        texto = estado.read_text(encoding="utf-8")
        self.assertIn("| Esperando aprobación | 1 |", texto)
        self.assertIn("- nota de la persona", texto)


if __name__ == "__main__":
    unittest.main()
