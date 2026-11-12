"""Servidor de sistemas de gobernanza: artefacto, índice, búsqueda, traer, instalar desde el servidor y publicar.

Levanta un servidor falso en 127.0.0.1 con la misma forma que `/v1/sistemas` del backend.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import threading
import unittest
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import _rutas  # noqa: F401
from _sistemas import completar
import artefacto
import catalogo
import fuentes
import generar
import remoto
import repo

base = catalogo.base
TOKEN = "tok_prueba_1234567890abcdef"
SESION = "uxk_sesion_de_prueba_1234567890abcdefgh"


class Falso(BaseHTTPRequestHandler):
    zips: dict = {}            # (editor, id, version) → bytes
    fichas: list = []
    publicados: list = []
    pedidos: list = []
    respuestas_token: list = []   # estados que devolverá /dispositivo/token, en orden
    revocadas: list = []
    biblioteca: list = []         # lo que devuelve /me/biblioteca (con sesión)
    de_pago: set = set()          # (editor, id) que solo se descargan con sesión
    reportes: list = []           # cuerpos recibidos en /sistemas/<editor>/<id>/reportes

    def log_message(self, *a):  # noqa: D401 - silencio
        pass

    def _json(self, datos, codigo=200, cabeceras=None):
        cuerpo = json.dumps(datos).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json")
        for k, v in (cabeceras or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def _indice(self):
        sistemas = {}
        for f in self.fichas:
            s = sistemas.setdefault((f["editor"], f["id"]), {k: f[k] for k in ("editor", "id", "titulo", "descripcion", "familia",
                                                                               "etiquetas", "problemas")} | {"versiones": []})
            s["versiones"].append({k: f[k] for k in ("version", "sha256", "tamano", "motor")} | {"retirada": f.get("retirada", False)})
        return {"formato": 1, "sistemas": list(sistemas.values())}

    def _cuerpo(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}") if n else {}

    def do_DELETE(self):  # noqa: N802
        if self.path == "/v1/dispositivo/sesion" and self.headers.get("Authorization") == f"Bearer {SESION}":
            Falso.revocadas.append(SESION)
            self.send_response(204)
            self.end_headers()
            return None
        return self._json({"message": "sin sesión"}, 401)

    def do_GET(self):  # noqa: N802
        url = urlparse(self.path)
        Falso.pedidos.append(url.path)
        partes = url.path.split("/")[2:]          # quita «/v1»
        if partes == ["dispositivo", "sesion"]:
            if self.headers.get("Authorization") != f"Bearer {SESION}" or SESION in Falso.revocadas:
                return self._json({"message": "sin sesión"}, 401)
            return self._json({"usuario": "ana", "email": "ana@x.com", "equipo": "Portátil", "conectado": "2026-11-11T00:00:00Z"})
        if partes == ["me", "biblioteca"]:
            if self.headers.get("Authorization") != f"Bearer {SESION}" or SESION in Falso.revocadas:
                return self._json({"message": "sin sesión"}, 401)
            etag = f'W/"{hashlib.sha256(json.dumps(self.biblioteca, sort_keys=True).encode()).hexdigest()[:16]}"'
            if self.headers.get("If-None-Match") == etag:
                self.send_response(304)
                self.end_headers()
                return None
            return self._json({"sistemas": self.biblioteca}, cabeceras={"ETag": etag})
        if partes == ["sistemas", "indice"]:
            etag = f'"{len(self.fichas)}"'
            if self.headers.get("If-None-Match") == etag:
                self.send_response(304)
                self.end_headers()
                return None
            return self._json(self._indice(), cabeceras={"ETag": etag})
        if partes == ["sistemas"]:
            q = parse_qs(url.query).get("q", [""])[0]
            return self._json({"sistemas": [s for s in self._indice()["sistemas"] if q in s["titulo"].lower() + s["id"]]})
        if len(partes) == 6 and partes[3] == "versiones" and partes[5] == "descarga":
            datos = self.zips.get((partes[1], partes[2], partes[4]))
            if datos is None:
                return self._json({"message": "no existe"}, 404)
            if (partes[1], partes[2]) in self.de_pago and self.headers.get("Authorization") != f"Bearer {SESION}":
                return self._json({"message": "Este sistema es de pago: cómpralo en el Mercado."}, 402)
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Length", str(len(datos)))
            self.end_headers()
            self.wfile.write(datos)
            return None
        return self._json({"message": "no existe"}, 404)

    def do_POST(self):  # noqa: N802
        if self.path == "/v1/dispositivo/codigo":
            equipo = self._cuerpo().get("equipo", "")
            return self._json({"codigo_dispositivo": "secreto-del-dispositivo-123", "codigo_usuario": "BCDF-GHJK",
                               "url": "http://web/conectar", "url_completa": "http://web/conectar?codigo=BCDF-GHJK",
                               "intervalo": 1, "caduca_en": 60, "_equipo": equipo}, 201)
        if self.path == "/v1/dispositivo/token":
            if self._cuerpo().get("codigo_dispositivo") != "secreto-del-dispositivo-123":
                return self._json({"estado": "caducado"}, 410)
            estado = Falso.respuestas_token.pop(0) if Falso.respuestas_token else "pendiente"
            if estado == "aprobado":
                return self._json({"estado": "aprobado", "token": SESION, "usuario": "ana"})
            return self._json({"estado": estado}, {"pendiente": 428, "lento": 429, "denegado": 403, "caducado": 410}[estado])
        partes = self.path.split("/")[2:]
        if len(partes) == 4 and partes[0] == "sistemas" and partes[3] == "reportes":
            if self.headers.get("Authorization") != f"Bearer {SESION}":
                return self._json({"message": "sin sesión"}, 401)
            if partes[1] == "ajeno":
                return self._json({"message": "Solo puedes reportar sistemas que tienes en tu biblioteca."}, 403)
            Falso.reportes.append({"editor": partes[1], "id": partes[2], **self._cuerpo()})
            return self._json({"id": len(Falso.reportes), "repetido": False}, 201)
        if self.path != "/v1/sistemas/publicar":
            return self._json({"message": "no existe"}, 404)
        if self.headers.get("Authorization") not in (f"Bearer {TOKEN}", f"Bearer {SESION}"):
            return self._json({"message": "token inválido"}, 401)
        datos = self.rfile.read(int(self.headers["Content-Length"]))
        Falso.publicados.append(datos)
        pid, m = artefacto.leer(datos)
        return self._json({"editor": "uxyngraphar", "id": pid, "version": m["version"]}, 201)


class TestRemoto(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), Falso)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        raiz = Path(self.tmp.name)
        self.cat, self.vacio, self.app, self.zips = raiz / "catalogo", raiz / "vacio", raiz / "app", raiz / "zips"
        for c in (self.cat, self.vacio, self.app):
            c.mkdir()
        completar(catalogo.crear("pruebas-demo", "Pruebas demo", "Sistema de prueba", self.cat))
        self.zip = artefacto.empaquetar("pruebas-demo", self.zips, self.cat)
        self.sha = artefacto.sha256_de(self.zip)
        with tempfile.TemporaryDirectory() as t:
            ficha = artefacto.ficha(artefacto.desempaquetar(self.zip, Path(t)), self.sha, self.zip.stat().st_size)
        Falso.fichas = [ficha]
        Falso.zips = {("uxyngraphar", "pruebas-demo", ficha["version"]): self.zip.read_bytes()}
        Falso.publicados, Falso.pedidos, Falso.respuestas_token, Falso.revocadas = [], [], [], []
        Falso.biblioteca, Falso.de_pago, Falso.reportes = [], set(), []
        self.antes = {k: os.environ.get(k) for k in ("UXYNGRAPHAR_SIN_RED", "UXYNGRAPHAR_SERVIDOR", "UXYNGRAPHAR_CATALOGO", "UXYNGRAPHAR_TOKEN")}
        os.environ.pop("UXYNGRAPHAR_SIN_RED", None)
        os.environ["UXYNGRAPHAR_SERVIDOR"] = f"http://127.0.0.1:{self.srv.server_address[1]}/v1"
        os.environ["UXYNGRAPHAR_CATALOGO"] = str(self.vacio)     # como el instalador: sin sistemas locales
        remoto._caido_hasta = 0.0  # noqa: SLF001
        remoto.limpiar_cache()

    def tearDown(self):
        for k, v in self.antes.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
        remoto.limpiar_cache()
        self.tmp.cleanup()

    # artefacto
    def test_artefacto_reproducible_y_con_una_raiz(self):
        otro = artefacto.empaquetar("pruebas-demo", self.zips / "otra", self.cat)
        self.assertEqual(self.zip.read_bytes(), otro.read_bytes())
        nombres = zipfile.ZipFile(self.zip).namelist()
        self.assertTrue(all(n.startswith("pruebas-demo/") for n in nombres))
        self.assertIn(f"pruebas-demo/{base.INTEGRIDAD}", nombres)
        self.assertIn("pruebas-demo/scripts/comun/uxyn_base.py", nombres)

    def test_artefacto_rechaza_rutas_peligrosas(self):
        for nombre in ("../fuera.txt", "/abs.txt", "a/../../b", "pruebas-demo/ñ.md", "otro/x.md"):
            malo = self.zips / "malo.zip"
            with zipfile.ZipFile(self.zip) as z, zipfile.ZipFile(malo, "w") as w:
                for e in z.infolist():
                    w.writestr(e, z.read(e))
                w.writestr(nombre, b"x")
            with self.assertRaises(artefacto.ArtefactoInvalido, msg=nombre):
                artefacto.leer(malo)

    def test_artefacto_alterado_no_valida(self):
        malo = self.zips / "alterado.zip"
        with zipfile.ZipFile(self.zip) as z, zipfile.ZipFile(malo, "w") as w:
            for e in z.infolist():
                w.writestr(e, z.read(e) + (b"\n" if e.filename.endswith("SISTEMA.md") else b""))
        with self.assertRaises(artefacto.ArtefactoInvalido):
            artefacto.desempaquetar(malo, self.zips / "x")

    # servidor
    def test_indice_y_busqueda(self):
        self.assertEqual([s["id"] for s in remoto.indice()["sistemas"]], ["pruebas-demo"])
        remoto.indice(refrescar=True)    # con ETag: 304 y se queda lo guardado
        self.assertEqual(remoto.versiones_disponibles()["pruebas-demo"]["version"], Falso.fichas[0]["version"])
        self.assertEqual([s["id"] for s in remoto.buscar("demo")], ["pruebas-demo"])
        self.assertEqual(remoto.buscar("nada-parecido"), [])

    def test_sin_red_usa_el_indice_guardado(self):
        remoto.indice()
        os.environ["UXYNGRAPHAR_SERVIDOR"] = "http://127.0.0.1:9/v1"
        remoto._caido_hasta = 0.0  # noqa: SLF001
        (remoto.cache() / remoto.ARCHIVO_INDICE).write_text(json.dumps({**remoto._indice_guardado(), "_recibido": 0}),  # noqa: SLF001
                                                             encoding="utf-8")
        self.assertEqual([s["id"] for s in remoto.buscar("demo")], ["pruebas-demo"])

    def test_resolver(self):
        version = Falso.fichas[0]["version"]
        self.assertEqual(remoto.resolver("pruebas-demo")["version"], version)
        self.assertEqual(remoto.resolver(f"uxyngraphar/pruebas-demo@{version}")["sha256"], self.sha)
        with self.assertRaises(remoto.NoEncontrado):
            remoto.resolver("pruebas-demo@9.9.9")
        with self.assertRaises(ValueError):
            remoto.resolver("Mal Id")

    def test_traer_comprueba_la_huella_y_guarda_en_cache(self):
        c = remoto.traer("pruebas-demo")
        self.assertTrue(base.integro(base.comprobar_integridad(c)))
        n = len(Falso.pedidos)
        self.assertEqual(remoto.traer("pruebas-demo"), c)       # segunda vez: de la caché, sin descargar
        self.assertFalse([p for p in Falso.pedidos[n:] if p.endswith("/descarga")])
        remoto.limpiar_cache()
        Falso.fichas[0]["sha256"] = "0" * 64
        with self.assertRaises(artefacto.ArtefactoInvalido):
            remoto.traer("pruebas-demo")

    def test_instalar_desde_el_servidor_con_el_catalogo_vacio(self):
        self.assertEqual(fuentes.origenes(), {"pruebas-demo": "servidor"})
        repo.instalar(self.app, ["pruebas-demo"])
        self.assertEqual([m["id"] for m in generar.instalados(self.app)], ["pruebas-demo"])
        (e,) = repo.estado(self.app)
        self.assertTrue(e["integro"])
        self.assertFalse(e["actualizable"])

    def test_el_catalogo_local_gana_a_igual_version(self):
        os.environ["UXYNGRAPHAR_CATALOGO"] = str(self.cat)
        self.assertEqual(fuentes.origenes(), {"pruebas-demo": "local"})
        catalogo.versionar("pruebas-demo", "parche", self.cat)
        self.assertEqual(fuentes.origenes(), {"pruebas-demo": "local"})

    def test_el_servidor_gana_si_trae_una_version_mas_alta(self):
        os.environ["UXYNGRAPHAR_CATALOGO"] = str(self.cat)
        Falso.fichas[0]["version"] = "9.0.0"
        remoto.indice(refrescar=True)
        self.assertEqual(fuentes.origenes(), {"pruebas-demo": "servidor"})

    def test_publicar_con_token(self):
        os.environ.pop("UXYNGRAPHAR_TOKEN", None)
        remoto.borrar_token()
        with self.assertRaises(PermissionError):
            remoto.publicar(self.zip)
        with self.assertRaises(PermissionError):
            remoto.publicar(self.zip, "otro_token_1234567890")
        r = remoto.publicar(self.zip, TOKEN)
        self.assertEqual((r["id"], len(Falso.publicados)), ("pruebas-demo", 1))
        self.assertEqual(Falso.publicados[0], self.zip.read_bytes())

    def test_iniciar_sesion_por_dispositivo(self):
        os.environ.pop("UXYNGRAPHAR_TOKEN", None)
        remoto.borrar_token()
        Falso.respuestas_token = ["pendiente", "lento", "aprobado"]
        vistos, esperas = [], []
        r = remoto.iniciar_sesion("Portátil", avisar=vistos.append, esperar=esperas.append)
        self.assertEqual(r, {"estado": "aprobado", "usuario": "ana"})
        self.assertEqual(vistos[0]["codigo_usuario"], "BCDF-GHJK")
        self.assertEqual(esperas, [1, 1, 6])               # «lento» alarga el intervalo
        guardada = remoto.sesion()
        self.assertEqual((guardada["tipo"], guardada["usuario"], guardada["token"]), ("sesion", "ana", SESION))
        self.assertEqual(guardada["servidor"], remoto.servidor())
        self.assertEqual(remoto.quien_soy()["usuario"], "ana")
        self.assertEqual(remoto.publicar(self.zip)["id"], "pruebas-demo")
        self.assertEqual(remoto.cerrar_sesion(), {"revocada": True, "borrada": True})
        self.assertEqual(Falso.revocadas, [SESION])
        self.assertEqual(remoto.sesion(), {})
        with self.assertRaises(PermissionError):
            remoto.quien_soy()

    def test_iniciar_sesion_rechazada(self):
        Falso.respuestas_token = ["pendiente", "denegado"]
        with self.assertRaises(remoto.SesionRechazada):
            remoto.iniciar_sesion("x", esperar=lambda _s: None)
        self.assertEqual(remoto.sesion(), {})

    def test_la_sesion_no_viaja_a_otro_servidor(self):
        remoto.guardar_token(SESION)
        self.assertEqual(remoto.token(), SESION)
        os.environ["UXYNGRAPHAR_SERVIDOR"] = "http://127.0.0.1:9/v1"
        self.assertIsNone(remoto.token())
        remoto.borrar_token()

    # biblioteca sincronizada (ADR 0012)
    def _de_pago(self) -> dict:
        """Publica «ana/pruebas-demo» como sistema de pago: fuera del índice, solo en la biblioteca."""
        version = Falso.fichas[0]["version"]
        Falso.zips[("ana", "pruebas-demo", version)] = self.zip.read_bytes()
        Falso.de_pago = {("ana", "pruebas-demo")}
        motor = Falso.fichas[0]["motor"]
        item = {"editor": "ana", "id": "pruebas-demo", "titulo": "Demo de pago", "version": version, "sha256": self.sha,
                "tamano": self.zip.stat().st_size, "motor": motor, "origen": "compra",
                "de_pago": True, "privado": False}
        Falso.biblioteca = [item]
        Falso.fichas = []                                 # lo de pago no sale en el índice público
        return item

    def test_sincronizar_trae_lo_adquirido_y_lo_resuelve_sin_red(self):
        os.environ.pop("UXYNGRAPHAR_TOKEN", None)
        item = self._de_pago()
        with self.assertRaises(PermissionError):
            remoto.sincronizar()                          # sin sesión
        remoto.guardar_token(SESION)
        r = fuentes.sincronizar_biblioteca()
        self.assertEqual((r["total"], r["descargados"], r["fallidos"]), (1, 1, []))
        self.assertIsNotNone(remoto.en_cache("ana", "pruebas-demo", item["version"]))
        n = len(Falso.pedidos)
        self.assertEqual(remoto.sincronizar()["al_dia"], ["ana/pruebas-demo"])   # 304 y ya en caché
        self.assertFalse([p for p in Falso.pedidos[n:] if p.endswith("/descarga")])
        self.assertEqual(remoto.resolver("ana/pruebas-demo")["sha256"], self.sha)
        os.environ["UXYNGRAPHAR_SIN_RED"] = "1"
        self.assertEqual(remoto._sistemas_biblioteca()[0]["id"], "pruebas-demo")  # noqa: SLF001
        os.environ.pop("UXYNGRAPHAR_SIN_RED")
        remoto.cerrar_sesion()
        self.assertEqual(remoto._sistemas_biblioteca(), [])  # noqa: SLF001 - cerrar sesión olvida la lista

    def test_lo_de_pago_sin_comprar_explica_el_motivo(self):
        os.environ.pop("UXYNGRAPHAR_TOKEN", None)
        self._de_pago()
        remoto.guardar_token(SESION)
        remoto.biblioteca()
        remoto.borrar_token()
        with self.assertRaises(remoto.DePago) as caso:
            remoto.traer("ana/pruebas-demo")
        self.assertIn("de pago", str(caso.exception))

    def test_la_huella_distinta_no_entra_en_la_cache(self):
        os.environ.pop("UXYNGRAPHAR_TOKEN", None)
        self._de_pago()["sha256"] = "0" * 64
        remoto.guardar_token(SESION)
        r = remoto.sincronizar()
        self.assertEqual(len(r["fallidos"]), 1)
        self.assertIn("sha256", r["fallidos"][0]["error"])
        self.assertEqual(remoto.en_cache("ana", "pruebas-demo", Falso.biblioteca[0]["version"]), None)
        remoto.borrar_token()

    def test_lo_adquirido_avisa_de_version_nueva_en_el_repo(self):
        os.environ.pop("UXYNGRAPHAR_TOKEN", None)
        self._de_pago()
        remoto.guardar_token(SESION)
        remoto.sincronizar()
        repo.instalar(self.app, ["pruebas-demo"])
        (e,) = repo.estado(self.app)
        self.assertFalse(e["actualizable"])
        Falso.biblioteca[0] = {**Falso.biblioteca[0], "version": "9.0.0"}
        remoto.biblioteca()
        (e,) = repo.estado(self.app)
        self.assertTrue(e["actualizable"])                 # se avisa; nunca se aplica solo
        self.assertNotEqual([m["version"] for m in generar.instalados(self.app)], ["9.0.0"])
        remoto.borrar_token()

    # reportes al autor (Fase 8)
    def test_reportar_ensena_lo_que_se_envia_y_envia_eso(self):
        import reportes
        os.environ.pop("UXYNGRAPHAR_TOKEN", None)
        repo.instalar(self.app, ["pruebas-demo"])
        datos = reportes.armar("pruebas-demo", "Problema", "  El agente se salta la fase 2.\r\n", self.app)
        version = Falso.fichas[0]["version"]
        self.assertEqual((datos["editor"], datos["id"], datos["version"], datos["tipo"]),
                         ("uxyngraphar", "pruebas-demo", version, "PROBLEMA"))
        self.assertEqual(set(datos["contexto"]), {"kit", "sistema_operativo", "python"})
        previa = reportes.vista_previa(datos)
        self.assertIn("El agente se salta la fase 2.", previa)
        self.assertNotIn(str(self.app), previa + json.dumps(datos))       # nunca rutas del proyecto
        with self.assertRaises(PermissionError):
            reportes.enviar(datos)                                        # sin sesión
        remoto.guardar_token(SESION)
        self.assertEqual(reportes.enviar(datos), {"id": 1, "repetido": False})
        (recibido,) = Falso.reportes
        self.assertEqual(recibido, {"editor": "uxyngraphar", "id": "pruebas-demo", "tipo": "PROBLEMA",
                                    "texto": "El agente se salta la fase 2.", "version": version,
                                    "contexto": datos["contexto"]})
        with self.assertRaises(PermissionError) as caso:
            reportes.enviar({**datos, "editor": "ajeno"})
        self.assertIn("biblioteca", str(caso.exception))
        remoto.borrar_token()

    def test_reportar_valida_antes_de_tocar_la_red(self):
        import reportes
        for ref, tipo, texto in (("../x", "duda", "texto suficiente"), ("pruebas-demo", "queja", "texto suficiente"),
                                 ("pruebas-demo", "duda", "corto"), ("desconocido", "duda", "texto suficiente")):
            with self.subTest(ref=ref, tipo=tipo), self.assertRaises(ValueError):
                reportes.armar(ref, tipo, texto)
        self.assertEqual(reportes.armar("ana/otro@2.0.0", "mejora", "Falta un ejemplo")["version"], "2.0.0")

    def test_reportar_desde_la_cli_simula_o_envia_con_si(self):
        import contextlib
        import io
        import cli
        os.environ.pop("UXYNGRAPHAR_TOKEN", None)
        remoto.guardar_token(SESION)
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            self.assertEqual(cli.main(["reportar", "pruebas-demo", "--tipo", "duda", "--texto", "¿Qué hago en la fase 3?",
                                       "--simular"]), 0)
        self.assertIn("Tipo: Duda", salida.getvalue())
        self.assertEqual(Falso.reportes, [])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["reportar", "pruebas-demo", "--tipo", "duda", "--texto", "¿Qué hago en la fase 3?",
                                       "--si"]), 0)
        self.assertEqual(len(Falso.reportes), 1)
        remoto.borrar_token()

    def test_sin_red_explicito(self):
        os.environ["UXYNGRAPHAR_SIN_RED"] = "1"
        self.assertIsNone(remoto.servidor())
        self.assertEqual(fuentes.versiones(), {})


if __name__ == "__main__":
    unittest.main()
