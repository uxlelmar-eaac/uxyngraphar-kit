"""Migración 1.x → 2.0 sobre instalaciones sintéticas y sobre copias de los repos reales (nunca los originales)."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import _rutas  # noqa: F401
import generar  # noqa: E402
import migrar  # noqa: E402
import limpieza  # noqa: E402
import repo  # noqa: E402

REALES = Path(__file__).resolve().parents[4]
AGENTES_1X = "# AGENTES — pack servidor\n\nLee docs/00-nucleo.\n"
CLAUDE_1X = "# CLAUDE.md\n\nEste proyecto usa uxyngraphar. Lee **solo** [AGENTES.md](AGENTES.md) y ejecuta docs/scripts/contexto.py.\n"


def huella(raiz: Path) -> dict[str, str]:
    return {p.relative_to(raiz).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(raiz.rglob("*")) if p.is_file() and ".git" not in p.relative_to(raiz).parts[:1]}


def escribir(raiz: Path, rel: str, texto: str) -> Path:
    f = raiz / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(texto, encoding="utf-8")
    return f


def app_1x(raiz: Path) -> Path:
    """App con un pack servidor 1.x en docs/, congelado, con protecciones fuera del pack y un gancho git."""
    app = raiz / "app"
    subprocess.run(["git", "init", "-q", str(app)], check=True)
    escribir(app, "src/main.ts", "export const x = 1;\n")
    archivos = {
        "00-nucleo/INDICE.md": "# Núcleo\n",
        "scripts/contexto.py": "print('1.x')\n",
        "00-nucleo/arquitectura.md": "# Arquitectura propia del proyecto\n",
        "05-instrucciones/03-completadas/2026-01-01/landing.md": "---\nid: INS-20260101-landing\nstatus: done\n---\n# Landing\n",
        "20-decisiones/03-completadas/2026-01-01/ADR-001-orm.md": "---\nid: ADR-001\nstatus: aceptada\n---\n# ORM\n",
        "25-areas/auth/RESUMEN.md": "---\nstatus: active\n---\n# auth\n",
        "95-memoria/nota.md": "# nota\n",
        "05-instrucciones/02-en-progreso/2026-01-02/api.md": "---\nid: INS-20260102-api\nstatus: executing\n---\n# API\n",
        "45-mejoras-propuestas/04-archivadas/2026-01-01/MEJ-001.md": "---\nid: MEJ-001\nstatus: archivada\n---\n# vieja\n",
        "40-auditorias/02-en-progreso/2026-01-01/AUD-001.md": ("---\nid: AUD-001\nstatus: activa\nfindings_count: 2\n---\n# Rendimiento\n\n"
                                                              "## Hallazgos\n1. Lento en `src/main.ts:1`\n2. Sin caché\n"),
        "50-sistema-integral/mapa-capas.md": "# Capas de este proyecto\n",
        "00-nucleo/restricciones.md": "# Restricciones propias\n",
        "46-evolucion-documentacion/matriz-cobertura-proyectos.md": "# Matriz\n",
        "46-evolucion-documentacion/01-pendientes/2026-01-03/EVO-20260103-cobertura.md": "---\nid: EVO-20260103-cobertura\nstatus: pending\ntipo: cobertura\n---\n# Cobertura\n\n## Evidencia\nx\n\n## Propuesta\ny\n",
        "96-reglas-proyecto/RP-001.md": "---\nid: RP-001\nstatus: propuesta\n---\n# Regla\n",
        "ESTADO.md": "# Estado del proyecto\n",
        ".decisiones/tokens/t1.json": '{"aprobado_por": "humano"}\n',
        "uxyngraphar.config.json": json.dumps({"codigo": {"raices": ["src"], "extensiones": [".ts"]}, "limite_lineas": 300,
                                               "secretos_permitir": ["src/fixtures/**"]}),
    }
    for rel, texto in archivos.items():
        escribir(app / "docs", rel, texto)
    escribir(app, "AGENTES.md", AGENTES_1X)
    escribir(app, "CLAUDE.md", CLAUDE_1X)
    nucleo = {rel: {"clase": migrar.cl1x.clasificar(rel), "sha256": migrar.sha256(app / "docs" / rel)}
              for rel in ("00-nucleo/INDICE.md", "scripts/contexto.py")}
    nucleo["AGENTES.md"] = {"clase": "N", "sha256": migrar.sha256(app / "AGENTES.md")}
    nucleo["50-sistema-integral/mapa-capas.md"] = {"clase": "N", "sha256": hashlib.sha256(b"# plantilla\n").hexdigest()}
    escribir(app / "docs", ".uxyngraphar.lock", json.dumps({"pack": "servidor", "version": "1.0.0", "archivos": nucleo}))
    escribir(app, ".claude/settings.json", json.dumps({"permissions": {"deny": ["Edit(docs/00-nucleo/**)", "Read(.env)"]}}))
    escribir(app, ".github/CODEOWNERS", "* @equipo\n# >>> uxyngraphar núcleo [docs]\n/docs/00-nucleo/ @dueno\n# <<< uxyngraphar núcleo [docs]\n")
    escribir(app, ".cursorignore", "# >>> uxyngraphar: fuera del alcance de la IA\ndocs/90-archivo/\n# <<< uxyngraphar\n")
    escribir(app, ".github/workflows/uxyngraphar.yml", "name: uxyngraphar\njobs:\n  x:\n    steps:\n      - run: python3 docs/scripts/validar-documentacion.py docs\n")
    escribir(app, ".git/hooks/pre-commit", f"#!/bin/sh\n{limpieza.MARCA_GANCHO}\npython3 docs/scripts/x.py\n")
    for rel in ("00-nucleo/INDICE.md", "scripts/contexto.py"):
        os.chmod(app / "docs" / rel, stat.S_IREAD)
    os.chmod(app / "docs" / "00-nucleo", stat.S_IREAD | stat.S_IEXEC)
    return app


class TestMigracion(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self.tmp.name)
        self.app = app_1x(self.raiz)

    def tearDown(self):
        limpieza.escribible(self.raiz)
        self.tmp.cleanup()

    def test_detecta_y_simula_sin_tocar_nada(self):
        antes = huella(self.app)
        informe = migrar.ejecutar(self.raiz)
        self.assertEqual(antes, huella(self.app))
        (i,) = informe["instalaciones"]
        self.assertFalse(informe["aplicada"])
        self.assertEqual((i["pack"], i["bloqueos"]), ("servidor", []))
        self.assertIn("rutas-de-api", i["paquetes"])

    def test_bloquea_lo_no_clasificable_y_el_nucleo_editado(self):
        escribir(self.app / "docs", "raro/zzz.md", "?\n")
        os.chmod(self.app / "docs" / "scripts" / "contexto.py", stat.S_IWUSR | stat.S_IREAD)
        (self.app / "docs" / "scripts" / "contexto.py").write_text("print('editado')\n", encoding="utf-8")
        antes = huella(self.app)
        (i,) = migrar.ejecutar(self.raiz, aplicar=True)["instalaciones"]
        self.assertFalse(i["aplicada"])
        self.assertTrue(any("raro/zzz.md" in b for b in i["bloqueos"]))
        self.assertTrue(any("scripts/contexto.py" in b for b in i["bloqueos"]))
        self.assertEqual(antes, huella(self.app))

    def test_aplica_conservando_todo_el_contenido(self):
        origen = {rel: h for rel, h in huella(self.app / "docs").items()}
        (i,) = migrar.ejecutar(self.raiz, aplicar=True)["instalaciones"]
        self.assertTrue(i["aplicada"], i)
        trabajo = self.app / migrar.TRABAJO
        esperados = {
            "00-nucleo/arquitectura.md": "arquitectura-monolitica-por-capas/ARQUITECTURA.md",
            "00-nucleo/restricciones.md": "arquitectura-monolitica-por-capas/RESTRICCIONES.md",
            "46-evolucion-documentacion/matriz-cobertura-proyectos.md": "evolucion-del-sistema/MATRIZ-COBERTURA.md",
            "46-evolucion-documentacion/01-pendientes/2026-01-03/EVO-20260103-cobertura.md": "evolucion-del-sistema/pendientes/EVO-20260103-cobertura.md",
            "96-reglas-proyecto/RP-001.md": "reglas-del-proyecto/reglas/RP-001.md",
            "ESTADO.md": "instrucciones-aprobadas/ESTADO.md",
            "05-instrucciones/03-completadas/2026-01-01/landing.md": "instrucciones-aprobadas/instrucciones/completadas/landing.md",
            "20-decisiones/03-completadas/2026-01-01/ADR-001-orm.md": "decisiones-de-arquitectura/completadas/ADR-001-orm.md",
            "25-areas/auth/RESUMEN.md": "mapa-de-modulos/auth/RESUMEN.md",
            "95-memoria/nota.md": "memoria-e-historial/memoria/nota.md",
            "50-sistema-integral/mapa-capas.md": "documentacion-espejo/mapa-capas.md",
            ".decisiones/tokens/t1.json": "_legado-1x/.decisiones/tokens/t1.json",
        }
        for viejo, nuevo in esperados.items():
            self.assertEqual(origen[viejo], migrar.sha256(trabajo / nuevo), nuevo)
        self.assertFalse((self.app / "docs").exists())
        self.assertTrue(all(e["integro"] for e in repo.estado(self.app)))
        self.assertEqual(len(repo.estado(self.app)), 18)
        self.assertEqual(json.loads((trabajo / "arquitectura-monolitica-por-capas/ajustes.json").read_text())["perfil"], "servidor")
        self.assertEqual(json.loads((trabajo / "calidad-de-codigo/ajustes.json").read_text())["limite_lineas"], 300)
        self.assertEqual(json.loads((trabajo / "secretos-y-credenciales/ajustes.json").read_text())["permitir"], ["src/fixtures/**"])
        flujo = generar.leer_flujo(self.app)
        self.assertEqual((flujo["modo"], flujo["trabajar_con"]), ("trabajar_con", migrar.PAQUETE_BASE))
        self.assertFalse((self.app / ".github/workflows/uxyngraphar.yml").exists())
        self.assertTrue((Path(i["respaldo"]) / "raiz/.github/workflows/uxyngraphar.yml").is_file())
        estados = {"instrucciones-aprobadas/instrucciones/en-progreso/api.md": "approved",
                   "deuda-y-mejoras/archivadas/MEJ-001.md": "archived", "auditorias-tecnicas/en-progreso/AUD-001.md": "activa"}
        for rel, status in estados.items():
            self.assertIn(f"status: {status}\n", (trabajo / rel).read_text(encoding="utf-8"), rel)
        self.assertEqual(len(i["normalizadas"]), 2)
        agentes = (self.app / "AGENTES.md").read_text(encoding="utf-8")
        self.assertIn(generar.INICIO, agentes)
        self.assertNotIn("pack servidor", agentes)
        self.assertNotIn("contexto.py", (self.app / "CLAUDE.md").read_text(encoding="utf-8"))
        self.assertFalse((self.app / ".git/hooks/pre-commit").exists())
        ignorados = (self.app / ".cursorignore").read_text(encoding="utf-8")
        self.assertIn("uxyngraphar/trabajo/memoria-e-historial/archivo/**", ignorados)
        self.assertNotIn("docs/90-archivo", ignorados)
        self.assertEqual((self.app / ".github/CODEOWNERS").read_text(encoding="utf-8"), "* @equipo\n")
        deny = json.loads((self.app / ".claude/settings.json").read_text())["permissions"]["deny"]
        self.assertIn("Read(.env)", deny)
        self.assertIn("Edit(uxyngraphar/paquetes/**)", deny)
        self.assertIn("Edit(uxyngraphar/trabajo/*/ajustes.json)", deny)
        self.assertNotIn("Edit(uxyngraphar/trabajo/**)", deny)
        self.assertFalse(any("docs/" in r for r in deny))
        respaldo = Path(i["respaldo"])
        self.assertEqual(origen, huella(respaldo / "docs"))
        self.assertTrue((respaldo / "git-hooks/pre-commit").is_file())
        self.assertTrue(all(r["codigo"] == 0 for r in repo.verificar(self.app)), repo.verificar(self.app))

    def test_un_fallo_revierte_todo(self):
        antes = huella(self.app)
        with mock.patch.object(repo, "instalar", side_effect=RuntimeError("fallo simulado")):
            with self.assertRaises(RuntimeError):
                migrar.ejecutar(self.raiz, aplicar=True)
        despues = {k: v for k, v in huella(self.app).items() if not k.startswith(migrar.RESPALDOS)}
        self.assertEqual(antes, despues)
        self.assertFalse((self.app / migrar.TRABAJO).exists())
        self.assertFalse((self.app / "uxyngraphar").exists())
        self.assertTrue((self.app / ".git/hooks/pre-commit").is_file())

    def test_mismo_nombre_en_dos_fechas_lleva_la_fecha_delante(self):
        escribir(self.app / "docs", "05-instrucciones/03-completadas/2026-02-02/landing.md", "---\nid: INS-2\nstatus: done\n---\n# 2\n")
        (i,) = migrar.ejecutar(self.raiz, aplicar=True)["instalaciones"]
        self.assertTrue(i["aplicada"], i["bloqueos"])
        completadas = self.app / migrar.TRABAJO / "instrucciones-aprobadas/instrucciones/completadas"
        self.assertEqual(sorted(p.name for p in completadas.iterdir()), ["2026-01-01-landing.md", "2026-02-02-landing.md"])

    def test_sin_lock_se_detecta_y_bloquea(self):
        (self.app / "docs" / ".uxyngraphar.lock").unlink()
        (i,) = migrar.ejecutar(self.raiz, aplicar=True)["instalaciones"]
        self.assertFalse(i["aplicada"])
        self.assertTrue(any(".uxyngraphar.lock" in b for b in i["bloqueos"]))
        self.assertTrue((self.app / "docs").is_dir())

    def test_carpeta_uxyngraphar_previa_bloquea(self):
        escribir(self.app, f"{migrar.TRABAJO}/algo.md", "x\n")
        (i,) = migrar.ejecutar(self.raiz)["instalaciones"]
        self.assertTrue(any("uxyngraphar/ además de docs/" in b for b in i["bloqueos"]))

    def test_pack_1x_en_uxyngraphar_se_reemplaza_en_su_sitio(self):
        (self.app / "docs").rename(self.app / "uxyngraphar")
        origen = huella(self.app / "uxyngraphar")
        (i,) = migrar.ejecutar(self.raiz, aplicar=True)["instalaciones"]
        self.assertTrue(i["aplicada"], i)
        trabajo = self.app / migrar.TRABAJO
        self.assertEqual(origen["95-memoria/nota.md"], migrar.sha256(trabajo / "memoria-e-historial/memoria/nota.md"))
        self.assertEqual(sorted(p.name for p in (self.app / "uxyngraphar").iterdir()), ["FLUJO.json", "INDICE.md", "paquetes", "trabajo"])
        self.assertFalse((self.app / migrar.PROVISIONAL).exists())
        self.assertTrue(all(e["integro"] for e in repo.estado(self.app)))


@unittest.skipUnless((REALES / "uxyngraphar-frontend/docs/.uxyngraphar.lock").is_file(), "sin repos reales al lado del kit")
class TestReposReales(unittest.TestCase):
    def test_copias_de_los_repos_reales(self):
        with tempfile.TemporaryDirectory() as t:
            destino = Path(t)
            ignorar = shutil.ignore_patterns("node_modules", ".next", "coverage", "dist")
            for nombre in ("uxyngraphar-frontend", "uxyngraphar-backend"):
                shutil.copytree(REALES / nombre, destino / nombre, symlinks=True, ignore=ignorar)
            informe = migrar.ejecutar(destino, aplicar=True)
            self.assertEqual(len(informe["instalaciones"]), 2)
            self.assertTrue(informe["aplicada"], [i["bloqueos"] for i in informe["instalaciones"]])
            for i in informe["instalaciones"]:
                app = Path(i["app"])
                fallos = [r for r in repo.verificar(app) if r["codigo"] != 0]
                self.assertEqual(fallos, [], i["app"])
            limpieza.escribible(destino)


if __name__ == "__main__":
    unittest.main()
