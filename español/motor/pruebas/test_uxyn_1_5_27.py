"""uxyn 2 en el kit (1.5.27): contrato compartido con el backend y la web, turno en vivo (SSE) con reserva por sondeo,
códigos de error públicos, tarjeta de cambios y aviso sin IA en el panel."""

from __future__ import annotations

import io
import json
import shutil
import subprocess
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

import _rutas  # noqa: F401
import agente
import especificacion as esp
import remoto
import rutas_panel

AQUI = Path(__file__).resolve().parent
WEB = AQUI.parent / "web"
CONTRATO = json.loads((AQUI / "contrato-uxyn.json").read_text(encoding="utf-8"))


def _sse(eventos, comentarios=True, crlf=False) -> list[bytes]:
    fin = "\r\n" if crlf else "\n"
    lineas = [f": abierto{fin}", fin] if comentarios else []
    for e in eventos:
        lineas += [f"data: {json.dumps(e, ensure_ascii=False)}{fin}", fin]
        if comentarios:
            lineas += [f": sigo{fin}", fin]
    return [x.encode("utf-8") for x in lineas]


class _Respuesta:
    def __init__(self, lineas, tipo="text/event-stream; charset=utf-8"):
        self.lineas = lineas
        self.headers = {"Content-Type": tipo}

    def __iter__(self):
        return iter(self.lineas)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class TestContrato(unittest.TestCase):
    def test_version_y_codigos_coinciden_con_el_contrato(self):
        self.assertEqual(agente.CONTRATO, CONTRATO["version"])
        self.assertEqual(list(agente.CODIGOS_ERROR), CONTRATO["codigos_error"])

    def test_piezas_del_esqueleto_existen_en_el_kit(self):
        propias = {"nucleo", "prompts", "config"}
        for pieza in CONTRATO["esqueleto"]:
            self.assertTrue(pieza in propias or pieza in esp.base.PIEZAS, pieza)

    def test_eventos_del_contrato_dan_el_resultado_y_el_progreso(self):
        agente._PROGRESO_LOCAL.clear()
        eventos = list(agente.eventos_sse(_sse(CONTRATO["ejemplo_eventos"], crlf=True)))
        self.assertEqual(eventos, CONTRATO["ejemplo_eventos"])
        r = agente.resultado_de_eventos(iter(eventos), "turno-123456")
        self.assertEqual(r["conversacion"], 12)
        cambios = [c for a in r["acciones"] for c in a.get("cambios") or []]
        self.assertEqual({c["ruta"] for c in cambios}, {"prompts/agente.md", "config/limites.json"})
        with mock.patch.object(remoto, "_pedir_json") as servidor:
            p = agente.progreso("turno-123456")
        servidor.assert_not_called()
        self.assertTrue(p["en_vivo"])
        self.assertEqual([s["estado"] for s in p["pasos"]], ["ok", "ok"])

    def test_error_del_contrato_es_agente_error_con_codigo(self):
        error = CONTRATO["ejemplo_error"]
        with self.assertRaises(agente.AgenteError) as ctx:
            agente.resultado_de_eventos(iter([{"tipo": "inicio"}, error]))
        self.assertEqual(ctx.exception.codigo, "SIN_IA")
        self.assertEqual(rutas_panel.codigo_error(ctx.exception), ("uxyn_sin_ia", "configurar_ia"))
        self.assertEqual(rutas_panel.estado_http(ctx.exception), 400)
        self.assertEqual(rutas_panel.codigo_error(agente.AgenteError("LIMITE", "x")), ("uxyn_limite", "reintentar"))
        self.assertEqual(agente.AgenteError("RARO", "x").codigo, "INTERNO")

    def test_flujo_cortado_sin_resultado(self):
        with self.assertRaises(agente.AgenteNoDisponible):
            agente.resultado_de_eventos(iter([{"tipo": "fase", "fase": "pensando"}]))


