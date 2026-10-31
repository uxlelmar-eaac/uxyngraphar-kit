"""Pruebas de la herramienta «uxyngraphar» instalada: proyectos, estado, autoactualizar, usar y desinstalar."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

from test_arranque import VERSION, WINDOWS, Entorno, arranque


def _siguiente(version: str) -> str:
    mayor, menor, _ = version.split(".")
    return f"{mayor}.{int(menor) + 1}.0"


class TestHerramienta(Entorno):
    def _instalar_herramienta(self) -> None:
        self.servir()
        r = self.por_tuberia(self.instalador())
        self.assertEqual(r.returncode, 0, r.stdout.decode() + r.stderr.decode())

    def _proyecto(self, nombre: str = "api") -> Path:
        p = self.t / nombre
        p.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=p, check=True)
        (p / "go.mod").write_text("module x\n")
        return p

    def _version_proyecto(self, p: Path) -> str:
        import json
        return json.loads((p / "docs" / ".uxyngraphar.lock").read_text(encoding="utf-8"))["version"]

    def test_ciclo_completo(self):
        self._instalar_herramienta()
        p = self._proyecto()
        r = self.uxyngraphar("instalar", str(p), "--si")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Proyecto registrado", r.stdout)
        self.assertEqual(self._version_proyecto(p), VERSION)

        r = self.uxyngraphar("estado", str(p))
        self.assertIn("al día", r.stdout)
        r = self.uxyngraphar("proyectos")
        self.assertIn(str(p.resolve()), r.stdout)

        nueva = _siguiente(VERSION)               # se publica una versión nueva
        self.servir(nueva)
        r = self.uxyngraphar("autoactualizar")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((self.uxy / "actual").read_text().strip(), nueva)
        self.assertEqual(self._version_proyecto(p), VERSION, "autoactualizar no debe tocar los proyectos")

        r = self.uxyngraphar("estado", str(p))
        self.assertIn("puedes actualizarlo", r.stdout)
        r = self.uxyngraphar("actualizar", "--todos", "--consola", "--si")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self._version_proyecto(p), nueva)

        r = self.uxyngraphar("usar", VERSION)      # vuelve a la anterior, guardada en el equipo (sin red)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((self.uxy / "actual").read_text().strip(), VERSION)
        r = self.uxyngraphar("estado", str(p))
        self.assertIn("más nueva que tu herramienta", r.stdout)

        perfil = None if WINDOWS else self.perfil()
        r = self.uxyngraphar("desinstalar", "--si")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse(self.uxy.exists())
        self.assertFalse(self.lanzador().exists())
        if not WINDOWS:
            self.assertNotIn(arranque.BLOQUE_INI, perfil.read_text())
        self.assertTrue((p / "docs" / ".uxyngraphar.lock").is_file(), "desinstalar no debe tocar los proyectos")

    def test_configuracion_del_proyecto(self):
        self._instalar_herramienta()
        p = self._proyecto()
        self.assertEqual(self.uxyngraphar("instalar", str(p), "--si").returncode, 0)
        archivo = p / "docs" / "uxyngraphar.config.json"
        self.assertTrue(archivo.is_file(), "el instalador debe crear el archivo de configuración del proyecto")
        r = self.uxyngraphar("configuracion", str(p))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('"go"', r.stdout)                      # pila detectada
        self.assertIn("configuracion-uxyngraphar.md", r.stdout)
        self.assertTrue((p / "docs" / "10-guias" / "configuracion-uxyngraphar.md").is_file())
        archivo.write_text('{"limite_lineas": 10}\n', encoding="utf-8")   # valor inválido: se informa, no se rompe
        r = self.uxyngraphar("configuracion", str(p))
        self.assertEqual(r.returncode, 1)
        self.assertIn("limite_lineas", r.stdout)

    def test_comando_desconocido_y_ayuda(self):
        self._instalar_herramienta()
        self.assertEqual(self.uxyngraphar("nada").returncode, 2)
        r = self.uxyngraphar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("autoactualizar", r.stdout)

    def test_proyecto_sin_pack(self):
        self._instalar_herramienta()
        p = self._proyecto("vacio")
        r = self.uxyngraphar("estado", str(p))
        self.assertEqual(r.returncode, 1)
        self.assertIn("uxyngraphar instalar", r.stdout)
        r = self.uxyngraphar("proyectos", "--agregar", str(p))
        self.assertEqual(r.returncode, 1)

    def test_lanzador_roto_explica(self):
        self._instalar_herramienta()
        (self.uxy / "actual").write_text("0.0.0\n")
        r = self.uxyngraphar("version")
        self.assertEqual(r.returncode, 1)
        self.assertIn("comando de instalación", r.stderr)


if __name__ == "__main__":
    unittest.main()
