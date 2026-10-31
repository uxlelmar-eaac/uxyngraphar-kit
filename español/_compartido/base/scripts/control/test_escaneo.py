"""Pruebas del escaneo de credenciales (árbol e historial)."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import escaneo  # noqa: E402
import secretos as sec  # noqa: E402

CLI = AQUI.parent / "escanear-secretos.py"
CLAVE = "AKIA" + "ABCDEFGHIJKLMNOP"


def git(repo: Path, *a: str) -> None:
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=repo, check=True, capture_output=True)


class TestSecretos(unittest.TestCase):
    def test_patrones_y_placeholders(self):
        positivos = [f'k = "{CLAVE}"', "ghp_" + "a" * 36, "-----BEGIN RSA " + "PRIVATE KEY-----", "sk-" + "a1" * 14,
                     "password = " + chr(34) + "Tr0ub4dor&3xyz" + chr(34), "mongodb://" + "root:hunter2pass@10.0.0.5/db", "AIza" + "B" * 35,
                     "eyJhbGciOiJIUzI1NiJ9." + "eyJzdWIiOiIxMjM0NTY3ODkwIn0.abcdefghij12345"]
        for l in positivos:
            self.assertIsNotNone(sec.en_linea(l), l)
        negativos = ['password = "<DB_PASSWORD>"', 'token = os.environ["TOKEN"]', 'API_KEY="changeme-123456"', "postgres://user:pass@host/db",
                     'password = "${DB_PASS}"', "clave de ejemplo: AKIA" + "EXAMPLE" + "A" * 9, f'x = "{CLAVE}"  # {sec.MARCA_PERMITIR}', "texto normal sin nada"]
        for l in negativos:
            self.assertIsNone(sec.en_linea(l), l)

    def test_enmascara_valor(self):
        _, muestra = sec.en_linea(f'k = "{CLAVE}"')
        self.assertNotIn(CLAVE, muestra)

    def test_archivos_prohibidos(self):
        for r in (".env", ".env.production", "a/b/server.pem", "id_rsa", "x/credentials.json", "terraform.tfstate", ".npmrc"):
            self.assertTrue(sec.archivo_prohibido(r), r)
        for r in (".env.example", "app.py", "README.md", "id_rsa.pub", "config/settings.json"):
            self.assertFalse(sec.archivo_prohibido(r), r)


class TestEscaneo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        git(self.repo, "init", "-q")
        (self.repo / "ok.py").write_text("x = 1\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "base")

    def tearDown(self):
        self.tmp.cleanup()

    def cli(self, *a: str):
        return subprocess.run([sys.executable, "-X", "utf8", "-I", str(CLI), "--repo", str(self.repo), *a], capture_output=True, text=True)

    def test_limpio(self):
        self.assertEqual(self.cli("--historia").returncode, 0)

    def test_arbol_detecta_y_respeta_gitignore(self):
        (self.repo / "cfg.py").write_text(f'K = "{CLAVE}"\n')
        r = self.cli()
        self.assertEqual(r.returncode, 1)
        self.assertIn("cfg.py:1", r.stdout)
        self.assertNotIn(CLAVE, r.stdout)
        (self.repo / ".gitignore").write_text("cfg.py\n.env\n")
        (self.repo / ".env").write_text("A=1\n")
        self.assertEqual(self.cli().returncode, 0)

    def test_historia_encuentra_secreto_ya_borrado(self):
        (self.repo / "cfg.py").write_text(f'K = "{CLAVE}"\n')
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "mal")
        git(self.repo, "rm", "-q", "cfg.py")
        git(self.repo, "commit", "-qm", "borrado")
        self.assertEqual(self.cli().returncode, 0)          # el árbol ya está limpio…
        r = self.cli("--historia")                           # …pero el historial lo conserva
        self.assertEqual(r.returncode, 1)
        self.assertIn("HISTORIA", r.stdout)


class TestRutasDePrueba(unittest.TestCase):
    LINEA = 'password: "Passw0rd-real-looking"'

    def test_debil_se_ignora_en_pruebas_pero_no_fuera(self):
        for ruta in ("test/app.e2e-spec.ts", "src/users/users.service.spec.ts", "tests/test_api.py", "cypress/e2e/login.cy.ts", "app/__tests__/a.js", "pkg/x_test.go"):
            self.assertTrue(sec.es_ruta_de_prueba(ruta), ruta)
            self.assertIsNone(sec.en_linea(self.LINEA, ruta), ruta)
        for ruta in ("src/config.ts", "app/settings.py", "contest/a.py", "latest/x.ts"):
            self.assertFalse(sec.es_ruta_de_prueba(ruta), ruta)
            self.assertIsNotNone(sec.en_linea(self.LINEA, ruta), ruta)

    def test_los_fuertes_se_detectan_tambien_en_pruebas(self):
        self.assertIsNotNone(sec.en_linea(f'k = "{CLAVE}"', "test/app.e2e-spec.ts"))
        self.assertIsNotNone(sec.en_linea("ghp_" + "a" * 36, "tests/a.py"))


if __name__ == "__main__":
    unittest.main()
