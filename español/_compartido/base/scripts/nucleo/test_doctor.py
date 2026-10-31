#!/usr/bin/env python3
"""Pruebas del doctor."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import doctor as dr  # noqa: E402
import lock  # noqa: E402
from test_nucleo import Base  # noqa: E402


class TestDoctor(Base):
    def setUp(self) -> None:
        super().setUp()
        self.instalar()

    def niveles(self, **kw):  # type: ignore[no-untyped-def]
        return {c.id: c.nivel for c in dr.diagnosticar(self.repo, "docs", **kw)}

    def test_instalacion_nueva_sin_errores_con_avisos_de_proteccion(self) -> None:
        n = self.niveles(pack=self.pack)
        self.assertNotIn("ERROR", n.values())
        self.assertEqual((n["nucleo"], n["version"], n["lock"]), ("OK", "OK", "OK"))
        self.assertEqual((n["deny"], n["codeowners"], n["gancho"]), ("WARN", "WARN", "WARN"))

    def test_fix_activa_deny_y_gancho_pero_no_toca_el_nucleo(self) -> None:
        antes = (self.repo / "docs/REGLAS.md").read_bytes()
        self.assertTrue(any("deny" in h for h in dr.arreglar(self.repo, "docs")))
        n = self.niveles()
        self.assertEqual((n["deny"], n["gancho"]), ("OK", "OK"))
        self.assertEqual((self.repo / "docs/REGLAS.md").read_bytes(), antes)

    def test_nucleo_alterado_es_error(self) -> None:
        (self.repo / "docs/REGLAS.md").write_text("relajada", encoding="utf-8")
        (self.repo / "docs/10-guias/mia.md").write_text("x", encoding="utf-8")
        ids = {c.id for c in dr.diagnosticar(self.repo, "docs") if c.nivel == "ERROR"}
        self.assertTrue({"nucleo-modificado", "nucleo-extendido"} <= ids)

    def test_lock_blanqueado_se_detecta_con_pack(self) -> None:
        (self.repo / "docs/REGLAS.md").write_text("relajada", encoding="utf-8")
        f = self.repo / "docs" / lock.LOCK_NOMBRE
        d = json.loads(f.read_text(encoding="utf-8"))
        d["archivos"]["REGLAS.md"]["sha256"] = lock.sha(self.repo / "docs/REGLAS.md")
        lock.escribir(self.repo, "docs", d)
        self.assertNotIn("nucleo-modificado", self.niveles())
        self.assertEqual(self.niveles(pack=self.pack).get("diverge-del-pack"), "ERROR")

    def test_version_nueva_y_conflictos_y_config(self) -> None:
        nuevo = self.tmp / "pack2"
        import shutil
        shutil.copytree(self.pack, nuevo)
        v = nuevo / "VERSION.md"
        v.write_text(v.read_text(encoding="utf-8").replace(f"version: {lock.version_de(nuevo)}", "version: 9.0.0", 1), encoding="utf-8")
        (self.repo / "docs/REGLAS.md.uxyngraphar-nuevo").write_text("x", encoding="utf-8")
        n = self.niveles(pack=nuevo)
        self.assertEqual((n["version"], n["conflictos"], n["config"]), ("WARN", "WARN", "WARN"))

    def test_sin_lock_y_sin_docs(self) -> None:
        (self.repo / "docs" / lock.LOCK_NOMBRE).unlink()
        self.assertEqual(self.niveles()["lock"], "ERROR")
        vacio = self.tmp / "vacio"
        vacio.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=vacio, check=True)
        self.assertEqual([c.id for c in dr.diagnosticar(vacio) if c.nivel == "ERROR"], ["docs"])

    def test_cli_codigos_de_salida_y_json(self) -> None:
        cli = str(AQUI.parent / "doctor.py")
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", cli, "--repo", str(self.repo)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", cli, "--repo", str(self.repo), "--strict"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", cli, "--repo", str(self.repo), "--json"], capture_output=True, text=True)
        self.assertTrue(any(c["id"] == "nucleo" for c in json.loads(r.stdout)))


if __name__ == "__main__":
    unittest.main()
