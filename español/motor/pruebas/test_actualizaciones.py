"""Actualizaciones que nunca dejan la herramienta rota, de punta a punta: paso desde el legado, número de versión repetido,
release rota, versión activa perdida (plan B y reparar), vuelta a una versión anterior con datos más nuevos y
desinstalación completa. Cada prueba usa un HOME falso y una «release» servida en 127.0.0.1."""

from __future__ import annotations

import json
import re
import shutil
import unittest
from pathlib import Path

from test_instalador import VERSION, WINDOWS, Entorno

import arranque

FORMATO_CASA = int(re.search(r"^FORMATO_CASA = (\d+)$", (Path(__file__).resolve().parents[1] / "casa.py").read_text(encoding="utf-8"), re.M).group(1))
SIGUIENTE = ".".join(VERSION.split(".")[:2] + [str(int(VERSION.split(".")[2]) + 1)])


def romper_arranque(motor: Path) -> None:
    with open(motor / "reparacion.py", "a", encoding="utf-8") as f:
        f.write("\nraise RuntimeError('release rota a propósito')\n")


def formato_2(motor: Path) -> None:
    casa = motor / "casa.py"
    texto = casa.read_text(encoding="utf-8")
    texto = texto.replace("FORMATO_CASA = 2\n", "FORMATO_CASA = 3\n").replace("MIGRACIONES = {1: _a_1, 2: _a_2}",
                                                                          "MIGRACIONES = {1: _a_1, 2: _a_2, 3: lambda: None}")
    casa.write_text(texto, encoding="utf-8")


