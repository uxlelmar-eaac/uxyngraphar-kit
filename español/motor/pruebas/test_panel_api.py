"""Pruebas del servidor del panel: estáticos de web/, token, sesión, API por áreas, instancia única y cierre solo."""

from __future__ import annotations

import json
import os
import threading
import time
import unittest
import urllib.error
import urllib.request
from unittest import mock

import _rutas  # noqa: F401
import panel
import repo
from test_proyectos import Entorno


class ConServidor(Entorno):
    inactividad: int | None = None

    def setUp(self):
        super().setUp()
        self.servidor, self.token = panel.crear_servidor(0, inactividad=self.inactividad)
        self.hilo = threading.Thread(target=self.servidor.serve_forever, daemon=True)
        self.hilo.start()
        self.url = f"http://127.0.0.1:{self.servidor.server_address[1]}"

    def tearDown(self):
        self.servidor.shutdown()
        self.servidor.server_close()
        self.hilo.join(5)
        super().tearDown()

    def pedir(self, ruta: str, datos: dict | None = None, token: str | None = None):
        cuerpo = json.dumps(datos).encode() if datos is not None else None
        pedido = urllib.request.Request(self.url + ruta, data=cuerpo, headers={"X-Uxyn-Token": token or self.token, "Content-Type": "application/json"})
        with urllib.request.urlopen(pedido, timeout=10) as r:
            return json.loads(r.read())["ok"]

    def error(self, ruta: str, datos: dict | None = None, token: str | None = None) -> tuple[int, str]:
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self.pedir(ruta, datos, token)
        with ctx.exception as e:
            error = json.loads(e.read() or b"{}").get("error", "")
            self.ultimo_error = error if isinstance(error, dict) else {}
            return e.code, error.get("mensaje", "") if isinstance(error, dict) else error


