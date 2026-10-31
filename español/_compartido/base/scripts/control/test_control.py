"""Pruebas de la configuración y la puerta de control de construcción."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import uxyngraphar_config as cfg  # noqa: E402
import puerta  # noqa: E402

CONTROLAR = AQUI.parent / "controlar.py"


def git(repo: Path, *a: str) -> None:
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=repo, check=True, capture_output=True)


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_defecto_sin_archivo(self):
        c, p = cfg.cargar(self.repo)
        self.assertEqual((c["limite_lineas"], p), (350, []))
        self.assertEqual(c["niveles"]["secretos"], "bloqueante")

    def test_detecta_pilas(self):
        (self.repo / "pyproject.toml").write_text("[project]\n")
        (self.repo / "src").mkdir()
        c = cfg.detectar(self.repo)
        self.assertEqual((c["pila"], c["codigo"]["raices"], c["codigo"]["extensiones"]), (["python"], ["src"], [".py"]))
        self.assertEqual(c["rol"], "servidor")

    def test_detecta_cliente_por_dependencia(self):
        (self.repo / "package.json").write_text('{"dependencies":{"react":"18"}}')
        self.assertEqual(cfg.detectar(self.repo)["rol"], "cliente")

    def test_archivo_corrupto_o_invalido(self):
        (self.repo / "docs").mkdir()
        (self.repo / "docs" / cfg.NOMBRE).write_text("{no json")
        c, p = cfg.cargar(self.repo)
        self.assertTrue(p and c["limite_lineas"] == 350)
        (self.repo / "docs" / cfg.NOMBRE).write_text(json.dumps({"niveles": {"lineas": "mal", "xx": "aviso"}}))
        _, p = cfg.cargar(self.repo)
        self.assertEqual(len(p), 2)

    def test_fusion_parcial_y_escribir_no_pisa(self):
        (self.repo / "docs").mkdir()
        (self.repo / "docs" / cfg.NOMBRE).write_text(json.dumps({"niveles": {"lineas": "bloqueante"}}))
        c, p = cfg.cargar(self.repo)
        self.assertEqual((p, c["niveles"]["lineas"], c["niveles"]["secretos"]), ([], "bloqueante", "bloqueante"))
        self.assertIsNone(cfg.escribir(self.repo, "docs", c))


class TestPuerta(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        git(self.repo, "init", "-q")
        (self.repo / "src").mkdir()
        (self.repo / "docs").mkdir()
        (self.repo / "docs" / cfg.NOMBRE).write_text(json.dumps({"codigo": {"raices": ["src"], "extensiones": [".py"]}, "niveles": {"lineas": "bloqueante", "nucleo": "apagado"}, "limite_lineas": 60}))
        (self.repo / "README.md").write_text("x")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "base")

    def tearDown(self):
        self.tmp.cleanup()

    def correr(self, *extra: str):
        return subprocess.run([sys.executable, "-X", "utf8", "-I", str(CONTROLAR), "--staged", *extra], cwd=self.repo, capture_output=True, text=True)

    def test_es_codigo(self):
        c, _ = cfg.cargar(self.repo)
        self.assertTrue(puerta.es_codigo("src/a.py", c, "docs"))
        self.assertFalse(puerta.es_codigo("docs/x.py", c, "docs"))
        self.assertFalse(puerta.es_codigo("src/a.txt", c, "docs"))
        self.assertFalse(puerta.es_codigo("tools/a.py", c, "docs"))
        self.assertFalse(puerta.es_codigo("src/migrations/0001.py", c, "docs"))

    def test_sin_cambios_ok(self):
        r = self.correr()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_limite_lineas_bloquea(self):
        (self.repo / "src" / "grande.py").write_text("x = 1\n" * 80)
        git(self.repo, "add", "-A")
        r = self.correr()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("[lineas]", r.stdout)
        self.assertIn("[instruccion]", r.stdout)   # además sin instrucción: aviso

    def test_exencion_de_lineas(self):
        c = json.loads((self.repo / "docs" / cfg.NOMBRE).read_text())
        c["exenciones_lineas"] = ["src/grande.py"]
        (self.repo / "docs" / cfg.NOMBRE).write_text(json.dumps(c))
        (self.repo / "src" / "grande.py").write_text("x = 1\n" * 80)
        git(self.repo, "add", "-A")
        self.assertEqual(self.correr().returncode, 0)

    def test_secreto_bloquea_y_placeholder_no(self):
        (self.repo / "src" / "a.py").write_text('KEY = "' + "AKIA" + "ABCDEFGHIJKLMNOP" + '"\n')
        git(self.repo, "add", "-A")
        r = self.correr()
        self.assertEqual(r.returncode, 1)
        self.assertIn("[secretos]", r.stdout)
        (self.repo / "src" / "a.py").write_text('password = "changeme-example-1"\npassword = os.environ["P"]\n')
        git(self.repo, "add", "-A")
        self.assertNotIn("[secretos]", self.correr().stdout)

    def test_archivo_env_y_llave_bloquean_pero_example_no(self):
        for nombre, bloquea in ((".env", True), ("deploy.pem", True), (".env.example", False), ("ruta/id_rsa", True), ("clave.pub", False)):
            (self.repo / Path(nombre).parent).mkdir(parents=True, exist_ok=True)
            (self.repo / nombre).write_text("A=1\n")
            git(self.repo, "add", "-f", nombre)
            r = self.correr()
            self.assertEqual("[secretos]" in r.stdout, bloquea, nombre + r.stdout)
            git(self.repo, "rm", "-q", "--cached", "-f", nombre)

    def test_secreto_en_docs_y_markdown_tambien_bloquea(self):
        (self.repo / "docs" / "nota.md").write_text("conexión: postgres://admin:S3cr3t-Pass@db.interno:5432/app\n")  # uxyngraphar:permitir-secreto
        git(self.repo, "add", "-A")
        r = self.correr()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("URL con credenciales", r.stdout)
        self.assertNotIn("S3cr3t", r.stdout)         # nunca se imprime el valor

    def test_secretos_permitir_de_la_config_exime_la_ruta(self):
        c = json.loads((self.repo / "docs" / cfg.NOMBRE).read_text())
        c["secretos_permitir"] = ["src/semillas/*"]
        (self.repo / "docs" / cfg.NOMBRE).write_text(json.dumps(c))
        (self.repo / "src" / "semillas").mkdir()
        (self.repo / "src" / "semillas" / "datos.py").write_text('password = "Tr0ub4dor-semilla"\n')
        (self.repo / "src" / "otro.py").write_text('password = "Tr0ub4dor-semilla"\n')
        git(self.repo, "add", "-A")
        r = self.correr()
        self.assertIn("src/otro.py", r.stdout)
        self.assertNotIn("semillas/datos.py: posible", r.stdout)

    def test_marca_permitir_secreto(self):
        (self.repo / "src" / "a.py").write_text('K = "' + "AKIA" + 'ABCDEFGHIJKLMNOP"  # uxyngraphar:permitir-secreto\n')
        git(self.repo, "add", "-A")
        self.assertNotIn("[secretos]", self.correr().stdout)

    def test_estricto_convierte_avisos_en_bloqueo(self):
        (self.repo / "src" / "a.py").write_text("x = 1\n")
        git(self.repo, "add", "-A")
        self.assertEqual(self.correr().returncode, 0)          # solo avisa (sin instrucción)
        self.assertEqual(self.correr("--estricto").returncode, 1)

    def test_instruccion_cubre_el_codigo(self):
        d = self.repo / "docs" / "05-instrucciones" / "02-en-progreso" / "2026-01-01"
        d.mkdir(parents=True)
        (d / "INS-1.md").write_text("---\nid: INS-1\nstatus: in-progress\nanclas_codigo:\n  - src/a.py\nespejo_actualizar:\n  - 50-sistema-integral/x.md\n---\n# x\n")
        (self.repo / "docs" / "50-sistema-integral").mkdir()
        (self.repo / "docs" / "50-sistema-integral" / "x.md").write_text("espejo\n")
        (self.repo / "src" / "a.py").write_text("x = 1\n")
        git(self.repo, "add", "-A")
        r = self.correr("--estricto")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_config_muestra_efectiva(self):
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(CONTROLAR), "--config"], cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(json.loads(r.stdout)["limite_lineas"], 60)


if __name__ == "__main__":
    unittest.main()
