"""Límites y permisos en el núcleo (protocolo v3, ADR 0010): LIMITES.md, PERMISOS.md, «permisos» y `exigir`."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import _rutas  # noqa: F401
from _sistemas import completar
import catalogo
import entrada
import protecciones
import uxyn_permisos as permisos

base = catalogo.base
esp = catalogo.esp

SCRIPT_PROPIO = """#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "comun"))
import uxyn_base as base
import uxyn_permisos as permisos
SISTEMA = base.carpeta_sistema(Path(__file__).resolve().parent)
if __name__ == "__main__":
    permisos.exigir(SISTEMA, "scripts/publicacion.py " + sys.argv[1])
    print("hecho")
"""


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cat = Path(self.tmp.name)
        self.c = completar(catalogo.crear("pruebas-permisos", "Pruebas permisos", "", self.cat))

    def tearDown(self):
        self.tmp.cleanup()

    def manifiesto(self, **cambios) -> dict:
        m = base.leer_manifiesto(self.c)
        m.update(cambios)
        (self.c / base.MANIFIESTO).write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
        entrada.actualizar(self.c)
        return m

    def errores(self) -> list[str]:
        return esp.validar_sistema(self.c)


class TestNucleo(Base):
    def test_el_sistema_creado_trae_limites_y_permisos(self):
        self.assertEqual(self.errores(), [])
        self.assertIn("permisos", base.leer_manifiesto(self.c))
        texto = (self.c / base.PERMISOS).read_text(encoding="utf-8")
        for seccion in ("## El agente puede", "## Solo una persona", "## Rutas", "memorias.py aprobar"):
            self.assertIn(seccion, texto)

    def test_faltan_los_archivos_del_nucleo(self):
        for nombre in (base.LIMITES, base.PERMISOS):
            with self.subTest(nombre=nombre):
                texto = (self.c / nombre).read_text(encoding="utf-8")
                (self.c / nombre).unlink()
                self.assertIn(f"falta {nombre}", self.errores())
                (self.c / nombre).write_text(texto, encoding="utf-8")

    def test_crear_deja_marcadores_en_limites_y_permisos(self):
        nuevo = catalogo.crear("pruebas-marcadores", "Pruebas marcadores", "", self.cat)
        errores = esp.validar_sistema(nuevo)
        self.assertTrue(any(e.startswith("LIMITES.md: marcadores") for e in errores), errores)
        self.assertTrue(any(e.startswith("PERMISOS.md: marcadores") for e in errores), errores)

    def test_forma_de_limites(self):
        ruta = self.c / base.LIMITES
        texto = ruta.read_text(encoding="utf-8")
        ruta.write_text(texto.replace("## Cuándo detenerse y preguntar", "## Otra"), encoding="utf-8")
        self.assertTrue(any("Cuándo detenerse y preguntar" in e for e in self.errores()))
        ruta.write_text(texto.replace("1. Solo", "Solo"), encoding="utf-8")
        self.assertTrue(any("regla numerada" in e for e in self.errores()))

    def test_bloque_de_permisos_desfasado(self):
        m = base.leer_manifiesto(self.c)
        m["permisos"]["rutas"]["protegidas"] = ["reglas/**"]
        (self.c / base.MANIFIESTO).write_text(json.dumps(m), encoding="utf-8")
        self.assertTrue(any(e.startswith("PERMISOS.md: el bloque") for e in self.errores()))
        self.assertTrue(catalogo.indice_sistema("pruebas-permisos", self.cat))
        self.assertEqual(self.errores(), [])
        self.assertIn("`reglas/**`", (self.c / base.PERMISOS).read_text(encoding="utf-8"))

    def test_el_readme_lleva_siempre_el_paso_de_limites_y_permisos(self):
        texto = (self.c / base.ENTRADA).read_text(encoding="utf-8")
        self.assertIn("Límites y permisos: lee `$P/LIMITES.md`", texto)
        self.assertIn("`$P/PERMISOS.md`", texto)


class TestManifiesto(Base):
    def test_permisos_obligatorio_y_con_forma(self):
        m = base.leer_manifiesto(self.c)
        sin = {k: v for k, v in m.items() if k != "permisos"}
        self.assertTrue(any(e.startswith("permisos:") for e in base.validar_manifiesto(sin)))
        malos = [
            {"rutas": {"protegidas": ["/absoluta"]}},
            {"rutas": {"protegidas": ["../fuera"]}},
            {"rutas": {"otra": []}},
            {"acciones": {"agente": ["otra/cosa.sh"]}},
            {"acciones": {"agente": ["scripts/x.py publicar"], "solo_persona": ["scripts/x.py  publicar"]}},
            {"otra": {}},
        ]
        for permisos_malos in malos:
            with self.subTest(permisos=permisos_malos):
                self.assertTrue(base.validar_manifiesto({**m, "permisos": permisos_malos}))

    def test_campos_sueltos_y_pieza_limites_ya_no_valen(self):
        m = base.leer_manifiesto(self.c)
        self.assertTrue(any("permisos.rutas.protegidas" in e for e in base.validar_manifiesto({**m, "protegidos": ["x"]})))
        self.assertTrue(any("permisos.rutas.fuera_de_ia" in e for e in base.validar_manifiesto({**m, "fuera_de_ia": ["x"]})))
        piezas = [*m["piezas"], "limites"]
        self.assertTrue(any("núcleo" in e for e in base.validar_manifiesto({**m, "piezas": piezas})))

    def test_acciones_con_scripts_que_no_existen(self):
        m = base.leer_manifiesto(self.c)
        m["permisos"]["acciones"]["solo_persona"] = ["scripts/publicacion.py publicar"]
        self.manifiesto(permisos=m["permisos"])
        self.assertIn("permisos.acciones: no existe scripts/publicacion.py", self.errores())
        m["permisos"]["acciones"]["solo_persona"] = ["scripts/comun/fichas.py estado"]
        self.manifiesto(permisos=m["permisos"])
        self.assertEqual(self.errores(), [], "los de scripts/comun/ salen de la base")


class TestExigir(Base):
    def setUp(self):
        super().setUp()
        m = base.leer_manifiesto(self.c)
        m["permisos"]["acciones"] = {"agente": ["scripts/publicacion.py previa"], "solo_persona": ["scripts/publicacion.py publicar"]}
        self.m = self.manifiesto(permisos=m["permisos"])

    def test_solo_persona_incluye_lo_implicito(self):
        self.assertTrue(permisos.es_solo_persona(self.m, "scripts/comun/memorias.py aprobar MEM-1"))
        self.assertTrue(permisos.es_solo_persona(self.m, "scripts/publicacion.py publicar --ya"))
        self.assertFalse(permisos.es_solo_persona(self.m, "scripts/publicacion.py previa"))
        self.assertFalse(permisos.es_solo_persona(self.m, "scripts/publicacion.py publicarlo"))

    def test_exigir_para_al_agente_y_deja_a_la_persona(self):
        with mock.patch.dict(os.environ, {"CI": "1", base.VARIABLE_HUMANO: ""}):
            with self.assertRaises(PermissionError):
                permisos.exigir(self.c, "scripts/publicacion.py publicar")
            permisos.exigir(self.c, "scripts/publicacion.py previa")
        with mock.patch.dict(os.environ, {base.VARIABLE_HUMANO: "1"}):
            permisos.exigir(self.c, "scripts/publicacion.py publicar")

    def test_script_propio_con_exigir_desde_un_agente(self):
        construido = self.cat / "construido"
        construido.mkdir()
        (self.c / "scripts" / "publicacion.py").write_text(SCRIPT_PROPIO, encoding="utf-8")
        self.assertEqual(self.errores(), [])
        salida = catalogo.construir("pruebas-permisos", construido, self.cat)
        script = salida / "scripts" / "publicacion.py"
        entorno = {k: v for k, v in os.environ.items() if k != base.VARIABLE_HUMANO}
        r = subprocess.run([sys.executable, str(script), "publicar"], capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, env={**entorno, "CI": "1"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("solo una persona", r.stderr)
        r = subprocess.run([sys.executable, str(script), "previa"], capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, env={**entorno, "CI": "1"})
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_avisa_si_el_script_no_llama_a_exigir(self):
        (self.c / "scripts" / "publicacion.py").write_text("print('publica sin preguntar')\n", encoding="utf-8")
        self.assertTrue(any("nunca llama a exigir" in a for a in esp.avisos_sistema(self.c)))

    def test_verificar_comprueba_limites_y_permisos(self):
        (self.c / "scripts" / "publicacion.py").write_text(SCRIPT_PROPIO, encoding="utf-8")
        construido = self.cat / "construido"
        construido.mkdir()
        salida = catalogo.construir("pruebas-permisos", construido, self.cat)
        errores, avisos = permisos.validar(salida)
        self.assertEqual((errores, avisos), ([], []))
        (salida / base.PERMISOS).write_text("# Permisos\n", encoding="utf-8")
        self.assertTrue(any("bloque de permisos" in e for e in permisos.validar(salida)[0]))


class TestProtecciones(unittest.TestCase):
    def test_reglas_desde_permisos_rutas(self):
        m = {"id": "demo", "permisos": {"rutas": {"protegidas": ["reglas/**"], "fuera_de_ia": ["archivo/"]},
                                       "acciones": {"agente": [], "solo_persona": []}}}
        reglas = protecciones.reglas_deny([m])
        for regla in ("Edit(uxyngraphar/trabajo/demo/reglas/**)", "Write(uxyngraphar/trabajo/demo/reglas/**)",
                      "Read(uxyngraphar/trabajo/demo/archivo/)"):
            self.assertIn(regla, reglas)
        self.assertEqual(protecciones.rutas_fuera_de_ia([m]), ["uxyngraphar/trabajo/demo/archivo/"])


if __name__ == "__main__":
    unittest.main()
