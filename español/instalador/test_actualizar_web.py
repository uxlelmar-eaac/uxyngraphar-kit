"""Pruebas del asistente de actualización: revisar sin escribir, comparar, aplicar y salto mayor."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import api  # noqa: E402
import servidor  # noqa: E402

TOKEN = "t0k3n"
VERSION = api.flujo.lock.version_de(api.PACKS["servidor"])       # versión vigente del pack: las pruebas no dependen de un número fijo
MAJ = int(VERSION.split(".")[0])
ANTERIOR_MAYOR = f"{MAJ - 1}.9.0"                                   # otra versión MAYOR, más antigua
POSTERIOR = f"{MAJ + 1}.0.0"                                        # más nueva que el pack (degradación)


class TestActualizarWeb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.repo = Path(cls.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=cls.repo, check=True)
        (cls.repo / "go.mod").write_text("module x\n")
        res = api.ejecutar({"proyecto": str(cls.repo), "pack": "servidor", "sub": ""})
        assert res["ok"], res
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), servidor.crear(TOKEN, lambda: None, "actualizar", [str(cls.repo)]))
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()
        cls.tmp.cleanup()

    def post(self, ruta, cuerpo=None):
        req = urllib.request.Request(self.base + ruta, json.dumps(cuerpo or {}).encode(), {"X-Token": TOKEN, "Content-Type": "application/json"})
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())

    def lock(self, **cambios):
        l = api.flujo.lock
        datos = l.leer(self.repo, "docs")
        datos.update({k: v for k, v in cambios.items() if k != "base"})
        for rel, h in cambios.get("base", {}).items():
            datos["archivos"][rel]["sha256"] = h
        l.escribir(self.repo, "docs", datos)

    def test_pagina_correcta_e_inicio(self):
        html = urllib.request.urlopen(self.base + "/").read().decode()
        self.assertIn("Actualizar uxyngraphar", html)
        self.assertIn(TOKEN, html)
        self.assertEqual(self.post("/api/inicio")["rutas"], [str(self.repo)])

    def test_flujo_completo(self):
        r = self.post("/api/act/revisar", {"rutas": [str(self.repo), "/no/existe", str(self.repo)]})["proyectos"]
        self.assertEqual([p["ok"] for p in r], [True, False, True])
        self.assertEqual(len(r[0]["packs"]), 1)
        self.assertEqual(r[2]["packs"], [])                       # el repetido no se duplica
        self.assertEqual(r[0]["packs"][0]["estado"], "al_dia")

        regla = self.repo / "docs" / "REGLAS.md"
        regla.write_text(regla.read_text(encoding="utf-8") + "\nmi nota\n", encoding="utf-8")
        self.lock(version=VERSION, base={"REGLAS.md": "0" * 64})
        ficha = self.post("/api/act/revisar", {"rutas": [str(self.repo)]})["proyectos"][0]["packs"][0]
        self.assertEqual(ficha["estado"], "actualizar")
        conflicto = next(g for g in ficha["grupos"] if g["tipo"] == "conflicto")
        self.assertIn("REGLAS.md", conflicto["archivos"])
        antes = regla.read_text(encoding="utf-8")

        d = self.post("/api/act/diferencia", {"repo": ficha["repo"], "docs": ficha["docs"], "rel": "REGLAS.md"})
        self.assertTrue(d["ok"] and any(l["x"] == "-mi nota" for l in d["lineas"]))
        self.assertFalse(self.post("/api/act/diferencia", {"repo": ficha["repo"], "docs": ficha["docs"], "rel": "../../etc/passwd"})["ok"])
        self.assertEqual(regla.read_text(encoding="utf-8"), antes)  # revisar y comparar no escriben

        res = self.post("/api/act/aplicar", {"seleccion": [{"repo": ficha["repo"], "docs": ficha["docs"]}]})
        self.assertTrue(res["ok"], res)
        self.assertEqual(regla.read_text(encoding="utf-8"), antes)  # lo editado por el usuario se conserva
        self.assertTrue(regla.with_name("REGLAS.md.uxyngraphar-nuevo").is_file())
        self.assertEqual(res["destinos"][0]["conflictos"], 1)
        self.assertTrue(any("uxyngraphar-nuevo" in s for s in res["siguientes"]))

    def test_salto_mayor_exige_instruccion(self):
        self.lock(version=ANTERIOR_MAYOR)
        ficha = self.post("/api/act/revisar", {"rutas": [str(self.repo)]})["proyectos"][0]["packs"][0]
        self.assertEqual(ficha["estado"], "mayor")
        res = self.post("/api/act/aplicar", {"seleccion": [{"repo": ficha["repo"], "docs": ficha["docs"]}]})
        self.assertFalse(res["ok"])
        self.assertEqual(api.flujo.lock.leer(self.repo, "docs")["version"], ANTERIOR_MAYOR)   # nada cambió

    def test_pack_mas_antiguo_no_se_aplica(self):
        self.lock(version=POSTERIOR)
        ficha = self.post("/api/act/revisar", {"rutas": [str(self.repo)]})["proyectos"][0]["packs"][0]
        self.assertEqual(ficha["estado"], "degradacion")
        res = self.post("/api/act/aplicar", {"seleccion": [{"repo": ficha["repo"], "docs": ficha["docs"], "migracion": "INS-x"}]})
        self.assertFalse(res["ok"])
        self.assertEqual(api.flujo.lock.leer(self.repo, "docs")["version"], POSTERIOR)   # nada cambió

    def test_no_confia_en_el_cliente(self):
        res = self.post("/api/act/aplicar", {"seleccion": [{"repo": "/no/existe", "docs": "docs"}, {"repo": tempfile.gettempdir(), "docs": "docs"}]})
        self.assertFalse(res["ok"])
        self.assertEqual(len(res["destinos"]), 2)


    def test_pregunta_una_vez_al_actualizar_un_proyecto_sin_respuesta(self):
        repo = Path(tempfile.mkdtemp(dir=self.tmp.name))
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        self.assertTrue(api.ejecutar({"proyecto": str(repo), "pack": "servidor", "sub": ""})["ok"])
        cfg_path = repo / "docs" / "uxyngraphar.config.json"
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        cfg["feedback"] = {"activo": False, "url": "", "consentimiento": "", "id_instalacion": "", "ocultar": []}   # colaboración aún sin responder
        cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
        ficha = self.post("/api/act/revisar", {"rutas": [str(repo)]})["proyectos"][0]["packs"][0]
        self.assertTrue(ficha["colaboracion_pendiente"])
        self.assertIn("pregunta", self.post("/api/act/colaboracion"))
        res = self.post("/api/act/aplicar", {"seleccion": [{"repo": ficha["repo"], "docs": ficha["docs"]}], "colaborar": "no"})
        self.assertTrue(res["ok"], res)
        fb = json.loads(cfg_path.read_text(encoding="utf-8"))["feedback"]
        self.assertEqual((fb["activo"], fb["respondido"], fb["origen"]), (False, "no", "actualizador"))
        ficha = self.post("/api/act/revisar", {"rutas": [str(repo)]})["proyectos"][0]["packs"][0]
        self.assertFalse(ficha["colaboracion_pendiente"])                 # no se vuelve a preguntar


if __name__ == "__main__":
    unittest.main()
