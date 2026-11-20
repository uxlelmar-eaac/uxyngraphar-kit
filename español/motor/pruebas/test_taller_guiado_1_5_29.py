"""1.5.29: el Taller es una ruta guiada de cinco pasos (Propósito → Reglas → Flujo y piezas → Probar → Entregar).

La pantalla anterior apilaba origen, ciclo, una acción suelta y la barra de salida antes de llegar al sistema, y no
decía qué hacer a continuación. Ahora cada hueco del validador cae en su paso, la ruta recomienda el siguiente y
«Ahora» ofrece una sola acción."""

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
globalThis.sessionStorage = globalThis.localStorage;
globalThis.location = { hash: '', pathname: '/' };
const m = await import('./vistas/creador-sistemas.js');
const resumen = (r) => [r.recomendado, Object.fromEntries(Object.entries(r.pasos).map(([k, v]) => [k, [v.hecho, v.huecos, v.problemas.length]]))];
"""


class TestRutaGuiada(unittest.TestCase):
    def node(self, programa: str):
        if not shutil.which("node"):
            self.skipTest("sin node")
        r = subprocess.run(["node", "--input-type=module", "-e", ENTORNO + programa], capture_output=True, text=True,
                           encoding="utf-8", cwd=WEB / "js", check=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def test_cinco_pasos_en_orden(self):
        self.assertEqual(self.node("console.log(JSON.stringify(m.PASOS.map((p) => p.id)));"),
                         ["proposito", "reglas", "piezas", "probar", "entregar"])

    def test_cada_archivo_en_su_paso(self):
        r = self.node("console.log(JSON.stringify(['sistema.json', 'README.md', 'LIMITES.md', 'PERMISOS.md', 'prompts/agente.md']"
                      ".map(m.pasoDeArchivo)));")
        self.assertEqual(r, ["proposito", "proposito", "reglas", "reglas", "piezas"])

    def test_errores_del_validador_van_a_su_archivo(self):
        r = self.node("console.log(JSON.stringify(['nomenclatura: README.md: la primera línea', 'activacion: debe incluir el id',"
                      " 'LIMITES.md: marcadores sin rellenar', 'algo general'].map(m.archivoDeError)));")
        self.assertEqual(r, ["README.md", "sistema.json", "LIMITES.md", None])

    def test_recomienda_el_primer_paso_con_huecos(self):
        r = self.node("""console.log(JSON.stringify(resumen(m.resolverPasos({ pendientes: { listo: false,
          errores: ['LIMITES.md: marcadores sin rellenar ({{a}})'],
          marcadores: [{ archivo: 'LIMITES.md', linea: 5, marcador: '{{a}}' }, { archivo: 'proceso/cerrar.md', linea: 2, marcador: '{{b}}' }] } }))));""")
        self.assertEqual(r[0], "reglas")
        self.assertEqual(r[1]["proposito"], [True, 0, 0])
        self.assertEqual(r[1]["reglas"], [False, 1, 0], "los marcadores no se cuentan dos veces")
        self.assertEqual(r[1]["piezas"], [False, 1, 0])

    def test_listo_lleva_a_entregar_y_en_uso_lo_marca(self):
        r = self.node("""console.log(JSON.stringify([
          resumen(m.resolverPasos({ pendientes: { listo: true, errores: [], marcadores: [] } })),
          resumen(m.resolverPasos({ pendientes: { listo: true, errores: [], marcadores: [] }, propuestas: 2 })),
          resumen(m.resolverPasos({ pendientes: { listo: true, errores: [], marcadores: [] }, enProyecto: ['web'] })),
          resumen(m.resolverPasos({}))]));""")
        self.assertEqual(r[0][0], "entregar")
        self.assertEqual(r[1][0], "probar", "con cambios de uxyn sin revisar no está listo para entregar")
        self.assertTrue(r[2][1]["entregar"][0])
        self.assertEqual(r[3][0], "proposito", "sin validador no se da nada por hecho")


class TestPantallaDelTaller(unittest.TestCase):
    def setUp(self):
        self.js = (VISTAS / "creador-sistemas.js").read_text(encoding="utf-8")

    def test_sin_bandas_antiguas_y_una_sola_salida(self):
        for viejo in ("franjaOrigen", "carrilCiclo", "plantillaNuevo", "taller-salida-barra"):
            self.assertNotIn(viejo, self.js)
        for texto in ("Instalar en proyecto", "Descargar .zip", "Guardar en la web", "Publicar"):
            self.assertIn(texto, self.js)

    def test_abrir_un_archivo_lleva_a_su_paso(self):
        self.assertIn("alPedirSeccion", self.js)
        editor = (VISTAS / "creador-editor.js").read_text(encoding="utf-8")
        self.assertIn("alPedirSeccion ? alPedirSeccion(s, rel) : elegirPestana(s)", editor)

    def test_el_simulador_se_abre_desde_probar(self):
        chat = (VISTAS / "creador.js").read_text(encoding="utf-8")
        self.assertIn("raiz.ponerModo", chat)
        self.assertIn('chatNodo?.ponerModo?.("simulador")', self.js)


if __name__ == "__main__":
    unittest.main()
