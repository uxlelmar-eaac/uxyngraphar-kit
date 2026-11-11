"""Prueba obligatoria del catálogo: cada sistema fuente, copiado tal cual y SOLO a una app vacía, funciona igual.

Por sistema: copiar sistemas-de-gobernanza/<id>/ a <app>/uxyngraphar/sistemas-de-gobernanza/<id>/ (sin motor, sin AGENTES, sin otros sistemas)
+ INTEGRIDAD.json → integridad,
fichas de cada tipo y verificaciones → nada escrito fuera de <app>/uxyngraphar/trabajo/<id>/ → solo imports locales o stdlib.
"""

from __future__ import annotations

import ast
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import _rutas  # noqa: F401
from _sistemas import completar
import catalogo
import repo

base = catalogo.base


def correr(script: Path, *args: str, cwd: Path, persona: bool | None = None) -> subprocess.CompletedProcess:
    """Sin terminal, como un agente. `persona` (por defecto: si pasa --humano) acredita a una persona con UXYNGRAPHAR_HUMANO=1."""
    entorno = {k: v for k, v in os.environ.items() if k not in ("UXYNGRAPHAR_HUMANO", "CI")}
    if persona if persona is not None else "--humano" in args:
        entorno["UXYNGRAPHAR_HUMANO"] = "1"
    return subprocess.run([sys.executable, "-X", "utf8", str(script), *args], cwd=cwd, capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, env=entorno)


def foto(carpeta: Path, excluir: Path) -> dict[str, bytes]:
    return {p.relative_to(carpeta).as_posix(): p.read_bytes() for p in carpeta.rglob("*")
            if p.is_file() and excluir not in p.parents and "__pycache__" not in p.parts}


class TestPortabilidad(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        # el kit llega sin sistemas: uno de prueba hecho con _base mantiene la prueba aunque el catálogo esté vacío
        cat = Path(cls.tmp.name) / "catalogo"
        cat.mkdir()
        completar(catalogo.crear("pruebas-portabilidad", "Pruebas portabilidad", "Sistema de prueba", cat))
        cls.casos = {m["id"]: None for m in catalogo.listar()} | {"pruebas-portabilidad": cat}

    @classmethod
    def tearDownClass(cls):
        repo.borrar_arbol(Path(cls.tmp.name))
        cls.tmp.cleanup()

    def test_catalogo_valida(self):
        for m in catalogo.listar():
            self.assertEqual(m["errores"], [], m["id"])
            self.assertEqual(m["avisos"], [], m["id"])

    def test_cada_sistema_aislado(self):
        for pid, cat in self.casos.items():
            with self.subTest(sistema=pid):
                self._probar(pid, cat)

    def _probar(self, pid: str, cat: Path | None) -> None:
        app = Path(self.tmp.name) / f"app-{pid}"
        (app / "src").mkdir(parents=True)
        (app / "src" / "index.ts").write_text("export const greeting = 'hello';\n", encoding="utf-8")
        # la construcción (con scripts/comun de _base e INTEGRIDAD.json), como se instala: la fuente no versiona comun (M-06)
        sistema = catalogo.construir(pid, app / "uxyngraphar" / "sistemas-de-gobernanza", cat)
        repo.solo_lectura(sistema)
        ajeno = Path(self.tmp.name) / "otro-cwd"
        ajeno.mkdir(exist_ok=True)
        trabajo = app / "uxyngraphar" / "trabajo" / pid
        antes = foto(app, trabajo)

        r = correr(sistema / "scripts" / "comun" / "verificar-integridad.py", cwd=ajeno)
        self.assertEqual(r.returncode, 0, r.stderr)
        for v in base.leer_manifiesto(sistema)["verificaciones"]:
            r = correr(sistema / v, cwd=ajeno)
            self.assertEqual(r.returncode, 0, f"{v}: {r.stdout}\n{r.stderr}")
        for tipo, d in base.leer_manifiesto(sistema).get("fichas", {}).items():
            humano = ["--humano"] if d["inicial"] in d.get("solo_humano", []) else []
            r = correr(sistema / "scripts" / "comun" / "fichas.py", "nueva", tipo, "--slug", "prueba-portabilidad", *humano, cwd=ajeno)
            self.assertEqual(r.returncode, 0, f"{tipo}: {r.stderr}")
            self.assertTrue(Path(r.stdout.strip()).resolve().is_relative_to(trabajo.resolve()), r.stdout)
        r = correr(sistema / "scripts" / "comun" / "verificar.py", cwd=ajeno)
        self.assertEqual(r.returncode, 0, f"fichas recién creadas: {r.stdout}\n{r.stderr}")

        self.assertEqual(foto(app, trabajo), antes, "el sistema escribió fuera de uxyngraphar/trabajo/<id>/")
        self.assertTrue(base.integro(base.comprobar_integridad(sistema)), "el sistema se modificó a sí mismo")
        self.assertEqual([p for p in sistema.rglob("__pycache__")], [], "el sistema dejó cachés dentro de sí")
        self._imports_locales(sistema)

    def _imports_locales(self, sistema: Path) -> None:
        locales = {p.stem for p in (sistema / "scripts").rglob("*.py")}
        permitidos = set(sys.stdlib_module_names) | locales | {"__future__"}
        for py in sistema.rglob("*.py"):
            arbol = ast.parse(py.read_text(encoding="utf-8"))
            for nodo in ast.walk(arbol):
                nombres = [a.name for a in nodo.names] if isinstance(nodo, ast.Import) else \
                          [nodo.module or ""] if isinstance(nodo, ast.ImportFrom) and not nodo.level else []
                for n in nombres:
                    self.assertIn(n.split(".")[0], permitidos, f"{py.name} importa «{n}» (fuera del sistema y de la stdlib)")
            self.assertNotIn("uxyngraphar-kit", py.read_text(encoding="utf-8"), py.name)


if __name__ == "__main__":
    unittest.main()
