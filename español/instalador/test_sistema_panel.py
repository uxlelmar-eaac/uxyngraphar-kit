"""Pruebas de la pestaña «Sistema» del panel (api_sistema): versiones, PATH, limpieza, desinstalar y reinicio tras actualizar."""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import time
import unittest
import urllib.request
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import api_sistema as sis  # noqa: E402
import servidor  # noqa: E402
import sistema  # noqa: E402

PERSONA = {k: "" for k in ("CI", "GITHUB_ACTIONS", "GITLAB_CI", "BUILDKITE", "JENKINS_URL", "CLAUDECODE", "UXYNGRAPHAR_AGENTE")}
# Un «uxyngraphar.py» mínimo: como el de verdad con `panel --fondo`, escribe su dirección donde dice UXYNGRAPHAR_PANEL_URL.
FALSO = ("import os, sys\nfrom pathlib import Path\nif sys.argv[1:] == ['panel', '--fondo']:\n"
         "    Path(os.environ['UXYNGRAPHAR_PANEL_URL']).write_text('http://127.0.0.1:1/?tab=sistema', encoding='utf-8')\n")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / "home"
        self.home.mkdir()
        self.env = mock.patch.dict(os.environ, {**PERSONA, "UXYNGRAPHAR_HOME": str(self.home), "UXYNGRAPHAR_BIN": "",
                                                "SHELL": "/bin/bash", "HOME": self.tmp.name})
        self.env.start()
        os.environ.pop("UXYNGRAPHAR_BIN")

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def version(self, v: str, cli: str = FALSO) -> None:
        carpeta = self.home / "versiones" / v
        carpeta.mkdir(parents=True)
        (carpeta / ".completa").write_text("")
        (carpeta / "uxyngraphar.py").write_text(cli)

    def agente(self):
        return mock.patch.dict(os.environ, {"CLAUDECODE": "1"})


class TestVersiones(Base):
    def test_info_y_usar_una_guardada(self):
        self.version("1.0.0")
        self.version("1.2.0")
        (self.home / "actual").write_text("1.2.0\n")
        i = sis.info()
        self.assertEqual((i["activa"], i["guardadas"]), ("1.2.0", ["1.0.0", "1.2.0"]))
        self.assertFalse(sis.usar("1.0")["ok"], "formato X.Y.Z")
        with self.agente():
            self.assertFalse(sis.usar("1.0.0")["ok"])
        r = sis.usar("v1.0.0")
        self.assertTrue(r["ok"], r)
        self.assertFalse(r["reiniciable"], "un panel anterior a 1.2.0 no sabe arrancar en segundo plano")
        self.assertEqual((self.home / "actual").read_text().strip(), "1.0.0")

    def test_usar_una_que_no_esta_la_descarga(self):
        with mock.patch.object(sis.panel, "ejecutar_herramienta", return_value={"ok": True, "salida": "Listo"}) as ej:
            r = sis.usar("1.3.0")
        self.assertTrue(r["ok"] and r["reiniciable"], r)
        self.assertEqual(ej.call_args.args[0], ["autoactualizar", "--version", "1.3.0"])
        with mock.patch.object(sis.panel, "ejecutar_herramienta", return_value={"ok": False, "error": "sin red"}):
            self.assertFalse(sis.usar("1.3.0")["ok"])


