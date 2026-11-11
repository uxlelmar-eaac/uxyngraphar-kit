"""Memorias del proyecto (núcleo del protocolo v3): `memorias.py` instalado, reglas de la persona, fichas y panel."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import _rutas  # noqa: F401
from _sistemas import completar
from test_portabilidad import correr
import catalogo
import entrada
import memorias_repo
import piezas
import repo

base = catalogo.base


class TestMemorias(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        raiz = Path(self.tmp.name)
        self.cat, self.app = raiz / "catalogo", raiz / "app"
        self.cat.mkdir()
        self.app.mkdir()
        c = completar(catalogo.crear("pruebas-demo", "Pruebas demo", "Sistema de prueba", self.cat))
        m = base.leer_manifiesto(c)
        m["fichas"] = {"nota": {"carpeta": ".", "prefijo": "PDN", "plantilla": "plantillas/nota.md", "inicial": "propuesta",
                                "status_validos": ["propuesta", "vigente"]}}
        (c / base.MANIFIESTO).write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
        (c / "plantillas").mkdir(exist_ok=True)
        (c / "plantillas" / "nota.md").write_text("---\nid: {{id}}\nstatus: propuesta\nfecha: {{fecha}}\n---\n# {{titulo}}\n",
                                                  encoding="utf-8")
        entrada.actualizar(c)
        repo.instalar(self.app, ["pruebas-demo"], self.cat)
        self.sistema = repo.carpeta_instalada(self.app, "pruebas-demo")
        self.script = self.sistema / "scripts" / "comun" / "memorias.py"
        self.trabajo = self.app / base.CARPETA_TRABAJO / "pruebas-demo"

    def tearDown(self):
        repo.borrar_arbol(Path(self.tmp.name))
        self.tmp.cleanup()

    def memorias(self, *args: str, persona: bool | None = None):
        return correr(self.script, *args, cwd=self.app, persona=persona)

    def test_el_nucleo_lleva_memorias(self):
        self.assertTrue((self.sistema / base.MEMORIAS).is_file())
        self.assertTrue(self.script.is_file())
        self.assertIn("memorias.py listar", (self.sistema / base.ENTRADA).read_text(encoding="utf-8"))
        texto = (self.app / "AGENTES.md").read_text(encoding="utf-8")
        self.assertIn("Memorias del proyecto", texto)

    def test_el_agente_propone_y_la_persona_aprueba(self):
        r = self.memorias("nueva", "--slug", "orm", "--titulo", "Usamos Prisma sin migraciones")
        self.assertEqual(r.returncode, 0, r.stderr)
        (ruta,) = (self.trabajo / base.CARPETA_MEMORIAS).glob("MEM-*-orm.md")
        mid = ruta.stem
        self.assertIn("status: propuesta", ruta.read_text(encoding="utf-8"))
        self.assertIn("autor: agente", ruta.read_text(encoding="utf-8"))
        self.assertIn("(sin memorias)", self.memorias("listar", "--vigentes").stdout)
        self.assertNotEqual(self.memorias("aprobar", mid).returncode, 0, "sin --humano no se aprueba")
        self.assertNotEqual(self.memorias("aprobar", mid, "--humano", persona=False).returncode, 0, "un agente no puede usar --humano")
        self.assertEqual(self.memorias("aprobar", mid, "--humano").returncode, 0)
        texto = ruta.read_text(encoding="utf-8")
        self.assertIn("status: vigente", texto)
        self.assertIn("aprobada_por: persona", texto)
        self.assertIn(mid, self.memorias("listar", "--vigentes").stdout)
        self.assertEqual(self.memorias("archivar", mid, "--humano").returncode, 0)
        self.assertIn("status: archivada", ruta.read_text(encoding="utf-8"))

    def test_la_persona_crea_vigentes(self):
        self.assertEqual(self.memorias("nueva", "--slug", "rama", "--titulo", "Rama principal: main", "--humano").returncode, 0)
        (ruta,) = (self.trabajo / base.CARPETA_MEMORIAS).glob("MEM-*-rama.md")
        self.assertIn("status: vigente", ruta.read_text(encoding="utf-8"))
        self.assertIn("autor: persona", ruta.read_text(encoding="utf-8"))

    def test_verificar_rechaza_vigentes_del_agente_sin_aprobar(self):
        carpeta = self.trabajo / base.CARPETA_MEMORIAS
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / "MEM-20261111-trampa.md").write_text(
            "---\nid: MEM-20261111-trampa\nstatus: vigente\nfecha: 2026-11-11\nautor: agente\n---\n# Trampa\n", encoding="utf-8")
        r = correr(self.sistema / "scripts" / "comun" / "verificar.py", cwd=self.app)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("sin aprobar por una persona", r.stderr)

    def test_las_memorias_no_son_fichas(self):
        self.memorias("nueva", "--slug", "orm", "--titulo", "Una memoria")
        r = correr(self.sistema / "scripts" / "comun" / "fichas.py", "listar", cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("MEM-", r.stdout)
        r = correr(self.sistema / "scripts" / "comun" / "verificar.py", cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_panel_lista_aprueba_y_crea(self):
        self.memorias("nueva", "--slug", "orm", "--titulo", "Una memoria")
        (s,) = memorias_repo.listar(self.app)
        self.assertEqual((s["id"], s["propuestas"]), ("pruebas-demo", 1))
        self.assertEqual(memorias_repo.propuestas(self.app), 1)
        memorias_repo.aprobar(self.app, "pruebas-demo", s["memorias"][0]["id"])
        self.assertEqual(memorias_repo.propuestas(self.app), 0)
        mid = memorias_repo.crear(self.app, "pruebas-demo", "otra", "Otra memoria")
        self.assertTrue(mid.startswith("MEM-"))
        self.assertEqual({m["status"] for m in memorias_repo.listar(self.app)[0]["memorias"]}, {"vigente"})
        with self.assertRaises(FileNotFoundError):
            memorias_repo.crear(self.app, "no-instalado", "x", "X")


class TestReservas(unittest.TestCase):
    def test_carpeta_y_prefijo_reservados(self):
        ficha = {"carpeta": "memorias", "prefijo": "MEM", "plantilla": "plantillas/x.md", "inicial": "a", "status_validos": ["a"]}
        errores = base._validar_fichas({"x": ficha})
        self.assertTrue(any("carpeta" in e and "reservada" in e for e in errores), errores)
        self.assertTrue(any("prefijo" in e and "reservado" in e for e in errores), errores)

    def test_memorias_md_exige_sus_secciones(self):
        with tempfile.TemporaryDirectory() as tmp:
            c = completar(catalogo.crear("pruebas-demo", "Pruebas demo", "Sistema de prueba", Path(tmp)))
            self.assertEqual(piezas.nucleo(c, base.leer_manifiesto(c)), [])
            (c / base.MEMORIAS).write_text("# Memorias\n\n## Qué recordar\n\n- algo\n", encoding="utf-8")
            errores = piezas.nucleo(c, base.leer_manifiesto(c))
            self.assertTrue(any("Qué no recordar" in e for e in errores), errores)
            (c / base.MEMORIAS).unlink()
            self.assertIn(f"falta {base.MEMORIAS}", catalogo.esp.validar_sistema(c))


if __name__ == "__main__":
    unittest.main()
