"""Pruebas funcionales de los paquetes temáticos extraídos del 1.x, instalados juntos en una app temporal."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import _rutas  # noqa: F401
import repo
from test_pilotos import correr

PAQUETES = ["calidad-de-codigo", "documentacion-espejo", "mapa-de-modulos", "rutas-de-api", "auditorias-tecnicas", "herramientas-autorizadas",
            "documentos-archivados", "decisiones-de-arquitectura"]


class TestExtraidos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.app = Path(cls.tmp.name) / "app"
        (cls.app / "src" / "orders").mkdir(parents=True)
        repo.instalar(cls.app, PAQUETES)

    @classmethod
    def tearDownClass(cls):
        repo.borrar_arbol(Path(cls.tmp.name))
        cls.tmp.cleanup()

    def s(self, pid: str, script: str) -> Path:
        scripts = self.app / "uxyngraphar" / "paquetes" / pid / "scripts"
        return scripts / "comun" / script if (scripts / "comun" / script).is_file() else scripts / script

    def trabajo(self, pid: str) -> Path:
        return self.app / "uxyngraphar" / "trabajo" / pid

    def escribir(self, ruta: Path, texto: str) -> Path:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(texto, encoding="utf-8")
        return ruta

    def test_calidad_limite_de_lineas(self):
        largo = self.escribir(self.app / "src" / "orders" / "big-service.ts", "export const x = 1;\n" * 351)
        r = correr(self.s("calidad-de-codigo", "calidad.py"), str(largo), cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("351 líneas", r.stdout)
        largo.write_text("export const x = 1;\n" * 10, encoding="utf-8")
        self.assertEqual(correr(self.s("calidad-de-codigo", "calidad.py"), str(largo), cwd=self.app).returncode, 0)

    def test_espejo_cobertura_y_huerfanos(self):
        self.escribir(self.app / "src" / "orders" / "service.ts", "export {};\n")
        r = correr(self.s("documentacion-espejo", "espejo.py"), "nuevo", "src/orders/service.ts", cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.trabajo("documentacion-espejo") / "src/orders/service.md").is_file())
        self.assertEqual(correr(self.s("documentacion-espejo", "verificar-espejo.py"), cwd=self.app).returncode, 0)
        huerfano = self.escribir(self.trabajo("documentacion-espejo") / "src/orders/borrado.md", "# x\n")
        r = correr(self.s("documentacion-espejo", "verificar-espejo.py"), cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("src/orders/borrado.md", r.stderr)
        huerfano.unlink()

    def test_areas_ciclo(self):
        areas = self.trabajo("mapa-de-modulos")
        self.escribir(areas / "a" / "CONTEXTO.md", "---\nid: a\nstatus: active\ndepends_on: [b]\n---\n# A\n")
        self.escribir(areas / "b" / "CONTEXTO.md", "---\nid: b\nstatus: active\ndepends_on: [a]\n---\n# B\n")
        r = correr(self.s("mapa-de-modulos", "verificar-areas.py"), cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("ciclo", r.stderr)
        (areas / "b" / "CONTEXTO.md").write_text("---\nid: b\nstatus: active\ndepends_on: [auth]\n---\n# B\n", encoding="utf-8")
        r = correr(self.s("mapa-de-modulos", "verificar-areas.py"), cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("aún no está documentada", r.stdout)

    def test_rutas_duplicadas(self):
        rutas = self.trabajo("rutas-de-api") / "orders"
        ficha = "---\nid: {i}\nstatus: activa\nmethod: get\npath: /orders\nauth: bearer\n---\n# GET /orders\n"
        self.escribir(rutas / "uno.md", ficha.format(i="uno"))
        self.assertEqual(correr(self.s("rutas-de-api", "verificar-rutas.py"), cwd=self.app).returncode, 0)
        self.escribir(rutas / "dos.md", ficha.format(i="dos").replace("get", "GET"))
        r = correr(self.s("rutas-de-api", "verificar-rutas.py"), cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("GET /orders", r.stderr)
        (rutas / "dos.md").unlink()

    def test_auditoria_severidad(self):
        r = correr(self.s("auditorias-tecnicas", "fichas.py"), "nueva", "auditoria", "--slug", "rendimiento", cwd=self.app)
        ruta = Path(r.stdout.strip())
        texto = ruta.read_text(encoding="utf-8").replace("|---|-----------|----------|-----------|",
                                                         "|---|-----------|----------|-----------|\n| 1 | grave | lento | `src/a.ts:1` |")
        ruta.write_text(texto, encoding="utf-8")
        r = correr(self.s("auditorias-tecnicas", "verificar-auditorias.py"), cwd=self.app)
        self.assertEqual(r.returncode, 1)
        ruta.write_text(texto.replace("| grave |", "| alta |"), encoding="utf-8")
        self.assertEqual(correr(self.s("auditorias-tecnicas", "verificar-auditorias.py"), cwd=self.app).returncode, 0)

    def test_autorizadas_solo_persona(self):
        fichas = self.s("herramientas-autorizadas", "fichas.py")
        r = correr(fichas, "nueva", "autorizada", "--slug", "deploy", cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("solo las crea una persona", r.stderr)
        self.assertEqual(correr(fichas, "nueva", "propuesta", "--slug", "deploy", cwd=self.app).returncode, 0)
        r = correr(self.s("decisiones-de-arquitectura", "fichas.py"), "nueva", "adr", "--slug", "db", cwd=self.app)
        fid = Path(r.stdout.strip()).stem
        self.assertEqual(correr(self.s("decisiones-de-arquitectura", "fichas.py"), "estado", fid, "aceptada", cwd=self.app).returncode, 1)
        self.assertEqual(correr(self.s("decisiones-de-arquitectura", "fichas.py"), "estado", fid, "en-evaluacion", cwd=self.app).returncode, 0)

    def test_archivar_solo_persona(self):
        doc = self.escribir(self.app / "NOTAS.md", "decision: usar postgres\n")
        archivo = self.s("documentos-archivados", "archivo.py")
        self.assertEqual(correr(archivo, "archivar", str(doc), cwd=self.app).returncode, 1)
        self.assertEqual(correr(archivo, "archivar", str(doc), "--humano", cwd=self.app).returncode, 0)
        self.assertIn("postgres", correr(archivo, "buscar", "POSTGRES", "--humano", cwd=self.app).stdout)


if __name__ == "__main__":
    unittest.main()
