"""Pruebas propias del paquete: ciclo de una evaluación y reglas de verificar-evaluaciones.py en una app temporal (sin el motor)."""

from __future__ import annotations

import json
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
FILA = "| 1 | H9 | 3 | El error no dice qué campo falla | `src/signup/form.tsx:88` | Mensaje bajo el campo | {aprobada} |\n"
METRICA = "| Pasos del alta | 7 | 4 | {despues} | conteo manual desde /signup |\n"


def correr(script: Path, *args: str, cwd: Path, humano: bool = False) -> subprocess.CompletedProcess:
    env = {"PYTHONDONTWRITEBYTECODE": "1", "PATH": os.environ.get("PATH", "")}
    if humano:
        env["UXYNGRAPHAR_HUMANO"] = "1"
    return subprocess.run([sys.executable, str(script), *args], cwd=cwd, capture_output=True, text=True, env=env,
                          stdin=subprocess.DEVNULL)


class TestEvaluaciones(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = Path(self.tmp.name)
        paquete = self.app / "uxyngraphar" / "paquetes" / ID
        shutil.copytree(PAQUETE, paquete, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "pruebas"))
        self.s = paquete / "scripts"
        self.trabajo = self.app / "uxyngraphar" / "trabajo" / ID

    def tearDown(self):
        self.tmp.cleanup()

    def nueva(self, slug: str) -> str:
        r = correr(self.s / "comun" / "fichas.py", "nueva", "evaluacion", "--slug", slug, "--titulo", slug, cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        return next(self.trabajo.rglob(f"*{slug}*.md")).stem

    def ruta(self, fid: str) -> Path:
        return next(self.trabajo.rglob(f"{fid}.md"))

    def estado(self, fid: str, status: str, humano: bool = False) -> subprocess.CompletedProcess:
        return correr(self.s / "comun" / "fichas.py", "estado", fid, status, *(["--humano"] if humano else []),
                      cwd=self.app, humano=humano)

    def rellenar(self, fid: str, titulo: str, filas: str) -> None:
        ruta = self.ruta(fid)
        cabecera, resto = ruta.read_text(encoding="utf-8").split(f"## {titulo}\n", 1)
        bloque, despues = resto.split("\n\n", 1)
        ruta.write_text(f"{cabecera}## {titulo}\n{bloque}\n{filas}\n{despues}", encoding="utf-8")

    def verificar(self) -> subprocess.CompletedProcess:
        return correr(self.s / "verificar-evaluaciones.py", cwd=self.app)

    def test_ciclo_completo(self):
        fid = self.nueva("alta")
        self.rellenar(fid, "Problemas", FILA.format(aprobada=""))
        self.assertEqual(self.estado(fid, "propuesta").returncode, 0)
        r = self.verificar()
        self.assertEqual(r.returncode, 1)
        self.assertIn("sin métricas", r.stderr)
        self.rellenar(fid, "Métricas", METRICA.format(despues=""))
        self.assertEqual(self.verificar().returncode, 0)
        self.assertNotEqual(self.estado(fid, "aprobada").returncode, 0)
        ruta = self.ruta(fid)
        ruta.write_text(ruta.read_text(encoding="utf-8").replace("| Mensaje bajo el campo |  |", "| Mensaje bajo el campo | sí |"),
                        encoding="utf-8")
        self.assertEqual(self.estado(fid, "aprobada", humano=True).returncode, 0)
        self.assertEqual(self.estado(fid, "implementada").returncode, 0)
        self.assertEqual(self.estado(fid, "validada", humano=True).returncode, 0)
        r = self.verificar()
        self.assertIn("sin Después", r.stderr)
        ruta = self.ruta(fid)
        ruta.write_text(ruta.read_text(encoding="utf-8").replace("| 7 | 4 |  |", "| 7 | 4 | 4 |"), encoding="utf-8")
        r = self.verificar()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("evaluaciones: 0 errores", r.stdout)

    def test_aprobada_por_el_agente_es_error(self):
        fid = self.nueva("pago")
        self.rellenar(fid, "Problemas", FILA.format(aprobada="sí"))
        r = self.verificar()
        self.assertEqual(r.returncode, 1)
        self.assertIn("aprueba una persona", r.stderr)

    def test_severidad_alta_sin_propuesta_y_valores_invalidos(self):
        fid = self.nueva("checkout")
        self.rellenar(fid, "Problemas", "| 1 | H5 | 4 | Se puede pagar dos veces | `src/pay.ts:12` | - | |\n"
                                        "| 2 | H99 | 9 | x | - | - | |\n")
        r = self.verificar()
        self.assertEqual(r.returncode, 1)
        for esperado in ("severidad 4 sin propuesta", "heurística «H99»", "severidad «9»", "sin evidencia"):
            self.assertIn(esperado, r.stderr)

    def test_archivada_no_se_revisa(self):
        fid = self.nueva("ajustes")
        self.rellenar(fid, "Problemas", "| 1 | H99 | 9 | x | - | - | |\n")
        self.assertEqual(self.estado(fid, "archivada").returncode, 0)
        self.assertEqual(self.verificar().returncode, 0)

    def test_heuristica_ajustada_por_el_proyecto(self):
        self.trabajo.mkdir(parents=True, exist_ok=True)
        (self.trabajo / "ajustes.json").write_text(json.dumps({"heuristicas": ["H1"]}), encoding="utf-8")
        fid = self.nueva("perfil")
        self.rellenar(fid, "Problemas", FILA.format(aprobada=""))
        r = self.verificar()
        self.assertIn("heurística «H9» no válida", r.stderr)


if __name__ == "__main__":
    unittest.main()
