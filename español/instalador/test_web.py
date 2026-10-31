"""Pruebas del servidor local del asistente: seguridad básica y flujo completo por HTTP."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import api  # noqa: E402
import servidor  # noqa: E402

TOKEN = "t0k3n"


class TestWeb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), servidor.crear(TOKEN, lambda: None))
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.tmp = tempfile.TemporaryDirectory()
        cls.repo = Path(cls.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=cls.repo, check=True)
        (cls.repo / "go.mod").write_text("module x\n")

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()
        cls.tmp.cleanup()

    def post(self, ruta, cuerpo, token=TOKEN):
        req = urllib.request.Request(self.base + ruta, json.dumps(cuerpo).encode(), {"X-Token": token, "Content-Type": "application/json"})
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())

    def test_pagina_lleva_token_y_sin_token_no_se_puede_operar(self):
        html = urllib.request.urlopen(self.base + "/").read().decode()
        self.assertIn(TOKEN, html)
        self.assertNotIn("__TOKEN__", html)
        with self.assertRaises(urllib.error.HTTPError) as e:
            self.post("/api/plan", {}, token="otro")
        self.assertEqual(e.exception.code, 403)

    def test_host_ajeno_rechazado(self):
        req = urllib.request.Request(self.base + "/", headers={"Host": "evil.example.com"})
        with self.assertRaises(urllib.error.HTTPError) as e:
            urllib.request.urlopen(req)
        self.assertEqual(e.exception.code, 404)

    def test_inspeccionar_plan_ejecutar(self):
        info = self.post("/api/inspeccionar", {"ruta": str(self.repo)})
        self.assertTrue(info["ok"] and info["git"])
        self.assertIn("go", info["pila"])
        self.assertFalse(self.post("/api/inspeccionar", {"ruta": "/no/existe"})["ok"])
        s = {"proyecto": str(self.repo), "pack": "servidor", "sub": ""}
        plan = self.post("/api/plan", s)
        self.assertTrue(plan["ok"])
        self.assertEqual(plan["destinos"][0]["modo"], "instalar")
        self.assertFalse((self.repo / "AGENTES.md").exists())      # planificar no escribe
        res = self.post("/api/ejecutar", s)
        self.assertTrue(res["ok"], res)
        self.assertTrue((self.repo / "AGENTES.md").is_file())
        self.assertTrue(res["siguientes"])
        self.assertEqual(self.post("/api/plan", s)["destinos"][0]["modo"], "actualizar")

    def test_validaciones_de_la_solicitud(self):
        base = {"proyecto": str(self.repo), "pack": "ambos", "mismo_repo": True}
        self.assertFalse(self.post("/api/plan", {**base, "sub_servidor": "app", "sub_cliente": "app"})["ok"])
        self.assertFalse(self.post("/api/plan", {**base, "sub_servidor": "../fuera", "sub_cliente": "web"})["ok"])
        self.assertFalse(self.post("/api/plan", {**base, "mismo_repo": False, "proyecto2": str(self.repo)})["ok"])
        self.assertFalse(api.planificar({"proyecto": "/no/existe", "pack": "servidor"})["ok"])


    def _repo_nuevo(self) -> Path:
        d = Path(tempfile.mkdtemp(dir=self.tmp.name))
        subprocess.run(["git", "init", "-q"], cwd=d, check=True)
        (d / "go.mod").write_text("module x\n")
        return d

    @staticmethod
    def _feedback(repo: Path) -> dict:
        return json.loads((repo / "docs" / "uxyngraphar.config.json").read_text(encoding="utf-8"))["feedback"]

    def test_pregunta_de_colaboracion_sin_opcion_marcada(self):
        html = urllib.request.urlopen(self.base + "/").read().decode()
        self.assertIn('name="colab" value="si"', html)
        self.assertNotIn('value="si" checked', html)
        info = self.post("/api/colaboracion", {})
        self.assertEqual(info["pregunta"], "¿Te gustaría colaborar en la mejora de uxyngraphar?")
        self.assertTrue(info["sale"] and info["no_sale"] and info["url"].startswith("https://"))

    def test_sin_respuesta_cuenta_como_no_y_no_se_vuelve_a_preguntar(self):
        import os
        from unittest import mock
        repo = self._repo_nuevo()
        self.assertTrue(self.post("/api/inspeccionar", {"ruta": str(repo)})["colaboracion_pendiente"])
        s = {"proyecto": str(repo), "pack": "servidor", "sub": ""}
        with mock.patch.dict(os.environ, {v: "" for v in api.feedback.ENTORNOS_SIN_PERSONA}):   # una persona delante
            self.assertTrue(any("sin respuesta (cuenta como No)" in l for l in self.post("/api/plan", s)["destinos"][0]["lineas"]))
            res = self.post("/api/ejecutar", s)
        self.assertTrue(res["ok"], res)
        fb = self._feedback(repo)
        self.assertEqual((fb["activo"], fb["respondido"], fb["origen"]), (False, "no", "instalador"))
        self.assertFalse(self.post("/api/inspeccionar", {"ruta": str(repo)})["colaboracion_pendiente"])

    def test_con_un_agente_sin_respuesta_queda_pendiente(self):
        """R-25: ni el CI ni un agente contestan la pregunta por la persona."""
        import os
        from unittest import mock
        repo = self._repo_nuevo()
        s = {"proyecto": str(repo), "pack": "servidor", "sub": ""}
        with mock.patch.dict(os.environ, {"CLAUDECODE": "1"}):
            self.assertTrue(any("queda pendiente" in l for l in self.post("/api/plan", s)["destinos"][0]["lineas"]))
            res = self.post("/api/ejecutar", s)
        self.assertTrue(res["ok"], res)
        self.assertTrue(any("Colaborar en la mejora: pendiente" in p["texto"] for p in res["destinos"][0]["pasos"]))
        self.assertFalse(self._feedback(repo).get("respondido"))
        self.assertTrue(self.post("/api/inspeccionar", {"ruta": str(repo)})["colaboracion_pendiente"])

    def test_respuesta_si_activa_el_envio_con_consentimiento(self):
        repo = self._repo_nuevo()
        res = self.post("/api/ejecutar", {"proyecto": str(repo), "pack": "servidor", "sub": "", "colaborar": "si"})
        self.assertTrue(res["ok"], res)
        self.assertTrue(any("Colaborar en la mejora: Sí" in p["texto"] for p in res["destinos"][0]["pasos"]))
        fb = self._feedback(repo)
        self.assertTrue(fb["activo"] and fb["consentimiento"] and fb["id_instalacion"])
        self.assertEqual((fb["respondido"], fb["origen"]), ("si", "instalador"))

    def test_receptor_inalcanzable_solo_avisa(self):
        """Con «Sí» y el receptor oficial sin resolver (DNS caído o dominio aún sin publicar), la instalación termina bien y solo avisa."""
        import os
        import socket
        from unittest import mock
        repo = self._repo_nuevo()
        real, salientes = urllib.request.urlopen, []

        def abrir(req, *a, **k):   # la pantalla local sigue funcionando; cualquier salida a internet falla como un DNS caído
            url = req.full_url if isinstance(req, urllib.request.Request) else str(req)
            if url.startswith("http://127.0.0.1"):
                return real(req, *a, **k)
            salientes.append(url)
            raise urllib.error.URLError(socket.gaierror(-2, "Name or service not known"))

        persona = {v: "" for v in api.feedback.ENTORNOS_SIN_PERSONA}   # como si lo ejecutara una persona, también dentro de CI
        with mock.patch.dict(os.environ, persona), mock.patch("urllib.request.urlopen", side_effect=abrir):
            res = self.post("/api/ejecutar", {"proyecto": str(repo), "pack": "servidor", "sub": "", "colaborar": "si"})
            self.assertTrue(res["ok"], res)
            self.assertTrue((repo / "docs/.uxyngraphar.lock").is_file())
            self.assertTrue(self._feedback(repo)["activo"])
            # Una ficha EVO nueva del proyecto: el siguiente instalar/actualizar intenta enviarla y el receptor no responde.
            d = repo / "docs/46-evolucion-documentacion/01-pendientes/2026-10-30"
            d.mkdir(parents=True, exist_ok=True)
            (d / "EVO-20261030-prueba-red.md").write_text("---\nid: EVO-20261030-prueba-red\nstatus: pending\n---\n# Prueba\n", encoding="utf-8")
            pasos = api.aplicar_colaboracion(repo, "docs", {}, "actualizador")
        self.assertTrue(salientes and salientes[0].startswith(api.feedback.URL_FEEDBACK_OFICIAL), salientes)
        self.assertEqual([e for t, e in pasos if "no se pudieron enviar" in t], ["aviso"], pasos)

    def test_consola_con_colaborar(self):
        repo = self._repo_nuevo()
        r = subprocess.run([sys.executable, str(Path(__file__).resolve().parent.parent / "instalar.py"), "--consola", "--proyecto", str(repo),
                            "--pack", "servidor", "--sub-servidor", "", "--si", "--colaborar", "si"], capture_output=True, text=True,
                           env={**__import__("os").environ, "CI": "true"})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Colaborar en la mejora: Sí", r.stdout)
        self.assertTrue(self._feedback(repo)["activo"])


if __name__ == "__main__":
    unittest.main()
