"""Pruebas del panel de configuración (uxyngraphar panel): proyecto, plantilla, bienvenida y seguridad."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import api_panel as panel  # noqa: E402
import servidor  # noqa: E402
import sistema  # noqa: E402

PERSONA = {k: "" for k in ("CI", "GITHUB_ACTIONS", "GITLAB_CI", "BUILDKITE", "JENKINS_URL", "CLAUDECODE", "UXYNGRAPHAR_AGENTE")}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        self.home, self.repo = t / "home", t / "proyecto"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        (self.repo / "go.mod").write_text("module x\n")
        docs = self.repo / "docs"
        shutil.copytree(sistema.ES / "backend" / "scripts", docs / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy(sistema.ES / "backend" / "VERSION.md", docs / "VERSION.md")
        lock = {"formato": 1, "version": sistema.version_herramienta(), "pack": "backend", "archivos": {}}
        (docs / ".uxyngraphar.lock").write_text(json.dumps(lock))
        cfgmod = sistema.modulo_config()
        cfgmod.escribir(self.repo, "docs", cfgmod.detectar(self.repo))
        self.env = mock.patch.dict(os.environ, {**PERSONA, "UXYNGRAPHAR_HOME": str(self.home)})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def config(self) -> dict:
        return json.loads((self.repo / "docs" / "uxyngraphar.config.json").read_text(encoding="utf-8"))

    def huella(self) -> str:
        return panel.ver(str(self.repo), "docs")["huella"]


class TestProyecto(Base):
    def test_ver_muestra_efectiva_y_opciones(self):
        v = panel.ver(str(self.repo), "docs")
        self.assertTrue(v["ok"])
        self.assertEqual(v["efectiva"]["limite_lineas"], 350)
        self.assertIn("reglas_proyecto", v["opciones"]["controles"])
        self.assertTrue(v["colaborar"]["disponible"])

    def test_solo_cambia_lo_editable(self):
        p = panel.previsualizar(str(self.repo), "docs", {"limite_lineas": 400, "version": 9, "pila": ["x"],
                                                         "idioma": {"artefactos": "es", "conversacion": "es"},
                                                         "feedback": {"activo": True, "ocultar": ["ACME"]}})
        self.assertEqual(sorted(p["cambios"]), ['feedback.ocultar: [] → ["ACME"]', 'idioma.conversacion: "espejo" → "es"',
                                                "limite_lineas: 350 → 400"])

    def test_guardar_respalda_y_escribe(self):
        r = panel.guardar(str(self.repo), "docs", {"niveles": {"lineas": "bloqueante"}}, self.huella())
        self.assertTrue(r["ok"], r)
        self.assertEqual(self.config()["niveles"]["lineas"], "bloqueante")
        copia = self.repo / ".uxyngraphar-respaldo" / r["respaldo"].split("/")[1]
        self.assertEqual(json.loads((copia / "docs" / "uxyngraphar.config.json").read_text())["niveles"]["lineas"], "aviso")
        self.assertEqual(json.loads((copia / "_respaldo.json").read_text())["archivos"], ["docs/uxyngraphar.config.json"])

    def test_no_pisa_un_archivo_cambiado_ni_guarda_invalidos(self):
        h = self.huella()
        self.assertIn("cambió", panel.guardar(str(self.repo), "docs", {"limite_lineas": 400}, "otra")["error"])
        self.assertFalse(panel.guardar(str(self.repo), "docs", {"limite_lineas": 10}, h)["ok"])
        self.assertEqual(self.config()["limite_lineas"], 350)

    def test_solo_humano_protege_las_reglas(self):
        self.assertTrue(panel.guardar(str(self.repo), "docs", {"reglas_proyecto": {"cambios_reglas": "solo_humano"}}, self.huella())["ok"])
        self.assertIn("Edit(docs/96-reglas-proyecto/**)", (self.repo / ".claude" / "settings.json").read_text())

    def test_colaborar_si_y_no(self):
        self.assertTrue(panel.colaborar(str(self.repo), "docs", True)["ok"])
        self.assertTrue(self.config()["feedback"]["activo"])
        self.assertTrue(panel.colaborar(str(self.repo), "docs", False)["ok"])
        self.assertEqual(self.config()["feedback"]["respondido"], "no")

    def test_un_agente_no_cambia_nada(self):
        h = self.huella()
        with mock.patch.dict(os.environ, {"CLAUDECODE": "1"}):
            self.assertFalse(panel.guardar(str(self.repo), "docs", {"limite_lineas": 400}, h)["ok"])
            self.assertFalse(panel.colaborar(str(self.repo), "docs", True)["ok"])
            self.assertFalse(panel.guardar_plantilla({"limite_lineas": 400})["ok"])
        self.assertEqual(self.config()["limite_lineas"], 350)


class TestPlantilla(Base):
    def test_plantilla_filtra_valida_y_se_aplica(self):
        r = panel.guardar_plantilla({"niveles": {"idioma": "bloqueante"}, "rol": "cliente", "codigo": {"raices": ["x"]},
                                     "idioma": {"conversacion": "es", "artefactos": "es"}})
        self.assertEqual(r["plantilla"], {"niveles": {"idioma": "bloqueante"}, "idioma": {"conversacion": "es"}})
        self.assertFalse(panel.guardar_plantilla({"limite_lineas": 5})["ok"])
        sim = panel.plantilla_en([{"ruta": str(self.repo), "docs": "docs"}], False)
        self.assertEqual(len(sim["destinos"][0]["cambios"]), 2)
        self.assertEqual(self.config()["niveles"]["idioma"], "aviso", "simular no escribe")
        self.assertEqual(panel.plantilla_al_instalar(self.repo, "docs")[1], "ok")
        self.assertEqual(self.config()["niveles"]["idioma"], "bloqueante")
        self.assertFalse((self.repo / ".uxyngraphar-respaldo").exists(), "al instalar no hace falta copia")

    def test_sin_plantilla_no_hace_nada(self):
        self.assertIsNone(panel.plantilla_al_instalar(self.repo, "docs"))


class TestSistema(Base):
    def test_registro_y_resumen(self):
        self.assertTrue(panel.agregar(str(self.repo))["ok"])
        self.assertEqual(panel.resumen()["proyectos"][0]["packs"][0]["estado"], "al día")
        self.assertFalse(panel.agregar(self.tmp.name)["ok"], "sin uxyngraphar no se registra")
        panel.quitar(str(self.repo.resolve()))
        self.assertEqual(panel.resumen()["proyectos"], [])

    def test_bienvenida_y_path_no(self):
        self.home.mkdir()
        datos = {"version": "1.0.0", "pasos": ["Listo"], "path_pendiente": True, "lanzador": "/x/uxyngraphar"}
        (self.home / "ultima-instalacion.json").write_text(json.dumps(datos))
        with mock.patch.dict(os.environ, {"UXYNGRAPHAR_BIN": str(self.home / "bin")}):
            self.assertTrue(panel.bienvenida()["path_pendiente"])
            self.assertIn("/x/uxyngraphar", panel.decidir_path(False)["texto"])
            self.assertFalse(panel.bienvenida()["path_pendiente"])


class TestHttp(Base):
    def test_rutas_del_panel_con_token(self):
        srv = ThreadingHTTPServer(("127.0.0.1", 0), servidor.crear("tk", lambda: None, "panel"))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{srv.server_address[1]}"
        cuerpo = json.dumps({"ruta": str(self.repo), "docs": "docs"}).encode()
        try:
            self.assertIn("Panel de uxyngraphar", urllib.request.urlopen(base + "/").read().decode())
            self.assertIn("Instalar uxyngraphar", urllib.request.urlopen(base + "/instalar?desde=panel").read().decode())
            with self.assertRaises(urllib.error.HTTPError):
                urllib.request.urlopen(urllib.request.Request(base + "/api/panel/ver", cuerpo, {"X-Token": "otro"}))
            r = urllib.request.urlopen(urllib.request.Request(base + "/api/panel/ver", cuerpo, {"X-Token": "tk"}))
            self.assertTrue(json.loads(r.read())["ok"])
        finally:
            srv.shutdown()
            srv.server_close()


if __name__ == "__main__":
    unittest.main()
