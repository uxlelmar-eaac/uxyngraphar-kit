"""Agente del Creador desde el kit: turnos, propuestas y decidir contra un servidor simulado (sin red)."""

from __future__ import annotations

import unittest
from unittest import mock

import _rutas  # noqa: F401
import agente
import remoto


class PruebasAgente(unittest.TestCase):
    def _con(self, respuestas):
        llamadas = []

        def falso(ruta, cuerpo=None, metodo="POST", con_sesion=False, segundos=0):
            llamadas.append((ruta, cuerpo, metodo, con_sesion))
            return respuestas.pop(0)

        return mock.patch.object(remoto, "_pedir_json", side_effect=falso), llamadas

    def test_turno_envia_mensaje_borrador_y_conversacion(self):
        parche, llamadas = self._con([(200, {"conversacion": 3, "respuesta": "Hola", "acciones": [], "propuestas": []})])
        with parche:
            r = agente.turno("  hola  ", 3, "revision-de-seguridad")
        self.assertEqual(r["respuesta"], "Hola")
        ruta, cuerpo, metodo, con_sesion = llamadas[0]
        self.assertEqual((ruta, metodo, con_sesion), ("/me/agente/turno", "POST", True))
        self.assertEqual(cuerpo, {"mensaje": "hola", "conversacion": 3, "borrador": "revision-de-seguridad"})

    def test_turno_valida_entrada(self):
        with self.assertRaises(ValueError):
            agente.turno("   ")
        with self.assertRaises(ValueError):
            agente.turno("hola", borrador="../fuera")

    def test_errores_del_servidor(self):
        parche, _ = self._con([(401, {"message": "sin sesión"}), (429, {"message": "límite diario"})])
        with parche:
            with self.assertRaises(PermissionError):
                agente.turno("hola")
            with self.assertRaisesRegex(remoto.SinServidor, "límite diario"):
                agente.turno("hola")

    def test_propuestas_y_decidir(self):
        lista = [{"id": 9, "titulo": "Rellenar", "archivos": [{"ruta": "SISTEMA.md", "estado": "pendiente"}]}]
        parche, llamadas = self._con([(200, lista), (404, {}), (200, {"id": 9, "estado": "ACCEPTED"})])
        with parche:
            self.assertEqual(agente.propuestas("contratos"), lista)
            self.assertEqual(agente.propuestas("otro"), [])
            r = agente.decidir("contratos", 9, ["SISTEMA.md"], [])
        self.assertEqual(r["estado"], "ACCEPTED")
        self.assertEqual(llamadas[0][:3], ("/me/creador/borradores/contratos/propuestas", None, "GET"))
        self.assertEqual(llamadas[2][0], "/me/creador/borradores/contratos/propuestas/9")
        self.assertEqual(llamadas[2][1], {"aceptar": ["SISTEMA.md"], "rechazar": []})


if __name__ == "__main__":
    unittest.main()
