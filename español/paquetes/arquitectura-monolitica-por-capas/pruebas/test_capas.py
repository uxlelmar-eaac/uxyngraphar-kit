"""Pruebas propias del paquete: andamiaje y revisión de capas en una app temporal (sin el motor, solo librería estándar)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
PAQUETE = Path(__file__).resolve().parents[1]
ID = PAQUETE.name


def correr(script: Path, *args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script), *args], cwd=cwd, capture_output=True, text=True,
                          env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": ""})


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = Path(self.tmp.name)
        self.paquete = self.app / "uxyngraphar" / "paquetes" / ID
        shutil.copytree(PAQUETE, self.paquete, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "pruebas"))
        self.s = self.paquete / "scripts"

    def tearDown(self):
        self.tmp.cleanup()

    def ajustes(self, valores: dict) -> None:
        trabajo = self.app / "uxyngraphar" / "trabajo" / ID
        trabajo.mkdir(parents=True, exist_ok=True)
        (trabajo / "ajustes.json").write_text(json.dumps(valores), encoding="utf-8")

    def andamiar(self, variante: str, nombre: str) -> subprocess.CompletedProcess:
        return correr(self.s / "comun" / "andamiar.py", variante, "--nombre", nombre, "--aplicar", cwd=self.app)


class TestAndamiaje(Base):
    def test_simular_no_crea_nada(self):
        r = correr(self.s / "comun" / "andamiar.py", "modulo-servidor", "--nombre", "orders", cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("crearía: src/modules/orders/domain/orders.entity.ts", r.stdout)
        self.assertFalse((self.app / "src").exists())

    def test_modulo_servidor_respeta_las_capas(self):
        self.assertEqual(self.andamiar("modulo-servidor", "orders").returncode, 0)
        entidad = (self.app / "src/modules/orders/domain/orders.entity.ts").read_text(encoding="utf-8")
        self.assertIn("export interface Orders", entidad)
        r = correr(self.s / "capas.py", "revisar", cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("capas: 0 imports fuera de las reglas", r.stdout)

    def test_modulo_cliente_respeta_las_capas(self):
        self.ajustes({"perfil": "cliente"})
        self.assertEqual(self.andamiar("modulo-cliente", "payment-methods").returncode, 0)
        self.assertTrue((self.app / "src/modules/payment-methods/hooks/use-payment-methods.ts").is_file())
        self.assertIn("PaymentMethods", (self.app / "src/modules/payment-methods/api/payment-methods.api.ts").read_text(encoding="utf-8"))
        r = correr(self.s / "capas.py", "revisar", cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_no_sobrescribe(self):
        destino = self.app / "src/modules/orders/domain/orders.entity.ts"
        destino.parent.mkdir(parents=True)
        destino.write_text("// propio\n", encoding="utf-8")
        r = self.andamiar("modulo-servidor", "orders")
        self.assertIn("omitido (ya existe): src/modules/orders/domain/orders.entity.ts", r.stdout)
        self.assertEqual(destino.read_text(encoding="utf-8"), "// propio\n")


class TestRevision(Base):
    def test_detecta_cruce_y_capa_no_permitida(self):
        self.andamiar("modulo-servidor", "orders")
        self.andamiar("modulo-servidor", "payments")
        uso = self.app / "src/modules/orders/application/confirm.usecase.ts"
        uso.write_text("import { X } from '../../payments/application/payments.usecase';\n", encoding="utf-8")
        dominio = self.app / "src/modules/orders/domain/reglas.ts"
        dominio.write_text("import { R } from '../infrastructure/orders.repository';\n", encoding="utf-8")
        r = correr(self.s / "capas.py", "revisar", cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("cruce de módulo orders → payments", r.stdout)
        self.assertIn("«domain» no puede importar «infrastructure»", r.stdout)
        self.assertEqual(correr(self.s / "verificar-capas.py", cwd=self.app).returncode, 0)
        self.ajustes({"nivel": "bloqueante"})
        self.assertEqual(correr(self.s / "verificar-capas.py", cwd=self.app).returncode, 1)


if __name__ == "__main__":
    unittest.main()
