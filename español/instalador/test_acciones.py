"""Pruebas de las acciones del panel sobre un proyecto (api_acciones): guardia de persona, vista previa, aplicar y errores."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest import mock

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import api  # noqa: E402
import api_acciones as acc  # noqa: E402
import servidor  # noqa: E402

PERSONA = {k: "" for k in ("CI", "GITHUB_ACTIONS", "GITLAB_CI", "BUILDKITE", "JENKINS_URL", "CLAUDECODE", "UXYNGRAPHAR_AGENTE")}
GIT = ("-c", "user.name=t", "-c", "user.email=t@t")
D = "uxyngraphar"
PLANTILLA: Path | None = None   # un proyecto instalado una vez y copiado en cada prueba (instalar es lo lento)
_TMP = tempfile.TemporaryDirectory()


def setUpModule():
    global PLANTILLA
    PLANTILLA = Path(_TMP.name) / "plantilla"
    PLANTILLA.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=PLANTILLA, check=True)
    (PLANTILLA / "go.mod").write_text("module x\n")
    with mock.patch.dict(os.environ, PERSONA):
        assert api.flujo.instalar_completo(api.PACKS["servidor"], PLANTILLA, D, proteger=True, ganchos=True).ok
    subprocess.run(["git", *GIT, "add", "-A"], cwd=PLANTILLA, check=True)
    subprocess.run(["git", *GIT, "commit", "-qm", "chore: pack"], cwd=PLANTILLA, check=True, capture_output=True)


def tearDownModule():
    _TMP.cleanup()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "proyecto"
        shutil.copytree(PLANTILLA, self.repo, symlinks=True)
        self.r = str(self.repo)
        self.env = mock.patch.dict(os.environ, {**PERSONA, "UXYNGRAPHAR_HOME": str(Path(self.tmp.name) / "home")})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def instruccion(self) -> Path:
        r = subprocess.run([sys.executable, f"{D}/scripts/decisiones/decisiones.py", "new", "instruccion", "--slug", "prueba-panel"],
                           cwd=self.repo, capture_output=True, text=True, check=True)
        return Path(r.stdout.split("Creada:", 1)[1].strip())

    def agente(self):
        return mock.patch.dict(os.environ, {"CLAUDECODE": "1"})


class TestSalud(Base):
    def test_doctor_lee_y_dice_que_arreglaria(self):
        d = acc.doctor(self.r, D)
        self.assertTrue(d["ok"], d)
        self.assertEqual(d["cuenta"]["ERROR"], 0)
        self.assertIn(".gitignore", d["archivos"])
        self.assertTrue(any("núcleo" in x for x in d["que_arregla"]))

    def test_arreglar_con_copia_y_solo_lo_que_cambia(self):
        gi = self.repo / ".gitignore"
        original = gi.read_text()
        gi.write_text("node_modules/\n")
        r = acc.arreglar(self.r, D)
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["cambiados"], [".gitignore"])
        self.assertIn(".uxyngraphar-respaldo", gi.read_text())
        copia = self.repo / ".uxyngraphar-respaldo" / r["respaldo"].split("/")[1]
        self.assertEqual((copia / ".gitignore").read_text(), "node_modules/\n")
        self.assertEqual(json.loads((copia / "_respaldo.json").read_text())["archivos"], [".gitignore"])
        self.assertEqual(acc.arreglar(self.r, D)["respaldo"], "", "sin cambios no deja copia")
        self.assertTrue(original)

    def test_un_agente_no_arregla(self):
        (self.repo / ".gitignore").write_text("x\n")
        with self.agente():
            self.assertFalse(acc.arreglar(self.r, D)["ok"])
        self.assertEqual((self.repo / ".gitignore").read_text(), "x\n")

    def test_pack_antiguo_sin_script(self):
        # R-20: con --proteger scripts/ y doctor.py están en solo lectura; hay que descongelar para simular el pack viejo.
        import proteccion
        proteccion.descongelar_fs(self.repo, D)
        (self.repo / D / "scripts" / "doctor.py").unlink()
        self.assertIn("actualízalo", acc.doctor(self.r, D)["error"])
        self.assertIn("actualízalo", acc.arreglar(self.r, D)["error"])


class TestPendientes(Base):
    def test_listar_leer_previa_decidir_y_deshacer(self):
        ficha = self.instruccion()
        p = acc.pendientes(self.r, D)
        self.assertTrue(p["ok"], p)
        it = next(i for i in p["items"] if i["tipo"] == "instruccion")
        self.assertIn("aprobar", [o["action"] for o in it["options"]])
        self.assertIn("awaiting_approval", acc.ficha(self.r, D, it["path"])["texto"])
        v = acc.decision_previa(self.r, D, it["id"], "aprobar")
        self.assertTrue(v["ok"], v)
        self.assertIn("+status: approved", v["resultados"][0]["diff"])
        self.assertTrue(ficha.is_file(), "la vista previa no mueve nada")
        r = acc.decidir(self.r, D, it["id"], "aprobar")
        self.assertTrue(r["ok"], r)
        self.assertFalse(ficha.exists())
        movida = self.repo / D / r["ruta_final"]
        self.assertIn("status: approved", movida.read_text())
        self.assertEqual(acc.pendientes(self.r, D)["items"], [])
        plan = acc.respaldo_plan(self.r, D, r["respaldo"])
        self.assertEqual(plan["retirar"], [f"{D}/{r['ruta_final']}"])
        self.assertTrue(acc.restaurar(self.r, D, r["respaldo"])["ok"])
        self.assertTrue(ficha.is_file() and not movida.exists(), "restaurar deshace la decisión")

    def test_errores_y_guardia(self):
        self.instruccion()
        self.assertFalse(acc.decision_previa(self.r, D, "NO-EXISTE", "aprobar")["ok"])
        it = acc.pendientes(self.r, D)["items"][0]
        self.assertFalse(acc.decision_previa(self.r, D, it["id"], "promover")["ok"], "acción no válida para el tipo")
        with self.agente():
            self.assertFalse(acc.decidir(self.r, D, it["id"], "aprobar")["ok"])
        self.assertEqual(len(acc.pendientes(self.r, D)["items"]), 1)

    def test_ficha_solo_dentro_del_pack(self):
        self.assertFalse(acc.ficha(self.r, D, "../go.mod")["ok"])
        self.assertFalse(acc.ficha(self.r, D, "../../../etc/passwd")["ok"])
        self.assertTrue(acc.ficha(self.r, D, "PROTOCOLO.md")["ok"])


class TestCopias(Base):
    def test_listar_diferencia_restaurar_y_limpiar(self):
        gi = self.repo / ".gitignore"
        gi.write_text("node_modules/\n")
        ident = acc.arreglar(self.r, D)["respaldo"]
        lista = acc.respaldos(self.r, D)
        self.assertTrue(lista["ok"], lista)
        self.assertEqual(lista["copias"][0]["id"], ident)
        self.assertIn("-.uxyngraphar-respaldo/", acc.respaldo_diferencia(self.r, D, ident, ".gitignore")["diff"])
        self.assertFalse(acc.respaldo_diferencia(self.r, D, ident, "../otro")["ok"])
        with self.agente():
            self.assertFalse(acc.restaurar(self.r, D, ident)["ok"])
        self.assertTrue(acc.restaurar(self.r, D, ident)["ok"])
        self.assertEqual(gi.read_text(), "node_modules/\n")
        self.assertTrue(acc.limpiar_respaldos(self.r, D, False)["nada"])
        self.assertFalse(acc.respaldo_plan(self.r, D, "actualizacion/nada")["ok"])


class TestOtras(Base):
    def test_memoria_solo_personas(self):
        r = acc.memoria(self.r, D, "buscar", texto="algo")
        self.assertTrue(r["ok"], r)
        self.assertIn("Nada encontrado", r["salida"])
        self.assertFalse(acc.memoria(self.r, D, "purgar", ident="X")["ok"], "purgar exige motivo")
        with self.agente():
            self.assertFalse(acc.memoria(self.r, D, "buscar", texto="algo")["ok"])

    def test_feedback_previsualiza_sin_enviar(self):
        r = acc.feedback(self.r, D, "previsualizar")
        self.assertTrue(r["ok"], r)
        self.assertIn('"fichas"', r["salida"])
        self.assertFalse(acc.feedback(self.r, D, "activar")["ok"])
        with self.agente():
            self.assertFalse(acc.feedback(self.r, D, "enviar")["ok"])

    def test_ganchos_y_propietario(self):
        p = acc.protecciones(self.r, D)
        self.assertTrue(p["ganchos"]["pre-commit"]["nuestro"])
        self.assertTrue(acc.ganchos(self.r, D, quitar=True)["ok"])
        self.assertFalse(acc.protecciones(self.r, D)["ganchos"]["pre-commit"]["existe"])
        self.assertTrue(acc.ganchos(self.r, D, pre_push=True)["ok"])
        self.assertTrue(acc.protecciones(self.r, D)["ganchos"]["pre-push"]["nuestro"])
        self.assertFalse(acc.propietario(self.r, D, "sin arroba", False)["ok"])
        v = acc.propietario(self.r, D, "@ana", False)
        self.assertEqual((v["despues"], "CAMBIAR" in v["antes"]), ("@ana", True))
        with self.agente():
            self.assertFalse(acc.propietario(self.r, D, "@ana", True)["ok"])
            self.assertFalse(acc.ganchos(self.r, D)["ok"])
        r = acc.propietario(self.r, D, "@ana", True)
        self.assertTrue(r["ok"] and r["respaldo"], r)
        self.assertEqual(acc.protecciones(self.r, D)["propietario"], "@ana")

    def test_reglas_y_ordenar(self):
        r = acc.reglas(self.r, D)
        self.assertTrue(r["ok"] and r["valido"], r)
        self.assertIn("Nada que archivar", acc.ordenar(self.r, D, "archivar", 90, False)["salida"])
        self.assertFalse(acc.ordenar(self.r, D, "borrar", 90, False)["ok"])
        with self.agente():
            self.assertFalse(acc.ordenar(self.r, D, "archivar", 90, True)["ok"])


class TestHttp(Base):
    def test_rutas_con_token_y_pagina_con_las_acciones(self):
        srv = ThreadingHTTPServer(("127.0.0.1", 0), servidor.crear("tk", lambda: None, "panel"))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{srv.server_address[1]}"
        cuerpo = json.dumps({"ruta": self.r, "docs": D}).encode()
        try:
            html = urllib.request.urlopen(base + "/").read().decode()
            self.assertIn("function vPend()", html)
            self.assertNotIn("<!--PROYECTO-->", html)
            for ruta in ("/api/panel/doctor", "/api/panel/pendientes", "/api/panel/respaldos", "/api/panel/protecciones", "/api/panel/reglas"):
                with self.assertRaises(urllib.error.HTTPError):
                    urllib.request.urlopen(urllib.request.Request(base + ruta, cuerpo, {"X-Token": "otro"}))
                r = json.loads(urllib.request.urlopen(urllib.request.Request(base + ruta, cuerpo, {"X-Token": "tk"})).read())
                self.assertTrue(r["ok"], (ruta, r))
        finally:
            srv.shutdown()
            srv.server_close()


if __name__ == "__main__":
    unittest.main()
