#!/usr/bin/env python3
"""Pruebas de CI en el servidor, higiene del repo (.gitignore/.gitattributes), lock sin rutas locales y protección de la config."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "control"))

import ci  # noqa: E402
import doctor as dr  # noqa: E402
import instalar as ins  # noqa: E402
import lock  # noqa: E402
import proteccion  # noqa: E402
import puerta  # noqa: E402
from test_nucleo import Base  # noqa: E402


def git(repo: Path, *a: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=repo, capture_output=True, text=True)


class TestServidor(Base):
    def setUp(self) -> None:
        super().setUp()
        self.instalar()
        git(self.repo, "init", "-q")

    def niveles(self) -> dict[str, str]:
        return {c.id: c.nivel for c in dr.diagnosticar(self.repo, "docs")}

    def test_gitignore_cubre_bytecode(self) -> None:
        texto = (self.repo / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("__pycache__/", texto)
        self.assertIn("*.pyc", texto)

    def test_gitattributes_se_crea_y_es_idempotente(self) -> None:
        f = self.repo / ".gitattributes"
        self.assertIn("docs/** text eol=lf", f.read_text(encoding="utf-8"))
        antes = f.read_text(encoding="utf-8")
        self.assertEqual(ins.asegurar_gitattributes(self.repo, "docs", False), [])
        self.assertEqual(f.read_text(encoding="utf-8"), antes)

    def test_lock_no_guarda_rutas_locales(self) -> None:
        fuente = lock.leer(self.repo, "docs")["fuente"]
        self.assertFalse(lock.es_ruta_local(fuente), fuente)
        self.assertNotIn(str(self.pack), fuente)
        self.assertEqual(lock.etiqueta_fuente("https://u:tok@github.com/o/r", "1.0.0"), "https://github.com/o/r")
        self.assertTrue(lock.es_ruta_local(r"D:\Repositorios\x"))

    def test_doctor_avisa_y_arregla_fuente_local(self) -> None:
        datos = lock.leer(self.repo, "docs")
        datos["fuente"] = r"D:\Repositorios\uxyngraphar\español\backend"
        lock.escribir(self.repo, "docs", datos)
        self.assertEqual(self.niveles()["lock-fuente"], "WARN")
        dr.arreglar(self.repo, "docs")
        self.assertNotIn("lock-fuente", self.niveles())

    def test_sin_workflow_el_doctor_avisa_y_proteger_lo_crea(self) -> None:
        self.assertEqual(self.niveles()["ci"], "WARN")
        f, creado = ci.workflow(self.repo, "docs")
        self.assertTrue(creado)
        self.assertEqual(f.relative_to(self.repo).as_posix(), ".github/workflows/uxyngraphar.yml")
        texto = f.read_text(encoding="utf-8")
        for paso in ("verificar-nucleo.py --docs docs", "controlar.py --docs docs", "escanear-secretos.py", "fetch-depth: 0", "permissions:"):
            self.assertIn(paso, texto)
        self.assertEqual(self.niveles()["ci"], "OK")
        self.assertFalse(ci.workflow(self.repo, "docs")[1])   # no sobrescribe

    def test_workflow_de_monorepo_tiene_nombre_propio(self) -> None:
        self.assertEqual(ci.nombre_archivo("apps/api/docs"), "uxyngraphar-apps-api.yml")
        self.assertIn("apps/api/docs/scripts/verificar-nucleo.py", ci.workflow(self.repo, "apps/api/docs")[0].read_text(encoding="utf-8"))

    def test_workflow_en_subcarpeta_se_detecta(self) -> None:
        mal = self.repo / "backend" / ".github" / "workflows" / "deploy.yml"
        mal.parent.mkdir(parents=True)
        mal.write_text("name: x\n", encoding="utf-8")
        git(self.repo, "add", "-A")
        self.assertEqual(self.niveles()["ci-ubicacion"], "WARN")

    def test_bytecode_versionado_se_detecta(self) -> None:
        pyc = self.repo / "docs" / "scripts" / "__pycache__" / "x.cpython-314.pyc"
        pyc.parent.mkdir(parents=True, exist_ok=True)
        pyc.write_bytes(b"\0")
        git(self.repo, "add", "-f", str(pyc))
        self.assertEqual(self.niveles()["pyc"], "WARN")

    def test_la_config_esta_protegida_para_agentes_y_revisores(self) -> None:
        self.assertIn("docs/uxyngraphar.config.json", proteccion.rutas_protegidas(self.repo, "docs"))
        proteccion.reglas_agente(self.repo, "docs")
        self.assertIn("Edit(docs/uxyngraphar.config.json)", (self.repo / ".claude/settings.json").read_text(encoding="utf-8"))
        self.assertIn("/docs/uxyngraphar.config.json", proteccion.codeowners(self.repo, "docs", "@x").read_text(encoding="utf-8"))

    def test_reparar_pone_al_dia_un_proyecto_instalado(self) -> None:
        proteccion.codeowners(self.repo, "docs", "@juan")
        hechas = dr.arreglar(self.repo, "docs")
        self.assertTrue(any(h.startswith("CI creado") for h in hechas), hechas)
        self.assertEqual(proteccion.propietario_actual(self.repo, "docs"), "@juan")
        self.assertIn("/docs/uxyngraphar.config.json @juan", (self.repo / ".github/CODEOWNERS").read_text(encoding="utf-8"))
        self.assertFalse(any(h.startswith("CI creado") for h in dr.arreglar(self.repo, "docs")))   # idempotente

    def test_la_puerta_senala_cambios_a_la_config(self) -> None:
        h = puerta.control_config(["src/a.py", "docs/uxyngraphar.config.json"], "docs", {})
        self.assertEqual([(x.control, x.nivel) for x in h], [("config", "aviso")])
        self.assertEqual(puerta.control_config(["src/a.py"], "docs", {}), [])


if __name__ == "__main__":
    unittest.main()
