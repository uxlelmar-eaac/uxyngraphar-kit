"""El catálogo real cumple el protocolo de paquetes (ESPECIFICACION.md §2) y las pruebas propias de cada paquete pasan."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest

import _rutas  # noqa: F401
import catalogo
import entrada
import piezas

base = catalogo.base
esp = catalogo.esp


class TestEstandar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paquetes = {m["id"]: (catalogo.carpeta(m["id"]), base.leer_manifiesto(catalogo.carpeta(m["id"])))
                        for m in catalogo.listar()}

    def test_nucleo_y_formato(self):
        for pid, (c, m) in self.paquetes.items():
            with self.subTest(paquete=pid):
                self.assertEqual(m["manifiesto_formato"], base.FORMATO_MANIFIESTO)
                for nombre in base.NUCLEO:
                    self.assertTrue((c / nombre).is_file(), nombre)
                self.assertTrue(base.ids_problemas(m), "alcance.problemas vacío")
                self.assertTrue(entrada.al_dia(c), "bloque de entrada del README desfasado")

    def test_estructura_regida_por_el_manifiesto(self):
        for pid, (c, m) in self.paquetes.items():
            with self.subTest(paquete=pid):
                permitidos = base.RESERVADOS | {r.strip("/") for r in m.get("extensiones") or {}}
                sobrantes = [p.name for p in c.iterdir() if p.name not in permitidos
                             and not base.IGNORAR.search(p.name) and not p.name.startswith(".")]
                self.assertEqual(sobrantes, [])
                for pieza in m["piezas"]:
                    self.assertTrue((c / base.PIEZAS[pieza]).exists(), pieza)

    def test_derivaciones_apuntan_al_catalogo(self):
        for pid, (_, m) in self.paquetes.items():
            for tema in m["alcance"]["fuera_de_alcance"]:
                if tema["derivar_a"] is not None:
                    with self.subTest(paquete=pid, tema=tema["tema"]):
                        self.assertIn(tema["derivar_a"], self.paquetes)
                        self.assertNotEqual(tema["derivar_a"], pid)

    def test_skills_solo_dentro_del_paquete(self):
        for pid, (c, m) in self.paquetes.items():
            with self.subTest(paquete=pid):
                self.assertFalse((c / ".cursor").exists() or (c / ".claude").exists())
                if "skills" in m["piezas"]:
                    self.assertTrue(piezas.skills_declaradas(c))

    def test_especializados(self):
        for pid, (_, m) in self.paquetes.items():
            with self.subTest(paquete=pid):
                self.assertLessEqual(len(base.ids_problemas(m)), piezas.MAX_PROBLEMAS)

    def test_piloto_usa_todas_las_piezas(self):
        _, m = self.paquetes["arquitectura-monolitica-por-capas"]
        self.assertEqual(m["piezas"], list(base.PIEZAS))


class TestPruebasDeCadaPaquete(unittest.TestCase):
    def test_pruebas_propias(self):
        entorno = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        for m in catalogo.listar():
            c = catalogo.carpeta(m["id"])
            if "pruebas" not in base.leer_manifiesto(c)["piezas"]:
                continue
            with self.subTest(paquete=m["id"]):
                r = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "pruebas", "-t", "pruebas"],
                                   cwd=c, capture_output=True, text=True, stdin=subprocess.DEVNULL, env=entorno)
                self.assertEqual(r.returncode, 0, r.stderr[-2000:])


if __name__ == "__main__":
    unittest.main()
