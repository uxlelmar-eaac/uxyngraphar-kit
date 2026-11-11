"""Pruebas del registro de proyectos del panel y de quitar uxyngraphar de un proyecto (repo.desinstalar)."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import _rutas  # noqa: F401
from _sistemas import completar
import catalogo
import generar
import proyectos
import repo

base = catalogo.base


class Entorno(unittest.TestCase):
    """HOME de uxyngraphar y catálogo propios en una carpeta temporal."""

    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.t = Path(self._t.name).resolve()
        self.cat = self.t / "catalogo"
        self.cat.mkdir()
        completar(catalogo.crear("pruebas-demo", "Pruebas demo", "Sistema de prueba", self.cat))
        completar(catalogo.crear("pruebas-otras", "Pruebas otras", "Segundo sistema", self.cat))
        self.parches = [mock.patch.dict(os.environ, {"UXYNGRAPHAR_HOME": str(self.t / "casa")}),
                        mock.patch.object(catalogo.esp, "CATALOGO", self.cat)]
        for p in self.parches:
            p.start()

    def tearDown(self):
        for p in reversed(self.parches):
            p.stop()
        repo.borrar_arbol(self.t)
        self._t.cleanup()

    def repo_git(self, *partes: str) -> Path:
        c = self.t.joinpath(*partes)
        (c / ".git").mkdir(parents=True)
        return c


class TestRegistro(Entorno):
    def test_agregar_quitar_y_formato_1x(self):
        a, b = self.repo_git("trabajo", "beta"), self.repo_git("trabajo", "alfa")
        proyectos.agregar([str(a), str(b), str(a)])
        self.assertEqual(proyectos.listar(), [str(b), str(a)])
        datos = json.loads((self.t / "casa" / "proyectos.json").read_text(encoding="utf-8"))
        self.assertEqual(datos, {"proyectos": [str(b), str(a)]})
        proyectos.quitar(str(a))
        self.assertEqual(proyectos.listar(), [str(b)])
        self.assertTrue(a.is_dir(), "quitar de la lista no toca la carpeta")

    def test_agregar_carpeta_inexistente(self):
        with self.assertRaises(ValueError):
            proyectos.agregar([str(self.t / "no-existe")])

    def test_buscar_no_entra_en_repos_ni_dependencias(self):
        self.repo_git("trabajo", "app")
        self.repo_git("trabajo", "app", "submodulo")
        self.repo_git("trabajo", "node_modules", "sistema")
        self.repo_git("trabajo", ".oculto", "x")
        self.repo_git("otro", "grupo", "api")
        hallados = sorted(Path(p["ruta"]).name for p in proyectos.buscar(str(self.t)))
        self.assertEqual(hallados, ["api", "app"])

    def test_carpetas_para_el_explorador(self):
        self.repo_git("trabajo", "app")
        (self.t / "trabajo" / ".oculta").mkdir()
        r = proyectos.carpetas(str(self.t / "trabajo"))
        self.assertEqual([(c["nombre"], c["repo"]) for c in r["carpetas"]], [("app", True)])
        self.assertEqual(r["padre"], str(self.t))
        with self.assertRaises(ValueError):
            proyectos.carpetas(str(self.t / "no-existe"))

    def test_resumen(self):
        app = self.repo_git("app")
        repo.instalar(app, ["pruebas-demo"], self.cat)
        proyectos.agregar([str(app), str(self.repo_git("vacio"))])
        filas = {Path(p["ruta"]).name: p for p in proyectos.resumenes()}
        self.assertEqual(filas["app"]["sistemas"], ["pruebas-demo"])
        self.assertEqual(filas["app"]["modo"], "manual")
        self.assertEqual(filas["vacio"]["sistemas"], [])
        catalogo.versionar("pruebas-demo", "menor", self.cat)
        self.assertEqual(proyectos.resumen(str(app))["actualizables"], 1)


class TestDesinstalar(Entorno):
    def test_quita_todo_y_conserva_el_trabajo(self):
        app = self.repo_git("app")
        (app / "AGENTES.md").write_text("# Mis reglas\n", encoding="utf-8")
        repo.instalar(app, ["pruebas-demo", "pruebas-otras"], self.cat)
        (app / base.CARPETA_TRABAJO / "pruebas-demo" / "nota.md").write_text("trabajo\n", encoding="utf-8")
        self.assertIn(generar.INICIO, (app / "AGENTES.md").read_text(encoding="utf-8"))
        quitados = repo.desinstalar(app)
        self.assertEqual(sorted(quitados), ["pruebas-demo", "pruebas-otras"])
        self.assertFalse((app / base.CARPETA_SISTEMAS_DE_GOBERNANZA).exists())
        self.assertFalse(generar.ruta_flujo(app).exists())
        self.assertEqual((app / "AGENTES.md").read_text(encoding="utf-8").strip(), "# Mis reglas")
        self.assertFalse((app / "AGENTS.md").exists(), "solo tenía el bloque de uxyngraphar")
        self.assertTrue((app / base.CARPETA_TRABAJO / "pruebas-demo" / "nota.md").is_file())

    def test_con_trabajo_no_deja_carpeta(self):
        app = self.repo_git("app")
        repo.instalar(app, ["pruebas-demo"], self.cat)
        repo.desinstalar(app, con_trabajo=True)
        self.assertFalse((app / base.CARPETA_RAIZ).exists())
        self.assertFalse((app / ".claude").exists())

    def test_respeta_reglas_propias_de_claude(self):
        app = self.repo_git("app")
        (app / ".claude").mkdir()
        (app / ".claude" / "settings.json").write_text('{"permissions": {"deny": ["Read(.env)"]}}', encoding="utf-8")
        repo.instalar(app, ["pruebas-demo"], self.cat)
        repo.desinstalar(app)
        self.assertIn("Read(.env)", (app / ".claude" / "settings.json").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
