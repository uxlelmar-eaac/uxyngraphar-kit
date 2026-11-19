"""El CLI explica lo que pasa en vez de quedarse callado o responder en inglés (hallazgos de la 1.5.14)."""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import _rutas  # noqa: F401
import catalogo
import cli


class TestMensajesDelCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cat = Path(self.tmp.name) / "sistemas-de-gobernanza"
        self.cat.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def correr(self, *argv: str) -> tuple[int, str, str]:
        salida, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(err), \
                mock.patch.object(catalogo.esp, "CATALOGO", self.cat):
            codigo = cli.main(list(argv))
        return codigo, salida.getvalue(), err.getvalue()

    def test_catalogo_y_validar_vacios_lo_dicen(self):
        for orden in ("catalogo", "validar"):
            codigo, texto, _ = self.correr(orden)
            self.assertEqual(codigo, 0, orden)
            self.assertIn("catálogo local está vacío", texto, orden)

    def test_validar_id_desconocido_falla_y_lo_dice(self):
        codigo, _, err = self.correr("validar", "no-existe")
        self.assertEqual(codigo, 1)
        self.assertIn("no están en el catálogo local: no-existe", err)

    def test_conexiones_sin_accion_es_ver(self):
        with mock.patch("conexiones.resumen", return_value=[]):
            codigo, _, err = self.correr("conexiones")
        self.assertEqual(codigo, 0)
        self.assertNotIn("required", err)


if __name__ == "__main__":
    unittest.main()
