"""Pruebas del explorador de carpetas (/api/carpetas) que usan los botones «Examinar…» de las páginas."""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import threading
import unittest
import unittest.mock
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import explorar  # noqa: E402
import servidor  # noqa: E402

TOKEN = "t0k3n"


class TestExplorar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), servidor.crear(TOKEN, lambda: None, "panel"))
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.tmp = tempfile.TemporaryDirectory()
        raiz = cls.raiz = Path(cls.tmp.name).resolve()
        (raiz / "beta" / ".git").mkdir(parents=True)
        (raiz / "Alfa" / "docs").mkdir(parents=True)
        (raiz / "Alfa" / "docs" / ".uxyngraphar.lock").write_text("{}")
        (raiz / "gamma" / "apps" / "api" / "docs").mkdir(parents=True)   # dos niveles abajo: no cuenta
        (raiz / "gamma" / "apps" / "api" / "docs" / ".uxyngraphar.lock").write_text("{}")
        (raiz / ".oculta").mkdir()
        (raiz / "archivo.txt").write_text("x")

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()
        cls.tmp.cleanup()

    def post(self, cuerpo, token=TOKEN):
        req = urllib.request.Request(self.base + "/api/carpetas", json.dumps(cuerpo).encode(), {"X-Token": token, "Content-Type": "application/json"})
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())

    def test_lista_solo_carpetas_ordenadas_y_sin_ocultas(self):
        r = self.post({"ruta": str(self.raiz)})
        self.assertTrue(r["ok"])
        self.assertEqual(r["ruta"], str(self.raiz))
        self.assertEqual(r["padre"], str(self.raiz.parent))
        self.assertEqual([c["nombre"] for c in r["carpetas"]], ["Alfa", "beta", "gamma"])
        self.assertFalse(r["truncada"])
        self.assertIn("Carpeta personal", [a["nombre"] for a in r["atajos"]])

    def test_muestra_ocultas_si_se_pide(self):
        r = self.post({"ruta": str(self.raiz), "ocultas": True})
        self.assertIn(".oculta", [c["nombre"] for c in r["carpetas"]])

    def test_marca_git_y_uxyngraphar(self):
        c = {x["nombre"]: x for x in self.post({"ruta": str(self.raiz)})["carpetas"]}
        self.assertTrue(c["beta"]["git"])
        self.assertFalse(c["beta"]["uxyngraphar"])
        self.assertTrue(c["Alfa"]["uxyngraphar"])
        self.assertFalse(c["Alfa"]["git"])
        self.assertFalse(c["gamma"]["uxyngraphar"])

    def test_sin_ruta_abre_la_carpeta_personal(self):
        r = self.post({})
        self.assertTrue(r["ok"])
        self.assertEqual(r["ruta"], str(Path.home().resolve()))

    def test_ruta_inexistente_o_archivo(self):
        r = self.post({"ruta": str(self.raiz / "no-existe")})
        self.assertFalse(r["ok"])
        self.assertIn("No existe", r["error"])
        self.assertFalse(self.post({"ruta": str(self.raiz / "archivo.txt")})["ok"])

    def test_raiz_no_tiene_padre(self):
        r = explorar.listar(os.path.abspath(os.sep))
        self.assertTrue(r["ok"])
        self.assertIsNone(r["padre"])

    def test_tope_de_carpetas(self):
        with tempfile.TemporaryDirectory() as t, unittest.mock.patch.object(explorar, "MAX_CARPETAS", 2):
            for n in "abc":
                Path(t, n).mkdir()
            r = explorar.listar(t)
            self.assertEqual(len(r["carpetas"]), 2)
            self.assertTrue(r["truncada"])

    def test_sin_token_rechazado(self):
        with self.assertRaises(urllib.error.HTTPError) as e:
            self.post({"ruta": str(self.raiz)}, token="otro")
        self.assertEqual(e.exception.code, 403)

    def test_paginas_llevan_el_explorador_y_ningun_alert(self):
        for camino in ("/", "/instalar", "/actualizar"):
            html = urllib.request.urlopen(self.base + camino).read().decode()
            self.assertIn('id="exp"', html, camino)
            self.assertIn("elegirCarpeta(", html, camino)
            self.assertNotIn("<!--EXPLORADOR-->", html, camino)
            self.assertNotIn("/api/carpeta\"", html, camino)
            self.assertIsNone(re.search(r"\balert\(", html), camino)


if __name__ == "__main__":
    unittest.main()
