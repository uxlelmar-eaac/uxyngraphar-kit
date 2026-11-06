"""Pruebas funcionales de los paquetes nuevos (no extraídos del 1.x): paginas-de-aterrizaje-bento y experiencia-de-usuario."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import _rutas  # noqa: F401
import repo
from test_pilotos import correr

MOSAICO_BIEN = """| 1 | 2x2 | 1 | Cobra en 2 minutos | Sin contratos ni permanencia | primario | img: panel de cobros en un móvil |
| 2 | 2x1 | 2 | Pagos en 30 países | Monedas locales y conversión automática | - | icono |
| 3 | 1x1 | 3 | Soporte 24/7 | Personas reales | - | - |
| 4 | 1x1 | 4 | Seguro | Cifrado de extremo a extremo | - | - |
| 5 | 4x1 | 5 | Empieza hoy | Cuenta gratis en un minuto | secundario | - |
"""
PROBLEMAS = """| 1 | H9 | 3 | El error del formulario no dice qué campo falla | `src/form.tsx:40` | Mensaje junto al campo | sí |
"""
METRICAS = "| Pasos del alta | 7 | 4 | {despues} | conteo manual |\n"


class TestNuevos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.app = Path(cls.tmp.name) / "app"
        cls.app.mkdir()
        repo.instalar(cls.app, ["paginas-de-aterrizaje-bento", "experiencia-de-usuario"])

    @classmethod
    def tearDownClass(cls):
        repo.borrar_arbol(Path(cls.tmp.name))
        cls.tmp.cleanup()

    def s(self, pid: str, script: str) -> Path:
        scripts = self.app / "uxyngraphar" / "paquetes" / pid / "scripts"
        return scripts / "comun" / script if (scripts / "comun" / script).is_file() else scripts / script

    def nueva(self, pid: str, tipo: str, slug: str) -> Path:
        r = correr(self.s(pid, "fichas.py"), "nueva", tipo, "--slug", slug, "--titulo", slug, cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        (ruta,) = (self.app / "uxyngraphar" / "trabajo" / pid).rglob(f"*{slug}*.md")
        return ruta

    def estado(self, pid: str, ruta: Path, nuevo: str, humano: bool = False) -> Path:
        fid = ruta.stem
        r = correr(self.s(pid, "fichas.py"), "estado", fid, nuevo, *(["--humano"] if humano else []), cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        (ruta,) = (self.app / "uxyngraphar" / "trabajo" / pid).rglob(f"{fid}.md")
        return ruta

    @staticmethod
    def rellenar(ruta: Path, titulo_tabla: str, filas: str) -> None:
        texto = ruta.read_text(encoding="utf-8")
        cabecera, resto = texto.split(f"## {titulo_tabla}\n", 1)
        bloque, despues = resto.split("\n\n", 1)
        ruta.write_text(f"{cabecera}## {titulo_tabla}\n{bloque}\n{filas}\n{despues}", encoding="utf-8")

    def test_bento_mosaico_y_checklist(self):
        pid = "paginas-de-aterrizaje-bento"
        ficha = self.nueva(pid, "landing", "inicio")
        r = correr(self.s(pid, "verificar-bento.py"), cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("mosaico está vacío", r.stdout)
        ficha = self.estado(pid, ficha, "en-curso")
        r = correr(self.s(pid, "verificar-bento.py"), cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.rellenar(ficha, "Mosaico", MOSAICO_BIEN)
        r = correr(self.s(pid, "verificar-bento.py"), cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        malo = MOSAICO_BIEN.replace("| 4x1 | 5 | Empieza hoy | Cuenta gratis en un minuto | secundario", "| 2x1 | 5 | Empieza hoy | Cuenta gratis en un minuto | primario")
        texto = ficha.read_text(encoding="utf-8")
        ficha.write_text(texto.replace(MOSAICO_BIEN, malo), encoding="utf-8")
        r = correr(self.s(pid, "verificar-bento.py"), cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("exactamente un CTA primario", r.stderr)
        self.assertIn("huecos", r.stderr)
        ficha.write_text(texto, encoding="utf-8")
        ficha = self.estado(pid, ficha, "revision")
        r = correr(self.s(pid, "verificar-bento.py"), cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("checklist incompleta", r.stderr)
        ficha.write_text(ficha.read_text(encoding="utf-8").replace("- [ ]", "- [x]"), encoding="utf-8")
        self.assertEqual(correr(self.s(pid, "verificar-bento.py"), cwd=self.app).returncode, 0)
        r = correr(self.s(pid, "fichas.py"), "estado", ficha.stem, "publicada", cwd=self.app)
        self.assertNotEqual(r.returncode, 0)
        self.estado(pid, ficha, "publicada", humano=True)
        self.assertEqual(correr(self.s(pid, "verificar.py"), cwd=self.app).returncode, 0)

    def test_ux_aprobacion_y_metricas(self):
        pid = "experiencia-de-usuario"
        ficha = self.nueva(pid, "evaluacion", "alta-usuario")
        self.assertEqual(correr(self.s(pid, "verificar-ux.py"), cwd=self.app).returncode, 0)
        self.rellenar(ficha, "Problemas", PROBLEMAS)
        ficha = self.estado(pid, ficha, "propuesta")
        r = correr(self.s(pid, "verificar-ux.py"), cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("aprueba una persona", r.stderr)
        self.assertIn("sin métricas", r.stderr)
        self.rellenar(ficha, "Métricas", METRICAS.format(despues=""))
        self.assertEqual(correr(self.s(pid, "verificar-ux.py"), cwd=self.app).returncode, 1)
        r = correr(self.s(pid, "fichas.py"), "estado", ficha.stem, "aprobada", cwd=self.app)
        self.assertNotEqual(r.returncode, 0)
        ficha = self.estado(pid, ficha, "aprobada", humano=True)
        self.assertEqual(correr(self.s(pid, "verificar-ux.py"), cwd=self.app).returncode, 0)
        ficha = self.estado(pid, ficha, "implementada")
        ficha = self.estado(pid, ficha, "validada", humano=True)
        r = correr(self.s(pid, "verificar-ux.py"), cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("sin Después", r.stderr)
        ficha.write_text(ficha.read_text(encoding="utf-8").replace("| 7 | 4 |  |", "| 7 | 4 | 4 |"), encoding="utf-8")
        r = correr(self.s(pid, "verificar-ux.py"), cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_ux_severidad_alta_sin_propuesta(self):
        pid = "experiencia-de-usuario"
        ficha = self.nueva(pid, "evaluacion", "checkout")
        self.rellenar(ficha, "Problemas", "| 1 | H5 | 4 | Se puede pagar dos veces | `src/pay.ts:12` | - | |\n| 2 | H99 | 9 | x | - | - | |\n")
        r = correr(self.s(pid, "verificar-ux.py"), cwd=self.app)
        self.assertEqual(r.returncode, 1)
        for esperado in ("severidad 4 sin propuesta", "heurística «H99»", "severidad «9»", "sin evidencia"):
            self.assertIn(esperado, r.stderr)
        ficha.unlink()


if __name__ == "__main__":
    unittest.main()
