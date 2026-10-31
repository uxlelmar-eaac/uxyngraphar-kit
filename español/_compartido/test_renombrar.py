"""Pruebas de la herramienta de renombre global de marca (marca ficticia: marcavieja -> marcanueva)."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("renombrar", Path(__file__).resolve().parent / "renombrar-marca.py")
rm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rm)

PARES = rm.variantes("marcavieja", "marcanueva")
SOPORTE = (".git", ".atl", "odd", "node_modules", "__pycache__")


class TestRenombrar(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self.tmp.name)
        (self.raiz / "docs" / "marcavieja-utils").mkdir(parents=True)
        (self.raiz / "docs" / "marcavieja-utils" / "guia.md").write_text("usa marcavieja y Marcavieja\nMARCAVIEJA_OK=1\n")
        (self.raiz / "Instalar-Marcavieja.txt").write_text("echo marcavieja")
        (self.raiz / "bin.pyc").write_bytes(b"\x00marcavieja\x00")

    def tearDown(self):
        self.tmp.cleanup()

    def test_simulacro_no_toca_nada(self):
        guia = self.raiz / "docs" / "marcavieja-utils" / "guia.md"
        antes = guia.read_bytes()
        plan = rm.planificar(self.raiz, PARES)
        self.assertEqual(sum(sum(c.values()) for _, c in plan["cambios"]), 4)
        self.assertEqual(len(plan["renombrar"]), 2)  # la carpeta y el .txt; guia.md no lleva marca en el nombre
        self.assertEqual(guia.read_bytes(), antes)

    def test_aplicar_reemplaza_y_renombra_profundo_primero(self):
        plan = rm.aplicar(self.raiz, PARES)
        self.assertEqual(plan["colisiones"], [])
        guia = self.raiz / "docs" / "marcanueva-utils" / "guia.md"
        self.assertEqual(guia.read_text(), "usa marcanueva y marcanueva\nMARCANUEVA_OK=1\n")
        self.assertEqual((self.raiz / "Instalar-marcanueva.txt").read_text(), "echo marcanueva")
        self.assertEqual((self.raiz / "bin.pyc").read_bytes(), b"\x00marcavieja\x00")  # binario intacto
        self.assertFalse((self.raiz / "docs" / "marcavieja-utils").exists())

    def test_excluye_carpetas_de_soporte(self):
        for nombre in SOPORTE:
            d = self.raiz / nombre
            d.mkdir()
            (d / "f.md").write_text("marcavieja")
        plan = rm.aplicar(self.raiz, PARES)
        for nombre in SOPORTE:
            self.assertEqual((self.raiz / nombre / "f.md").read_text(), "marcavieja")
        self.assertEqual(sum(sum(c.values()) for _, c in plan["cambios"]), 4)

    def test_colision_no_escribe_nada(self):
        (self.raiz / "docs" / "marcanueva-utils").mkdir()  # el destino de la carpeta ya existe
        plan = rm.aplicar(self.raiz, PARES)
        self.assertTrue(plan["colisiones"])
        guia = self.raiz / "docs" / "marcavieja-utils" / "guia.md"
        self.assertEqual(guia.read_text(), "usa marcavieja y Marcavieja\nMARCAVIEJA_OK=1\n")
        self.assertTrue((self.raiz / "Instalar-Marcavieja.txt").exists())

    def test_capitalizar_opcional(self):
        pares = rm.variantes("marcavieja", "marcanueva", capitalizar=True)
        rm.aplicar(self.raiz, pares)
        guia = self.raiz / "docs" / "marcanueva-utils" / "guia.md"
        self.assertIn("y Marcanueva\n", guia.read_text())
        self.assertTrue((self.raiz / "Instalar-Marcanueva.txt").exists())


class TestMain(unittest.TestCase):
    def test_rechaza_nombres_invalidos(self):
        self.assertEqual(rm.main(["--desde", "marcavieja", "--hacia", "marcavieja"]), 1)
        self.assertEqual(rm.main(["--desde", "marcavieja", "--hacia", "la-marcavieja-x"]), 1)
        self.assertEqual(rm.main(["--desde", "MarcaVieja", "--hacia", "marcanueva"]), 1)

    def test_raiz_inexistente(self):
        self.assertEqual(rm.main(["--desde", "marcavieja", "--hacia", "marcanueva", "--raiz", "no/existe"]), 1)


if __name__ == "__main__":
    unittest.main()
