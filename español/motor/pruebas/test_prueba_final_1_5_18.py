"""Fallos vistos al crear un sistema desde el panel (Taller) con la 1.5.18, como una persona normal."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import _rutas  # noqa: F401
import catalogo

VISTAS = Path(__file__).resolve().parents[1] / "web" / "js" / "vistas"


class TestPlantillaDelNucleo(unittest.TestCase):
    def test_sistemas_complementarios_no_se_cita_a_si_mismo(self):
        with tempfile.TemporaryDirectory() as t:
            c = catalogo.crear("revision-de-codigo", "Revisión de código", "", Path(t), familia="codigo")
            texto = (c / "SISTEMA.md").read_text(encoding="utf-8")
            complementarios = texto.split("## Sistemas complementarios", 1)[1]
            self.assertNotIn("revision-de-codigo", complementarios)
            self.assertIn("{{", complementarios, "sigue siendo un hueco por rellenar")


def _funciones_del_formulario() -> str:
    js = (VISTAS / "creador-editor.js").read_text(encoding="utf-8")
    inicio = js.index("  const sinTildes = ")
    fin = js.index("  const separar = ", inicio)
    return js[inicio:fin]


class TestFormularioLoBasico(unittest.TestCase):
    def test_ids_y_frases_de_activacion(self):
        if not shutil.which("node"):
            self.skipTest("sin node")
        casos = ["Errores y regresiones que una revisión atenta habría detectado",
                 "Comentarios de revisión vagos que no dicen qué cambiar ni por qué", "Corto", "x" * 60]
        frases = ["revisar un PR", "Revisión, de código!", "revision-de-codigo", "foo - bar"]
        programa = _funciones_del_formulario() + (
            f"console.log(JSON.stringify({{ids: {json.dumps(casos)}.map((t, i) => slug(t, i)),"
            f" frases: {json.dumps(frases)}.map(frase)}}));")
        with tempfile.TemporaryDirectory() as t:
            guion = Path(t) / "formulario.js"
            guion.write_text(programa, encoding="utf-8")
            r = subprocess.run(["node", str(guion)], capture_output=True, text=True, encoding="utf-8", check=True)
        datos = json.loads(r.stdout)
        self.assertEqual(datos["ids"][:3], ["errores-y-regresiones-que-una-revision", "comentarios-de-revision-vagos-que-no", "corto"])
        self.assertEqual(len(datos["ids"][3]), 40)
        self.assertTrue(all(len(i) <= 40 and not i.endswith("-") for i in datos["ids"]))
        self.assertEqual(datos["frases"], ["revisar un pr", "revision de codigo", "revision-de-codigo", "foo-bar"])
        frase = re.compile(r"^[a-z0-9]+(?:[ -][a-z0-9]+)*$")   # nomenclatura.FRASE
        self.assertTrue(all(frase.match(f) for f in datos["frases"]))

    def test_activacion_se_normaliza_al_guardar(self):
        js = (VISTAS / "creador-editor.js").read_text(encoding="utf-8")
        self.assertIn('activacion.value.split(",").map(frase)', js)


class TestTallerTrasInstalar(unittest.TestCase):
    def test_instalar_en_proyecto_refresca_la_franja(self):
        js = (VISTAS / "creador-sistemas.js").read_text(encoding="utf-8")
        tramo = js[js.index("await instalarEnProyecto(id"):]
        tramo = tramo[:tramo.index("}, {")]
        self.assertLess(tramo.index("cache.proyectos = null"), tramo.index("await pintarFranjas()"))


if __name__ == "__main__":
    unittest.main()
