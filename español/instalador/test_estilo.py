"""Pruebas del aspecto de la consola: color solo en terminales, marcas ASCII, tablas ajustadas, ayuda y panel."""

from __future__ import annotations

import io
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

import arranque
import arranque_descarga
import estilo

ES = Path(__file__).resolve().parent.parent


class Terminal(io.StringIO):
    """Un flujo que dice ser una terminal."""

    def __init__(self, encoding: str = "utf-8"):
        super().__init__()
        self._encoding = encoding

    @property
    def encoding(self):
        return self._encoding

    def isatty(self):
        return True


class TestEstilo(unittest.TestCase):
    def setUp(self):
        self.entorno = mock.patch.dict(os.environ, {"TERM": "xterm"})
        self.entorno.start()
        os.environ.pop("NO_COLOR", None)

    def tearDown(self):
        self.entorno.stop()

    def test_sin_color_si_no_es_terminal(self):
        self.assertEqual(estilo.linea("ok", "hecho", "", io.StringIO()), "✓ hecho")
        self.assertNotIn("\x1b", estilo.pintar("x", "error", io.StringIO()))

    def test_color_en_terminal_y_no_color(self):
        t = Terminal()
        self.assertIn("\x1b[32m", estilo.linea("ok", "hecho", "", t))
        with mock.patch.dict(os.environ, {"NO_COLOR": "1"}):
            self.assertEqual(estilo.linea("ok", "hecho", "", t), "✓ hecho")
        with mock.patch.dict(os.environ, {"TERM": "dumb"}):
            self.assertNotIn("\x1b", estilo.pintar("x", "ok", t))

    def test_marcas_ascii_si_la_terminal_no_puede(self):
        t = Terminal("ascii")
        with mock.patch.dict(os.environ, {"NO_COLOR": "1"}):
            self.assertEqual(estilo.marca("ok", t), "+")
            self.assertEqual(estilo.marca("error", t), "x")
        self.assertEqual(estilo.marca("error", io.StringIO()), "✕")

    def test_tabla_se_ajusta_al_ancho(self):
        largo = "palabra " * 30
        lineas = estilo.tabla([("corto", largo), ("una-opcion-muy-larga-que-no-cabe-en-la-columna", "algo")], ancho=60)
        self.assertTrue(all(len(estilo.sin_color(l)) <= 60 for l in lineas), lineas)
        columna = 2 + 60 * 2 // 5 + 3      # sangría + primera columna (tope: 2/5 del ancho) + separación
        self.assertTrue(lineas[0].startswith("  corto" + " " * (columna - 7) + "palabra"), lineas[0])
        self.assertTrue(lineas[1].startswith(" " * columna + "palabra"))   # sangría colgante
        larga = [l for l in lineas if "una-opcion" in l][0]
        self.assertEqual(larga.strip(), "una-opcion-muy-larga-que-no-cabe-en-la-columna")   # descripción en la línea siguiente

    def test_instalador_guarda_pasos_sin_codigos(self):
        arranque_descarga.PASOS.clear()
        with mock.patch.object(sys, "stdout", Terminal()):
            arranque_descarga.decir("  Huella SHA256 verificada.", "ok")
            pantalla = sys.stdout.getvalue()
        self.assertIn("\x1b[", pantalla)
        self.assertIn("✓", pantalla)
        self.assertEqual(arranque_descarga.PASOS, ["  Huella SHA256 verificada."])

    def test_marcas_iguales_en_el_instalador(self):
        self.assertEqual(arranque_descarga.MARCAS, estilo.MARCAS)
        self.assertEqual(arranque_descarga.MARCAS_ASCII, estilo.MARCAS_ASCII)


class TestAyuda(unittest.TestCase):
    def correr(self, *args):
        env = {k: v for k, v in os.environ.items() if k != "NO_COLOR"}
        return subprocess.run([sys.executable, str(ES / "uxyngraphar.py"), *args], capture_output=True, text=True, env=env, encoding="utf-8")

    def test_ayuda_lista_todos_los_comandos_por_grupos(self):
        sys.path.insert(0, str(ES))
        import uxyngraphar
        self.assertEqual(set(uxyngraphar.AYUDA), set(uxyngraphar.COMANDOS))
        self.assertEqual(sorted(c for _, cs in uxyngraphar.GRUPOS for c in cs), sorted(uxyngraphar.COMANDOS))
        r = self.correr()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("\x1b", r.stdout)
        for c in uxyngraphar.COMANDOS:
            self.assertRegex(r.stdout, rf"(?m)^  {c}\b")
        for grupo, _ in uxyngraphar.GRUPOS:
            self.assertIn(grupo, r.stdout)
        self.assertIn("uxyngraphar ayuda <comando>", r.stdout)

    def test_ayuda_de_un_comando(self):
        r = self.correr("ayuda", "instalar")
        self.assertEqual(r.returncode, 0, r.stderr)
        for opcion in ("--pack", "--mismo-repo", "--colaborar", "--consola"):
            self.assertIn(opcion, r.stdout)
        self.assertEqual(self.correr("--help", "nada").returncode, 2)

    def test_comando_desconocido(self):
        r = self.correr("nada")
        self.assertEqual(r.returncode, 2)
        self.assertIn("Comando desconocido: nada", r.stderr)
        self.assertIn("uxyngraphar ayuda", r.stderr)


class TestPanelSoloSiHayCambios(unittest.TestCase):
    def _main(self, codigo):
        with mock.patch.object(arranque, "instalar", return_value=codigo), \
             mock.patch.object(arranque, "puede_abrir_panel", return_value=True), \
             mock.patch.object(arranque, "abrir_panel", return_value=0) as panel, \
             mock.patch.dict(os.environ, {"UXYNGRAPHAR_CONSOLA": ""}):
            r = arranque.main(["--version", "1.0.0"])
        return r, panel.called

    def test_ya_al_dia_no_abre_el_panel(self):
        self.assertEqual(self._main(arranque.SIN_CAMBIOS), (0, False))

    def test_version_nueva_abre_el_panel(self):
        self.assertEqual(self._main(0), (0, True))


if __name__ == "__main__":
    unittest.main()
