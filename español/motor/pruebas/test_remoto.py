"""Servidor de sistemas de gobernanza: artefacto, índice, búsqueda, traer, instalar desde el servidor y publicar.

Levanta un servidor falso en 127.0.0.1 con la misma forma que `/v1/sistemas` del backend.
"""

from __future__ import annotations

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


class Falso(BaseHTTPRequestHandler):
    zips: dict = {}            # (editor, id, version) → bytes
    fichas: list = []
    publicados: list = []
    pedidos: list = []

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

    def do_GET(self):  # noqa: N802
        url = urlparse(self.path)
        Falso.pedidos.append(url.path)
        partes = url.path.split("/")[2:]          # quita «/v1»
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
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Length", str(len(datos)))
            self.end_headers()
            self.wfile.write(datos)
            return None
        return self._json({"message": "no existe"}, 404)

    def do_POST(self):  # noqa: N802
        if self.path != "/v1/sistemas/publicar":
            return self._json({"message": "no existe"}, 404)
        if self.headers.get("Authorization") != f"Bearer {TOKEN}":
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
        Falso.publicados, Falso.pedidos = [], []
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
        with self.assertRaises(remoto.SinServidor):
            remoto.publicar(self.zip, "otro_token_1234567890")
        r = remoto.publicar(self.zip, TOKEN)
        self.assertEqual((r["id"], len(Falso.publicados)), ("pruebas-demo", 1))
        self.assertEqual(Falso.publicados[0], self.zip.read_bytes())

    def test_sin_red_explicito(self):
        os.environ["UXYNGRAPHAR_SIN_RED"] = "1"
        self.assertIsNone(remoto.servidor())
        self.assertEqual(fuentes.versiones(), {})


if __name__ == "__main__":
    unittest.main()
