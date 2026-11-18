"""Pruebas de la organización de «Mis proyectos»: carpetas, etiquetas y orden manual (organizacion.json)."""

from __future__ import annotations

import json
import unittest

import _rutas  # noqa: F401
import organizacion
import proyectos
from test_panel_api import ConServidor
from test_proyectos import Entorno


class TestOrganizacion(Entorno):
    def setUp(self):
        super().setUp()
        self.a, self.b, self.c = (str(self.repo_git("trabajo", n)) for n in ("alfa", "beta", "gamma"))
        proyectos.agregar([self.a, self.b, self.c])

    def test_sin_archivo_hay_una_organizacion_vacia(self):
        self.assertEqual(organizacion.leer(), {"formato": 1, "carpetas": [], "etiquetas": [], "proyectos": {}, "orden": []})

    def test_carpetas_mover_y_ordenar(self):
        org = organizacion.crear_carpeta("  Clientes  ", "verde")
        cid = org["carpetas"][0]["id"]
        self.assertEqual(org["carpetas"][0]["nombre"], "Clientes")
        with self.assertRaises(FileExistsError):
            organizacion.crear_carpeta("clientes")
        with self.assertRaises(ValueError):
            organizacion.crear_carpeta("x", "morado")
        org = organizacion.mover([self.c, self.a], cid)
        self.assertEqual(org["proyectos"][self.c]["carpeta"], cid)
        self.assertEqual(org["orden"].index(self.c) + 1, org["orden"].index(self.a), "se mueven en el orden pedido")
        org = organizacion.mover([self.b], cid, antes=self.c)
        self.assertEqual([r for r in org["orden"] if org["proyectos"].get(r, {}).get("carpeta") == cid], [self.b, self.c, self.a])
        otra = organizacion.crear_carpeta("Personales")["carpetas"][1]["id"]
        org = organizacion.ordenar_carpetas([otra, cid])
        self.assertEqual([c["nombre"] for c in org["carpetas"]], ["Personales", "Clientes"])
        org = organizacion.cambiar_carpeta(cid, nombre="Trabajo", color="rojo")
        self.assertEqual((org["carpetas"][1]["nombre"], org["carpetas"][1]["color"]), ("Trabajo", "rojo"))
        org = organizacion.borrar_carpeta(cid)
        self.assertEqual(org["proyectos"], {}, "sus proyectos pasan a «Sin carpeta»")
        self.assertTrue(all(proyectos.registrado(r) for r in (self.a, self.b, self.c)))

    def test_etiquetas(self):
        org = organizacion.etiquetar([self.a, self.b], "urgente")   # se crea al ponerla
        self.assertEqual([e["nombre"] for e in org["etiquetas"]], ["urgente"])
        self.assertEqual(org["proyectos"][self.a]["etiquetas"], ["urgente"])
        org = organizacion.poner_etiquetas(self.a, ["URGENTE", "cliente"])
        self.assertEqual(org["proyectos"][self.a]["etiquetas"], ["urgente", "cliente"])
        org = organizacion.cambiar_etiqueta("urgente", nuevo="prisa", color="naranja")
        self.assertEqual(org["proyectos"][self.b]["etiquetas"], ["prisa"])
        org = organizacion.etiquetar([self.b], "prisa", poner=False)
        self.assertNotIn(self.b, org["proyectos"])
        org = organizacion.borrar_etiqueta("cliente")
        self.assertEqual(org["proyectos"][self.a]["etiquetas"], ["prisa"])
        with self.assertRaises(FileNotFoundError):
            organizacion.etiquetar([self.a], "no-existe", poner=False)

    def test_solo_proyectos_registrados_y_archivo_roto(self):
        with self.assertRaises(ValueError):
            organizacion.etiquetar([str(self.t)], "x")
        (self.t / "casa").mkdir(exist_ok=True)
        (self.t / "casa" / organizacion.ARCHIVO).write_text(json.dumps({"carpetas": [{"id": "c-1", "nombre": "A", "color": "??"}, "basura"],
            "etiquetas": [{"nombre": "x"}, {"nombre": "X"}], "proyectos": {self.a: {"carpeta": "c-9", "etiquetas": ["x", "y"]}}}),
            encoding="utf-8")
        org = organizacion.leer()
        self.assertEqual(org["carpetas"], [{"id": "c-1", "nombre": "A", "color": "oro"}])
        self.assertEqual(org["etiquetas"], [{"nombre": "x", "color": "gris"}])
        self.assertEqual(org["proyectos"], {self.a: {"carpeta": None, "etiquetas": ["x"]}})

    def test_quitar_de_la_lista_olvida_su_organizacion(self):
        organizacion.etiquetar([self.a], "x")
        proyectos.quitar(self.a)
        organizacion.olvidar(self.a)
        self.assertNotIn(self.a, organizacion.leer()["proyectos"])


class TestOrganizacionApi(ConServidor):
    def test_rutas(self):
        a = str(self.repo_git("trabajo", "alfa"))
        self.pedir("/api/proyectos/agregar", {"rutas": [a]})
        org = self.pedir("/api/organizacion/carpeta", {"accion": "crear", "nombre": "Clientes"})
        cid = org["carpetas"][0]["id"]
        self.pedir("/api/organizacion/mover", {"rutas": [a], "carpeta": cid})
        self.pedir("/api/organizacion/etiquetar", {"rutas": [a], "etiqueta": "urgente"})
        org = self.pedir("/api/organizacion")
        self.assertEqual(org["proyectos"][a], {"carpeta": cid, "etiquetas": ["urgente"]})
        codigo, _ = self.error("/api/organizacion/carpeta", {"accion": "volar"})
        self.assertEqual(codigo, 400)
        self.pedir("/api/proyectos/quitar", {"ruta": a})
        self.assertEqual(self.pedir("/api/organizacion")["proyectos"], {})


if __name__ == "__main__":
    unittest.main()
