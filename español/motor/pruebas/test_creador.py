"""Creador (ADR 0013): puente del servidor (validar, nuevo, desde-spec, empaquetar en una carpeta suelta),
sincronización de borradores con conflictos y la IA local (Ollama / LM Studio falsos en 127.0.0.1)."""

from __future__ import annotations

import io
import json
import os
import tempfile
import threading
import unittest
import zipfile
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import _rutas  # noqa: F401
import cli
import creador
import generador
import ia_local
import remoto

SESION = "uxk_sesion_creador_1234567890abcdefghij"


class Servidor(BaseHTTPRequestHandler):
    """Borradores del Creador web (`/v1/me/creador/borradores`) y modelos locales falsos."""
    borradores: dict = {}      # slug → {"revision": n, "titulo": t, "archivos": {ruta: contenido}}
    puts: list = []

    def log_message(self, *a):  # noqa: D401 - silencio
        pass

    def _json(self, datos, codigo=200):
        cuerpo = json.dumps(datos).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def _con_sesion(self) -> bool:
        return self.headers.get("Authorization") == f"Bearer {SESION}"

    def do_GET(self):  # noqa: N802
        if self.path == "/api/tags":
            return self._json({"models": [{"name": "llama3.2:3b"}]})
        if self.path == "/v1/models":
            return self._json({"data": [{"id": "qwen2.5-7b"}]})
        if not self._con_sesion():
            return self._json({"message": "sin sesión"}, 401)
        if self.path == "/v1/me/creador/borradores":
            return self._json({"borradores": [{"slug": s, "titulo": b["titulo"], "revision": b["revision"]}
                                              for s, b in sorted(self.borradores.items())]})
        slug = self.path.rsplit("/", 1)[-1]
        b = self.borradores.get(slug)
        if not b:
            return self._json({"message": "no existe"}, 404)
        return self._json({"slug": slug, "titulo": b["titulo"], "revision": b["revision"],
                           "archivos": [{"ruta": r, "contenido": c} for r, c in sorted(b["archivos"].items())]})

    def do_PUT(self):  # noqa: N802
        if not self._con_sesion():
            return self._json({"message": "sin sesión"}, 401)
        cuerpo = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        slug = self.path.rsplit("/", 1)[-1]
        Servidor.puts.append((slug, cuerpo["revision"]))
        b = self.borradores.get(slug)
        actual = b["revision"] if b else 0
        if cuerpo["revision"] != actual:
            return self._json({"message": "conflicto", "revision": actual}, 409)
        self.borradores[slug] = {"titulo": slug, "revision": actual + 1,
                                 "archivos": {a["ruta"]: a["contenido"] for a in cuerpo["archivos"]}}
        return self._json({"slug": slug, "revision": actual + 1})

    def do_POST(self):  # noqa: N802
        cuerpo = json.loads(self.rfile.read(int(self.headers["Content-Length"])) or b"{}")
        if self.path == "/api/chat":
            return self._json({"message": {"content": "```\n# Mejorado\n```"}, "model": cuerpo["model"]})
        if self.path == "/v1/chat/completions":
            return self._json({"choices": [{"message": {"content": f"hola desde {cuerpo['model']}"}}]})
        if self.path == "/v1/me/ia/completar":
            if not self._con_sesion():
                return self._json({"message": "sin sesión"}, 401)
            return self._json({"texto": f"{len(cuerpo['mensajes'])} mensajes · {cuerpo.get('proposito')}", "modelo": "gpt-4.1-mini"})
        return self._json({"message": "no existe"}, 404)


def _sistema_valido(carpeta: Path, pid: str = "contratos-de-pago") -> dict:
    return creador.desde_spec(carpeta, generador.plantilla_spec(pid))


