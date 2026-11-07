"""Pruebas propias del paquete: reglas comprobables y excepciones en una app temporal (sin el motor)."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
PAQUETE = Path(__file__).resolve().parents[1]
ID = PAQUETE.name


def correr(script: Path, *args: str, cwd: Path, humano: bool = False) -> subprocess.CompletedProcess:
    env = {"PYTHONDONTWRITEBYTECODE": "1", "PATH": os.environ.get("PATH", "")}
    if humano:
        env["UXYNGRAPHAR_HUMANO"] = "1"
    return subprocess.run([sys.executable, str(script), *args], cwd=cwd, capture_output=True, text=True,
                          env=env, stdin=subprocess.DEVNULL)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = Path(self.tmp.name)
        self.paquete = self.app / "uxyngraphar" / "paquetes" / ID
        shutil.copytree(PAQUETE, self.paquete, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "pruebas"))
        self.s = self.paquete / "scripts"
        (self.app / "src").mkdir()
        (self.app / "src" / "main.ts").write_text('console.log("listening");\n', encoding="utf-8")
        (self.app / "src" / "order.ts").write_text('export const total = 1;\n', encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def nueva(self, tipo: str, slug: str, campos: dict[str, str]) -> str:
        ruta = Path(correr(self.s / "comun" / "fichas.py", "nueva", tipo, "--slug", slug, cwd=self.app).stdout.strip())
        texto = ruta.read_text(encoding="utf-8")
        for clave, valor in campos.items():
            texto = re.sub(rf"(?m)^{clave}:.*$", lambda _: f"{clave}: {valor}", texto, count=1)
        ruta.write_text(texto, encoding="utf-8")
        return ruta.stem

    def estado(self, fid: str, status: str, humano: bool = True) -> subprocess.CompletedProcess:
        args = ["estado", fid, status] + (["--humano"] if humano else [])
        return correr(self.s / "comun" / "fichas.py", *args, cwd=self.app, humano=humano)

    def regla(self) -> str:
        fid = self.nueva("regla", "sin-console-log", {"comprobacion_prohibido": '"console\\.log\\("',
                                                       "resumen": "Sin console.log en src."})
        self.assertEqual(self.estado(fid, "activa").returncode, 0)
        return fid


class TestReglas(Base):
    def test_solo_una_persona_activa(self):
        fid = self.nueva("regla", "sin-console-log", {"comprobacion_prohibido": '"console\\.log\\("'})
        self.assertNotEqual(self.estado(fid, "activa", humano=False).returncode, 0)
        self.assertIn("ninguna regla", correr(self.s / "reglas.py", "para", "src/main.ts", cwd=self.app).stdout)

    def test_incumplimiento_y_excepcion(self):
        regla = self.regla()
        self.assertIn(regla, correr(self.s / "reglas.py", "para", "src/main.ts:1-1", cwd=self.app).stdout)
        r = correr(self.s / "reglas.py", "comprobar", cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("src/main.ts: " + regla + " [bloqueante] línea 1", r.stdout)
        exc = self.nueva("excepcion", "log-de-arranque", {"regla": regla, "archivos": "[src/main.ts]", "aprobada_por": "ana"})
        self.assertEqual(correr(self.s / "reglas.py", "comprobar", cwd=self.app).returncode, 1)
        self.assertEqual(self.estado(exc, "aprobada").returncode, 0)
        r = correr(self.s / "reglas.py", "comprobar", cwd=self.app)
        self.assertEqual(r.returncode, 0)
        self.assertIn("[excepción aprobada]", r.stdout)
        self.assertIn("0 errores, 0 avisos", correr(self.s / "verificar-reglas.py", cwd=self.app).stdout)

    def test_regex_con_doble_barra_es_invalida(self):
        fid = self.nueva("regla", "doble-barra", {"comprobacion_prohibido": '"console\\\\.log\\\\("'})
        r = correr(self.s / "verificar-reglas.py", cwd=self.app)
        self.assertIn(f"aviso: {fid}: comprobacion_prohibido: regex inválida", r.stdout)


class TestSinAjustes(Base):
    def test_ajustes_locales_ya_no_son_de_este_paquete(self):
        self.assertNotEqual(correr(self.s / "reglas.py", "ajustes", "otro-paquete", cwd=self.app).returncode, 0)
        self.assertNotEqual(correr(self.s / "comun" / "fichas.py", "nueva", "ajuste", "--slug", "x", cwd=self.app).returncode, 0)


if __name__ == "__main__":
    unittest.main()
