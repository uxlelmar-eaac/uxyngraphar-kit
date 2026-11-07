"""Pruebas propias del paquete: ajustes locales, huella y recordatorio de reglas en una app temporal (sin el motor)."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
PAQUETE = Path(__file__).resolve().parents[1]
ID = PAQUETE.name


def correr(script: Path, *args: str, cwd: Path, humano: bool = False) -> subprocess.CompletedProcess:
    env = {"PYTHONDONTWRITEBYTECODE": "1", "PATH": os.environ.get("PATH", "")}
    if humano:
        env["UXYNGRAPHAR_HUMANO"] = "1"
    return subprocess.run([sys.executable, str(script), *args], cwd=cwd, capture_output=True, text=True,
                          env=env, stdin=subprocess.DEVNULL)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = Path(self.tmp.name)
        self.paquete = self.app / "uxyngraphar" / "paquetes" / ID
        shutil.copytree(PAQUETE, self.paquete, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "pruebas"))
        self.s = self.paquete / "scripts"
        self.otro = self.app / "uxyngraphar" / "paquetes" / "otro-paquete"
        self.otro.mkdir(parents=True)
        (self.otro / "paquete.json").write_text('{"id": "otro-paquete"}', encoding="utf-8")
        (self.otro / "README.md").write_text("# Otro\n\n1. Ejecuta npm test.\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def nueva(self, slug: str, campos: dict[str, str]) -> str:
        ruta = Path(correr(self.s / "comun" / "fichas.py", "nueva", "ajuste", "--slug", slug, cwd=self.app).stdout.strip())
        texto = ruta.read_text(encoding="utf-8")
        for clave, valor in campos.items():
            texto = re.sub(rf"(?m)^{clave}:.*$", lambda _: f"{clave}: {valor}", texto, count=1)
        ruta.write_text(texto, encoding="utf-8")
        return ruta.stem

    def ajustes(self, pid: str = "otro-paquete") -> str:
        return correr(self.s / "adaptaciones.py", "ajustes", pid, cwd=self.app).stdout

    def aprobar(self, fid: str, humano: bool = True) -> subprocess.CompletedProcess:
        args = ["aprobar-ajuste", fid] + (["--humano"] if humano else [])
        return correr(self.s / "adaptaciones.py", *args, cwd=self.app, humano=humano)


class TestAjustes(Base):
    def test_ajuste_local_y_huella(self):
        fid = self.nueva("pnpm", {"paquete": "otro-paquete", "aplica_a": "README.md"})
        rel = Path("uxyngraphar/trabajo") / ID / "ajustes-locales" / f"{fid}.md"
        self.assertTrue((self.app / rel).is_file())
        self.assertIn("otro-paquete: 0 ajustes locales activos", self.ajustes())
        self.assertNotEqual(self.aprobar(fid, humano=False).returncode, 0)
        self.assertEqual(self.aprobar(fid).returncode, 0)
        self.assertRegex((self.app / rel).read_text(encoding="utf-8"), r"huella: [0-9a-f]{64}")
        r = self.ajustes()
        self.assertIn(f"## {fid} → manda sobre otro-paquete/README.md\n", r)
        self.assertIn("otro-paquete: 1 ajustes locales activos", r)
        self.assertNotIn("POR REVISAR", r)
        self.assertIn("0 errores, 0 avisos", correr(self.s / "verificar-adaptaciones.py", cwd=self.app).stdout)

    def test_ajuste_desfasado_queda_por_revisar(self):
        fid = self.nueva("pnpm", {"paquete": "otro-paquete", "aplica_a": "README.md"})
        self.assertEqual(self.aprobar(fid).returncode, 0)
        (self.otro / "README.md").write_text("# Otro\n\n1. Ejecuta pnpm test.\n", encoding="utf-8")
        self.assertIn("(POR REVISAR: por revisar; síguelo y avisa a la persona)", self.ajustes())
        r = correr(self.s / "verificar-adaptaciones.py", cwd=self.app)
        self.assertEqual(r.returncode, 0)
        self.assertIn("cambió desde que se aprobó", r.stdout)
        self.assertEqual(self.aprobar(fid).returncode, 0)
        self.assertNotIn("POR REVISAR", self.ajustes())

    def test_ajuste_sin_paquete(self):
        fid = self.nueva("pnpm", {"paquete": "otro-paquete", "aplica_a": "README.md"})
        self.assertEqual(self.aprobar(fid).returncode, 0)
        shutil.rmtree(self.otro)
        self.assertIn("POR REVISAR: sin paquete", self.ajustes())
        self.assertIn("no está instalado", correr(self.s / "verificar-adaptaciones.py", cwd=self.app).stdout)

    def test_no_aprueba_si_el_archivo_no_existe(self):
        fid = self.nueva("falta", {"paquete": "otro-paquete", "aplica_a": "proceso/no-existe.md"})
        r = self.aprobar(fid)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("no existe", r.stderr)


class TestReglasDelProyecto(Base):
    def test_recuerda_reglas_activas_solo_si_esta_instalado(self):
        reglas = self.app / "uxyngraphar" / "trabajo" / "reglas-del-proyecto" / "reglas"
        reglas.mkdir(parents=True)
        (reglas / "REG-20261106-a.md").write_text("---\nid: REG-20261106-a\nstatus: activa\n---\n# A\n", encoding="utf-8")
        (reglas / "REG-20261106-b.md").write_text("---\nid: REG-20261106-b\nstatus: propuesta\n---\n# B\n", encoding="utf-8")
        self.assertNotIn("reglas del proyecto activas", self.ajustes())
        (self.app / "uxyngraphar" / "paquetes" / "reglas-del-proyecto").mkdir()
        self.assertIn("otro-paquete: 0 ajustes locales activos · 1 reglas del proyecto activas", self.ajustes())


if __name__ == "__main__":
    unittest.main()
