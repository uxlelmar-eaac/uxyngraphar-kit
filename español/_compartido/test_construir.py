"""Pruebas del constructor de packs desde la fuente compartida."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location("construir", Path(__file__).resolve().parent / "construir-packs.py")
cp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cp)


class TestConstruir(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        self.base, self.packs, self.man = t / "base", t / "packs", t / "generados.txt"
        (self.base / "scripts").mkdir(parents=True)
        (self.base / "scripts" / "a.py").write_text("A")
        (self.base / "x.md").write_text("X")
        for p in ("uno", "dos"):
            (self.packs / p).mkdir(parents=True)
            (self.packs / p / "propio.md").write_text(p)
        self.args = (self.packs, ("uno", "dos"), self.base, self.man)

    def tearDown(self):
        self.tmp.cleanup()

    def test_construye_y_es_idempotente(self):
        plan = cp.construir(*self.args)
        self.assertEqual(len(plan["escribir"]), 4)
        self.assertEqual((self.packs / "dos" / "scripts" / "a.py").read_text(), "A")
        self.assertEqual((self.packs / "uno" / "propio.md").read_text(), "uno")   # lo específico no se toca
        self.assertEqual(cp.planificar(*self.args), {"escribir": [], "borrar": [], "colisiones": []})

    def test_detecta_deriva_y_la_corrige(self):
        cp.construir(*self.args)
        (self.packs / "uno" / "x.md").write_text("editado a mano")
        self.assertEqual(cp.planificar(*self.args)["escribir"], [("uno", "x.md")])
        cp.construir(*self.args)
        self.assertEqual((self.packs / "uno" / "x.md").read_text(), "X")

    def test_colision_con_archivo_especifico_no_escribe_nada(self):
        (self.packs / "uno" / "x.md").write_text("específico")
        plan = cp.construir(*self.args)
        self.assertEqual(plan["colisiones"], [("uno", "x.md")])
        self.assertFalse((self.packs / "dos" / "x.md").exists())

    def test_borra_lo_que_deja_de_ser_compartido(self):
        cp.construir(*self.args)
        (self.base / "x.md").unlink()
        plan = cp.construir(*self.args)
        self.assertEqual(sorted(plan["borrar"]), [("dos", "x.md"), ("uno", "x.md")])
        self.assertFalse((self.packs / "uno" / "x.md").exists())
        self.assertTrue((self.packs / "uno" / "propio.md").exists())


class TestFuenteParcial(unittest.TestCase):
    """Las pruebas de _compartido/base/scripts no se ejecutan como si fuera un pack: se omiten con el motivo."""

    def test_ejecutar_pruebas_desde_la_fuente_se_omite(self):
        import subprocess
        import sys
        script = Path(__file__).resolve().parent / "base" / "scripts" / "ejecutar-pruebas.py"
        r = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Omitido", r.stdout)
        self.assertIn("construir-packs.py", r.stdout)


if __name__ == "__main__":
    unittest.main()