@unittest.skipIf(WINDOWS, "el legado y el lanzador se simulan con rutas de Linux/macOS")
class TestActualizaciones(Entorno):
    def instalar(self, version: str = VERSION, *args: str, codigo: int = 0) -> str:
        r = self.por_tuberia(self.instalador(version), *args)
        salida = r.stdout.decode() + r.stderr.decode()
        self.assertEqual(r.returncode, codigo, salida)
        return salida

    def actual(self) -> str:
        return (self.uxy / "actual").read_text(encoding="utf-8").strip()

    def registro(self) -> dict:
        return json.loads((self.uxy / "instalacion.json").read_text(encoding="utf-8"))

    def legado(self, *versiones: str) -> Path:
        """Una casa como la que dejaban los instaladores antiguos 1.0.0–1.2.4: .completa en texto plano, uxyngraphar.py
        en la raíz de la versión y el comando en ~/.local/bin."""
        for v in versiones:
            carpeta = self.uxy / "versiones" / v
            carpeta.mkdir(parents=True)
            (carpeta / ".completa").write_text(v + "\n", encoding="utf-8")
            (carpeta / "uxyngraphar.py").write_text("print('uxyngraphar del legado')\n", encoding="utf-8")
        (self.uxy / "actual").write_text(versiones[-1] + "\n", encoding="utf-8")
        lanzador = self.lanzador()
        lanzador.parent.mkdir(parents=True)
        lanzador.write_text(f"#!/usr/bin/python3\n# {arranque.MARCA}: lo creó el instalador de uxyngraphar.\nimport runpy\n", encoding="utf-8")
        (self.uxy / "instalacion.json").write_text(json.dumps({"lanzadores": [str(lanzador)]}), encoding="utf-8")
        (self.uxy / "proyectos.json").write_text(json.dumps({"proyectos": ["/no/existe"]}), encoding="utf-8")
        return lanzador

    def test_desde_el_legado_con_numero_repetido_y_vuelta_atras(self):
        self.legado(VERSION, "1.2.4")
        self.servir()
        salida = self.instalar()
        self.assertIn("del legado", salida)
        for v in (VERSION, "1.2.4"):
            self.assertTrue((self.uxy / "legado" / v / "uxyngraphar.py").is_file(), v)
        marca = json.loads((self.uxy / "versiones" / VERSION / ".completa").read_text(encoding="utf-8"))
        self.assertEqual((marca["linea"], marca["version"]), ("uxyngraphar", VERSION))
        self.assertEqual(self.actual(), VERSION)
        self.assertEqual(self.registro()["ultima_buena"], VERSION)
        self.assertEqual(json.loads((self.uxy / "proyectos.json").read_text())["proyectos"], ["/no/existe"])
        self.assertEqual(json.loads((self.uxy / "casa.json").read_text())["formato"], FORMATO_CASA)
        self.assertIn(f"uxyngraphar {VERSION}", self.uxyngraphar("version").stdout)
        self.assertFalse((self.uxy / "bin" / "uxyngraphar").exists(), "un solo comando: el de ~/.local/bin")

        self.servir(SIGUIENTE)
        self.instalar(SIGUIENTE)
        self.assertEqual(self.actual(), SIGUIENTE)
        self.assertEqual(self.registro()["anterior"], VERSION)
        self.assertTrue(list((self.uxy / "respaldos").glob("casa-*")), "se respaldan los datos antes de cambiar de versión")
        r = self.uxyngraphar("usar", "anterior")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.actual(), VERSION)
        self.assertIn(f"uxyngraphar {VERSION}", self.uxyngraphar("version").stdout)

    def test_release_rota_no_se_activa(self):
        self.servir()
        self.instalar()
        self.servir(SIGUIENTE, cambiar=romper_arranque)
        salida = self.instalar(SIGUIENTE, codigo=1)
        self.assertIn("comprobación de arranque", salida)
        self.assertEqual(self.actual(), VERSION)
        self.assertFalse((self.uxy / "versiones" / SIGUIENTE).exists())
        self.assertFalse(list((self.uxy / "versiones").glob("*.tmp")))
        self.assertEqual(self.uxyngraphar("version").returncode, 0)

    def test_version_activa_perdida_plan_b_y_reparar(self):
        self.servir()
        self.instalar()
        self.servir(SIGUIENTE)
        self.instalar(SIGUIENTE)
        (self.uxy / "versiones" / SIGUIENTE / ".completa").unlink()   # como si se hubiera cortado o borrado a mano
        (self.uxy / "versiones" / f"{SIGUIENTE}.tmp").mkdir()
        r = self.uxyngraphar("version")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"uxyngraphar {VERSION}", r.stdout, "el comando sigue funcionando con la última buena")
        self.assertIn("reparar", r.stderr)
        r = self.uxyngraphar("reparar")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.actual(), SIGUIENTE)
        r = self.uxyngraphar("version")
        self.assertIn(f"uxyngraphar {SIGUIENTE}", r.stdout)
        self.assertEqual(r.stderr, "")
        self.assertFalse((self.uxy / "versiones" / f"{SIGUIENTE}.tmp").exists())

    def test_reparar_desde_el_instalador_si_no_arranca_nada(self):
        self.servir()
        self.instalar()
        (self.uxy / "versiones" / VERSION / "motor" / "uxyngraphar.py").unlink()
        self.assertNotEqual(self.uxyngraphar("version").returncode, 0)
        self.assertIn("reparado", self.instalar(VERSION, "--reparar"))
        self.assertIn(f"uxyngraphar {VERSION}", self.uxyngraphar("version").stdout)

    def test_volver_a_una_version_con_datos_mas_nuevos(self):
        self.servir()
        self.instalar()
        self.servir(SIGUIENTE, cambiar=formato_2)
        self.instalar(SIGUIENTE)
        self.assertEqual(json.loads((self.uxy / "casa.json").read_text())["formato"], FORMATO_CASA + 1)
        r = self.uxyngraphar("usar", VERSION)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(json.loads((self.uxy / "casa.json").read_text())["formato"], FORMATO_CASA, "restaura el respaldo compatible")

        self.assertEqual(self.uxyngraphar("usar", SIGUIENTE).returncode, 0)
        shutil.rmtree(self.uxy / "respaldos")   # sin respaldo compatible: no se cambia y no se rompe nada
        r = self.uxyngraphar("usar", VERSION)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("más nueva", r.stdout + r.stderr)
        self.assertEqual(self.actual(), SIGUIENTE)
        self.assertIn(f"uxyngraphar {SIGUIENTE}", self.uxyngraphar("version").stdout)

    def test_desinstalar_todo_no_deja_nada(self):
        self.servir()
        self.instalar()
        proyecto = self.t / "proyecto"
        (proyecto / "uxyngraphar" / "trabajo").mkdir(parents=True)
        (proyecto / "codigo.py").write_text("x = 1\n")
        (self.uxy / "proyectos.json").write_text(json.dumps({"proyectos": [str(proyecto)]}), encoding="utf-8")
        simulado = self.uxyngraphar("desinstalar", "--alcance", "todo", "--simular")
        self.assertEqual(simulado.returncode, 0, simulado.stdout + simulado.stderr)
        self.assertIn("simulación", simulado.stdout)
        self.assertTrue(self.uxy.is_dir())
        self.assertEqual(self.uxyngraphar("desinstalar", "--alcance", "todo").returncode, 2, "sin --si ni terminal no borra nada")
        r = self.uxyngraphar("desinstalar", "--alcance", "todo", "--si")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("no queda nada", r.stdout)
        self.assertFalse(self.uxy.exists())
        self.assertFalse(self.lanzador().exists())
        self.assertNotIn(arranque.BLOQUE_INI, (self.home / ".bashrc").read_text() if (self.home / ".bashrc").exists() else "")
        self.assertTrue((proyecto / "codigo.py").is_file(), "el código del proyecto no se toca")
        self.assertTrue((proyecto / "uxyngraphar" / "trabajo").is_dir(), "el trabajo se conserva sin --con-trabajo")


if __name__ == "__main__":
    unittest.main()