class TestPuente(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / "borrador"
        self.dir.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_nuevo_desde_base_deja_pendientes_y_no_valida(self):
        r = creador.nuevo(self.dir, "pagos-recurrentes", "Pagos recurrentes", "proceso", "Cobros periódicos")
        self.assertIn("sistema.json", r["archivos"])
        self.assertFalse(any(rel.startswith("scripts/comun/") for rel in r["archivos"]))
        v = creador.validar(self.dir)
        self.assertEqual(v["id"], "pagos-recurrentes")
        self.assertFalse(v["valido"])
        self.assertTrue(v["marcadores"])
        self.assertIn("Rellena", v["siguiente"])

    def test_desde_spec_valida_y_empaqueta(self):
        r = _sistema_valido(self.dir)
        self.assertEqual(r["errores"], [])
        v = creador.validar(self.dir)
        self.assertTrue(v["valido"], v["errores"])
        z = creador.empaquetar(self.dir, Path(self.tmp.name) / "zips")
        self.assertEqual(len(z["sha256"]), 64)
        nombres = zipfile.ZipFile(z["zip"]).namelist()
        self.assertIn("contratos-de-pago/INTEGRIDAD.json", nombres)
        self.assertIn("contratos-de-pago/scripts/comun/uxyn_base.py", nombres)

    def test_escribir_y_leer_sin_reservados(self):
        archivos = _sistema_valido(self.dir)["archivos"]
        otro = Path(self.tmp.name) / "otro"
        creador.escribir(otro, "contratos-de-pago", archivos)
        self.assertEqual(creador.leer(otro, "contratos-de-pago"), archivos)
        self.assertTrue(creador.validar(otro)["valido"])
        for malo in ("../fuera.md", "/abs.md", "a//b.md", "scripts/comun/x.py", "INTEGRIDAD.json", "con espacio.md", "ñ.md"):
            with self.assertRaises(ValueError, msg=malo):
                creador.escribir(otro, "contratos-de-pago", {**archivos, malo: "x"})

    def test_carpeta_con_varios_sistemas_no_se_acepta(self):
        _sistema_valido(self.dir)
        _sistema_valido(self.dir, "auditoria-de-pagos")
        with self.assertRaises(ValueError):
            creador.validar(self.dir)

    def test_cli_puente_en_json(self):
        salida = io.StringIO()
        with redirect_stdout(salida):
            codigo = cli.main(["creador", "nuevo", "--dir", str(self.dir), "--id", "pagos-recurrentes", "--titulo",
                               "Pagos recurrentes", "--json"])
        self.assertEqual(codigo, 0)
        self.assertEqual(json.loads(salida.getvalue())["id"], "pagos-recurrentes")
        salida = io.StringIO()
        with redirect_stdout(salida):
            codigo = cli.main(["creador", "validar", "--dir", str(self.dir), "--json"])
        self.assertEqual(codigo, 0)
        self.assertFalse(json.loads(salida.getvalue())["valido"])

    def test_diferencias_por_archivo(self):
        d = creador.diferencias({"a.md": "uno\n", "b.md": "x"}, {"a.md": "dos\n", "c.md": "y"})
        self.assertEqual([(x["ruta"], x["cambio"]) for x in d], [("a.md", "cambiado"), ("b.md", "borrado"), ("c.md", "nuevo")])
        self.assertIn("+dos", d[0]["diff"])


class ConServidor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), Servidor)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cat = Path(self.tmp.name) / "catalogo"
        self.cat.mkdir()
        self.antes = {k: os.environ.get(k) for k in ("UXYNGRAPHAR_SIN_RED", "UXYNGRAPHAR_SERVIDOR", "UXYNGRAPHAR_TOKEN")}
        os.environ.pop("UXYNGRAPHAR_SIN_RED", None)
        os.environ.pop("UXYNGRAPHAR_TOKEN", None)
        self.url = f"http://127.0.0.1:{self.srv.server_address[1]}"
        os.environ["UXYNGRAPHAR_SERVIDOR"] = f"{self.url}/v1"
        remoto._caido_hasta = 0.0  # noqa: SLF001
        remoto.guardar_token(SESION)
        Servidor.borradores, Servidor.puts = {}, []

    def tearDown(self):
        remoto.borrar_token()
        for k, v in self.antes.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
        self.tmp.cleanup()


