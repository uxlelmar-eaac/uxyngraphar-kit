"""Pruebas propias del paquete: reglas del mosaico y de la checklist de verificar-bento.py en una app temporal (sin el motor)."""

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
MOSAICO = """| 1 | 2x2 | 1 | Cobra en 2 minutos | Sin contratos ni permanencia | primario | img: panel de cobros en un móvil |
| 2 | 2x1 | 2 | Pagos en 30 países | Monedas locales y conversión automática | - | icono |
| 3 | 1x1 | 3 | Soporte 24/7 | Personas reales | - | - |
| 4 | 1x1 | 4 | Seguro | Cifrado de extremo a extremo | - | - |
| 5 | 4x1 | 5 | Empieza hoy | Cuenta gratis en un minuto | secundario | - |
"""


def correr(script: Path, *args: str, cwd: Path, humano: bool = False) -> subprocess.CompletedProcess:
    env = {"PYTHONDONTWRITEBYTECODE": "1", "PATH": os.environ.get("PATH", "")}
    if humano:
        env["UXYNGRAPHAR_HUMANO"] = "1"
    return subprocess.run([sys.executable, str(script), *args], cwd=cwd, capture_output=True, text=True, env=env,
                          stdin=subprocess.DEVNULL)


class TestBento(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = Path(self.tmp.name)
        paquete = self.app / "uxyngraphar" / "paquetes" / ID
        shutil.copytree(PAQUETE, paquete, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "pruebas"))
        self.s = paquete / "scripts"
        self.trabajo = self.app / "uxyngraphar" / "trabajo" / ID

    def tearDown(self):
        self.tmp.cleanup()

    def nueva(self, slug: str, mosaico: str = "") -> str:
        r = correr(self.s / "comun" / "fichas.py", "nueva", "landing", "--slug", slug, "--titulo", slug, cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        ruta = next(self.trabajo.rglob(f"*{slug}*.md"))
        if mosaico:
            cabecera, resto = ruta.read_text(encoding="utf-8").split("## Mosaico\n", 1)
            bloque, despues = resto.split("\n\n", 1)
            ruta.write_text(f"{cabecera}## Mosaico\n{bloque}\n{mosaico}\n{despues}", encoding="utf-8")
        return ruta.stem

    def ruta(self, fid: str) -> Path:
        return next(self.trabajo.rglob(f"{fid}.md"))

    def estado(self, fid: str, status: str, humano: bool = False) -> subprocess.CompletedProcess:
        return correr(self.s / "comun" / "fichas.py", "estado", fid, status, *(["--humano"] if humano else []),
                      cwd=self.app, humano=humano)

    def verificar(self) -> subprocess.CompletedProcess:
        return correr(self.s / "verificar-bento.py", cwd=self.app)

    def test_borrador_avisa_y_en_curso_falla(self):
        fid = self.nueva("vacia")
        r = self.verificar()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("aviso:", r.stdout)
        self.assertEqual(self.estado(fid, "en-curso").returncode, 0)
        self.assertEqual(self.verificar().returncode, 1)

    def test_mosaico_valido_y_publicacion_humana(self):
        fid = self.nueva("cobros", MOSAICO)
        self.assertEqual(self.estado(fid, "en-curso").returncode, 0)
        self.assertIn("bento: 0 errores, 0 avisos", self.verificar().stdout)
        self.assertEqual(self.estado(fid, "revision").returncode, 0)
        r = self.verificar()
        self.assertIn("checklist incompleta", r.stderr)
        ruta = self.ruta(fid)
        ruta.write_text(ruta.read_text(encoding="utf-8").replace("- [ ]", "- [x]"), encoding="utf-8")
        self.assertEqual(self.verificar().returncode, 0)
        self.assertNotEqual(self.estado(fid, "publicada").returncode, 0)
        self.assertEqual(self.estado(fid, "publicada", humano=True).returncode, 0)

    def test_jerarquia_cta_huecos_y_alt(self):
        malo = (MOSAICO.replace("| 4x1 | 5 | Empieza hoy | Cuenta gratis en un minuto | secundario",
                                "| 2x1 | 5 | Empieza hoy | Cuenta gratis en un minuto | primario")
                .replace("img: panel de cobros en un móvil", "img:")
                .replace("| 3 | 1x1 | 3 |", "| 3 | 3x3 | 3 |"))
        fid = self.nueva("mala", malo)
        self.assertEqual(self.estado(fid, "en-curso").returncode, 0)
        r = self.verificar()
        for esperado in ("exactamente un CTA primario", "sin texto alternativo", "tamaño «3x3» no permitido"):
            self.assertIn(esperado, r.stderr)

    def test_ajustes_del_proyecto(self):
        self.trabajo.mkdir(parents=True, exist_ok=True)
        (self.trabajo / "ajustes.json").write_text(json.dumps({"palabras_titulo": 2}), encoding="utf-8")
        fid = self.nueva("corta", MOSAICO)
        self.assertEqual(self.estado(fid, "en-curso").returncode, 0)
        self.assertIn("de más de 2 palabras", self.verificar().stderr)


if __name__ == "__main__":
    unittest.main()