class TestServidor(ConServidor):
    def test_estaticos_y_rutas_protegidas(self):
        with urllib.request.urlopen(self.url + "/") as r:
            self.assertIn(b"js/app.js", r.read())
            self.assertIn("text/html", r.headers["Content-Type"])
        with urllib.request.urlopen(self.url + "/js/app.js") as r:
            self.assertIn("javascript", r.headers["Content-Type"])
        for malo in ("/../panel.py", "/%2e%2e/panel.py", "/js/../../cli.py", "/no-existe.js"):
            with self.assertRaises(urllib.error.HTTPError, msg=malo) as ctx:
                urllib.request.urlopen(self.url + malo)
            self.assertEqual(ctx.exception.code, 404, malo)

    def test_token_y_sesion(self):
        self.assertEqual(self.error("/api/sesion", token="otro")[0], 403)
        sesion = self.pedir("/api/sesion")
        self.assertEqual(sesion["pid"], os.getpid())
        self.assertIn("version", sesion)
        self.assertEqual(self.error("/api/no-existe")[0], 404)

    def test_cuenta_sin_sesion(self):
        cuenta = self.pedir("/api/cuenta?comprobar=1")
        self.assertEqual((cuenta["tipo"], cuenta["usuario"], cuenta["valida"]), ("ninguna", None, None))
        self.assertEqual(self.error("/api/cuenta/consultar", {})[0], 400)
        self.assertEqual(self.pedir("/api/cuenta/cerrar", {}), {"revocada": False, "borrada": False})

    def test_biblioteca_sin_sesion(self):
        b = self.pedir("/api/biblioteca")
        self.assertEqual((b["sesion"], b["sistemas"], b["en_curso"]), (False, [], False))
        codigo, cuerpo = self.error("/api/biblioteca/sincronizar", {})
        self.assertEqual(codigo, 400)
        self.assertIn("sin sesión", json.dumps(cuerpo, ensure_ascii=False))

    def test_herramienta_reparar_anterior_y_desinstalar_simulado(self):
        app = self.repo_git("app")
        self.pedir("/api/proyectos/agregar", {"rutas": [str(app)]})
        self.pedir("/api/repo/instalar", {"repo": str(app), "ids": ["pruebas-demo"]})
        informe = self.pedir("/api/herramienta/reparar", {"proyectos": True})
        self.assertEqual(informe["problemas"], [])
        self.assertEqual([p["error"] for p in informe["proyectos"]], [""])
        self.assertEqual(self.error("/api/herramienta/anterior", {})[0], 400)
        plan = self.pedir("/api/herramienta/desinstalar", {"alcance": "proyectos", "rutas": [str(app)], "simular": True})
        self.assertTrue(plan["simulado"])
        self.assertIn("uxyngraphar/sistemas-de-gobernanza/pruebas-demo/", plan["proyectos"][0]["quitar"])
        self.assertTrue((app / "uxyngraphar" / "sistemas-de-gobernanza" / "pruebas-demo").is_dir())
        self.assertEqual(self.error("/api/herramienta/desinstalar", {"alcance": "nada", "simular": True})[0], 400)
        self.assertEqual(self.pedir("/api/sesion")["pid"], os.getpid(), "simular no cierra el panel")

    def test_proyectos_y_flujos_por_la_api(self):
        app = self.repo_git("app")
        self.assertEqual(self.pedir("/api/proyectos/agregar", {"rutas": [str(app)]}), [str(app)])
        self.pedir("/api/repo/instalar", {"repo": str(app), "ids": ["pruebas-demo"]})
        estado = self.pedir(f"/api/repo/estado?repo={app}")
        self.assertEqual([p["id"] for p in estado["sistemas"]], ["pruebas-demo"])
        self.assertTrue(estado["registrado"])
        self.assertEqual(estado["flujo"]["modo"], "manual")
        flujo = {**estado["flujo"], "modo": "trabajar_con", "trabajar_con": "pruebas-demo"}
        self.pedir("/api/repo/flujo", {"repo": str(app), "flujo": flujo})
        codigo, mensaje = self.error("/api/repo/flujo", {"repo": str(app), "flujo": {**flujo, "trabajar_con": "pruebas-otras"}})
        self.assertEqual(codigo, 400)
        self.assertIn("no instalado", mensaje)
        fid = self.pedir("/api/flujos/desde-proyecto", {"repo": str(app), "nombre": "Base demo"})
        otro = self.repo_git("otro")
        codigo, mensaje = self.error("/api/flujos/aplicar", {"id": fid, "repos": [str(otro)]})
        self.assertEqual(codigo, 400)
        self.assertIn("Mis proyectos", mensaje, "solo se cambian proyectos registrados (C-11)")
        self.assertFalse((otro / "uxyngraphar").exists())
        self.pedir("/api/proyectos/agregar", {"rutas": [str(otro)]})
        [r] = self.pedir("/api/flujos/aplicar", {"id": fid, "repos": [str(otro)]})
        self.assertEqual((r["instalados"], r["error"]), (["pruebas-demo"], ""))
        [r] = self.pedir("/api/catalogo/instalar-en", {"ids": ["pruebas-otras"], "repos": [str(otro)]})
        self.assertEqual(r["instalados"], ["pruebas-otras"])
        resumen = {p["nombre"]: p for p in self.pedir("/api/proyectos")}
        self.assertEqual(resumen["app"]["modo"], "trabajar_con")
        self.assertEqual(self.pedir("/api/repo/desinstalar", {"repo": str(otro)})["hechos"], ["sistemas retirados: pruebas-demo, pruebas-otras"])
        self.assertFalse((otro / repo.base.CARPETA_SISTEMAS_DE_GOBERNANZA).exists())

    def test_generador_desde_el_panel(self):
        spec = self.pedir("/api/catalogo/plantilla-spec?id=pagos-de-proveedor")
        self.assertEqual(spec["id"], "pagos-de-proveedor")
        simulado = self.pedir("/api/catalogo/generar", {"spec": spec})
        self.assertEqual((simulado["errores"], simulado["aplicado"]), ([], False))
        self.assertFalse((self.cat / "pagos-de-proveedor").exists())
        self.assertTrue(self.pedir("/api/catalogo/generar", {"spec": spec, "aplicar": True})["aplicado"])
        self.assertTrue(self.pedir("/api/catalogo/pendientes?id=pagos-de-proveedor")["listo"])
        malo = self.pedir("/api/catalogo/generar", {"spec": {**spec, "id": "otros-pagos", "titulo": "Pagos"}, "aplicar": True})
        self.assertTrue(malo["errores"])
        self.assertEqual(self.error("/api/catalogo/pendientes?id=no-existe")[0], 400)

    def test_explorador_y_errores_legibles(self):
        self.repo_git("zona", "app")
        r = self.pedir(f"/api/proyectos/carpetas?ruta={self.t / 'zona'}")
        self.assertEqual([c["nombre"] for c in r["carpetas"]], ["app"])
        codigo, mensaje = self.error("/api/repo/estado?repo=/no/existe")
        self.assertEqual(codigo, 400)
        self.assertIn("proyecto", mensaje)

    def test_latido_y_cerrar(self):
        antes = self.servidor.latido
        time.sleep(0.05)
        self.pedir("/api/latido", {})
        self.assertGreater(self.servidor.latido, antes)
        self.assertTrue(self.pedir("/api/cerrar", {}))
        self.hilo.join(5)
        self.assertFalse(self.hilo.is_alive(), "cerrar apaga el servidor")


