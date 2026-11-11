"""Pruebas del generador de sistemas (GENERADOR.md): especificación, generación transaccional, pendientes y CLI en JSON."""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import _rutas  # noqa: F401
from _sistemas import completar
import catalogo
import cli
import especificacion as esp
import generador


def spec_completa(pid: str = "contratos-de-pago") -> dict:
    spec = generador.plantilla_spec(pid, "proceso")
    spec["fichas"] = {"contrato": {"inicial": "propuesta", "estados": {"propuesta": "pendientes", "aprobada": "completadas"},
                                   "solo_humano": ["aprobada"], "secciones": ["Partes", "Condiciones"]}}
    spec["ejemplos"] = [{"nombre": "caso-basico", "titulo": "Un contrato simple", "pedido": "Registrar un contrato.",
                         "recorrido": "preparar con accion-principal.", "resultado": "Una ficha CON en propuesta."}]
    spec["piezas_extra"] = ["pruebas"]
    return spec


class Base(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.cat = Path(self._t.name)
        completar(catalogo.crear("pruebas-demo", "Pruebas demo", "Sistema de prueba", self.cat))

    def tearDown(self):
        self._t.cleanup()

    def ocultas(self) -> list[str]:
        return [p.name for p in self.cat.iterdir() if p.name.startswith(".")]


class TestEspecificacion(Base):
    def test_plantilla_es_valida(self):
        self.assertEqual(generador.validar_spec(generador.plantilla_spec(), self.cat), {"errores": [], "avisos": []})

    def test_errores_antes_de_escribir(self):
        casos = {
            "titulo": ("titulo", "Pagos"),
            "familia": ("familia", "varias"),
            "derivar_a": ("fuera_de_alcance", [{"tema": "Otra cosa", "derivar_a": "no-existe-aqui"}]),
            "marcador": ("resumen", "{{rellenar}}"),
            "resuelve": ("skills", [{**generador.plantilla_spec()["skills"][0], "resuelve": ["otro-problema"]}]),
            "skills": ("proceso", [{**generador.plantilla_spec()["proceso"][0], "skills": ["no-existe"]}]),
            "piezas_extra": ("piezas_extra", ["proceso"]),
        }
        for nombre, (campo, valor) in casos.items():
            spec = generador.plantilla_spec()
            spec[campo] = valor
            self.assertTrue(generador.validar_spec(spec, self.cat)["errores"], nombre)
        spec = generador.plantilla_spec("pruebas-demo")
        spec["titulo"] = "Pruebas demo"
        self.assertTrue(any("ya existe" in e for e in generador.validar_spec(spec, self.cat)["errores"]))

    def test_avisos_de_diseno(self):
        spec = generador.plantilla_spec()
        spec["problemas"] += [{"id": f"problema-{n}", "descripcion": "Otro síntoma."} for n in ("uno", "dos", "tres", "cuatro", "cinco")]
        avisos = generador.validar_spec(spec, self.cat)["avisos"]
        self.assertTrue(any("generalista" in a for a in avisos))
        self.assertTrue(any("no lo cubre ninguna fase" in a for a in avisos))


class TestDesdeSpec(Base):
    def test_simular_no_escribe(self):
        r = generador.desde_spec(spec_completa(), aplicar=False, raiz=self.cat)
        self.assertEqual(r["errores"], [])
        self.assertFalse(r["aplicado"])
        self.assertIn("SISTEMA.md", r["archivos"])
        self.assertFalse((self.cat / "contratos-de-pago").exists())
        self.assertEqual(self.ocultas(), [])

    def test_aplicar_deja_un_sistema_valido_y_sin_marcadores(self):
        r = generador.desde_spec(spec_completa(), aplicar=True, raiz=self.cat)
        self.assertTrue(r["aplicado"], r["errores"])
        c = self.cat / "contratos-de-pago"
        self.assertEqual(esp.validar_sistema(c), [])
        m = esp.base.leer_manifiesto(c)
        self.assertEqual(m["piezas"], ["proceso", "skills", "plantillas", "ejemplos", "pruebas", "cambios"])
        self.assertIn("## Cuándo detenerse y preguntar", (c / esp.base.LIMITES).read_text(encoding="utf-8"))
        self.assertIn("## Solo una persona", (c / esp.base.PERMISOS).read_text(encoding="utf-8"))
        self.assertEqual(m["fichas"]["contrato"]["prefijo"], "CON")
        self.assertIn("## Partes", (c / "plantillas" / "contrato.md").read_text(encoding="utf-8"))
        p = generador.pendientes("contratos-de-pago", self.cat)
        self.assertTrue(p["listo"], p)
        self.assertEqual(p["marcadores"], [])
        self.assertEqual(self.ocultas(), [])
        otra = generador.desde_spec(spec_completa(), aplicar=True, raiz=self.cat)
        self.assertTrue(any("ya existe" in e for e in otra["errores"]))

    def test_spec_invalida_no_deja_rastro(self):
        spec = spec_completa()
        spec["proceso"][0]["resuelve"] = ["no-existe"]
        r = generador.desde_spec(spec, aplicar=True, raiz=self.cat)
        self.assertTrue(r["errores"])
        self.assertFalse(r["aplicado"])
        self.assertFalse((self.cat / "contratos-de-pago").exists())
        self.assertEqual(self.ocultas(), [])

    def test_error_de_nomenclatura_cruzada_no_aplica(self):
        spec = spec_completa()
        spec["activacion"] = ["pruebas demo"]
        r = generador.desde_spec(spec, aplicar=True, raiz=self.cat)
        self.assertTrue(any("activacion" in e for e in r["errores"]), r["errores"])
        self.assertFalse(r["aplicado"])
        self.assertEqual(self.ocultas(), [])


class TestPendientes(Base):
    def test_esqueleto_lista_marcadores_con_linea(self):
        catalogo.crear("pagos-de-proveedor", "Pagos de proveedor", "", self.cat)
        p = generador.pendientes("pagos-de-proveedor", self.cat)
        self.assertFalse(p["listo"])
        primero = p["marcadores"][0]
        self.assertEqual((primero["archivo"], primero["linea"]), ("SISTEMA.md", 3))
        self.assertIn("SISTEMA.md:3", p["siguiente"])
        self.assertFalse(any(x["archivo"].startswith("plantillas/") for x in p["marcadores"]))

    def test_sistema_completo_esta_listo(self):
        p = generador.pendientes("pruebas-demo", self.cat)
        self.assertTrue(p["listo"], p)
        self.assertEqual(p["errores"], [])


class TestCli(Base):
    def correr(self, *argv: str) -> tuple[int, str]:
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida), mock.patch.object(catalogo.esp, "CATALOGO", self.cat):
            codigo = cli.main(list(argv))
        return codigo, salida.getvalue()

    def test_flujo_completo_en_json(self):
        codigo, texto = self.correr("generar", "plantilla", "--id", "contratos-de-pago")
        self.assertEqual(codigo, 0)
        ruta = self.cat.parent / "spec.json"
        ruta.write_text(texto, encoding="utf-8")
        codigo, texto = self.correr("generar", "desde", str(ruta), "--json")
        self.assertEqual((codigo, json.loads(texto)["aplicado"]), (0, False))
        codigo, texto = self.correr("generar", "desde", str(ruta), "--aplicar", "--json")
        self.assertTrue(json.loads(texto)["aplicado"])
        codigo, texto = self.correr("generar", "pendientes", "contratos-de-pago", "--json")
        self.assertEqual((codigo, json.loads(texto)["listo"]), (0, True))
        codigo, texto = self.correr("validar", "contratos-de-pago", "--json")
        self.assertEqual((codigo, json.loads(texto)[0]["errores"]), (0, []))

    def test_crear_json_trae_pendientes(self):
        codigo, texto = self.correr("crear", "pagos-de-proveedor", "--titulo", "Pagos de proveedor", "--familia", "proceso", "--json")
        datos = json.loads(texto)
        self.assertEqual(codigo, 0)
        self.assertFalse(datos["pendientes"]["listo"])
        self.assertEqual(self.correr("generar", "pendientes", "pagos-de-proveedor")[0], 1)


if __name__ == "__main__":
    unittest.main()
