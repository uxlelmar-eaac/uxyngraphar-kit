"""Pruebas propias del paquete: hallazgos, findings_count y auditorías estancadas con verificar-auditorias.py (sin el motor)."""

from __future__ import annotations

import json
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
HALLAZGOS = """| 1 | alta | El listado hace una consulta por pedido | `src/orders/list.ts:42` |
| 2 | info | La tabla orders tiene 2 millones de filas | `SELECT count(*) FROM orders` |
"""


def correr(script: Path, *args: str, cwd: Path) -> subprocess.CompletedProcess:
    env = {"PYTHONDONTWRITEBYTECODE": "1", "PATH": os.environ.get("PATH", "")}
    return subprocess.run([sys.executable, str(script), *args], cwd=cwd, capture_output=True, text=True, env=env,
                          stdin=subprocess.DEVNULL)


class TestAuditorias(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = Path(self.tmp.name)
        paquete = self.app / "uxyngraphar" / "paquetes" / ID
        shutil.copytree(PAQUETE, paquete, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "pruebas"))
        self.s = paquete / "scripts"
        self.trabajo = self.app / "uxyngraphar" / "trabajo" / ID

    def tearDown(self):
        self.tmp.cleanup()

    def nueva(self, slug: str, hallazgos: str = "", contador: int = 0) -> str:
        r = correr(self.s / "comun" / "fichas.py", "nueva", "auditoria", "--slug", slug, "--titulo", slug, cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        ruta = next(self.trabajo.rglob(f"*{slug}*.md"))
        texto = ruta.read_text(encoding="utf-8").replace("findings_count: 0", f"findings_count: {contador}")
        texto = texto.replace("|---|-----------|----------|-----------|\n", "|---|-----------|----------|-----------|\n" + hallazgos)
        ruta.write_text(texto, encoding="utf-8")
        return ruta.stem

    def verificar(self) -> subprocess.CompletedProcess:
        return correr(self.s / "verificar-auditorias.py", cwd=self.app)

    def estado(self, fid: str, status: str) -> None:
        r = correr(self.s / "comun" / "fichas.py", "estado", fid, status, cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_hallazgos_validos(self):
        self.nueva("listado-lento", HALLAZGOS, contador=2)
        r = self.verificar()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("auditorias: 0 errores, 0 avisos", r.stdout)

    def test_severidad_y_evidencia(self):
        self.nueva("mala", "| 1 | grave | Algo va mal | `src/a.ts:1` |\n| 2 | media | Otra cosa |  |\n", contador=2)
        r = self.verificar()
        self.assertEqual(r.returncode, 1)
        self.assertIn("hallazgo 1 sin severidad válida", r.stderr)
        self.assertIn("hallazgo 2 sin evidencia", r.stderr)

    def test_contador_avisa_en_activa_y_falla_en_cerrada(self):
        fid = self.nueva("contador", HALLAZGOS, contador=1)
        r = self.verificar()
        self.assertEqual(r.returncode, 0)
        self.assertIn("findings_count=1 pero hay 2 hallazgos", r.stdout)
        self.estado(fid, "cerrada")
        r = self.verificar()
        self.assertEqual(r.returncode, 1)
        self.assertIn("findings_count=1 pero hay 2 hallazgos", r.stderr)

    def test_activa_estancada_y_demasiadas_activas(self):
        self.trabajo.mkdir(parents=True, exist_ok=True)
        (self.trabajo / "ajustes.json").write_text(json.dumps({"max_activas": 1}), encoding="utf-8")
        fid = self.nueva("vieja")
        self.nueva("nueva")
        ruta = next(self.trabajo.rglob(f"{fid}.md"))
        ruta.write_text(re.sub(r"actualizado: \S+", "actualizado: 2020-01-01", ruta.read_text(encoding="utf-8")), encoding="utf-8")
        r = self.verificar()
        self.assertIn("activa sin cambios hace", r.stdout)
        self.assertIn("2 auditorías activas (máximo 1)", r.stdout)


if __name__ == "__main__":
    unittest.main()