class TestCierreSolo(ConServidor):
    inactividad = 1

    def test_se_apaga_sin_latidos(self):
        self.servidor.vigilar()
        self.hilo.join(10)
        self.assertFalse(self.hilo.is_alive(), "sin pestañas que manden latidos, el panel se cierra")


class TestInstanciaUnica(ConServidor):
    def test_reabre_el_panel_abierto(self):
        panel.casa.escribir_json(panel.ESTADO, {"puerto": self.servidor.server_address[1], "token": self.token, "pid": os.getpid()})
        self.assertEqual(panel.panel_abierto()["token"], self.token)
        with mock.patch.object(panel.webbrowser, "open") as abrir, mock.patch.object(panel, "crear_servidor") as crear:
            self.assertEqual(panel.servir(abrir=True), 0)
            crear.assert_not_called()
            url = abrir.call_args[0][0]
            self.assertNotIn(self.token, url, "la URL ya no lleva el token (M-14)")
            self.assertTrue(self.servidor.canjear(url.split("#c=", 1)[1]), "lleva un código de un solo uso válido")

    def test_estado_viejo_no_cuenta(self):
        panel.casa.escribir_json(panel.ESTADO, {"puerto": 1, "token": "x", "pid": 999999999})
        self.assertIsNone(panel.panel_abierto())


