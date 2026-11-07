"""Pruebas propias del paquete: patrones, enmascarado y escaneo en una app temporal (sin el motor, solo librería estándar)."""

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
sys.path.insert(0, str(PAQUETE / "scripts"))

import secretos_patrones as pat  # noqa: E402

# Valores construidos en tiempo de ejecución para que este archivo no contenga ninguno literal.
CLAVE_AWS = "AKIA" + "ABCDEFGHIJKLMNOP"
CLAVE_STRIPE = "sk_live_" + "a1B2c3D4e5F6g7H8i9J0k1L2"


def correr(script: str, *args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, script, *args], cwd=cwd, capture_output=True, text=True,
                          env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin"})


class TestPatrones(unittest.TestCase):
    def test_detecta_y_enmascara(self):
        (tipo, muestra), = [pat.en_linea(f"const k = '{CLAVE_STRIPE}';")]
        self.assertEqual(tipo, "clave Stripe")
        self.assertEqual(muestra, "sk_l…(32 car.)")
        self.assertNotIn(CLAVE_STRIPE, muestra)

    def test_placeholders_y_marca(self):
        self.assertIsNone(pat.en_linea("const key = process.env.STRIPE_SECRET_KEY;"))
        self.assertIsNone(pat.en_linea("api_key = '<API_KEY>'"))
        self.assertIsNone(pat.en_linea(f"const k = '{CLAVE_AWS}'; // {pat.MARCA_PERMITIR}"))

    def test_heuristica_debil_no_aplica_en_pruebas(self):
        linea = 'const password = "hunter2hunter2";'
        self.assertIsNotNone(pat.en_linea(linea, "src/auth.ts"))
        self.assertIsNone(pat.en_linea(linea, "src/auth.spec.ts"))
        self.assertIsNotNone(pat.en_linea(f"const k = '{CLAVE_AWS}';", "src/auth.spec.ts"))

    def test_archivos_por_nombre(self):
        self.assertTrue(pat.archivo_prohibido(".env"))
        self.assertTrue(pat.archivo_prohibido("deploy/server.pem"))
        self.assertFalse(pat.archivo_prohibido(".env.example"))
        self.assertFalse(pat.archivo_prohibido("keys/id_rsa.pub"))


class TestEscaneo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = Path(self.tmp.name)
        self.paquete = self.app / "uxyngraphar" / "paquetes" / ID
        shutil.copytree(PAQUETE, self.paquete, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "pruebas"))
        (self.app / "src").mkdir()
        self.script = str(self.paquete / "scripts" / "secretos.py")

    def tearDown(self):
        self.tmp.cleanup()

    def escanear(self, *args: str) -> subprocess.CompletedProcess:
        return correr(self.script, *args, cwd=self.app)

    def test_hallazgos_informe_y_correccion(self):
        cliente = self.app / "src" / "stripe-client.ts"
        cliente.write_text(f"new Stripe('{CLAVE_STRIPE}');\n", encoding="utf-8")
        (self.app / ".env").write_text("X=1\n", encoding="utf-8")
        r = self.escanear("--informe")
        self.assertEqual(r.returncode, 1)
        self.assertIn("src/stripe-client.ts:1: clave Stripe", r.stdout)
        self.assertIn(".env: archivo de secretos", r.stdout)
        self.assertNotIn(CLAVE_STRIPE, r.stdout)
        informes = list((self.app / "uxyngraphar" / "trabajo" / ID / "informes").glob("escaneo-*.md"))
        self.assertEqual(len(informes), 1)
        self.assertNotIn(CLAVE_STRIPE, informes[0].read_text(encoding="utf-8"))
        cliente.write_text("new Stripe(process.env.STRIPE_SECRET_KEY);\n", encoding="utf-8")
        (self.app / ".env").rename(self.app / ".env.example")
        self.assertEqual(self.escanear().returncode, 0)

    def test_permitir_de_la_persona(self):
        (self.app / "src" / "aws.ts").write_text(f"const k = '{CLAVE_AWS}';\n", encoding="utf-8")
        trabajo = self.app / "uxyngraphar" / "trabajo" / ID
        trabajo.mkdir(parents=True)
        (trabajo / "ajustes.json").write_text(json.dumps({"permitir": ["src/aws.ts"]}), encoding="utf-8")
        self.assertEqual(self.escanear().returncode, 0)


if __name__ == "__main__":
    unittest.main()