class TestReinicio(Base):
    def test_arranca_el_panel_nuevo_y_devuelve_su_direccion(self):
        self.version("1.2.0")
        (self.home / "actual").write_text("1.2.0\n")
        r = sis.reiniciar(espera=20)
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["url"], "http://127.0.0.1:1/?tab=sistema")
        self.assertEqual(list(self.home.glob(".panel-*.url")), [], "el aviso se borra")

    def test_no_reinicia_versiones_viejas_ni_sin_persona(self):
        self.version("1.1.0")
        (self.home / "actual").write_text("1.1.0\n")
        self.assertIn("vuelve a abrirlo", sis.reiniciar()["error"])
        with self.agente():
            self.assertFalse(sis.reiniciar()["ok"])

    def test_tarda_demasiado(self):
        self.version("1.2.0", "import time\ntime.sleep(5)\n")
        (self.home / "actual").write_text("1.2.0\n")
        self.assertIn("no respondió", sis.reiniciar(espera=0.5)["error"])

    @unittest.skipIf(os.name == "nt", "un enlace simbólico en Windows pide permisos")
    def test_panel_real_en_segundo_plano(self):
        (self.home / "versiones").mkdir()
        (self.home / "versiones" / "1.2.0").symlink_to(sistema.ES, target_is_directory=True)   # la herramienta de este repositorio
        (self.home / "actual").write_text("1.2.0\n")
        r = sis.reiniciar(espera=30)
        self.assertTrue(r["ok"], r)
        html = urllib.request.urlopen(r["url"], timeout=10).read().decode()
        token = re.search(r'const TOKEN="([^"]+)"', html).group(1)
        base = r["url"].split("?")[0]
        hecho = urllib.request.urlopen(urllib.request.Request(base + "api/salir", b"{}", {"X-Token": token}), timeout=10)
        self.assertTrue(json.loads(hecho.read())["ok"])
        time.sleep(0.5)
        with self.assertRaises(OSError):
            urllib.request.urlopen(base, timeout=3)


class TestPathLimpiezaDesinstalar(Base):
    def test_path_con_carpeta_propia_no_se_toca(self):
        r = sis.path(True)
        self.assertFalse(r["ok"])
        self.assertIn("UXYNGRAPHAR_HOME", r["error"])

    @unittest.skipIf(os.name == "nt", "el PATH de Windows vive en el registro")
    def test_path_anadir_y_quitar(self):
        with mock.patch.dict(os.environ, {"UXYNGRAPHAR_BIN": str(self.home / "bin"), "PATH": "/usr/bin"}):
            self.assertTrue(sis.path(True)["ok"])
            perfil = Path(self.tmp.name) / ".bashrc"
            self.assertIn(">>> uxyngraphar >>>", perfil.read_text())
            self.assertTrue(sis.info()["path_nuestro"])
            with self.agente():
                self.assertFalse(sis.path(False)["ok"])
            self.assertIn("Quité", sis.path(False)["texto"])
            self.assertNotIn("uxyngraphar", perfil.read_text())

    def test_limpiar_registro_y_candado(self):
        vivo = Path(self.tmp.name) / "vivo"
        (vivo / "uxyngraphar").mkdir(parents=True)
        (vivo / "uxyngraphar" / ".uxyngraphar.lock").write_text(json.dumps({"version": "1.1.0", "pack": "backend"}))
        sistema.guardar_proyectos([str(vivo), str(Path(self.tmp.name) / "borrado")])
        candado = self.home / ".instalando"
        candado.write_text("")
        os.utime(candado, (time.time() - 3600, time.time() - 3600))
        v = sis.limpiar(False)
        self.assertEqual([x["ruta"] for x in v["rotos"]], [str(Path(self.tmp.name) / "borrado")])
        self.assertTrue(v["candado"]["abandonado"])
        self.assertTrue(candado.is_file(), "ver no cambia nada")
        with self.agente():
            self.assertFalse(sis.limpiar(True)["ok"])
        self.assertTrue(sis.limpiar(True)["candado_quitado"])
        self.assertEqual(sistema.leer_proyectos(), [str(vivo)])
        self.assertFalse(candado.exists())

    def test_desinstalar_exige_escribirlo_y_cierra_el_panel(self):
        self.version("1.2.0")
        self.assertFalse(sis.desinstalar("si")["ok"])
        with self.agente():
            self.assertFalse(sis.desinstalar("desinstalar")["ok"])
        apagado = []
        rutas = servidor.rutas_sistema(lambda: apagado.append(True))
        r = rutas["/api/sistema/desinstalar"]({"confirmacion": "desinstalar"})
        self.assertTrue(r["ok"], r)
        self.assertFalse(self.home.exists())
        self.assertEqual(apagado, [True])
        self.assertIn("se desinstaló", servidor.ESTADO["despedida"])
        servidor.ESTADO["despedida"] = ""


if __name__ == "__main__":
    unittest.main()
