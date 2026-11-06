"""Prueba obligatoria del catálogo: cada paquete, copiado SOLO a una app vacía, funciona igual.

Por paquete: construir → copiar a <app>/uxyngraphar/<id>/ (sin motor, sin AGENTES, sin otros paquetes) → integridad,
fichas de cada tipo y verificaciones → nada escrito fuera de <app>/uxyngraphar/trabajo/<id>/ → solo imports locales o stdlib.
"""

from __future__ import annotations

import ast
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import _rutas  # noqa: F401
import catalogo
import repo

base = catalogo.base


def correr(script: Path, *args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-X", "utf8", str(script), *args], cwd=cwd, capture_output=True, text=True)


def foto(carpeta: Path, excluir: Path) -> dict[str, bytes]:
    return {p.relative_to(carpeta).as_posix(): p.read_bytes() for p in carpeta.rglob("*")
            if p.is_file() and excluir not in p.parents and "__pycache__" not in p.parts}


class TestPortabilidad(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dist = Path(cls.tmp.name) / "dist"
        cls.ids = [m["id"] for m in catalogo.listar()]

    @classmethod
    def tearDownClass(cls):
        repo.borrar_arbol(Path(cls.tmp.name))
        cls.tmp.cleanup()

    def test_catalogo_valida(self):
        self.assertTrue(self.ids, "el catálogo está vacío")
        for m in catalogo.listar():
            self.assertEqual(m["errores"], [], m["id"])

    def test_cada_paquete_aislado(self):
        for pid in self.ids:
            with self.subTest(paquete=pid):
                self._probar(pid)

    def _probar(self, pid: str) -> None:
        construido = catalogo.construir(pid, self.dist)
        app = Path(self.tmp.name) / f"app-{pid}"
        (app / "src").mkdir(parents=True)
        (app / "src" / "index.ts").write_text("export const greeting = 'hello';\n", encoding="utf-8")
        paquete = app / "uxyngraphar" / "paquetes" / pid
        shutil.copytree(construido, paquete)
        repo.solo_lectura(paquete)
        ajeno = Path(self.tmp.name) / "otro-cwd"
        ajeno.mkdir(exist_ok=True)
        trabajo = app / "uxyngraphar" / "trabajo" / pid
        antes = foto(app, trabajo)

        r = correr(paquete / "scripts" / "comun" / "verificar-integridad.py", cwd=ajeno)
        self.assertEqual(r.returncode, 0, r.stderr)
        for v in base.leer_manifiesto(paquete)["verificaciones"]:
            r = correr(paquete / v, cwd=ajeno)
            self.assertEqual(r.returncode, 0, f"{v}: {r.stdout}\n{r.stderr}")
        for tipo, d in base.leer_manifiesto(paquete).get("fichas", {}).items():
            humano = ["--humano"] if d["inicial"] in d.get("solo_humano", []) else []
            r = correr(paquete / "scripts" / "comun" / "fichas.py", "nueva", tipo, "--slug", "prueba-portabilidad", *humano, cwd=ajeno)
            self.assertEqual(r.returncode, 0, f"{tipo}: {r.stderr}")
            self.assertTrue(Path(r.stdout.strip()).resolve().is_relative_to(trabajo.resolve()), r.stdout)
        r = correr(paquete / "scripts" / "comun" / "verificar.py", cwd=ajeno)
        self.assertEqual(r.returncode, 0, f"fichas recién creadas: {r.stdout}\n{r.stderr}")

        self.assertEqual(foto(app, trabajo), antes, "el paquete escribió fuera de uxyngraphar/trabajo/<id>/")
        self.assertTrue(base.integro(base.comprobar_integridad(paquete)), "el paquete se modificó a sí mismo")
        self.assertEqual([p for p in paquete.rglob("__pycache__")], [], "el paquete dejó cachés dentro de sí")
        self._imports_locales(paquete)

    def _imports_locales(self, paquete: Path) -> None:
        locales = {p.stem for p in (paquete / "scripts").rglob("*.py")}
        permitidos = set(sys.stdlib_module_names) | locales | {"__future__"}
        for py in paquete.rglob("*.py"):
            arbol = ast.parse(py.read_text(encoding="utf-8"))
            for nodo in ast.walk(arbol):
                nombres = [a.name for a in nodo.names] if isinstance(nodo, ast.Import) else \
                          [nodo.module or ""] if isinstance(nodo, ast.ImportFrom) and not nodo.level else []
                for n in nombres:
                    self.assertIn(n.split(".")[0], permitidos, f"{py.name} importa «{n}» (fuera del paquete y de la stdlib)")
            self.assertNotIn("uxyngraphar-kit", py.read_text(encoding="utf-8"), py.name)


if __name__ == "__main__":
    unittest.main()