class TestSincronizacion(ConServidor):
    def _web(self, slug="contratos-de-pago", revision=3):
        with tempfile.TemporaryDirectory() as t:
            archivos = _sistema_valido(Path(t), slug)["archivos"]
        Servidor.borradores[slug] = {"titulo": "Contratos", "revision": revision, "archivos": archivos}
        return archivos

    def test_bajar_editar_subir(self):
        web = self._web()
        filas = creador.borradores(self.cat)
        self.assertEqual([(f["slug"], f["en_equipo"]) for f in filas], [("contratos-de-pago", False)])
        r = creador.bajar("contratos-de-pago", cat=self.cat)
        self.assertEqual((r["accion"], r["revision"]), ("nuevo", 3))
        self.assertEqual(creador.leer(self.cat, "contratos-de-pago"), web)
        self.assertEqual(creador.bajar("contratos-de-pago", cat=self.cat)["accion"], "al_dia")
        (self.cat / "contratos-de-pago" / "LIMITES.md").write_text("# Límites\n\nEditado aquí.\n", encoding="utf-8")
        r = creador.subir("contratos-de-pago", cat=self.cat)
        self.assertEqual((r["accion"], r["revision"]), ("subido", 4))
        self.assertEqual(Servidor.puts, [("contratos-de-pago", 3)])
        self.assertIn("Editado aquí", Servidor.borradores["contratos-de-pago"]["archivos"]["LIMITES.md"])

    def test_cambios_en_los_dos_lados_son_conflicto(self):
        self._web()
        creador.bajar("contratos-de-pago", cat=self.cat)
        (self.cat / "contratos-de-pago" / "LIMITES.md").write_text("# Límites\n\nLocal.\n", encoding="utf-8")
        Servidor.borradores["contratos-de-pago"]["archivos"]["LIMITES.md"] = "# Límites\n\nWeb.\n"
        Servidor.borradores["contratos-de-pago"]["revision"] = 5
        with self.assertRaises(creador.Conflicto) as e:
            creador.subir("contratos-de-pago", cat=self.cat)
        self.assertEqual(e.exception.revision_web, 5)
        self.assertEqual([d["ruta"] for d in e.exception.diferencias], ["LIMITES.md"])
        with self.assertRaises(creador.Conflicto):
            creador.bajar("contratos-de-pago", cat=self.cat)
        self.assertIn("Local.", (self.cat / "contratos-de-pago" / "LIMITES.md").read_text(encoding="utf-8"))
        r = creador.subir("contratos-de-pago", "local", cat=self.cat)
        self.assertEqual(r["revision"], 6)
        self.assertIn("Local.", Servidor.borradores["contratos-de-pago"]["archivos"]["LIMITES.md"])

    def test_conservar_la_web(self):
        self._web()
        creador.bajar("contratos-de-pago", cat=self.cat)
        (self.cat / "contratos-de-pago" / "LIMITES.md").write_text("# Límites\n\nLocal.\n", encoding="utf-8")
        Servidor.borradores["contratos-de-pago"]["archivos"]["LIMITES.md"] = "# Límites\n\nWeb.\n"
        Servidor.borradores["contratos-de-pago"]["revision"] = 9
        r = creador.bajar("contratos-de-pago", "web", cat=self.cat)
        self.assertEqual(r["revision"], 9)
        self.assertIn("Web.", (self.cat / "contratos-de-pago" / "LIMITES.md").read_text(encoding="utf-8"))

    def test_subir_crea_el_borrador(self):
        _sistema_valido(self.cat, "auditoria-de-pagos")
        r = creador.subir("auditoria-de-pagos", cat=self.cat)
        self.assertEqual(r["revision"], 1)
        self.assertNotIn("scripts/comun/uxyn_base.py", Servidor.borradores["auditoria-de-pagos"]["archivos"])

    def test_sin_sesion(self):
        remoto.borrar_token()
        with self.assertRaises(PermissionError):
            creador.borradores(self.cat)


class TestIaLocal(ConServidor):
    def setUp(self):
        super().setUp()
        self.antes_ia = dict(ia_local.LOCALES)
        ia_local.LOCALES.update(ollama=self.url, lmstudio=self.url)

    def tearDown(self):
        ia_local.LOCALES.clear()
        ia_local.LOCALES.update(self.antes_ia)
        super().tearDown()

    def test_modelos_y_respuestas_locales(self):
        self.assertEqual(ia_local.modelos(), [{"proveedor": "ollama", "modelo": "llama3.2:3b"},
                                              {"proveedor": "lmstudio", "modelo": "qwen2.5-7b"}])
        r = ia_local.mejorar("ollama", "llama3.2:3b", "README.md", "# Antes\n", "más claro")
        self.assertEqual(r["propuesta"], "# Mejorado\n")
        r = ia_local.completar("lmstudio", [{"role": "user", "content": "hola"}], "", "qwen2.5-7b")
        self.assertEqual(r["texto"], "hola desde qwen2.5-7b")

    def test_clave_de_la_cuenta_via_servidor(self):
        r = ia_local.completar("servidor", [{"role": "user", "content": "hola"}], "eres útil")
        self.assertEqual((r["texto"], r["modelo"]), ("1 mensajes · creador-local", "gpt-4.1-mini"))

    def test_solo_direcciones_locales(self):
        ia_local.LOCALES["ollama"] = "https://ejemplo.com"
        with self.assertRaises(ValueError):
            ia_local.completar("ollama", [{"role": "user", "content": "hola"}], "", "m")
        self.assertEqual([m["proveedor"] for m in ia_local.modelos()], ["lmstudio"])

    def test_proveedor_desconocido(self):
        with self.assertRaises(ValueError):
            ia_local.completar("openai", [{"role": "user", "content": "hola"}])


if __name__ == "__main__":
    unittest.main()
