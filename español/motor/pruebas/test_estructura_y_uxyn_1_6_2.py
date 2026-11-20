"""1.6.2: Mis sistemas enseña la estructura de cada sistema (carpetas y archivos) y el panel de uxyn es más limpio."""

from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path

import _rutas  # noqa: F401

WEB = Path(__file__).resolve().parents[1] / "web"
VISTAS = WEB / "js" / "vistas"

ENTORNO = """
globalThis.document = { getElementById: () => null, createElement: () => ({}), createElementNS: () => ({ setAttribute() {}, append() {} }), addEventListener() {} };
globalThis.window = { addEventListener() {} };
globalThis.localStorage = { getItem: () => null, setItem() {} };
globalThis.location = { hash: '', pathname: '/' };
const m = await import('./vistas/estructura-sistema.js');
"""


class TestEstructura(unittest.TestCase):
    def node(self, programa: str):
        if not shutil.which("node"):
            self.skipTest("sin node")
        r = subprocess.run(["node", "--input-type=module", "-e", ENTORNO + programa], capture_output=True, text=True,
                           encoding="utf-8", cwd=WEB / "js", check=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def test_cuenta_carpetas_anidadas_y_archivos(self):
        r = self.node("console.log(JSON.stringify(m.contarEstructura(['README.md', 'proceso/01.md', 'proceso/02.md',"
                      " 'skills/revisar/SKILL.md'])));")
        self.assertEqual(r, {"carpetas": 3, "archivos": 4})

    def test_describe_las_piezas_del_esqueleto(self):
        r = self.node("console.log(JSON.stringify(['LIMITES.md', 'proceso', 'skills', 'config'].map((k) => Boolean(m.QUE_ES[k]))));")
        self.assertEqual(r, [True, True, True, True])

    def test_mis_sistemas_ofrece_revisar_archivos_y_el_taller_abre_el_archivo(self):
        mis = (VISTAS / "mis-sistemas.js").read_text(encoding="utf-8")
        self.assertIn('"Revisar archivos"', mis)  # 1.6.3: lleva a la revisión a pantalla completa
        taller = (VISTAS / "creador-sistemas.js").read_text(encoding="utf-8")
        self.assertIn("params.archivo", taller)


class TestPanelUxyn(unittest.TestCase):
    def test_sin_textos_repetidos_ni_lista_vacia(self):
        js = (VISTAS / "creador.js").read_text(encoding="utf-8")
        self.assertNotIn("pistaModo", js)
        self.assertNotIn('"Sin conversaciones"', js)
        self.assertIn("chat-sugerencias", js)
        taller = (VISTAS / "creador-sistemas.js").read_text(encoding="utf-8")
        self.assertNotIn("Pídele que complete un paso", taller)


if __name__ == "__main__":
    unittest.main()
