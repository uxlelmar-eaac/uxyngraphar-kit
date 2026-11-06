"""Pruebas del motor 2.0: catálogo, construcción, instalación, actualización, quitar, generados y panel."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

import _rutas  # noqa: F401
import catalogo
import generar
import panel
import repo

base = catalogo.base


def huella(carpeta: Path) -> dict[str, str]:
    return {p.relative_to(carpeta).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(carpeta.rglob("*")) if p.is_file()}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        raiz = Path(self.tmp.name)
        self.cat = raiz / "catalogo"
        self.cat.mkdir()
        self.repo = raiz / "repo"
        self.repo.mkdir()
        catalogo.crear("demo", "Demo", "Paquete de prueba", self.cat)
        catalogo.crear("otro", "Otro", "Segundo paquete", self.cat)

    def tearDown(self):
        repo.borrar_arbol(Path(self.tmp.name))
        self.tmp.cleanup()


class TestCatalogo(Base):
    def test_listar_y_validar(self):
        self.assertEqual([(m["id"], m["errores"], m["avisos"]) for m in catalogo.listar(self.cat)],
                         [("demo", [], []), ("otro", [], [])])

    def test_crear_parte_de_la_plantilla(self):
        demo = self.cat / "demo"
        self.assertEqual(base.leer_manifiesto(demo)["activacion"], ["demo"])
        self.assertIn("# Demo", (demo / base.ENTRADA).read_text(encoding="utf-8"))
        self.assertNotIn("{{", (demo / base.ENTRADA).read_text(encoding="utf-8"))
        self.assertTrue((demo / "scripts" / "comun" / "fichas.py").is_file())

    def test_construir_es_portatil_e_integro(self):
        salida = catalogo.construir("demo", Path(self.tmp.name) / "dist", self.cat)
        self.assertEqual(set(base.archivos_del_paquete(salida)), set(base.archivos_del_paquete(self.cat / "demo")))
        self.assertTrue((salida / base.INTEGRIDAD).is_file())
        self.assertTrue(base.integro(base.comprobar_integridad(salida)))

    def test_editar_y_versionar(self):
        self.assertEqual(catalogo.guardar_archivo("demo", "docs/nueva.md", "# Guía\n", self.cat), [])
        self.assertIn("docs/nueva.md", catalogo.archivos("demo", self.cat))
        self.assertEqual(catalogo.versionar("demo", "menor", self.cat), "0.2.0")
        with self.assertRaises(ValueError):
            catalogo.leer_archivo("demo", "../otro/README.md", self.cat)
        malo = json.dumps({"id": "demo"})
        self.assertTrue(catalogo.guardar_archivo("demo", base.MANIFIESTO, malo, self.cat)[0].startswith("no guardado"))
        self.assertEqual(base.leer_manifiesto(self.cat / "demo")["version"], "0.2.0")

    def test_script_comun_cambiado_avisa_sin_fallar(self):
        fichas = "scripts/comun/fichas.py"
        texto = catalogo.leer_archivo("demo", fichas, self.cat) + "# cambio propio del paquete\n"
        self.assertEqual(catalogo.guardar_archivo("demo", fichas, texto, self.cat), [])
        (demo,) = [m for m in catalogo.listar(self.cat) if m["id"] == "demo"]
        self.assertEqual(demo["errores"], [])
        self.assertEqual(demo["avisos"], [f"{fichas}: difiere de paquetes/!base"])
        catalogo.construir("demo", Path(self.tmp.name) / "dist", self.cat)


class TestRepo(Base):
    def test_instalar_genera_indice_agentes_y_flujo(self):
        (self.repo / "AGENTES.md").write_text("# Mis reglas\n\nNo tocar.\n", encoding="utf-8")
        repo.instalar(self.repo, ["demo"], self.cat)
        paquete = self.repo / "uxyngraphar" / "paquetes" / "demo"
        self.assertTrue((paquete / base.INTEGRIDAD).is_file())
        self.assertFalse(os.access(paquete / "README.md", os.W_OK))
        self.assertTrue((self.repo / "uxyngraphar" / "trabajo" / "demo").is_dir())
        self.assertIn("`demo`", (self.repo / "uxyngraphar" / "INDICE.md").read_text(encoding="utf-8"))
        agentes = (self.repo / "AGENTES.md").read_text(encoding="utf-8")
        self.assertTrue(agentes.startswith("# Mis reglas\n\nNo tocar.\n"))
        self.assertEqual(agentes.count(generar.INICIO), 1)
        self.assertTrue((self.repo / "AGENTS.md").is_file())
        self.assertEqual(generar.leer_flujo(self.repo)["modo"], "manual")
        repo.instalar(self.repo, ["otro"], self.cat)
        self.assertEqual((self.repo / "AGENTES.md").read_text(encoding="utf-8").count(generar.INICIO), 1)

    def test_actualizar_no_toca_el_trabajo(self):
        repo.instalar(self.repo, ["demo"], self.cat)
        trabajo = self.repo / "uxyngraphar" / "trabajo" / "demo"
        (trabajo / "fichas").mkdir()
        (trabajo / "fichas" / "mia.md").write_text("---\nid: x\nstatus: abierta\n---\n", encoding="utf-8")
        (trabajo / "ajustes.json").write_text('{"limite": 3}', encoding="utf-8")
        antes = huella(self.repo / "uxyngraphar" / "trabajo")
        self.assertEqual(repo.actualizar(self.repo, None, self.cat), [])
        catalogo.guardar_archivo("demo", "README.md", "# Demo v2\n", self.cat)
        catalogo.versionar("demo", "menor", self.cat)
        self.assertTrue(repo.estado(self.repo, self.cat)[0]["actualizable"])
        self.assertEqual(repo.actualizar(self.repo, None, self.cat), ["demo"])
        self.assertEqual(base.leer_manifiesto(self.repo / "uxyngraphar" / "paquetes" / "demo")["version"], "0.2.0")
        self.assertEqual(huella(self.repo / "uxyngraphar" / "trabajo"), antes)

    def test_alterado_se_detecta_y_se_repara(self):
        repo.instalar(self.repo, ["demo"], self.cat)
        reglas = self.repo / "uxyngraphar" / "paquetes" / "demo" / "README.md"
        reglas.chmod(0o644)
        reglas.write_text("# hackeado\n", encoding="utf-8")
        self.assertFalse(repo.estado(self.repo, self.cat)[0]["integro"])
        self.assertEqual(repo.actualizar(self.repo, ["demo"], self.cat), ["demo"])
        self.assertTrue(repo.estado(self.repo, self.cat)[0]["integro"])

    def test_quitar_conserva_trabajo_y_limpia_flujo(self):
        repo.instalar(self.repo, ["demo", "otro"], self.cat)
        self.assertEqual(generar.guardar_flujo(self.repo, {**generar.leer_flujo(self.repo), "modo": "trabajar_con", "trabajar_con": "demo"}), [])
        repo.quitar(self.repo, "demo")
        self.assertFalse((self.repo / "uxyngraphar" / "paquetes" / "demo").exists())
        self.assertTrue((self.repo / "uxyngraphar" / "trabajo" / "demo").is_dir())
        flujo = generar.leer_flujo(self.repo)
        self.assertEqual((flujo["modo"], flujo["trabajar_con"]), ("manual", None))
        repo.quitar(self.repo, "otro", con_trabajo=True)
        self.assertFalse((self.repo / "uxyngraphar" / "trabajo" / "otro").exists())

    def test_flujo_humano_no_se_sobrescribe(self):
        repo.instalar(self.repo, ["demo"], self.cat)
        self.assertEqual(generar.guardar_flujo(self.repo, {**generar.leer_flujo(self.repo), "modo": "secuencia", "secuencia": ["demo"]}), [])
        repo.instalar(self.repo, ["otro"], self.cat)
        self.assertEqual(generar.leer_flujo(self.repo)["modo"], "secuencia")
        self.assertTrue(generar.guardar_flujo(self.repo, {**generar.leer_flujo(self.repo), "secuencia": ["noexiste"]}))

    def test_paquete_base_al_instalar(self):
        with self.assertRaises(ValueError):
            repo.instalar(self.repo, ["demo"], self.cat, paquete_base="otro")
        repo.instalar(self.repo, ["otro"], self.cat, paquete_base="otro")
        flujo = generar.leer_flujo(self.repo)
        self.assertEqual((flujo["modo"], flujo["trabajar_con"]), ("trabajar_con", "otro"))
        self.assertIn("aplícalo en **cada** pedido", (self.repo / "AGENTES.md").read_text(encoding="utf-8"))

    def test_protecciones_siguen_a_los_paquetes(self):
        ajustes = self.repo / ".claude" / "settings.json"
        ajustes.parent.mkdir()
        ajustes.write_text(json.dumps({"permissions": {"deny": ["Read(.env)"]}}), encoding="utf-8")
        catalogo.guardar_archivo("demo", "paquete.json", json.dumps(
            {**base.leer_manifiesto(self.cat / "demo"), "protegidos": ["reglas/**"], "fuera_de_ia": ["archivo/"]}), self.cat)
        repo.instalar(self.repo, ["demo"], self.cat)
        deny = json.loads(ajustes.read_text(encoding="utf-8"))["permissions"]["deny"]
        for regla in ("Read(.env)", "Edit(uxyngraphar/paquetes/**)", "Write(uxyngraphar/FLUJO.json)",
                      "Edit(uxyngraphar/trabajo/*/ajustes.json)", "Edit(uxyngraphar/trabajo/demo/reglas/**)", "Bash(UXYNGRAPHAR_HUMANO=1:*)"):
            self.assertIn(regla, deny)
        self.assertIn("uxyngraphar/trabajo/demo/archivo/", (self.repo / ".cursorignore").read_text(encoding="utf-8"))
        repo.instalar(self.repo, ["otro"], self.cat)
        self.assertEqual(json.loads(ajustes.read_text(encoding="utf-8"))["permissions"]["deny"], deny)
        repo.quitar(self.repo, "demo")
        repo.quitar(self.repo, "otro")
        self.assertEqual(json.loads(ajustes.read_text(encoding="utf-8"))["permissions"]["deny"], ["Read(.env)"])
        self.assertFalse((self.repo / ".cursorignore").exists())

    def test_rechaza_instalacion_1x(self):
        (self.repo / "docs").mkdir()
        (self.repo / "docs" / ".uxyngraphar.lock").write_text("{}", encoding="utf-8")
        with self.assertRaises(repo.InstalacionAntigua):
            repo.instalar(self.repo, ["demo"], self.cat)

    def test_verificar_ejecuta_scripts(self):
        repo.instalar(self.repo, ["demo"], self.cat)
        r = repo.verificar(self.repo)
        self.assertEqual([(x["paquete"], x["codigo"]) for x in r], [("demo", 0)])


class TestPanel(unittest.TestCase):
    def test_api_exige_token(self):
        servidor, token = panel.crear_servidor(0)
        hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
        hilo.start()
        url = f"http://127.0.0.1:{servidor.server_address[1]}"
        try:
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                urllib.request.urlopen(url + "/api/catalogo")
            self.assertEqual(ctx.exception.code, 403)
            pedido = urllib.request.Request(url + "/api/catalogo", headers={"X-Uxyn-Token": token})
            with urllib.request.urlopen(pedido) as r:
                self.assertIsInstance(json.loads(r.read())["ok"], list)
            with urllib.request.urlopen(url + "/") as r:
                self.assertIn(b"uxyngraphar 2.0", r.read())
        finally:
            servidor.shutdown()
            servidor.server_close()
            hilo.join(5)


if __name__ == "__main__":
    unittest.main()
