"""Pruebas de «mover la carpeta del pack» desde la herramienta: CLI (uxyngraphar mover-carpeta) y panel."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import api  # noqa: E402
import api_mover  # noqa: E402
import servidor  # noqa: E402

PERSONA = {k: "" for k in ("CI", "GITHUB_ACTIONS", "GITLAB_CI", "BUILDKITE", "JENKINS_URL", "CLAUDECODE", "UXYNGRAPHAR_AGENTE")}
GIT = ("-c", "user.name=t", "-c", "user.email=t@t")
TOKEN = "t" * 32


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "proyecto"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        (self.repo / "go.mod").write_text("module x\n")
        r = api.flujo.instalar_completo(api.PACKS["servidor"], self.repo, "docs", proteger=True, ganchos=True)   # como una instalación 1.0.x
        self.assertTrue(r.ok)
        subprocess.run(["git", *GIT, "add", "-A"], cwd=self.repo, check=True)
        subprocess.run(["git", *GIT, "commit", "-qm", "chore: pack"], cwd=self.repo, check=True, capture_output=True)
        self.env = mock.patch.dict(os.environ, {**PERSONA, "UXYNGRAPHAR_HOME": str(Path(self.tmp.name) / "home")})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()


class TestApiMover(Base):
    def test_candidatos_ver_y_aplicar(self):
        self.assertEqual(api_mover.candidatos(str(self.repo)), [{"ruta": str(self.repo.resolve()), "docs": "docs", "hacia": "uxyngraphar"}])
        v = api_mover.ver(str(self.repo), "docs")
        self.assertTrue(v["ok"], v)
        self.assertIn("Mover docs/ → uxyngraphar/", v["texto"])
        self.assertTrue((self.repo / "docs").is_dir())
        r = api_mover.aplicar(str(self.repo), "docs")
        self.assertTrue(r["ok"], r)
        self.assertTrue((self.repo / "uxyngraphar/.uxyngraphar.lock").is_file())
        self.assertEqual([x["docs"] for x in api.inspeccionar(str(self.repo))["instalados"]], ["uxyngraphar"])
        self.assertEqual(api_mover.candidatos(str(self.repo)), [])

    def test_un_agente_no_mueve(self):
        with mock.patch.dict(os.environ, {"CLAUDECODE": "1"}):
            r = api_mover.aplicar(str(self.repo), "docs")
        self.assertFalse(r["ok"])
        self.assertIn("persona", r["error"])
        self.assertTrue((self.repo / "docs").is_dir())

    def test_panel_por_http(self):
        srv = ThreadingHTTPServer(("127.0.0.1", 0), servidor.crear(TOKEN, lambda: None, "panel"))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.server_close)
        self.addCleanup(srv.shutdown)

        def post(ruta, cuerpo):
            req = urllib.request.Request(f"http://127.0.0.1:{srv.server_address[1]}{ruta}", json.dumps(cuerpo).encode(),
                                         {"X-Token": TOKEN, "Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read())
        html = urllib.request.urlopen(f"http://127.0.0.1:{srv.server_address[1]}/").read().decode()
        self.assertIn("tarjetaMover", html)
        v = post("/api/panel/mover/ver", {"ruta": str(self.repo), "docs": "docs"})
        self.assertTrue(v["ok"] and v["hacia"] == "uxyngraphar", v)
        r = post("/api/panel/mover/aplicar", {"ruta": str(self.repo), "docs": "docs"})
        self.assertTrue(r["ok"], r)
        self.assertFalse(post("/api/panel/mover/ver", {"ruta": str(self.repo), "docs": "docs"})["ok"])   # ya no hay nada en docs/


class TestCli(Base):
    def correr(self, *a):
        return subprocess.run([sys.executable, "-X", "utf8", str(AQUI.parent / "uxyngraphar.py"), "mover-carpeta", *a], cwd=self.repo,
                              capture_output=True, text=True, stdin=subprocess.DEVNULL, env={**os.environ, "UXYNGRAPHAR_SIN_PATH": "1"})

    def test_sin_si_solo_muestra_y_con_si_mueve(self):
        r = self.correr()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Mover docs/ → uxyngraphar/", r.stdout)
        self.assertIn("--si", r.stdout + r.stderr)
        self.assertTrue((self.repo / "docs").is_dir())
        r = self.correr("--si")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.repo / "uxyngraphar").is_dir() and not (self.repo / "docs").exists())
        self.assertIn("no hay nada que mover", self.correr().stdout)

    def test_ayuda(self):
        r = subprocess.run([sys.executable, "-X", "utf8", str(AQUI.parent / "uxyngraphar.py"), "ayuda", "mover-carpeta"], capture_output=True, text=True)
        self.assertIn("git mv", r.stdout)


if __name__ == "__main__":
    unittest.main()
