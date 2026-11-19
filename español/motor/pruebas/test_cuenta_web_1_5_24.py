"""1.5.24: lo encontrado probando con una cuenta real (archivar un borrador que solo está en la web)."""

from __future__ import annotations

import contextlib
import io

import _rutas  # noqa: F401
import cli
from test_proyectos import Entorno


class TestArchivarSoloWeb(Entorno):
    def _cli(self, *args: str) -> str:
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            self.assertEqual(cli.main(list(args)), 0)
        return salida.getvalue()

    def test_mensaje_segun_este_o_no_en_el_catalogo(self):
        self.assertIn("sigue en tu catálogo", self._cli("archivar", "pruebas-demo"))
        texto = self._cli("archivar", "borrador-solo-web")
        self.assertIn("olvidado en el Taller de este equipo", texto)
        self.assertNotIn("sigue en tu catálogo", texto)
        self.assertIn("de vuelta en el Taller", self._cli("desarchivar", "borrador-solo-web"))
