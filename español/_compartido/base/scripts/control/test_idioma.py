"""Pruebas de R-22 (control/idioma.py y su integración en controlar.py)."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import idioma  # noqa: E402
import uxyngraphar_config as cfgmod  # noqa: E402

CONTROLAR = AQUI.parent / "controlar.py"


def git(repo: Path, *a: str) -> None:
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=repo, check=True, capture_output=True)


class TestHeuristica(unittest.TestCase):
    def test_palabras(self):
        self.assertEqual(idioma.palabras("obtenerUserById"), ["obtener", "user", "by", "id"])
        self.assertEqual(idioma.palabras("HTTPServerError"), ["http", "server", "error"])
        self.assertEqual(idioma.palabras("retencion_fiscal"), ["retencion", "fiscal"])

    def test_no_ascii_es_fiable(self):
        f, _ = idioma.revisar_linea("src/a.ts", "const retenciónFiscal = 1;", set())
        self.assertTrue(f and "retenciónFiscal" in f[0])

    def test_mezclado_y_espanol_son_heuristicos(self):
        f, h = idioma.revisar_linea("src/a.ts", "function obtenerUserById(id) { return getUsuario(id) }", set())
        self.assertEqual(f, [])
        self.assertTrue(any("mezclado «obtenerUserById»" in x for x in h))
        self.assertTrue(any("getUsuario" in x for x in h))
        _, h = idioma.revisar_linea("src/a.py", "def calcular_saldo(cuenta):", set())
        self.assertTrue(any("en español «calcular_saldo»" in x for x in h))

    def test_ingles_limpio_no_se_senala(self):
        for linea in ("export function getUserById(id: string): User {", "def is_valid_email(value):", "const MAX_RETRY_COUNT = 3; // retry budget for flaky gateways",
                      'logger.info("payment declined")'):
            self.assertEqual(idioma.revisar_linea("src/a.ts", linea, set()), ([], []), linea)

    def test_cadenas_y_comentarios(self):
        f, h = idioma.revisar_linea("src/a.ts", 'throw new Error("No se encontró el usuario") // revisa si el pago es válido', set())
        self.assertEqual(f, [])   # acentos dentro de cadenas y comentarios no son identificadores
        self.assertTrue(any("texto en español" in x for x in h))
        self.assertTrue(any("comentario en español" in x for x in h))

    def test_tests_pueden_tener_datos_en_espanol(self):
        _, h = idioma.revisar_linea("src/__tests__/user.test.ts", 'const name = "José Pérez";', set())
        self.assertEqual(h, [])

    def test_glosario_permite_terminos(self):
        _, h = idioma.revisar_linea("src/a.ts", "const expedienteId = loadExpediente();", {"expediente"})
        self.assertEqual(h, [])
        _, h = idioma.revisar_linea("src/a.ts", "const cuentaId = 1;", {"expediente"})
        self.assertTrue(h)

    def test_marca_exime(self):
        self.assertEqual(idioma.revisar_linea("src/a.ts", "const año = 1; // uxyngraphar:permitir-idioma", set()), ([], []))

    def test_hash_solo_es_comentario_en_lenguajes_que_lo_usan(self):
        _, h = idioma.revisar_linea("src/a.ts", "this.#cacheSize = 10;", set())
        self.assertEqual(h, [])

    def test_mensajes_de_commit(self):
        self.assertEqual(idioma.revisar_mensaje("feat(billing): add refund endpoint\n\nbody"), [])
        self.assertEqual(idioma.revisar_mensaje("Merge branch 'main' into feat/x"), [])
        self.assertEqual(len(idioma.revisar_mensaje("agregué validación del pago")), 2)
        self.assertEqual(len(idioma.revisar_mensaje("fix: corrige el cálculo del saldo")), 1)
        self.assertEqual(len(idioma.revisar_mensaje("update stuff")), 1)

    def test_ramas(self):
        cfg = cfgmod.por_defecto()
        for ok in ("main", "feat/billing-add-refund", "fix/login-timeout", "release/2.0.0"):
            self.assertEqual(idioma.revisar_rama(ok, cfg), [], ok)
        for mal in ("nueva-funcion", "feat/AgregarPago", "feature/x"):
            self.assertTrue(idioma.revisar_rama(mal, cfg), mal)
        cfg["idioma"]["ramas"] = r"^feature/.+$"
        self.assertEqual(idioma.revisar_rama("feature/x", cfg), [])

    def test_glosario_desde_archivo(self):
        with tempfile.TemporaryDirectory() as t:
            g = Path(t) / "docs" / "00-nucleo" / "glosario-dominio.md"
            g.parent.mkdir(parents=True)
            g.write_text("| Término | Glosa |\n|---|---|\n| `retencion_fiscal` | tax withholding |\n| ejemplo | example |\n", encoding="utf-8")
            terms = idioma.glosario(Path(t), "docs", cfgmod.por_defecto())
            self.assertIn("retencion_fiscal", terms)
            self.assertIn("retencion", terms)
            self.assertNotIn("término", terms)


class TestConfigIdioma(unittest.TestCase):
    def test_defecto_y_validacion(self):
        c = cfgmod.por_defecto()
        self.assertEqual((c["idioma"]["artefactos"], c["niveles"]["idioma"], c["niveles"]["commits"]), ("en", "aviso", "aviso"))
        self.assertEqual(cfgmod.validar(c), [])
        c["idioma"].update({"artefactos": "es", "commits": "x", "legacy": "src/**", "ramas": "("})
        self.assertEqual(len(cfgmod.validar(c)), 4)


class TestPuertaIdioma(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        git(self.repo, "init", "-q", "-b", "main")
        (self.repo / "src").mkdir()
        (self.repo / "docs").mkdir()
        self.cfg = {"codigo": {"raices": ["src"], "extensiones": [".ts"]}, "niveles": {"nucleo": "apagado", "instruccion": "apagado", "espejo": "apagado"}}
        self.escribir_cfg()
        (self.repo / "README.md").write_text("x")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "chore: base")

    def tearDown(self):
        self.tmp.cleanup()

    def escribir_cfg(self):
        (self.repo / "docs" / cfgmod.NOMBRE).write_text(json.dumps(self.cfg))

    def correr(self, *extra: str):
        return subprocess.run([sys.executable, "-X", "utf8", "-I", str(CONTROLAR), "--staged", *extra], cwd=self.repo, capture_output=True, text=True)

    def test_aviso_por_defecto_y_bloqueo_configurable(self):
        (self.repo / "src" / "a.ts").write_text("const añoFiscal = obtenerUserById(1);\n", encoding="utf-8")
        git(self.repo, "add", "-A")
        r = self.correr()
        self.assertEqual(r.returncode, 0, r.stdout)          # por defecto solo avisa (adopción gradual)
        self.assertIn("[idioma]", r.stdout)
        self.cfg["niveles"]["idioma"] = "bloqueante"
        self.escribir_cfg()
        git(self.repo, "add", "-A")
        r = self.correr()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("ERROR [idioma] src/a.ts: identificador no-ASCII «añoFiscal»", r.stdout)
        self.assertIn("WARN [idioma] src/a.ts: identificador mezclado", r.stdout)   # lo heurístico nunca bloquea

    def test_legacy_solo_avisa(self):
        self.cfg["niveles"]["idioma"] = "bloqueante"
        self.cfg["idioma"] = {"legacy": ["src/viejo/**"]}
        self.escribir_cfg()
        (self.repo / "src" / "viejo").mkdir()
        (self.repo / "src" / "viejo" / "a.ts").write_text("const año = 1;\n", encoding="utf-8")
        git(self.repo, "add", "-A")
        r = self.correr()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("WARN [idioma]", r.stdout)

    def test_nombres_de_archivo_y_locales(self):
        self.cfg["niveles"]["idioma"] = "bloqueante"
        self.escribir_cfg()
        (self.repo / "src" / "facturación.ts").write_text("export const x = 1;\n", encoding="utf-8")
        (self.repo / "src" / "locales").mkdir()
        (self.repo / "src" / "locales" / "es.ts").write_text('export default { "errors.payment.declined": "Pago rechazado, inténtalo de nuevo" };\n', encoding="utf-8")
        git(self.repo, "add", "-A")
        r = self.correr()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("facturación.ts: nombre de archivo", r.stdout)
        self.assertNotIn("locales/es.ts", r.stdout)          # las traducciones no son código

    def test_docs_no_se_revisa(self):
        (self.repo / "docs" / "nota.md").write_text("Guía en español con acentos: dirección, sesión.\n", encoding="utf-8")
        git(self.repo, "add", "-A")
        self.assertNotIn("[idioma]", self.correr().stdout)

    def test_mensaje_de_commit(self):
        msg = self.repo / "MSG"
        msg.write_text("agregué el endpoint de reembolsos\n", encoding="utf-8")
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(CONTROLAR), "--mensaje", str(msg)], cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("[commits]", r.stdout)
        self.cfg["niveles"]["commits"] = "bloqueante"
        self.escribir_cfg()
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(CONTROLAR), "--mensaje", str(msg)], cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(r.returncode, 1, r.stdout)
        msg.write_text("feat(billing): add refund endpoint\n", encoding="utf-8")
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(CONTROLAR), "--mensaje", str(msg)], cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_ci_revisa_commits_del_rango(self):
        git(self.repo, "checkout", "-q", "-b", "feat/billing-refund")
        (self.repo / "src" / "a.ts").write_text("export const refundLimit = 3;\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "cambios varios del pago")
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(CONTROLAR), "--base", "main"], cwd=self.repo, capture_output=True, text=True)
        self.assertIn("[commits]", r.stdout)
        self.assertNotIn("rama", r.stdout)


if __name__ == "__main__":
    unittest.main()
