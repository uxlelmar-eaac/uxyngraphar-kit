"""Fallos vistos usando la 1.5.16 como una persona normal (contenedor limpio, Python 3.10): cada prueba los reproduce."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import _rutas  # noqa: F401
import catalogo
import cli
import desinstalacion
import nomenclatura
import uxyngraphar
from test_informe_qa_1_5_15 import SinCatalogoElegido, salida, sistema_de_autor

base = catalogo.base


class TestCrearConPrimeraPalabraCorta(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.cat = Path(self._t.name)

    def tearDown(self):
        self._t.cleanup()

    def test_prefijo_de_ids_con_primera_palabra_corta(self):
        self.assertEqual(nomenclatura.proponer_prefijo("mi-sistema", set()), "MIS")
        self.assertEqual(nomenclatura.proponer_prefijo("ux-ab", set()), "UXA")
        # Lo que ya funcionaba no cambia de prefijo.
        self.assertEqual(nomenclatura.proponer_prefijo("contratos-de-pago", set()), "CON")
        self.assertEqual(nomenclatura.proponer_prefijo("revision-de-pagos", set()), "REV")

    def test_crear_mi_sistema(self):
        c = catalogo.crear("mi-sistema", "Mi sistema", "", self.cat, familia="proceso")
        m = json.loads((c / base.MANIFIESTO).read_text(encoding="utf-8"))
        self.assertTrue(all(nomenclatura.PREFIJO.match(f["prefijo"]) for f in m["fichas"].values()), m["fichas"])

    def test_crear_que_falla_no_deja_restos(self):
        with mock.patch.object(catalogo, "_agregar_pieza", side_effect=ValueError("falla a propósito")), \
                self.assertRaises(ValueError):
            catalogo.crear("mi-sistema", "Mi sistema", "", self.cat)
        self.assertFalse((self.cat / "mi-sistema").exists(), "no queda una carpeta a medias")
        catalogo.crear("mi-sistema", "Mi sistema", "", self.cat)   # y reintentar ya no dice «ya existe»


class TestMensajesVacios(SinCatalogoElegido):
    def test_nomenclatura_sin_pendientes_lo_dice(self):
        codigo, out, _ = salida(cli.main, ["nomenclatura"])
        self.assertEqual(codigo, 0)
        self.assertIn("Nada pendiente", out)

    def test_deshacer_lista_sin_respaldos_lo_dice(self):
        proyecto = self.t / "proyecto"
        (proyecto / ".git").mkdir(parents=True)
        codigo, out, _ = salida(cli.main, ["deshacer", "--repo", str(proyecto), "--lista"])
        self.assertEqual(codigo, 0)
        self.assertIn("No hay cambios que deshacer", out)

    def test_desinstalar_con_un_sistema_en_singular(self):
        sistema_de_autor(self.home / "catalogo", "mio")
        codigo, _, err = salida(uxyngraphar.main, ["desinstalar", "--alcance", "herramienta", "--si"])
        self.assertEqual(codigo, 2)
        self.assertIn("se borraría 1 sistema que escribiste", err)
        with self.assertRaisesRegex(desinstalacion.CatalogoSinConfirmar, "se borraría 1 sistema que"):
            desinstalacion.ejecutar("herramienta")
        sistema_de_autor(self.home / "catalogo", "otro")
        self.assertIn("se borrarían 2 sistemas que escribiste", salida(uxyngraphar.main, ["desinstalar", "--alcance", "herramienta", "--si"])[2])


class TestOpcionesDeSubcomandos(unittest.TestCase):
    def test_buscar_familia_inexistente(self):
        codigo, out, err = salida(cli.main, ["buscar", "--familia", "nada"])
        self.assertEqual(codigo, 2)
        self.assertEqual(out, "")
        self.assertIn("uxyngraphar buscar: error: --familia", err)
        for familia in nomenclatura.NORMA["familias"]:
            self.assertIn(familia, err)

    def test_opcion_desconocida_da_el_uso_del_subcomando(self):
        for args, orden in ((["buscar", "--nada"], "uxyngraphar buscar"), (["estado", "--zzz"], "uxyngraphar estado"),
                            (["creador", "modelos", "--x"], "uxyngraphar creador modelos"),
                            (["catalogo", "extra"], "uxyngraphar catalogo")):
            codigo, out, err = salida(cli.main, args)
            self.assertEqual(codigo, 2, args)
            self.assertEqual(out, "", args)
            self.assertIn(f"uso: {orden} [-h]", err, args)
            self.assertIn(f"{orden}: error:", err, args)
            self.assertIn(args[-1], err, args)
            self.assertIn(f"{orden} --help", err, args)
            self.assertNotIn("COMANDO ...", err, args)

    def test_por_el_lanzador_tambien(self):
        codigo, _, err = salida(uxyngraphar.main, ["buscar", "--nada"])
        self.assertEqual(codigo, 2)
        self.assertIn("uxyngraphar buscar: error: opción desconocida: --nada", err)


if __name__ == "__main__":
    unittest.main()
