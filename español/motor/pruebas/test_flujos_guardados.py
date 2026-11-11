"""Pruebas de los flujos guardados: guardar, validar, aplicar a proyectos, duplicar, exportar e importar."""

from __future__ import annotations

import unittest

import _rutas  # noqa: F401
import flujos_guardados as guardados
import generar
import repo
from test_proyectos import Entorno

SECUENCIA = {"formato": 1, "modo": "secuencia", "leer_por_defecto": [], "trabajar_con": None,
             "secuencia": ["pruebas-otras", "pruebas-demo"], "conflictos": "preguntar"}


class TestFlujosGuardados(Entorno):
    def nuevo(self, nombre="API con revisión", **extra) -> str:
        return guardados.guardar({"nombre": nombre, "sistemas": ["pruebas-demo", "pruebas-otras"], "flujo": SECUENCIA, **extra})

    def test_guardar_listar_y_id_legible(self):
        fid = self.nuevo()
        self.assertEqual(fid, "api-con-revision")
        self.assertEqual(self.nuevo(), "api-con-revision-2")
        lista = guardados.listar()
        self.assertEqual([g["id"] for g in lista], ["api-con-revision", "api-con-revision-2"])
        self.assertEqual(lista[0]["flujo"]["secuencia"], ["pruebas-otras", "pruebas-demo"])

    def test_validacion(self):
        with self.assertRaisesRegex(ValueError, "nombre"):
            guardados.guardar({"nombre": " ", "sistemas": [], "flujo": {}})
        with self.assertRaisesRegex(ValueError, "no están en el catálogo"):
            guardados.guardar({"nombre": "x", "sistemas": ["no-existe"], "flujo": {}})
        with self.assertRaisesRegex(ValueError, "no está en el flujo"):
            guardados.guardar({"nombre": "x", "sistemas": ["pruebas-demo"], "flujo": SECUENCIA})
        with self.assertRaises(ValueError):
            guardados.leer("../fuera")

    def test_aplicar_instala_lo_que_falta_y_escribe_el_flujo(self):
        fid = self.nuevo()
        a, b = self.repo_git("a"), self.repo_git("b")
        repo.instalar(b, ["pruebas-demo"], self.cat)
        r = {x["ruta"]: x for x in guardados.aplicar(fid, [str(a), str(b), str(self.t / "no-existe")])}
        self.assertEqual(sorted(r[str(a)]["instalados"]), ["pruebas-demo", "pruebas-otras"])
        self.assertEqual(r[str(b)]["instalados"], ["pruebas-otras"])
        self.assertTrue(r[str(self.t / "no-existe")]["error"])
        for c in (a, b):
            self.assertEqual(generar.leer_flujo(c)["secuencia"], ["pruebas-otras", "pruebas-demo"])

    def test_desde_proyecto(self):
        app = self.repo_git("app")
        repo.instalar(app, ["pruebas-demo"], self.cat, sistema_base="pruebas-demo")
        g = guardados.leer(guardados.desde_proyecto(app, "Base demo", "con sistema base"))
        self.assertEqual((g["sistemas"], g["flujo"]["modo"], g["flujo"]["trabajar_con"]), (["pruebas-demo"], "trabajar_con", "pruebas-demo"))

    def test_editar_duplicar_borrar_exportar_importar(self):
        fid = self.nuevo()
        self.assertEqual(guardados.guardar({**guardados.leer(fid), "descripcion": "cambiada"}), fid)
        self.assertEqual(guardados.leer(fid)["descripcion"], "cambiada")
        copia = guardados.duplicar(fid)
        self.assertEqual(guardados.leer(copia)["nombre"], "API con revisión (copia)")
        exportado = guardados.exportar(fid)
        self.assertNotIn("id", exportado)
        guardados.borrar(fid)
        self.assertEqual(guardados.importar(exportado), fid)
        with self.assertRaises(FileNotFoundError):
            guardados.borrar("no-existe")


if __name__ == "__main__":
    unittest.main()
