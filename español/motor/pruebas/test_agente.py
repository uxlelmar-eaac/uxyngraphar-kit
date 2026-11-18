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

    def test_turno_envia_adjuntos_y_valida_limites(self):
        parche, llamadas = self._con([(200, {"conversacion": 4, "respuesta": "Creado", "borrador": "pagos"})])
        with parche:
            agente.turno("crea uno", adjuntos=[{"nombre": "idea.md", "contenido": "Pagos > 1000 €"}])
        self.assertEqual(llamadas[0][1]["adjuntos"], [{"nombre": "idea.md", "contenido": "Pagos > 1000 €"}])
        with self.assertRaisesRegex(ValueError, "demasiados"):
            agente.turno("x", adjuntos=[{"nombre": f"a{i}", "contenido": "x"} for i in range(agente.MAX_ADJUNTOS + 1)])
        with self.assertRaisesRegex(ValueError, "demasiado grandes"):
            agente.turno("x", adjuntos=[{"nombre": f"a{i}", "contenido": "x" * 90_000} for i in range(3)])
        with self.assertRaises(ValueError):
            agente.turno("x", adjuntos=[{"nombre": "a", "contenido": None}])

    def test_conversacion(self):
        parche, llamadas = self._con([(200, {"id": 4, "borrador": "pagos", "mensajes": []})])
        with parche:
            self.assertEqual(agente.conversacion(4)["borrador"], "pagos")
        self.assertEqual(llamadas[0][:3], ("/me/agente/conversaciones/4", None, "GET"))

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


class PruebasPanelAgente(unittest.TestCase):
    def test_un_sistema_nuevo_del_agente_se_trae_a_este_equipo(self):
        import creador
        import rutas_panel
        respuesta = {"conversacion": 4, "respuesta": "Creado", "borrador": "pagos", "propuestas": [1]}
        with mock.patch.object(agente, "turno", return_value=dict(respuesta)) as turno, \
                mock.patch.object(creador, "bajar", return_value={"accion": "nuevo"}) as bajar, \
                mock.patch.object(creador, "subir") as subir:
            r = rutas_panel._agente_turno({"mensaje": "crea", "adjuntos": [{"nombre": "a.md", "contenido": "x"}]})
        subir.assert_not_called()
        bajar.assert_called_once_with("pagos")
        self.assertEqual(r["traido"], "pagos")
        self.assertEqual(turno.call_args.args[4], [{"nombre": "a.md", "contenido": "x"}])

    def test_con_sistema_abierto_no_se_vuelve_a_traer(self):
        import creador
        import rutas_panel
        with mock.patch.object(agente, "turno", return_value={"borrador": "pagos"}), \
                mock.patch.object(creador, "bajar") as bajar, mock.patch.object(creador, "subir"):
            r = rutas_panel._agente_turno({"mensaje": "mejora", "id": "pagos"})
        bajar.assert_not_called()
        self.assertNotIn("traido", r)


if __name__ == "__main__":
    unittest.main()
