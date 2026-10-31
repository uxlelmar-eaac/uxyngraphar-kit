#!/usr/bin/env python3
"""Pruebas de clasificación, instalación, verificación, actualización y protección del núcleo."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PACK = AQUI.parent.parent
sys.path.insert(0, str(AQUI))

if not (PACK / "AGENTES.md").is_file():   # instalado en un proyecto: estas pruebas necesitan el pack fuente (con AGENTES.md dentro)
    raise unittest.SkipTest("requiere el repo fuente de uxyngraphar (pack con AGENTES.md); se omite en un proyecto instalado")

import actualizar as act  # noqa: E402
import clasificacion as cl  # noqa: E402
import instalar as ins  # noqa: E402
import lock  # noqa: E402
import proteccion  # noqa: E402
import verificar as ver  # noqa: E402

EVO = "---\nid: EVO-20261015-x\nstatus: approved\n---\n# e\n"


_CACHE = tempfile.TemporaryDirectory()
_BASE = Path(_CACHE.name) / "pack"
shutil.copytree(PACK, _BASE, ignore=shutil.ignore_patterns("__pycache__", ".decisiones", ".git"))


def copiar_pack(destino: Path) -> Path:
    shutil.copytree(_BASE, destino)   # copia desde disco local: el pack real puede estar en un montaje lento
    return destino


class TestClasificacion(unittest.TestCase):
    def test_casos(self) -> None:
        casos = {
            "REGLAS.md": "N", "AGENTES.md": "N", "scripts/decisiones/common.py": "N", "10-guias/nueva.md": "N",
            "00-nucleo/configuracion-proyecto.md": "P", "00-nucleo/ciclo-vinculante.md": "N", "ESTADO.md": "P",
            "15-rutas/INDICE.md": "M", "15-rutas/mod/x.md": "C", "15-rutas/_PLANTILLA.md": "N", "25-areas/a/CONTEXTO.md": "C",
            "50-sistema-integral/src/a.md": "C", "50-sistema-integral/vision-espejo.md": "N",
            "46-evolucion-documentacion/03-completadas/2026-08-23/EVO-x.md": "C",
            "46-evolucion-documentacion/03-completadas/2026-08-23/README.md": "N",
            "05-instrucciones/02-en-progreso/2026-01-01/a.md": "C", "35-herramientas/autorizadas/decisiones-pendientes.md": "N",
            "35-herramientas/autorizadas/mi-herramienta.md": "C", "scripts/__pycache__/a.pyc": "X", "PARIDAD-PACKS.md": "X", "docs-extra.md": None,
        }
        for rel, esperado in casos.items():
            self.assertEqual(cl.clasificar(rel), esperado, rel)

    def test_todo_el_pack_esta_clasificado(self) -> None:
        inv = lock.inventario(PACK)
        self.assertGreater(len(inv), 150)
        self.assertIn("AGENTES.md", inv)

    def test_destino_y_origen(self) -> None:
        self.assertEqual(cl.destino("AGENTES.md", "docs"), "AGENTES.md")
        self.assertEqual(cl.destino("REGLAS.md", "docs"), "docs/REGLAS.md")
        self.assertEqual(cl.origen("docs/REGLAS.md", "docs"), "REGLAS.md")
        self.assertIsNone(cl.origen("src/a.py", "docs"))


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.tmp = Path(self._t.name)
        self.pack = copiar_pack(self.tmp / "pack")
        self.repo = self.tmp / "proy"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)

    def instalar(self, **kw):  # type: ignore[no-untyped-def]
        return ins.instalar(self.pack, self.repo, **kw)


class TestInstalar(Base):
    def test_instala_n_p_m_y_no_contenido(self) -> None:
        r = self.instalar()
        self.assertTrue((self.repo / "AGENTES.md").is_file())
        self.assertTrue((self.repo / "docs/REGLAS.md").is_file())
        self.assertTrue((self.repo / "docs/00-nucleo/configuracion-proyecto.md").is_file())
        self.assertFalse(list((self.repo / "docs/46-evolucion-documentacion/03-completadas").rglob("EVO-*.md")))
        self.assertEqual(r.conflictos, [])
        self.assertIn(".decisiones/", (self.repo / ".gitignore").read_text(encoding="utf-8"))
        datos = lock.leer(self.repo, "docs")
        self.assertEqual(datos["version"], lock.version_de(self.pack))

    def test_no_reinstala_ni_pisa_docs_existentes(self) -> None:
        self.instalar()
        with self.assertRaises(ins.ErrorInstalacion):
            self.instalar()
        otro = self.tmp / "otro"
        (otro / "docs").mkdir(parents=True)
        subprocess.run(["git", "init", "-q"], cwd=otro, check=True)
        (otro / "docs" / "mio.md").write_text("mío", encoding="utf-8")
        with self.assertRaises(ins.ErrorInstalacion):
            ins.instalar(self.pack, otro)

    def test_adoptar_no_pisa(self) -> None:
        otro = self.tmp / "otro"
        (otro / "docs").mkdir(parents=True)
        subprocess.run(["git", "init", "-q"], cwd=otro, check=True)
        (otro / "docs" / "REGLAS.md").write_text("reglas propias", encoding="utf-8")
        r = ins.instalar(self.pack, otro, adoptar=True)
        self.assertEqual((otro / "docs" / "REGLAS.md").read_text(encoding="utf-8"), "reglas propias")
        self.assertIn("REGLAS.md", r.conflictos)
        self.assertTrue((otro / "docs" / "REGLAS.md.uxyngraphar-nuevo").is_file())

    def test_dry_run_no_escribe(self) -> None:
        self.instalar(dry_run=True)
        self.assertFalse((self.repo / "docs").exists())

    def test_exige_git(self) -> None:
        sin = self.tmp / "sin"
        sin.mkdir()
        with self.assertRaises(ins.ErrorInstalacion):
            ins.instalar(self.pack, sin)

    def test_perfil_minimo_omite_espejo(self) -> None:
        self.instalar(perfil="minimo")
        self.assertFalse((self.repo / "docs/55-automatizaciones").exists())
        self.assertTrue((self.repo / "docs/05-instrucciones/_PLANTILLA.md").is_file())


class TestVerificar(Base):
    def setUp(self) -> None:
        super().setUp()
        self.instalar()

    def codigos(self) -> set[str]:
        return {h.codigo for h in ver.verificar(self.repo)}

    def test_recien_instalado_es_integro(self) -> None:
        self.assertEqual(ver.verificar(self.repo), [])

    def test_contenido_y_plantillas_no_cuentan(self) -> None:
        f = self.repo / "docs/25-areas/pagos/CONTEXTO.md"
        f.parent.mkdir(parents=True)
        f.write_text("x", encoding="utf-8")
        (self.repo / "docs/00-nucleo/configuracion-proyecto.md").write_text("rellena", encoding="utf-8")
        self.assertEqual(ver.verificar(self.repo), [])

    def test_modificado_eliminado_extendido_y_fuera(self) -> None:
        (self.repo / "docs/REGLAS.md").write_text("relajada", encoding="utf-8")
        (self.repo / "docs/PROTOCOLO.md").unlink()
        (self.repo / "docs/10-guias/mia.md").write_text("x", encoding="utf-8")
        (self.repo / "docs/MEJORAS-uxyngraphar.md").write_text("x", encoding="utf-8")
        self.assertEqual(self.codigos(), {"NUCLEO-MODIFICADO", "NUCLEO-ELIMINADO", "NUCLEO-EXTENDIDO", "FUERA-DE-TAXONOMIA"})

    def test_sin_lock(self) -> None:
        (self.repo / "docs" / lock.LOCK_NOMBRE).unlink()
        self.assertEqual(self.codigos(), {"SIN-LOCK"})

    def test_lock_editado_a_mano_se_detecta(self) -> None:
        f = self.repo / "docs" / lock.LOCK_NOMBRE
        datos = json.loads(f.read_text(encoding="utf-8"))
        datos["archivos"]["REGLAS.md"]["sha256"] = lock.sha(self.repo / "docs/REGLAS.md")  # intento de «blanquear»
        datos["archivos"]["REGLAS.md"]["sha256"] = "0" * 64
        f.write_text(json.dumps(datos), encoding="utf-8")
        self.assertIn("LOCK-ALTERADO", self.codigos())

    def test_contra_pack_ignora_el_lock(self) -> None:
        (self.repo / "docs/REGLAS.md").write_text("relajada", encoding="utf-8")
        f = self.repo / "docs" / lock.LOCK_NOMBRE
        datos = json.loads(f.read_text(encoding="utf-8"))
        datos["archivos"]["REGLAS.md"]["sha256"] = lock.sha(self.repo / "docs/REGLAS.md")
        lock.escribir(self.repo, "docs", datos)   # lock «blanqueado» y resellado
        self.assertEqual(ver.verificar(self.repo), [])
        self.assertEqual({h.codigo for h in ver.contra_pack(self.repo, "docs", self.pack)}, {"DIVERGE-DEL-PACK"})

    def test_no_existe_aceptar(self) -> None:
        self.assertFalse(hasattr(ver, "aceptar"))


class TestActualizar(Base):
    def setUp(self) -> None:
        super().setUp()
        self.instalar()
        self.nuevo = copiar_pack(self.tmp / "pack2")
        self._version(self.nuevo, f"{lock.mayor(lock.version_de(self.pack))}.99.0")   # misma versión MAYOR, más nueva

    def _version(self, pack: Path, v: str) -> None:
        f = pack / "VERSION.md"
        f.write_text(f.read_text(encoding="utf-8").replace(f"version: {lock.version_de(pack)}", f"version: {v}", 1), encoding="utf-8")

    def plan(self, **kw):  # type: ignore[no-untyped-def]
        return act.planificar(self.nuevo, self.repo, "docs", **kw)

    def test_al_dia(self) -> None:
        p = act.planificar(self.pack, self.repo, "docs")
        self.assertEqual(p.acciones, [])

    def test_reemplaza_nucleo_sin_tocar_contenido_ni_plantillas(self) -> None:
        (self.nuevo / "REGLAS.md").write_text("regla nueva", encoding="utf-8")
        (self.nuevo / "10-guias/guia-nueva.md").write_text("g", encoding="utf-8")
        (self.nuevo / "00-nucleo/configuracion-proyecto.md").write_text("plantilla v2", encoding="utf-8")
        propio = self.repo / "docs/25-areas/pagos/CONTEXTO.md"
        propio.parent.mkdir(parents=True)
        propio.write_text("mi contexto", encoding="utf-8")
        mia = self.repo / "docs/00-nucleo/configuracion-proyecto.md"
        mia.write_text("mi config", encoding="utf-8")
        p = self.plan()
        self.assertEqual({a.rel for a in p.de("reemplazar")}, {"REGLAS.md", "VERSION.md"})
        self.assertEqual([a.rel for a in p.de("añadir")], ["10-guias/guia-nueva.md"])
        self.assertEqual([a.rel for a in p.de("plantilla-cambiada")], ["00-nucleo/configuracion-proyecto.md"])
        respaldo = act.aplicar(self.nuevo, self.repo, "docs", p)
        self.assertEqual((self.repo / "docs/REGLAS.md").read_text(encoding="utf-8"), "regla nueva")
        self.assertEqual(mia.read_text(encoding="utf-8"), "mi config")
        self.assertEqual(propio.read_text(encoding="utf-8"), "mi contexto")
        self.assertIsNotNone(respaldo)
        self.assertEqual(lock.leer(self.repo, "docs")["version"], lock.version_de(self.nuevo))
        self.assertEqual(ver.verificar(self.repo), [])
        self.assertIn(f"{lock.version_de(self.pack)} → {lock.version_de(self.nuevo)}",(self.repo / "docs/90-archivo/cambios-pack.md").read_text(encoding="utf-8"))

    def test_editado_localmente_no_se_pisa(self) -> None:
        (self.repo / "docs/REGLAS.md").write_text("editada", encoding="utf-8")
        p = self.plan()
        self.assertEqual([a.rel for a in p.de("modificado-local")], ["REGLAS.md"])
        act.aplicar(self.nuevo, self.repo, "docs", p)
        self.assertEqual((self.repo / "docs/REGLAS.md").read_text(encoding="utf-8"), "editada")
        self.assertEqual({h.codigo for h in ver.verificar(self.repo)}, {"NUCLEO-MODIFICADO"})

    def test_restaurar_nucleo(self) -> None:
        (self.repo / "docs/REGLAS.md").write_text("editada", encoding="utf-8")
        act.aplicar(self.nuevo, self.repo, "docs", self.plan(restaurar=True))
        self.assertEqual((self.repo / "docs/REGLAS.md").read_bytes(), (self.nuevo / "REGLAS.md").read_bytes())

    def test_conflicto_deja_nuevo_al_lado(self) -> None:
        (self.repo / "docs/REGLAS.md").write_text("editada", encoding="utf-8")
        (self.nuevo / "REGLAS.md").write_text("regla nueva", encoding="utf-8")
        p = self.plan()
        self.assertEqual([a.rel for a in p.de("conflicto")], ["REGLAS.md"])
        act.aplicar(self.nuevo, self.repo, "docs", p)
        self.assertEqual((self.repo / "docs/REGLAS.md").read_text(encoding="utf-8"), "editada")
        self.assertEqual((self.repo / "docs/REGLAS.md.uxyngraphar-nuevo").read_text(encoding="utf-8"), "regla nueva")
        self.assertEqual(lock.leer(self.repo, "docs")["archivos"]["REGLAS.md"]["sha256"], lock.sha(self.pack / "REGLAS.md"))

    def test_salto_mayor_exige_migracion_aprobada(self) -> None:
        self._version(self.nuevo, "3.0.0")
        p = self.plan()
        with self.assertRaises(act.ErrorActualizacion):
            act.aplicar(self.nuevo, self.repo, "docs", p)
        inst = self.repo / "docs/05-instrucciones/02-en-progreso/2026-10-15/migrar.md"
        inst.parent.mkdir(parents=True)
        inst.write_text("---\nid: 20261015-001-migrar\nstatus: approved\n---\n", encoding="utf-8")
        act.aplicar(self.nuevo, self.repo, "docs", p, "20261015-001-migrar")
        self.assertEqual(lock.leer(self.repo, "docs")["version"], "3.0.0")

    def test_retirado_del_pack_solo_se_informa(self) -> None:
        (self.nuevo / "10-guias/pruebas.md").unlink()
        p = self.plan()
        self.assertEqual([a.rel for a in p.de("retirado")], ["10-guias/pruebas.md"])
        act.aplicar(self.nuevo, self.repo, "docs", p)
        self.assertTrue((self.repo / "docs/10-guias/pruebas.md").is_file())

    def test_sin_lock_trata_diferencias_como_conflicto(self) -> None:
        (self.repo / "docs" / lock.LOCK_NOMBRE).unlink()
        (self.nuevo / "REGLAS.md").write_text("regla nueva", encoding="utf-8")
        p = self.plan()
        self.assertTrue(p.sin_lock)
        self.assertEqual({a.rel for a in p.de("conflicto")}, {"REGLAS.md", "VERSION.md"})
        self.assertEqual(p.de("reemplazar"), [])

    def test_fallo_a_mitad_revierte(self) -> None:
        (self.nuevo / "REGLAS.md").write_text("regla nueva", encoding="utf-8")
        p = self.plan()
        original = (self.repo / "docs/REGLAS.md").read_bytes()
        (self.nuevo / "VERSION.md").unlink()   # el origen desaparece a mitad del lote
        with self.assertRaises(FileNotFoundError):
            act.aplicar(self.nuevo, self.repo, "docs", p)
        self.assertEqual((self.repo / "docs/REGLAS.md").read_bytes(), original)


class TestProteccion(Base):
    def test_reglas_y_codeowners_idempotentes(self) -> None:
        self.instalar()
        for _ in range(2):
            f = proteccion.reglas_agente(self.repo, "docs")
            proteccion.codeowners(self.repo, "docs", "@yo")
        deny = json.loads(f.read_text(encoding="utf-8"))["permissions"]["deny"]
        self.assertIn("Edit(docs/REGLAS.md)", deny)
        self.assertIn("Write(docs/10-guias/**)", deny)
        for extra in ("Edit(docs/.uxyngraphar.lock)", "Edit(.claude/settings.json)", "Edit(.github/CODEOWNERS)"):
            self.assertIn(extra, deny)
        self.assertNotIn("Edit(docs/00-nucleo/configuracion-proyecto.md)", deny)
        self.assertEqual(len(deny), len(set(deny)))
        co = (self.repo / ".github/CODEOWNERS").read_text(encoding="utf-8")
        self.assertEqual(co.count(proteccion.MARCA_INI), 1)
        self.assertIn("/docs/REGLAS.md @yo", co)

    def test_respeta_configuracion_existente(self) -> None:
        self.instalar()
        f = self.repo / ".claude" / "settings.json"
        f.parent.mkdir()
        f.write_text(json.dumps({"permissions": {"allow": ["Bash(ls)"]}, "otra": 1}), encoding="utf-8")
        proteccion.reglas_agente(self.repo, "docs")
        cfg = json.loads(f.read_text(encoding="utf-8"))
        self.assertEqual(cfg["otra"], 1)
        self.assertEqual(cfg["permissions"]["allow"], ["Bash(ls)"])


if __name__ == "__main__":
    unittest.main()
