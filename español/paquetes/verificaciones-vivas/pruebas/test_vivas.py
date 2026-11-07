"""Pruebas propias del paquete: normalización de rutas, anclas, vínculos, humo e informe en una app temporal (sin el motor)."""

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
sys.path[:0] = [str(PAQUETE / "scripts"), str(PAQUETE / "scripts" / "comun")]

import vivas_datos as datos  # noqa: E402


class TestNormalizar(unittest.TestCase):
    def test_parametros_y_barras(self):
        for ruta in ("/orders/:id", "orders/{id}", "/orders/[id]/", "//orders/:orderId"):
            self.assertEqual(datos.normalizar(ruta), "/orders/{}")
        self.assertEqual(datos.normalizar(""), "/")


class TestRevisiones(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = Path(self.tmp.name)
        self.paquete = self.app / "uxyngraphar" / "paquetes" / ID
        shutil.copytree(PAQUETE, self.paquete, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "pruebas"))
        self.trabajo = self.app / "uxyngraphar" / "trabajo"
        (self.app / "src" / "billing").mkdir(parents=True)
        (self.app / "src" / "billing" / "orders.service.ts").write_text("export {};\n", encoding="utf-8")
        nota = self.trabajo / "otro-paquete" / "NOTA.md"
        nota.parent.mkdir(parents=True)
        nota.write_text("# Nota\n\n## Archivos ancla\n- `src/billing/orders.service.ts`\n- `src/orders/orders.service.ts`\n\n"
                        "Ver RUT-20260101-pedidos-viejos.\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def vivas(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(self.paquete / "scripts" / "vivas.py"), *args], cwd=self.app,
                              capture_output=True, text=True, env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": os.environ.get("PATH", "")})

    def test_anclas_y_vinculos(self):
        r = self.vivas("anclas", "vinculos")
        self.assertEqual(r.returncode, 1)
        self.assertIn("ancla rota: src/orders/orders.service.ts (¿ahora en src/billing/orders.service.ts?)", r.stdout)
        self.assertNotIn("ancla rota: src/billing/orders.service.ts", r.stdout)
        self.assertIn("id colgante: RUT-20260101-pedidos-viejos", r.stdout)
        self.assertIn("verificaciones-vivas: 2 hallazgos", r.stdout)

    def test_paquetes_ausentes_son_notas(self):
        r = self.vivas("rutas", "decisiones")
        self.assertEqual(r.returncode, 0)
        self.assertIn("info: rutas-de-api no está instalado", r.stdout)

    def test_humo_solo_con_ejecutar(self):
        trabajo = self.trabajo / ID
        trabajo.mkdir(parents=True)
        (trabajo / "ajustes.json").write_text(json.dumps({"humo": [{"nombre": "arranque", "comando": "exit 3"}]}), encoding="utf-8")
        r = self.vivas("humo")
        self.assertEqual(r.returncode, 0)
        self.assertIn("sin ejecutar", r.stdout)
        r = self.vivas("humo", "--ejecutar")
        self.assertEqual(r.returncode, 1)
        self.assertIn("humo «arranque» falla (código 3)", r.stdout)

    def test_informe_sin_auditorias(self):
        r = self.vivas("anclas", "--informe")
        self.assertIn("informe: uxyngraphar/trabajo/verificaciones-vivas/INFORME-", r.stdout)
        (informe,) = (self.trabajo / ID).glob("INFORME-*-anclas.md")
        texto = informe.read_text(encoding="utf-8")
        self.assertIn("| 1 | media | anclas: ancla rota: src/orders/orders.service.ts", texto)
        self.assertIn("`vivas.py anclas` (verificaciones-vivas)", texto)

    def test_revision_desconocida(self):
        r = self.vivas("todo")
        self.assertEqual(r.returncode, 2)
        self.assertIn("revisión desconocida", r.stderr)


if __name__ == "__main__":
    unittest.main()