class TestPublicarCatalogo(ConServidor):
    """POST /api/catalogo/publicar: simular no sube; sin sesión falla; con servidor falso publica."""

    def test_simular_no_llama_publicar(self):
        with mock.patch("remoto.publicar") as pub:
            r = self.pedir("/api/catalogo/publicar", {"id": "pruebas-demo", "simular": True})
        pub.assert_not_called()
        self.assertTrue(r["simulado"])
        self.assertEqual(r["id"], "pruebas-demo")
        self.assertIn("sha256", r)
        self.assertGreater(r["tamano"], 0)

    def test_sin_sesion_no_publica(self):
        codigo, mensaje = self.error("/api/catalogo/publicar", {"id": "pruebas-demo", "simular": False})
        self.assertEqual(codigo, 400)
        self.assertIn("sin sesión", mensaje.lower())

    def test_sistema_con_errores(self):
        malo = self.cat / "pruebas-demo" / "sistema.json"
        datos = json.loads(malo.read_text(encoding="utf-8"))
        datos["version"] = "no-semver"
        malo.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        codigo, mensaje = self.error("/api/catalogo/publicar", {"id": "pruebas-demo", "simular": True})
        self.assertEqual(codigo, 400)
        self.assertIn("errores", mensaje.lower())

    def test_publicar_con_sesion_y_servidor_falso(self):
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        import artefacto
        import remoto

        publicados: list = []

        class Falso(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_POST(self):
                if self.path != "/v1/sistemas/publicar":
                    self.send_response(404)
                    self.end_headers()
                    return
                if self.headers.get("Authorization") != "Bearer uxk_sesion_de_prueba_1234567890abcdefgh":
                    self.send_response(401)
                    self.end_headers()
                    return
                cuerpo = self.rfile.read(int(self.headers["Content-Length"]))
                publicados.append(cuerpo)
                pid, m = artefacto.leer(cuerpo)
                resp = json.dumps({"editor": "ana", "id": pid, "version": m["version"]}).encode()
                self.send_response(201)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(resp)))
                self.end_headers()
                self.wfile.write(resp)

        srv = ThreadingHTTPServer(("127.0.0.1", 0), Falso)
        hilo = threading.Thread(target=srv.serve_forever, daemon=True)
        hilo.start()
        url = f"http://127.0.0.1:{srv.server_address[1]}/v1"
        try:
            with mock.patch.dict(os.environ, {"UXYNGRAPHAR_SERVIDOR": url}, clear=False):
                os.environ.pop("UXYNGRAPHAR_SIN_RED", None)
                os.environ.pop("UXYNGRAPHAR_TOKEN", None)
                remoto.guardar_token("uxk_sesion_de_prueba_1234567890abcdefgh")
                # alinear editor con @ana (el falso responde como ana)
                import casa
                s = casa.leer_json("sesion.json", {})
                s["usuario"] = "ana"
                casa.escribir_json("sesion.json", s, privado=True)
                r = self.pedir("/api/catalogo/publicar", {"id": "pruebas-demo", "simular": False, "alinear_editor": True})
            self.assertEqual((r["editor"], r["id"]), ("ana", "pruebas-demo"))
            self.assertTrue(publicados)
            self.assertTrue(r.get("alineado"))
        finally:
            srv.shutdown()
            srv.server_close()
            hilo.join(5)


class TestSinNombreDelEquipo(unittest.TestCase):
    def test_arranca_sin_resolver_el_nombre_del_equipo(self):
        with mock.patch("socket.getfqdn", side_effect=AssertionError("getfqdn se cuelga en macOS fuera de la terminal")):
            servidor, _ = panel.crear_servidor(0)
        servidor.server_close()
        self.assertEqual(servidor.server_name, "127.0.0.1")


class TestSinTerminal(Entorno):
    def test_sigue_abierto_sin_la_terminal_y_se_cierra(self):
        with mock.patch.object(panel.webbrowser, "open") as abrir:
            self.assertEqual(panel.lanzar(abrir=True), 0)
        try:
            abierto = panel.panel_abierto()
            self.assertIsNotNone(abierto)
            self.assertNotEqual(abierto["pid"], os.getpid(), "el panel corre en su propio proceso")
            self.assertNotIn(abierto["token"], abrir.call_args[0][0])
            self.assertIn("/#c=", abrir.call_args[0][0])
            if os.name != "nt":
                self.assertEqual(os.getsid(abierto["pid"]), abierto["pid"], "en su propia sesión: cerrar la terminal no lo cierra")
            with mock.patch.object(panel.webbrowser, "open"):
                self.assertEqual(panel.lanzar(abrir=True), 0)
            self.assertEqual(panel.panel_abierto()["pid"], abierto["pid"], "uno solo por equipo: se reabre el mismo")
        finally:
            cerrado = panel.cerrar_abierto()
        self.assertEqual(cerrado["pid"], abierto["pid"])
        self.assertIsNone(panel.panel_abierto())


if __name__ == "__main__":
    unittest.main()
