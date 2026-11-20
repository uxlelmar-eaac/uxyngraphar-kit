"""1.6.3: revisión de archivos a pantalla completa con notas, resaltados y «Mejorar» de un fragmento.

Las anotaciones son de la persona y viven fuera del sistema (`.anotaciones.json` del catálogo): no cambian su
validación ni su zip. uxyn las recibe en un pedido con el mismo texto en el kit y en la web."""

from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path
from unittest import mock

import _rutas  # noqa: F401
import anotaciones
import catalogo
import ia_local
from test_panel_api import ConServidor

WEB = Path(__file__).resolve().parents[1] / "web"


class TestAnotacionesPanel(ConServidor):
    def test_crear_listar_resolver_y_borrar(self):
        texto = catalogo.leer_archivo("pruebas-demo", "LIMITES.md")
        cita = texto.strip().splitlines()[0]
        inicio = texto.index(cita)
        a = self.pedir("/api/anotaciones/crear", {"id": "pruebas-demo", "archivo": "LIMITES.md", "tipo": "resaltado",
                                                    "cita": cita, "inicio": inicio, "fin": inicio + len(cita)})
        n = self.pedir("/api/anotaciones/crear", {"id": "pruebas-demo", "archivo": "LIMITES.md", "tipo": "nota",
                                                    "cita": cita, "inicio": inicio, "fin": inicio + len(cita), "nota": "Más concreto"})
        lista = self.pedir("/api/anotaciones?id=pruebas-demo")
        self.assertEqual([x["tipo"] for x in lista], ["resaltado", "nota"])
        self.assertEqual(self.pedir("/api/anotaciones/cambiar", {"id": "pruebas-demo", "anotacion": a["id"], "estado": "resuelta"})["estado"], "resuelta")
        self.pedir("/api/anotaciones/borrar", {"id": "pruebas-demo", "anotacion": n["id"]})
        self.assertEqual(len(self.pedir("/api/anotaciones?id=pruebas-demo")), 1)
        # Fuera del sistema: no aparece entre sus archivos.
        self.assertNotIn(".anotaciones.json", self.pedir("/api/catalogo/archivos?id=pruebas-demo"))
        self.assertTrue((self.cat / anotaciones.ARCHIVO).is_file())

    def test_rechaza_lo_que_no_vale(self):
        base = {"id": "pruebas-demo", "archivo": "LIMITES.md", "cita": "x", "inicio": 0, "fin": 1}
        self.assertEqual(self.error("/api/anotaciones/crear", {**base, "tipo": "otro"})[0], 400)
        self.assertEqual(self.error("/api/anotaciones/crear", {**base, "tipo": "nota"})[0], 400, "una nota sin texto no sirve")
        self.assertEqual(self.error("/api/anotaciones/crear", {**base, "tipo": "resaltado", "archivo": "../x.md"})[0], 400)
        self.assertEqual(self.error("/api/anotaciones/crear", {**base, "tipo": "resaltado", "id": "no-existe"})[0], 400)

    def test_mejorar_fragmento_usa_la_ia_de_la_cuenta_con_uxyn(self):
        with mock.patch.object(ia_local, "completar", return_value={"texto": "Nuevo texto", "modelo": "m", "proveedor": "servidor"}) as c:
            r = self.pedir("/api/creador/mejorar-fragmento", {"id": "pruebas-demo", "rel": "LIMITES.md", "fragmento": "algo",
                                                              "proveedor": "agente"})
        self.assertEqual(r["propuesta"], "Nuevo texto")
        self.assertEqual(c.call_args.args[0], "servidor")
        self.assertIn("=== Fragmento que debes reescribir ===\nalgo", c.call_args.args[1][0]["content"])


class TestPedidoYTramos(unittest.TestCase):
    NOTAS = [{"archivo": "LIMITES.md", "tipo": "nota", "cita": "a  b", "nota": "Más", "estado": "abierta"},
             {"archivo": "SISTEMA.md", "tipo": "resaltado", "cita": "c", "estado": "abierta"},
             {"archivo": "X.md", "tipo": "nota", "cita": "d", "nota": "no", "estado": "resuelta"}]

    def node(self, programa: str):
        if not shutil.which("node"):
            self.skipTest("sin node")
        r = subprocess.run(["node", "--input-type=module", "-e", "const m = await import('./vistas/anotaciones-texto.js');\n" + programa],
                           capture_output=True, text=True, encoding="utf-8", cwd=WEB / "js", check=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def test_el_pedido_para_uxyn_es_el_mismo_en_python_y_en_el_panel(self):
        js = self.node(f"console.log(JSON.stringify(m.pedidoParaUxyn({json.dumps(self.NOTAS)})));")
        self.assertEqual(js, anotaciones.pedido_para_uxyn(self.NOTAS))
        self.assertIn("- LIMITES.md: «a b» → nota: Más", js)
        self.assertNotIn("X.md", js, "las resueltas no se piden")
        self.assertEqual(anotaciones.pedido_para_uxyn([]), "")

    def test_tramos_vuelve_a_encontrar_la_cita_si_el_texto_cambio(self):
        r = self.node("""console.log(JSON.stringify(m.tramos('hola mundo y adiós', [
          { id: 'a', cita: 'mundo', inicio: 0, fin: 5 }, { id: 'b', cita: 'no está' }, { id: 'c', cita: 'adiós', inicio: 13, fin: 18 }])
          .map((t) => [t.texto, t.anotacion && t.anotacion.id])));""")
        self.assertEqual(r, [["hola ", None], ["mundo", "a"], [" y ", None], ["adiós", "c"]])


class TestPantalla(unittest.TestCase):
    def test_vista_registrada_y_tres_herramientas(self):
        app = (WEB / "js" / "app.js").read_text(encoding="utf-8")
        self.assertIn('import * as revision from "./vistas/revision.js"', app)
        js = (WEB / "js" / "vistas" / "revision.js").read_text(encoding="utf-8")
        for texto in ('"Mejorar"', '"Añadir nota"', '"Resaltar"', "/api/creador/mejorar-fragmento", '"Pedir a uxyn que use mis notas"'):
            self.assertIn(texto, js)
        taller = (WEB / "js" / "vistas" / "creador-sistemas.js").read_text(encoding="utf-8")
        self.assertIn('params.pedir === "notas"', taller)


if __name__ == "__main__":
    unittest.main()
