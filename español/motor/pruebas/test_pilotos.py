"""Pruebas funcionales de los paquetes piloto, instalados en una app temporal: secretos y instrucciones-aprobadas."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import _rutas  # noqa: F401
import repo


def correr(script: Path, *args: str, cwd: Path, persona: bool | None = None) -> subprocess.CompletedProcess:
    """Sin terminal, como un agente. `persona` (por defecto: si pasa --humano) acredita a una persona con UXYNGRAPHAR_HUMANO=1."""
    entorno = {k: v for k, v in os.environ.items() if k not in ("UXYNGRAPHAR_HUMANO", "CI")}
    if persona if persona is not None else "--humano" in args:
        entorno["UXYNGRAPHAR_HUMANO"] = "1"
    return subprocess.run([sys.executable, "-X", "utf8", str(script), *args], cwd=cwd, capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, env=entorno)


class BaseApp(unittest.TestCase):
    PAQUETES: list[str] = []

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = Path(self.tmp.name) / "app"
        (self.app / "src").mkdir(parents=True)
        repo.instalar(self.app, self.PAQUETES)

    def tearDown(self):
        repo.borrar_arbol(Path(self.tmp.name))
        self.tmp.cleanup()

    def s(self, pid: str, script: str) -> Path:
        scripts = self.app / "uxyngraphar" / "paquetes" / pid / "scripts"
        return scripts / "comun" / script if (scripts / "comun" / script).is_file() else scripts / script


class TestSecretos(BaseApp):
    PAQUETES = ["secretos-y-credenciales"]

    def test_detecta_y_respeta_placeholders(self):
        escanear = self.s("secretos-y-credenciales", "secretos.py")
        (self.app / "src" / "config.ts").write_text("export const key = '<PLACEHOLDER>';\n", encoding="utf-8")
        self.assertEqual(correr(escanear, cwd=self.app).returncode, 0)
        clave = "AKIA" + "ABCDEFGHIJKLMNOP"
        (self.app / "src" / "aws.ts").write_text(f"const awsKey = '{clave}';\n", encoding="utf-8")
        (self.app / ".env").write_text("X=1\n", encoding="utf-8")
        r = correr(escanear, "--informe", cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("src/aws.ts:1: clave AWS", r.stdout)
        self.assertIn(".env: archivo de secretos", r.stdout)
        self.assertNotIn(clave, r.stdout)
        self.assertTrue(list((self.app / "uxyngraphar" / "trabajo" / "secretos-y-credenciales" / "informes").glob("escaneo-*.md")))

    def test_ajustes_del_proyecto(self):
        (self.app / "src" / "aws.ts").write_text("const k = '" + "AKIA" + "ABCDEFGHIJKLMNOP';\n", encoding="utf-8")
        (self.app / "uxyngraphar" / "trabajo" / "secretos-y-credenciales" / "ajustes.json").write_text(json.dumps({"permitir": ["src/aws.ts"]}), encoding="utf-8")
        self.assertEqual(correr(self.s("secretos-y-credenciales", "secretos.py"), cwd=self.app).returncode, 0)


class TestCiclo(BaseApp):
    PAQUETES = ["instrucciones-aprobadas"]

    def nueva(self, slug: str, anclas: list[str]) -> str:
        r = correr(self.s("instrucciones-aprobadas", "fichas.py"), "nueva", "instruccion", "--slug", slug, cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        ruta = Path(r.stdout.strip())
        bloque = "anclas_codigo:\n" + "".join(f"  - {a}\n" for a in anclas)
        ruta.write_text(ruta.read_text(encoding="utf-8").replace("anclas_codigo: []\n", bloque), encoding="utf-8")
        return ruta.stem

    def test_ciclo_completo(self):
        (self.app / "src" / "a.ts").write_text("\n".join(f"line{i}" for i in range(1, 31)), encoding="utf-8")
        fid = self.nueva("cambiar-a", ["src/a.ts:10-12"])
        ciclo = self.s("instrucciones-aprobadas", "ciclo.py")
        self.assertEqual(correr(ciclo, "contexto", fid, cwd=self.app).returncode, 3)
        r = correr(ciclo, "aprobar", fid, cwd=self.app)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("solo lo asigna una persona", r.stderr)
        r = correr(ciclo, "aprobar", fid, "--humano", cwd=self.app, persona=False)
        self.assertEqual(r.returncode, 1, "un agente sin terminal no puede aprobar aunque pase --humano")
        self.assertIn("solo una persona", r.stderr)
        self.assertEqual(correr(ciclo, "aprobar", fid, "--humano", cwd=self.app).returncode, 0)
        r = correr(ciclo, "contexto", fid, cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("   10| line10", r.stdout)
        self.assertNotIn("line13", r.stdout)
        self.assertEqual(correr(ciclo, "cerrar", fid, cwd=self.app).returncode, 0)
        hechas = list((self.app / "uxyngraphar/trabajo/instrucciones-aprobadas/instrucciones/completadas").rglob(f"{fid}.md"))
        self.assertEqual(len(hechas), 1)
        texto = hechas[0].read_text(encoding="utf-8")
        self.assertIn("status: done", texto)
        self.assertNotIn("executed_at: null", texto)
        self.assertEqual(correr(self.s("instrucciones-aprobadas", "verificar-ciclo.py"), cwd=self.app).returncode, 0)
        self.assertEqual(correr(self.s("instrucciones-aprobadas", "verificar.py"), cwd=self.app).returncode, 0)

    def test_alcance_excesivo_no_se_aprueba(self):
        fid = self.nueva("demasiado", [f"src/m{i}.ts" for i in range(7)])
        r = correr(self.s("instrucciones-aprobadas", "ciclo.py"), "aprobar", fid, "--humano", cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("7 archivos de código", r.stderr)
        self.assertEqual(correr(self.s("instrucciones-aprobadas", "verificar-ciclo.py"), cwd=self.app).returncode, 1)


if __name__ == "__main__":
    unittest.main()
