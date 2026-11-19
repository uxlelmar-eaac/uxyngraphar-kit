"""1.5.25: la pestaña del panel nota reinicios, permisos perdidos y versiones nuevas (y se reconecta sola), ninguna
zona del Taller se queda en «Cargando…», la CLI no dice «quitado de la lista» si no estaba y, sin IA, el kit explica
qué opciones hay y dónde se configuran."""

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import subprocess
import unittest
from pathlib import Path

import _rutas  # noqa: F401
import cli
import ia_local
import repo
from test_panel_api import ConServidor
from test_quitar_y_taller_1_5_21 import ConProyecto

WEB = Path(__file__).resolve().parents[1] / "web"


class TestLatido(ConServidor):
    def test_latido_dice_pid_y_version(self):
        r = self.pedir("/api/latido", {})
        self.assertEqual(r["pid"], os.getpid())
        self.assertRegex(r["version"], r"^\d+\.\d+\.\d+$")
        self.assertTrue(r["activa"], "sin instalación, la activa es la del propio proceso")

    def test_sin_permiso_el_latido_es_403_abrir_de_nuevo(self):
        codigo, _ = self.error("/api/latido", {}, token="viejo-" + "x" * 30)
        self.assertEqual((codigo, self.ultimo_error.get("accion")), (403, "abrir_de_nuevo"))


class TestWebLatido(unittest.TestCase):
    def node(self, programa: str) -> str:
        if not shutil.which("node"):
            self.skipTest("sin node")
        r = subprocess.run(["node", "--input-type=module", "-e", programa], capture_output=True, text=True, encoding="utf-8",
                           cwd=WEB / "js", check=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_decidir_latido(self):
        programa = """
globalThis.document = { getElementById: () => null, createElement: () => ({}), addEventListener() {} };
globalThis.window = { addEventListener() {} };
globalThis.location = { hash: '', pathname: '/' };
const { decidirLatido } = await import('./api.js');
const m = { version: '1.5.25', fallos: 0, perdida: false, avisadaActiva: '' };
const ok = (version, activa) => ({ tipo: 'ok', estado: { version, activa: activa || version } });
const pasos = [
  decidirLatido(ok('1.5.25'), m),
  decidirLatido({ tipo: 'caido' }, m),
  decidirLatido({ tipo: 'caido' }, m),
  decidirLatido(ok('1.5.25'), m),
];
const m2 = { version: '1.5.25', fallos: 0, perdida: false, avisadaActiva: '' };
const sesion = [decidirLatido({ tipo: 'sin_sesion' }, m2), decidirLatido({ tipo: 'sin_sesion' }, m2), decidirLatido(ok('1.5.25'), m2)];
const m3 = { version: '1.5.24', fallos: 0, perdida: false, avisadaActiva: '' };
const version = [decidirLatido(ok('1.5.25'), m3)];
const m4 = { version: '1.5.24', fallos: 0, perdida: false, avisadaActiva: '' };
const activa = [decidirLatido(ok('1.5.24', '1.5.25'), m4), decidirLatido(ok('1.5.24', '1.5.25'), m4)];
console.log(JSON.stringify({ pasos, sesion, version, activa }));
"""
        datos = json.loads(self.node(programa))
        self.assertEqual(datos["pasos"], ["nada", "esperar", "caido", "recargar"], "un fallo suelto no tapa la UI; al volver, recarga")
        self.assertEqual(datos["sesion"], ["sin_sesion", "sin_sesion", "recargar"], "con el permiso nuevo de otra pestaña se reconecta sola")
        self.assertEqual(datos["version"], ["recargar"], "el proceso cambió de versión: recarga con el código nuevo")
        self.assertEqual(datos["activa"], ["version_nueva", "nada"], "la versión nueva instalada se avisa una sola vez")

    def test_la_regex_de_sin_ia(self):
        programa = """
globalThis.document = { getElementById: () => null, createElement: () => ({}), addEventListener() {} };
globalThis.window = { addEventListener() {} };
globalThis.location = { hash: '', pathname: '/' };
const { RE_SIN_IA } = await import('./vistas/agente-chat.js');
console.log(JSON.stringify([
  RE_SIN_IA.test('Añade una clave de IA en «Cuenta → IA y conexiones» para usar el agente.'),
  RE_SIN_IA.test('HTTP 500'),
]));
"""
        self.assertEqual(json.loads(self.node(programa)), [True, False])

    def test_el_panel_avisa_y_el_taller_no_se_queda_cargando(self):
        app = (WEB / "js" / "app.js").read_text(encoding="utf-8")
        for texto in ("cuandoPierdaSesion", "permiso viejo", "se reconecta sola", "Reiniciar el panel con la"):
            self.assertIn(texto, app)
        taller = (WEB / "js" / "vistas" / "creador-sistemas.js").read_text(encoding="utf-8")
        self.assertIn('"data-cargando": "1", texto: "Cargando sistemas…"', taller)
        self.assertIn("No se pudo cargar:", taller)
        self.assertIn("Reintentar", taller)
        for nombre in ("creador.js", "creador-inicio.js"):
            self.assertIn("ayudaSinIA(", (WEB / "js" / "vistas" / nombre).read_text(encoding="utf-8"))


class TestCliQuitar(ConProyecto):
    def test_ultima_linea_no_dice_quitado_si_no_estaba(self):
        r = self.repo_git("suelto")
        repo.instalar(r, ["pruebas-demo"])
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.main(["proyectos", "quitar", str(r), "--todo", "--si"]), 0)
        ultima = salida.getvalue().strip().splitlines()[-1]
        self.assertTrue(ultima.startswith("limpiado (no estaba en la lista):"), ultima)
        self.assertNotIn("quitado de la lista:", salida.getvalue())

    def test_ultima_linea_dice_quitado_si_estaba(self):
        r = self.proyecto("listado")
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.main(["proyectos", "quitar", str(r)]), 0)
        self.assertTrue(salida.getvalue().strip().splitlines()[-1].startswith("quitado de la lista:"))


class TestSinIA(unittest.TestCase):
    def test_ayuda_solo_cuando_falta_la_ia(self):
        ayuda = ia_local.ayuda_sin_ia("Añade una clave de IA en «Cuenta → IA y conexiones» para usar el agente.")
        for texto in ("Cuenta → IA y conexiones", "Ollama", "LM Studio", "Claude Code", "Codex", "Copilot", "Qwen Code",
                      "uxyngraphar creador modelos"):
            self.assertIn(texto, ayuda)
        self.assertEqual(ia_local.ayuda_sin_ia("HTTP 500"), "")

    def test_la_cli_imprime_la_ayuda(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            cli._imprimir_error(ValueError("Añade una clave de IA en «Cuenta → IA y conexiones» para usar el agente."))
        self.assertIn("error: Añade una clave de IA", err.getvalue())
        self.assertIn("Ollama", err.getvalue())


if __name__ == "__main__":
    unittest.main()
