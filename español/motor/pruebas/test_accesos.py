"""Pruebas de los accesos directos (Linux, Windows y macOS simulados) y de las preguntas del instalador.
No llama de verdad a gsettings, PowerShell ni defaults: `_acc_ejecutar` se sustituye."""

from __future__ import annotations

import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import _rutas  # noqa: F401

sys.path.insert(0, str(_rutas.MOTOR / "distribucion"))
import accesos  # noqa: E402
import arranque  # noqa: E402


class Simulado(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.t = Path(self._t.name)
        self.home = self.t / "casa"
        (self.home / "versiones" / "9.9.9" / "motor" / "web").mkdir(parents=True)
        (self.home / "versiones" / "9.9.9" / "motor" / "web" / "icono.svg").write_text("<svg/>", encoding="utf-8")
        (self.home / "actual").write_text("9.9.9\n", encoding="utf-8")
        self.lanzador = str(self.t / "bin" / "uxyngraphar")
        self.ordenes: list[list[str]] = []
        self.favoritos = "['org.gnome.Nautilus.desktop']"
        entorno = {"HOME": str(self.t), "XDG_DATA_HOME": str(self.t / "datos"), "XDG_DESKTOP_DIR": str(self.t / "Escritorio"),
                   "XDG_CURRENT_DESKTOP": "ubuntu:GNOME"}
        self.parches = [mock.patch.dict(os.environ, entorno), mock.patch.object(accesos, "_acc_ejecutar", self.ejecutar),
                        mock.patch.object(accesos.shutil, "which", lambda n: "/usr/bin/" + n)]
        for p in self.parches:
            p.start()

    def tearDown(self):
        for p in reversed(self.parches):
            p.stop()
        self._t.cleanup()

    def ejecutar(self, orden):
        self.ordenes.append(orden)
        if orden[:3] == ["gsettings", "get", "org.gnome.shell"]:
            return 0, self.favoritos + "\n"
        if orden[:3] == ["gsettings", "set", "org.gnome.shell"]:
            self.favoritos = orden[4]
            return 0, ""
        if orden[0] == "powershell":
            return 0, "C:\\Usuarios\\x\\uxyngraphar.lnk\n"
        return 0, ""


@unittest.skipIf(os.name == "nt", "simulación de Linux")
class TestLinux(Simulado):
    def test_menu_escritorio_y_favoritos_ida_y_vuelta(self):
        registro: dict = {}
        with mock.patch.object(accesos, "_acc_sistema", lambda: "linux"):
            avisos = accesos.crear_accesos(str(self.home), self.lanzador, ["menu", "escritorio", "barra"], registro)
        self.assertEqual(avisos, [])
        menu = self.t / "datos" / "applications" / "uxyngraphar.desktop"
        escritorio = self.t / "Escritorio" / "uxyngraphar.desktop"
        texto = menu.read_text(encoding="utf-8")
        self.assertIn(f'"{self.lanzador}" panel', texto)
        self.assertIn("Terminal=false", texto)
        self.assertIn("Icon=" + str(self.home / "icono.svg"), texto)
        self.assertTrue(escritorio.is_file() and os.access(escritorio, os.X_OK))
        self.assertIn("uxyngraphar.desktop", self.favoritos)
        self.assertEqual(sorted(a["tipo"] for a in registro["accesos"]), ["barra", "escritorio", "menu"])
        accesos.quitar_accesos(registro)
        self.assertFalse(menu.exists() or escritorio.exists())
        self.assertEqual(self.favoritos, "['org.gnome.Nautilus.desktop']")
        self.assertEqual(registro["accesos"], [])

    def test_no_borra_lo_que_no_es_suyo(self):
        ajeno = self.t / "ajeno.desktop"
        ajeno.write_text("[Desktop Entry]\nName=otro\n", encoding="utf-8")
        accesos.quitar_accesos({"accesos": [{"tipo": "menu", "ruta": str(ajeno)}]})
        self.assertTrue(ajeno.is_file())

    def test_sin_gnome_no_ofrece_anclar(self):
        with mock.patch.dict(os.environ, {"XDG_CURRENT_DESKTOP": "KDE"}), mock.patch.object(accesos, "_acc_sistema", lambda: "linux"):
            barra = [d for d in accesos.accesos_disponibles() if d["tipo"] == "barra"][0]
            self.assertFalse(barra["posible"])
            self.assertTrue(barra["nota"])


class TestOtrosSistemas(Simulado):
    def test_windows_lnk_por_powershell_y_barra_con_instrucciones(self):
        registro: dict = {}
        with mock.patch.object(accesos, "_acc_sistema", lambda: "windows"):
            avisos = accesos.crear_accesos(str(self.home), self.lanzador, ["menu", "barra"], registro)
        self.assertEqual([o[0] for o in self.ordenes], ["powershell"])
        self.assertIn("WScript.Shell", self.ordenes[0][-1])
        self.assertEqual(registro["accesos"], [{"tipo": "menu", "ruta": "C:\\Usuarios\\x\\uxyngraphar.lnk"}])
        self.assertTrue(any("Anclar a la barra de tareas" in a for a in avisos))

    @unittest.skipIf(os.name == "nt", "enlaces simbólicos")
    def test_mac_app_y_dock(self):
        registro: dict = {}
        with mock.patch.object(accesos, "_acc_sistema", lambda: "mac"):
            accesos.crear_accesos(str(self.home), self.lanzador, ["menu", "escritorio", "barra"], registro)
        app = self.t / "Applications" / "uxyngraphar.app"
        self.assertIn(self.lanzador, (app / "Contents" / "MacOS" / "uxyngraphar").read_text(encoding="utf-8"))
        self.assertTrue((self.t / "Escritorio" / "uxyngraphar.app").is_symlink())
        self.assertTrue(any(o[:2] == ["defaults", "write"] for o in self.ordenes))
        accesos.quitar_accesos(registro)
        self.assertFalse(app.exists())


class TestPreguntas(Simulado):
    def test_el_instalador_las_usa(self):
        self.assertIs(arranque.elegir_accesos, accesos.elegir_accesos)

    def test_pedidos_explicitos_no_preguntan(self):
        self.assertEqual(accesos.elegir_accesos(["menu"]), ["menu"])
        self.assertEqual(accesos.elegir_accesos([]), [])

    def test_sin_terminal_lo_deja_para_el_panel(self):
        with mock.patch.object(accesos, "abrir_terminal", lambda: None):
            self.assertIsNone(accesos.elegir_accesos(None))

    def test_pregunta_en_la_terminal_con_valores_por_defecto(self):
        terminal = io.StringIO("\ns\n\n")   # menú: por defecto sí; escritorio: sí; barra: por defecto no
        with mock.patch.object(accesos, "abrir_terminal", lambda: terminal), mock.patch.object(accesos, "_acc_sistema", lambda: "linux"), \
                mock.patch("sys.stdout", io.StringIO()):
            self.assertEqual(accesos.elegir_accesos(None), ["menu", "escritorio"])

    def test_en_ci_no_abre_la_terminal(self):
        with mock.patch.dict(os.environ, {"CI": "true"}):
            self.assertIsNone(accesos.abrir_terminal())


if __name__ == "__main__":
    unittest.main()
