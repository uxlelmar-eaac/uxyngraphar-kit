#!/usr/bin/env python3
"""Pruebas del envío voluntario de sugerencias: apagado por defecto, solo fichas EVO, limpieza, consentimiento, pregunta de colaboración,
envío automático solo con una persona delante (nunca en CI ni con un agente) y revocación."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SCRIPTS = AQUI.parent
sys.path.insert(0, str(AQUI))

import cliente  # noqa: E402
import uxyngraphar_config as cfgmod  # noqa: E402

EVO = ("---\nid: EVO-20261030-paso\nstatus: pending\ntipo: proceso\nimpacto: ambos\nareas: [pagos]\npropuesta_cambio:\n  - 10-guias/guia.md\n---\n"
       "# EVO-20261030-paso\n\nEn tienda-acme falta un paso. Lo vi en /home/ana/tienda-acme/src/app.py y lo comenté con ana@acme.com\n"
       "en https://intranet.acme.com/wiki.\n<!-- nota privada -->\npassword = \"s3cr3t0-muy-largo\"\n")


class Receptor(BaseHTTPRequestHandler):
    recibidos: list = []

    def log_message(self, *args: object) -> None:
        pass

    def do_POST(self) -> None:  # noqa: N802
        Receptor.recibidos.append((self.path, json.loads(self.rfile.read(int(self.headers["Content-Length"])))))
        self._ok({"guardadas": 1})

    def do_DELETE(self) -> None:  # noqa: N802
        Receptor.recibidos.append((self.path, None))
        self._ok({"borradas": 1})

    def _ok(self, cuerpo: dict) -> None:
        datos = json.dumps(cuerpo).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)


class TestFeedback(unittest.TestCase):
    def setUp(self) -> None:
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.repo = Path(self._t.name) / "tienda-acme"
        self.docs = self.repo / "docs"
        d = self.docs / "46-evolucion-documentacion" / "01-pendientes" / "2026-10-30"
        d.mkdir(parents=True)
        (d / "EVO-20261030-paso.md").write_text(EVO, encoding="utf-8")
        (self.docs / "uxyngraphar.config.json").write_text(json.dumps({"limite_lineas": 400}), encoding="utf-8")
        Receptor.recibidos = []
        self.srv = ThreadingHTTPServer(("127.0.0.1", 0), Receptor)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.addCleanup(self.srv.server_close)
        self.addCleanup(self.srv.shutdown)
        self.url = f"http://127.0.0.1:{self.srv.server_port}/v1"

    def _cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPTS / "feedback.py"), "--repo", str(self.repo), *args],
                              capture_output=True, text=True, stdin=subprocess.DEVNULL)

    def test_apagado_por_defecto_y_nunca_envia_sin_activar(self) -> None:
        self.assertFalse(cfgmod.por_defecto()["feedback"]["activo"])
        r = self._cli("enviar")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertEqual(Receptor.recibidos, [])

    def test_la_ficha_sale_limpia(self) -> None:
        [(_md, ficha)] = cliente.fichas(self.docs, "tienda-acme")
        texto = json.dumps(ficha, ensure_ascii=False)
        for fuga in ("tienda-acme", "/home/ana", "ana@acme.com", "intranet.acme.com", "s3cr3t0", "nota privada", "pagos"):
            self.assertNotIn(fuga, texto)
        self.assertIn("[proyecto]", ficha["cuerpo"])
        self.assertIn("[línea omitida", ficha["cuerpo"])
        self.assertEqual(ficha["propuesta_cambio"], ["10-guias/guia.md"])

    def test_ocultar_nombres_propios(self) -> None:
        [(_md, ficha)] = cliente.fichas(self.docs, "otro-nombre", ocultar=("Tienda-ACME", "acme"))
        self.assertNotIn("acme", json.dumps(ficha, ensure_ascii=False).lower())
        self.assertIn("[oculto]", ficha["cuerpo"])

    def test_activar_sin_terminal_exige_acepto_y_no_cambia_nada(self) -> None:
        r = self._cli("activar", "--url", self.url)
        self.assertEqual(r.returncode, 2)
        self.assertNotIn("feedback", json.loads((self.docs / "uxyngraphar.config.json").read_text(encoding="utf-8")))
        self.assertEqual(self._cli("activar", "--url", "http://servidor-ajeno.com/v1", "--acepto").returncode, 2)   # http fuera del equipo: no

    def test_activar_enviar_una_vez_y_revocar(self) -> None:
        r = self._cli("activar", "--url", self.url, "--acepto")
        self.assertEqual(r.returncode, 0, r.stderr)
        cfg = json.loads((self.docs / "uxyngraphar.config.json").read_text(encoding="utf-8"))
        self.assertEqual(cfg["limite_lineas"], 400)   # el resto de la configuración no se toca
        self.assertTrue(cfg["feedback"]["activo"] and cfg["feedback"]["consentimiento"] and cfg["feedback"]["id_instalacion"])
        self.assertEqual(Receptor.recibidos, [])       # activar no envía
        r = self._cli("enviar")
        self.assertEqual(r.returncode, 0, r.stderr)
        ruta, cuerpo = Receptor.recibidos[0]
        self.assertEqual(ruta, "/v1/sugerencias")
        self.assertEqual(cuerpo["id_instalacion"], cfg["feedback"]["id_instalacion"])
        self.assertEqual([f["id"] for f in cuerpo["fichas"]], ["EVO-20261030-paso"])
        self.assertNotIn("tienda-acme", json.dumps(cuerpo))
        self.assertEqual(self._cli("enviar").returncode, 1)   # sin cambios: no se repite
        evo = next(self.docs.glob("46-*/01-*/*/EVO-*.md"))
        evo.write_text(evo.read_text(encoding="utf-8").replace("falta un paso", "faltan dos pasos"), encoding="utf-8")
        self.assertEqual(self._cli("enviar").returncode, 0)   # cambió: se vuelve a enviar
        r = self._cli("revocar", "--borrar-remoto")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(Receptor.recibidos[-1][0].startswith("/v1/instalaciones/"))
        cfg = json.loads((self.docs / "uxyngraphar.config.json").read_text(encoding="utf-8"))
        self.assertFalse(cfg["feedback"]["activo"])
        self.assertEqual(self._cli("enviar").returncode, 2)

    def test_config_activa_a_mano_sin_consentimiento_es_invalida(self) -> None:
        cfg = cfgmod.por_defecto()
        cfg["feedback"] = {"activo": True, "url": "https://x.org/v1", "consentimiento": "", "id_instalacion": ""}
        self.assertTrue(any("consentimiento" in e for e in cfgmod.validar(cfg)))


    def test_el_envio_solo_lleva_fichas_evo(self) -> None:
        _rutas, datos = cliente.paquete(self.docs, cfgmod.por_defecto(), "tienda-acme", "1.0.0", "servidor")
        self.assertEqual(datos["formato"], 1)
        self.assertNotIn("ajustes", datos)
        self.assertEqual([f["id"] for f in datos["fichas"]], ["EVO-20261030-paso"])

    def test_registrar_respuesta_si_y_no(self) -> None:
        cfg = cfgmod.cargar(self.repo)[0]
        self.assertTrue(cliente.necesita_respuesta(cfg))
        fb = cliente.registrar_respuesta(self.repo, "docs", False, "instalador", fecha="2026-10-30")
        self.assertEqual((fb["activo"], fb["respondido"], fb["respondido_en"], fb["origen"]), (False, "no", "2026-10-30", "instalador"))
        cfg, problemas = cfgmod.cargar(self.repo)
        self.assertEqual(problemas, [])
        self.assertFalse(cliente.necesita_respuesta(cfg))                 # no se vuelve a preguntar
        self.assertEqual(cfg["limite_lineas"], 400)                        # el resto no se toca
        fb = cliente.registrar_respuesta(self.repo, "docs", True, "actualizador", fecha="2026-10-31")
        self.assertTrue(fb["activo"])
        self.assertEqual(fb["url"], cliente.URL_FEEDBACK_OFICIAL)
        self.assertEqual(fb["consentimiento"], "2026-10-31 (v1)")
        self.assertRegex(fb["id_instalacion"], r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
        self.assertEqual(cfgmod.cargar(self.repo)[1], [])
        with self.assertRaises(ValueError):
            cliente.registrar_respuesta(self.repo, "docs", True, "agente")

    def test_activar_a_mano_cuenta_como_respuesta(self) -> None:
        self.assertEqual(self._cli("activar", "--url", self.url, "--acepto").returncode, 0)
        cfg = cfgmod.cargar(self.repo)[0]
        self.assertEqual((cfg["feedback"]["respondido"], cfg["feedback"]["origen"]), ("si", "manual"))
        self.assertFalse(cliente.necesita_respuesta(cfg))

    def test_respondido_invalido(self) -> None:
        cfg = cfgmod.por_defecto()
        cfg["feedback"]["respondido"] = "quizas"
        self.assertTrue(any("respondido" in e for e in cfgmod.validar(cfg)))

    def test_enviar_si_corresponde_solo_con_persona_y_envio_activo(self) -> None:
        self.assertIsNone(cliente.enviar_si_corresponde(self.repo, "docs", entorno={}))   # apagado: no hace nada
        self.assertEqual(self._cli("activar", "--url", self.url, "--acepto").returncode, 0)
        for entorno in ({"CI": "true"}, {"GITHUB_ACTIONS": "true"}, {"CLAUDECODE": "1"}, {"UXYNGRAPHAR_AGENTE": "1"}):
            self.assertIsNone(cliente.enviar_si_corresponde(self.repo, "docs", entorno=entorno))
        self.assertEqual(Receptor.recibidos, [])                                          # ni CI ni agente envían
        linea = cliente.enviar_si_corresponde(self.repo, "docs", entorno={"CI": "false"})
        self.assertIn("enviadas 1 ficha(s) EVO", linea)
        ruta, cuerpo = Receptor.recibidos[0]
        self.assertEqual(ruta, "/v1/sugerencias")
        self.assertNotIn("ajustes", cuerpo)
        self.assertIn("no hay fichas EVO nuevas", cliente.enviar_si_corresponde(self.repo, "docs", entorno={}))

    def test_enviar_si_corresponde_sin_red_avisa_y_no_lanza(self) -> None:
        self.assertEqual(self._cli("activar", "--url", "http://127.0.0.1:9/v1", "--acepto").returncode, 0)
        linea = cliente.enviar_si_corresponde(self.repo, "docs", entorno={})
        self.assertIn("no se pudieron enviar", linea)
        self.assertEqual(Receptor.recibidos, [])

    def test_texto_de_la_pregunta(self) -> None:
        texto = cliente.texto_colaboracion()
        self.assertTrue(texto.startswith("¿Te gustaría colaborar en la mejora de uxyngraphar?"))
        self.assertIn("Qué sale:", texto)
        self.assertIn("Qué no sale nunca:", texto)
        self.assertEqual(set(cliente.info_colaboracion()), {"pregunta", "url", "sale", "no_sale", "cuando"})


if __name__ == "__main__":
    unittest.main()