class TestTurnoEnVivo(unittest.TestCase):
    def setUp(self):
        agente._ESTADO["sin_stream"] = False
        agente._PROGRESO_LOCAL.clear()
        self.addCleanup(agente._ESTADO.__setitem__, "sin_stream", False)
        servidor = mock.patch.object(remoto, "servidor", return_value="http://127.0.0.1:9/v1")
        servidor.start()
        self.addCleanup(servidor.stop)

    def test_usa_el_stream_y_deja_el_progreso_en_memoria(self):
        pedidos = []

        def abrir(pedido, timeout=0):
            pedidos.append(pedido)
            return _Respuesta(_sse(CONTRATO["ejemplo_eventos"]))

        with mock.patch("urllib.request.urlopen", side_effect=abrir), mock.patch.object(remoto, "_pedir_json") as clasico:
            r = agente.turno("mejora los prompts", borrador="contratos-de-pago", progreso_id="turno-abcdef12")
        clasico.assert_not_called()
        self.assertEqual(pedidos[0].full_url, "http://127.0.0.1:9/v1/me/agente/turno/stream")
        self.assertEqual(pedidos[0].get_header("Accept"), "text/event-stream")
        self.assertEqual(json.loads(pedidos[0].data)["borrador"], "contratos-de-pago")
        self.assertEqual(r["propuestas"], [41])
        self.assertTrue(agente.progreso("turno-abcdef12")["en_vivo"])

    def test_servidor_sin_stream_usa_el_turno_clasico_el_resto_de_la_sesion(self):
        def no_existe(pedido, timeout=0):
            raise urllib.error.HTTPError(pedido.full_url, 404, "Not Found", {}, io.BytesIO(b"{}"))

        respuesta = (200, {"conversacion": 1, "respuesta": "ok", "acciones": [], "propuestas": []})
        with mock.patch("urllib.request.urlopen", side_effect=no_existe) as abrir, \
                mock.patch.object(remoto, "_pedir_json", return_value=respuesta) as clasico:
            self.assertEqual(agente.turno("hola")["respuesta"], "ok")
            self.assertEqual(agente.turno("otra vez")["respuesta"], "ok")
        self.assertEqual(abrir.call_count, 1)
        self.assertEqual(clasico.call_count, 2)
        self.assertTrue(agente._ESTADO["sin_stream"])

    def test_sin_conexion_no_desactiva_el_stream(self):
        respuesta = (200, {"conversacion": 1, "respuesta": "ok", "acciones": [], "propuestas": []})
        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("rechazada")), \
                mock.patch.object(remoto, "_pedir_json", return_value=respuesta):
            agente.turno("hola")
        self.assertFalse(agente._ESTADO["sin_stream"])

    def test_respuesta_que_no_es_sse_vuelve_al_clasico(self):
        respuesta = (200, {"conversacion": 1, "respuesta": "clásico", "acciones": [], "propuestas": []})
        with mock.patch("urllib.request.urlopen", return_value=_Respuesta([b"{}"], tipo="application/json")), \
                mock.patch.object(remoto, "_pedir_json", return_value=respuesta):
            self.assertEqual(agente.turno("hola")["respuesta"], "clásico")

    def test_error_sin_ia_en_el_stream_llega_con_codigo(self):
        with mock.patch("urllib.request.urlopen", return_value=_Respuesta(_sse([CONTRATO["ejemplo_error"]]))), \
                mock.patch.object(remoto, "_pedir_json") as clasico, self.assertRaises(agente.AgenteError) as ctx:
            agente.turno("hola")
        clasico.assert_not_called()
        self.assertEqual(ctx.exception.codigo, "SIN_IA")

    def test_sin_sesion_es_permission_error(self):
        def sin_sesion(pedido, timeout=0):
            raise urllib.error.HTTPError(pedido.full_url, 401, "Unauthorized", {}, io.BytesIO('{"message":"sin sesión"}'.encode()))

        with mock.patch("urllib.request.urlopen", side_effect=sin_sesion), self.assertRaises(PermissionError):
            agente.turno("hola")

    def test_tiempo_agotado_no_repite_el_turno(self):
        with mock.patch("urllib.request.urlopen", side_effect=TimeoutError()), \
                mock.patch.object(remoto, "_pedir_json") as clasico, self.assertRaises(agente.AgenteNoDisponible):
            agente.turno("hola")
        clasico.assert_not_called()


class TestPanelUxyn(unittest.TestCase):
    def node(self, programa: str) -> str:
        if not shutil.which("node"):
            self.skipTest("sin node")
        r = subprocess.run(["node", "--input-type=module", "-e", programa], capture_output=True, text=True, encoding="utf-8",
                           cwd=WEB / "js", check=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_resumen_de_cambios_y_aviso_sin_ia_con_el_contrato(self):
        resultado = next(e for e in CONTRATO["ejemplo_eventos"] if e["tipo"] == "resultado")["resultado"]
        programa = """
globalThis.document = { getElementById: () => null, createElement: () => ({}), createElementNS: () => ({ setAttribute() {}, append() {} }), addEventListener() {} };
globalThis.window = { addEventListener() {} };
globalThis.localStorage = { getItem: () => null, setItem() {} };
globalThis.location = { hash: '', pathname: '/' };
const m = await import('./vistas/agente-chat.js');
const acciones = __ACCIONES__;
const doble = [...acciones, { cambios: [{ ruta: 'prompts/agente.md', tipo: 'cambiado', mas: 1, menos: 1 }, { ruta: 7 }] }];
console.log(JSON.stringify([m.resumenCambios(acciones), m.resumenCambios(doble).mas, m.resumenCambios([]).archivos.length,
  m.RE_SIN_IA.test('Añade una clave de IA'), m.PEDIDO_COMPLETAR.includes('esqueleto')]));
""".replace("__ACCIONES__", json.dumps(resultado["acciones"]))
        r = json.loads(self.node(programa))
        self.assertEqual(r[0], {"archivos": [{"ruta": "prompts/agente.md", "tipo": "cambiado", "mas": 6, "menos": 2},
                                             {"ruta": "config/limites.json", "tipo": "nuevo", "mas": 5, "menos": 0}],
                                "mas": 11, "menos": 2})
        self.assertEqual(r[1:], [12, 0, True, True])

    def test_chat_del_panel_pinta_cambios_capacidades_y_aviso_sin_ia(self):
        chat = (WEB / "js" / "vistas" / "agente-chat.js").read_text(encoding="utf-8")
        creador = (WEB / "js" / "vistas" / "creador.js").read_text(encoding="utf-8")
        inicio = (WEB / "js" / "vistas" / "creador-inicio.js").read_text(encoding="utf-8")
        self.assertIn('codigo !== "uxyn_sin_ia"', chat)
        self.assertIn("cambiosAgente(acciones, alRevisar)", chat)
        self.assertIn('obtener("/api/agente/info")', creador)
        self.assertIn('obtener("/api/agente/info")', inicio)
        self.assertIn("alRevisar: irARevisar", creador)
        self.assertIn('"Completar el sistema"', creador)
        self.assertIn("ayudaSinIA(e.message, e.codigo)", inicio)
        css = (WEB / "estilos.css").read_text(encoding="utf-8")
        for clase in (".tarjeta-cambios", ".lista-cambios", ".capacidades-agente", ".cambio-mas", ".cambio-menos"):
            self.assertIn(clase, css)
        self.assertNotIn("#", css[css.index(".tarjeta-cambios"):css.index(".aviso-sin-ia")], "colores desde los tokens")


if __name__ == "__main__":
    unittest.main()
