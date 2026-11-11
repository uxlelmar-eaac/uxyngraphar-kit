"""Pruebas de PLAN-MEJORAS: panel con código de un solo uso, cookie, CSP y control de Host/Origin (M-14) y comprobación de
la procedencia de las descargas en el instalador (M-12)."""

from __future__ import annotations

import http.client
import json
import os
import subprocess
import time
import unittest
from pathlib import Path
from unittest import mock

import _rutas  # noqa: F401
from _sistemas import catalogo_de_prueba
import panel  # pone distribucion/ en sys.path (vía casa)
import arranque_descarga as ad  # noqa: E402
from test_panel_api import ConServidor


class TestPanelSeguro(ConServidor):
    """M-14: la pestaña entra con un código de un solo uso; el token queda para la CLI."""

    def crudo(self, metodo: str, ruta: str, cuerpo: dict | None = None, cabeceras: dict | None = None):
        puerto = self.servidor.server_address[1]
        con = http.client.HTTPConnection("127.0.0.1", puerto, timeout=10)
        try:
            datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
            base = {"Host": f"127.0.0.1:{puerto}", "Content-Type": "application/json"}
            con.request(metodo, ruta, body=datos, headers={**base, **(cabeceras or {})})
            r = con.getresponse()
            return r.status, dict(r.getheaders()), r.read()
        finally:
            con.close()

    def cookie(self, codigo: str) -> str:
        estado, cabeceras, _ = self.crudo("POST", "/api/canjear", {"codigo": codigo})
        self.assertEqual(estado, 200)
        galleta = cabeceras["Set-Cookie"]
        for atributo in ("HttpOnly", "SameSite=Strict", "Path=/"):
            self.assertIn(atributo, galleta)
        return galleta.split(";", 1)[0]

    def test_codigo_de_un_solo_uso(self):
        codigo = self.servidor.url.split("#c=", 1)[1]
        galleta = self.cookie(codigo)
        self.assertEqual(self.crudo("POST", "/api/canjear", {"codigo": codigo})[0], 403, "no se puede reutilizar")
        estado, _, cuerpo = self.crudo("GET", "/api/sesion", cabeceras={"Cookie": galleta})
        self.assertEqual(estado, 200, cuerpo)
        self.assertEqual(self.crudo("GET", "/api/sesion")[0], 403, "sin cookie ni token no hay API")
        self.assertEqual(self.crudo("GET", "/api/sesion", cabeceras={"Cookie": "uxyn_sesion=otra"})[0], 403)

    def test_codigo_caducado(self):
        codigo = self.servidor.nuevo_codigo()
        with mock.patch.object(panel.time, "time", return_value=time.time() + panel.CODIGO_SEGUNDOS + 1):
            self.assertEqual(self.crudo("POST", "/api/canjear", {"codigo": codigo})[0], 403)

    def test_la_cli_pide_codigos_con_el_token(self):
        abierto = {"puerto": self.servidor.server_address[1], "token": self.token}
        url = panel.url_con_codigo(abierto, bienvenida=True)
        self.assertTrue(url.endswith("&bienvenida=1"))
        self.assertNotIn(self.token, url)
        self.assertEqual(self.crudo("POST", "/api/codigo", {})[0], 403, "pedir códigos exige el token")

    def test_host_ajeno(self):
        self.assertEqual(self.crudo("GET", "/", cabeceras={"Host": "atacante.example:80"})[0], 403)
        self.assertEqual(self.crudo("GET", "/api/sesion", cabeceras={"Host": "atacante.example", "X-Uxyn-Token": self.token})[0], 403)
        puerto = self.servidor.server_address[1]
        self.assertEqual(self.crudo("GET", "/", cabeceras={"Host": f"localhost:{puerto}"})[0], 200)

    def test_origin_ajeno_en_post(self):
        estado, _, _ = self.crudo("POST", "/api/latido", {}, {"X-Uxyn-Token": self.token, "Origin": "http://atacante.example"})
        self.assertEqual(estado, 403)
        puerto = self.servidor.server_address[1]
        estado, _, _ = self.crudo("POST", "/api/latido", {}, {"X-Uxyn-Token": self.token, "Origin": f"http://127.0.0.1:{puerto}"})
        self.assertEqual(estado, 200)

    def test_csp_en_todas_las_respuestas(self):
        for metodo, ruta in (("GET", "/"), ("GET", "/js/app.js"), ("GET", "/no-existe"), ("GET", "/api/sesion")):
            _, cabeceras, _ = self.crudo(metodo, ruta)
            self.assertIn("default-src 'self'", cabeceras.get("Content-Security-Policy", ""), ruta)
            self.assertIn("frame-ancestors 'none'", cabeceras["Content-Security-Policy"])
            self.assertEqual(cabeceras.get("Referrer-Policy"), "no-referrer")
            self.assertEqual(cabeceras.get("X-Frame-Options"), "DENY")

    def test_la_web_no_usa_html_inyectado_ni_token(self):
        web = panel.WEB / "js"
        for archivo in sorted(web.rglob("*.js")):
            texto = archivo.read_text(encoding="utf-8")
            self.assertNotIn("innerHTML", texto, archivo.name)
            self.assertNotIn("X-Uxyn-Token", texto, archivo.name)


class TestProcedencia(unittest.TestCase):
    """M-12: el instalador comprueba con gh la atestación de procedencia cuando puede."""

    def setUp(self):
        self.parches = [mock.patch.dict(os.environ, {}, clear=False), mock.patch.object(ad, "decir")]
        for p in self.parches:
            p.start()
        os.environ.pop("UXYNGRAPHAR_URL_BASE", None)
        os.environ.pop("UXYNGRAPHAR_SIN_FIRMA", None)
        ad.OPCIONES["sin_firma"] = False

    def tearDown(self):
        for p in reversed(self.parches):
            p.stop()

    def gh(self, codigo: int, salida: str = ""):
        return mock.patch.object(ad.subprocess, "run", return_value=subprocess.CompletedProcess([], codigo, salida))

    def test_verificada(self):
        with mock.patch.object(ad.shutil, "which", return_value="/usr/bin/gh"), self.gh(0) as run:
            self.assertTrue(ad.verificar_procedencia("x.zip", "1.3.0"))
        self.assertEqual(run.call_args[0][0][1:4], ["attestation", "verify", "x.zip"])

    def test_atestacion_que_no_corresponde_no_instala(self):
        with mock.patch.object(ad.shutil, "which", return_value="/usr/bin/gh"), self.gh(1, "verification failed: no matching attestations"):
            with self.assertRaises(ad.ErrorInstalacion):
                ad.verificar_procedencia("x.zip", "1.3.0")

    def test_sin_gh_sin_sesion_o_version_antigua_avisa_y_sigue(self):
        with mock.patch.object(ad.shutil, "which", return_value=None):
            self.assertFalse(ad.verificar_procedencia("x.zip", "1.3.0"))
        with mock.patch.object(ad.shutil, "which", return_value="/usr/bin/gh"), self.gh(4, "To get started with GitHub CLI, please run:  gh auth login"):
            self.assertFalse(ad.verificar_procedencia("x.zip", "1.3.0"))
        with mock.patch.object(ad.shutil, "which", return_value="/usr/bin/gh"), self.gh(1, "fallo") as run:
            self.assertFalse(ad.verificar_procedencia("x.zip", "1.2.0"))
        run.assert_not_called()

    def test_sin_firma_y_espejos(self):
        with mock.patch.object(ad.shutil, "which", return_value="/usr/bin/gh"), self.gh(1, "fallo") as run:
            ad.OPCIONES["sin_firma"] = True
            self.assertFalse(ad.verificar_procedencia("x.zip", "1.3.0"))
            ad.OPCIONES["sin_firma"] = False
            os.environ["UXYNGRAPHAR_URL_BASE"] = "http://127.0.0.1:1/releases"
            self.assertFalse(ad.verificar_procedencia("x.zip", "1.3.0"))
        run.assert_not_called()


class TestVocabulario(unittest.TestCase):
    """M-05: «nomenclatura migrar» pasa las fichas de un proyecto al vocabulario de NOMENCLATURA.md."""

    def setUp(self):
        import tempfile
        from pathlib import Path
        import repo
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.app = Path(self._t.name).resolve() / "app"
        (self.app / ".git").mkdir(parents=True)
        cat = catalogo_de_prueba(Path(self._t.name) / "catalogo", "pruebas-demo", "pruebas-otras")
        self.parche = mock.patch.dict(os.environ, {"UXYNGRAPHAR_HOME": str(Path(self._t.name) / "casa"), "UXYNGRAPHAR_CATALOGO": str(cat)})
        self.parche.start()
        self.addCleanup(self.parche.stop)
        import vocabulario
        tabla = {"pruebas-demo": {"done": "cerrada"}, "pruebas-otras": {"abierta": "en-curso"}}
        parche_tabla = mock.patch.object(vocabulario, "migraciones", return_value=tabla)
        parche_tabla.start()
        self.addCleanup(parche_tabla.stop)
        repo.instalar(self.app, ["pruebas-demo", "pruebas-otras"])
        trabajo = self.app / "uxyngraphar" / "trabajo"
        self.ins = trabajo / "pruebas-demo" / "completadas" / "PRU-20260101-vieja.md"
        self.eva = trabajo / "pruebas-otras" / "pendientes" / "PRU-20260101-alta.md"
        for ruta, status in ((self.ins, "done"), (self.eva, "abierta")):
            ruta.parent.mkdir(parents=True, exist_ok=True)
            ruta.write_text(f"---\nid: {ruta.stem}\nstatus: {status}\n---\n# {ruta.stem}\n\nTrabajo de la persona.\n", encoding="utf-8")

    def test_simula_aplica_y_mueve(self):
        import vocabulario
        antes = {r: r.read_text(encoding="utf-8") for r in (self.ins, self.eva)}
        cambios = vocabulario.plan(self.app)
        self.assertEqual({(c["antes"], c["despues"]) for c in cambios}, {("done", "cerrada"), ("abierta", "en-curso")})
        self.assertEqual({r: r.read_text(encoding="utf-8") for r in (self.ins, self.eva)}, antes, "simular no toca nada")
        self.assertEqual(vocabulario.pendientes(self.app), 2)
        r = vocabulario.aplicar(self.app)
        self.assertEqual(len(r["cambios"]), 2)
        self.assertIn("status: cerrada\n", self.ins.read_text(encoding="utf-8"))
        self.assertFalse(self.eva.exists())
        movida = self.eva.parent.parent / "en-progreso" / self.eva.name
        self.assertEqual(movida.read_text(encoding="utf-8"), antes[self.eva].replace("status: abierta", "status: en-curso"))
        self.assertEqual(vocabulario.pendientes(self.app), 0)

    def test_un_fallo_restaura(self):
        import vocabulario
        antes = self.ins.read_text(encoding="utf-8")
        with mock.patch.object(vocabulario, "_aplicar_cambio", side_effect=[None, OSError("disco lleno")]):
            with self.assertRaises(OSError):
                vocabulario.aplicar(self.app)
        self.assertEqual(self.ins.read_text(encoding="utf-8"), antes)
        self.assertTrue(self.eva.is_file())

    def test_actualizar_avisa(self):
        import contextlib
        import io
        import cli
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            self.assertEqual(cli.main(["actualizar", "--repo", str(self.app)]), 0)
        self.assertIn("nomenclatura migrar", salida.getvalue())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["nomenclatura", "migrar", "--repo", str(self.app), "--aplicar"]), 0)
        self.assertIn("status: cerrada", self.ins.read_text(encoding="utf-8"))


class TestCrearConPruebas(unittest.TestCase):
    """M-07: un sistema nuevo trae pruebas de serie y un script propio queda probado sin trabajo manual."""

    def test_crear_trae_pruebas_que_cubren_un_script_nuevo(self):
        import sys
        import tempfile
        from pathlib import Path
        import catalogo
        from _sistemas import completar
        with tempfile.TemporaryDirectory() as t:
            cat = Path(t) / "catalogo"
            cat.mkdir()
            c = completar(catalogo.crear("pruebas-serie", "Pruebas serie", "Sistema de prueba", cat))
            self.assertIn("pruebas", catalogo.base.leer_manifiesto(c)["piezas"])
            (c / "scripts" / "serie.py").write_text(
                "import argparse\nargparse.ArgumentParser(description='serie').parse_args()\n", encoding="utf-8")
            self.assertFalse([a for a in catalogo.esp.avisos_sistema(c) if "pruebas" in a], "C-30 no avisa")
            construido = catalogo.construir("pruebas-serie", Path(t) / "dist", cat)
            r = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "pruebas", "-t", "pruebas"],
                               cwd=construido, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("Ran 3 tests", r.stderr)


class TestDeshacer(ConServidor):
    """M-09: deshacer el último cambio, y deshacer el deshacer."""

    def huella(self, app):
        import hashlib
        return {q.relative_to(app).as_posix(): hashlib.sha256(q.read_bytes()).hexdigest()
                for q in sorted(app.rglob("*")) if q.is_file() and ".git" not in q.parts}

    def test_instalar_deshacer_y_rehacer(self):
        import repo
        import transaccion
        app = self.repo_git("app")
        (app / "AGENTES.md").write_text("# propio\n", encoding="utf-8")
        inicial = self.huella(app)
        repo.instalar(app, ["pruebas-demo"])
        instalado = self.huella(app)
        self.assertEqual(transaccion.listar(app)[0]["motivo"], "instalar")
        transaccion.deshacer(app)
        self.assertEqual(self.huella(app), inicial)
        transaccion.deshacer(app)
        self.assertEqual(self.huella(app), instalado)

    def test_respaldos_configurables_y_api(self):
        import repo
        import transaccion
        casa_ = panel.casa
        casa_.escribir_json(casa_.ARCHIVO_FORMATO, {"formato": casa_.FORMATO_CASA, "respaldos_por_proyecto": 5})
        app = self.repo_git("app")
        self.pedir("/api/proyectos/agregar", {"rutas": [str(app)]})
        repo.instalar(app, ["pruebas-demo"])
        for _ in range(6):
            repo.actualizar(app, forzar=True)
        self.assertEqual(len(transaccion.respaldos(app)), 5)
        lista = self.pedir(f"/api/repo/respaldos?repo={app}")
        self.assertEqual(len(lista), 5)
        self.assertEqual(self.error("/api/repo/deshacer", {"repo": str(app)})[0], 400, "pide confirmar")
        r = self.pedir("/api/repo/deshacer", {"repo": str(app), "confirmar": "app", "respaldo": lista[-1]["nombre"]})
        self.assertEqual(r["deshecho"], lista[-1]["nombre"])
        self.assertEqual(self.error("/api/repo/deshacer", {"repo": str(app), "confirmar": "app", "respaldo": "no-existe"})[0], 400)


class TestAuditoria(ConServidor):
    """M-11: una línea por operación que cambia algo, desde la CLI y desde el panel, también cuando falla."""

    def test_cli_y_panel(self):
        import contextlib
        import io
        import auditoria
        import cli
        app = self.repo_git("app")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.main(["instalar", "pruebas-demo", "--repo", str(app)]), 0)
            self.assertEqual(cli.main(["instalar", "pruebas-demo", "--repo", str(app)]), 1)   # ya instalado: falla
            self.assertEqual(cli.main(["estado", "--repo", str(app)]), 0)                     # consultar no se registra
        self.pedir("/api/proyectos/agregar", {"rutas": [str(app)]})
        self.pedir("/api/repo/quitar", {"repo": str(app), "id": "pruebas-demo"})
        self.error("/api/repo/quitar", {"repo": str(app), "id": "pruebas-demo"})
        lineas = auditoria.leer()
        self.assertEqual([(x["accion"], x["resultado"]) for x in reversed(lineas)],
                         [("instalar", "ok"), ("instalar", "error"), ("quitar", "ok"), ("quitar", "error")])
        self.assertEqual(lineas[0]["origen"], "cli", "este proceso no es el panel lanzado")
        self.assertEqual(lineas[-1]["ids"], ["pruebas-demo"])
        self.assertEqual(self.pedir("/api/historial?limite=2")[0]["accion"], "quitar")

    def test_rota_por_tamano(self):
        import auditoria
        auditoria.casa.carpeta().mkdir(parents=True, exist_ok=True)
        with mock.patch.object(auditoria, "MAX_BYTES", 200):
            for i in range(20):
                auditoria.registrar("instalar", f"/p/{i}")
        self.assertTrue(auditoria.ruta().with_name("acciones.jsonl.1").is_file())
        self.assertEqual(auditoria.leer(3)[0]["proyecto"], "/p/19")


class TestProteccionesAmpliadas(unittest.TestCase):
    """M-15: reglas de lectura, freno por la shell, copilot, huella de FLUJO.json y reglas propias que sobreviven."""

    def setUp(self):
        import tempfile
        from pathlib import Path
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.app = Path(self._t.name).resolve() / "app"
        (self.app / ".git").mkdir(parents=True)
        cat = catalogo_de_prueba(Path(self._t.name) / "catalogo", "pruebas-demo")
        parche = mock.patch.dict(os.environ, {"UXYNGRAPHAR_HOME": str(Path(self._t.name) / "casa"), "UXYNGRAPHAR_CATALOGO": str(cat)})
        parche.start()
        self.addCleanup(parche.stop)

    def deny(self):
        return json.loads((self.app / ".claude" / "settings.json").read_text(encoding="utf-8"))["permissions"]["deny"]

    def test_reglas_nuevas_y_propias(self):
        import repo
        (self.app / ".claude").mkdir()
        propia = "Edit(uxyngraphar/trabajo/notas-de-memoria/privado.md)"
        (self.app / ".claude" / "settings.json").write_text(json.dumps({"permissions": {"deny": [propia, "Read(.env)"]}}), encoding="utf-8")
        repo.instalar(self.app, ["pruebas-demo"])
        deny = self.deny()
        self.assertIn("Bash(rm -rf uxyngraphar/sistemas-de-gobernanza:*)", deny)
        self.assertIn(propia, deny, "una regla propia que menciona uxyngraphar/ sobrevive")
        repo.actualizar(self.app, forzar=True)
        repo.desinstalar(self.app)
        self.assertEqual(self.deny(), [propia, "Read(.env)"])

    def test_copilot_solo_si_existe(self):
        import generar
        import repo
        repo.instalar(self.app, ["pruebas-demo"])
        copilot = self.app / ".github" / "copilot-instructions.md"
        self.assertFalse(copilot.exists())
        copilot.parent.mkdir()
        copilot.write_text("# Instrucciones propias\n", encoding="utf-8")
        generar.regenerar(self.app)
        self.assertIn(generar.INICIO, copilot.read_text(encoding="utf-8"))
        repo.desinstalar(self.app)
        self.assertEqual(copilot.read_text(encoding="utf-8"), "# Instrucciones propias\n")

    def test_flujo_cambiado_fuera(self):
        import sys
        import generar
        import repo
        repo.instalar(self.app, ["pruebas-demo"])
        script = self.app / "uxyngraphar" / "sistemas-de-gobernanza" / "pruebas-demo" / "scripts" / "comun" / "verificar-integridad.py"
        correr = lambda: subprocess.run([sys.executable, str(script)], cwd=self.app, capture_output=True, text=True, env=dict(os.environ))  # noqa: E731
        self.assertNotIn("AVISO", correr().stderr)
        generar.guardar_flujo(self.app, {**generar.leer_flujo(self.app), "modo": "leer_por_defecto", "leer_por_defecto": ["pruebas-demo"]})
        self.assertNotIn("AVISO", correr().stderr, "lo que escribe el motor no avisa")
        ruta = generar.ruta_flujo(self.app)
        ruta.chmod(0o644)
        ruta.write_text(ruta.read_text(encoding="utf-8").replace("leer_por_defecto\"", "manual\"", 1), encoding="utf-8")
        r = correr()
        self.assertEqual(r.returncode, 0)
        self.assertIn("FLUJO.json cambió fuera del panel", r.stderr)


class TestVerificarJson(unittest.TestCase):
    """M-16: verificar en JSON, en paralelo, con códigos 0/1/2 e integración opcional en CI."""

    def setUp(self):
        import tempfile
        from pathlib import Path
        import repo
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.app = Path(self._t.name).resolve() / "app"
        subprocess.run(["git", "init", "-q", str(self.app)], check=True)
        ids = ["pruebas-demo", "pruebas-otras", "pruebas-terceras"]
        cat = catalogo_de_prueba(Path(self._t.name) / "catalogo", *ids)
        parche = mock.patch.dict(os.environ, {"UXYNGRAPHAR_HOME": str(Path(self._t.name) / "casa"), "UXYNGRAPHAR_CATALOGO": str(cat)})
        parche.start()
        self.addCleanup(parche.stop)
        repo.instalar(self.app, ids)

    def cli(self, *args):
        import contextlib
        import io
        import cli
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            codigo = cli.main(list(args))
        return codigo, salida.getvalue()

    def test_json_estable_y_orden_en_paralelo(self):
        codigo, texto = self.cli("verificar", "--repo", str(self.app), "--formato", "json", "--trabajos", "4")
        datos = json.loads(texto)
        self.assertEqual((codigo, datos["formato"], datos["codigo"]), (0, 1, 0))
        uno = json.loads(self.cli("verificar", "--repo", str(self.app), "--formato", "json")[1])
        self.assertEqual([(r["sistema"], r["verificacion"]) for r in datos["resultados"]],
                         [(r["sistema"], r["verificacion"]) for r in uno["resultados"]])
        self.assertEqual(set(datos["resultados"][0]), {"sistema", "verificacion", "codigo", "salida"})

    def test_codigos(self):
        import repo
        self.assertEqual(repo.codigo_verificacion([{"codigo": 0, "salida": ""}]), 0)
        self.assertEqual(repo.codigo_verificacion([{"codigo": 0, "salida": ""}, {"codigo": 1, "salida": "error: x"}]), 1)
        self.assertEqual(repo.codigo_verificacion([{"codigo": 1, "salida": ""}, {"codigo": repo.AGOTADO, "salida": ""}]), 2)
        self.assertEqual(repo.codigo_verificacion([{"codigo": 1, "salida": "Traceback (most recent call last):"}]), 2)

    def test_integracion_opcional(self):
        import integracion
        import repo
        self.assertEqual(integracion.estado(self.app), {"workflow": False, "precommit": False})
        integracion.agregar(self.app, "workflow")
        integracion.agregar(self.app, "precommit")
        self.assertEqual(integracion.estado(self.app), {"workflow": True, "precommit": True})
        self.assertIn("verificar --repo . --formato json", (self.app / integracion.WORKFLOW).read_text(encoding="utf-8"))
        self.assertTrue(integracion.quitar(self.app, "workflow"))
        ajeno = self.app / integracion.WORKFLOW
        ajeno.write_text("name: mio\n", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            integracion.agregar(self.app, "workflow")
        self.assertFalse(integracion.quitar(self.app, "workflow"), "no toca un archivo que no es de uxyngraphar")
        repo.desinstalar(self.app)
        self.assertEqual(integracion.estado(self.app)["precommit"], False, "retirar quita el gancho")
        self.assertEqual(ajeno.read_text(encoding="utf-8"), "name: mio\n")


class TestDiagnosticoYAvisos(ConServidor):
    """M-17 y M-28: el informe y los avisos de la portada señalan actualizaciones y cambios a medias."""

    def test_informe_y_avisos(self):
        import diagnostico
        import proyectos
        import repo
        import transaccion
        sin_uxy, al_dia, cortado = self.repo_git("sin-uxy"), self.repo_git("al-dia"), self.repo_git("cortado")
        repo.instalar(al_dia, ["pruebas-demo"])
        repo.instalar(cortado, ["pruebas-demo"])
        transaccion.respaldar(cortado, "instalar")   # «en_curso» y sin nadie con el candado: interrumpida
        proyectos.agregar([str(sin_uxy), str(al_dia), str(cortado)])
        with mock.patch.object(diagnostico.fuentes, "versiones", return_value={"pruebas-demo": "9.0.0", "pruebas-otras": "0.1.0"}):
            datos = diagnostico.informe(red=False)
            avisos = diagnostico.avisos(red=False)
            texto = diagnostico.texto(datos)
        self.assertIn("sin-uxy: sin uxyngraphar", texto)
        self.assertIn("actualizables: pruebas-demo", texto)
        self.assertEqual({(a["tipo"], Path(a["ruta"]).name) for a in avisos} >= {("actualizable", "al-dia"),
                                                                                   ("interrumpida", "cortado")}, True, avisos)
        anonimo = json.dumps(diagnostico.anonimizar(datos))
        self.assertNotIn(str(self.t), anonimo)
        self.assertIn("<proyecto al-dia>", anonimo)
        self.assertIsInstance(self.pedir("/api/avisos"), list)


class TestGrupos(ConServidor):
    """M-18: un grupo se actualiza y se verifica de una vez; la verificación compara los contratos entre sus repos."""

    def test_grupo_con_contrato_desalineado(self):
        import grupos
        import proyectos
        import repo
        api, web = self.repo_git("api"), self.repo_git("web")
        cat = catalogo_de_prueba(self.t / "catalogo-grupos", grupos.CONTRATOS, "pruebas-demo")
        # el motor solo lanza «contratos.py comparar <otros repos>» y lee su código de salida
        (cat / grupos.CONTRATOS / "scripts" / "contratos.py").write_text(
            "import pathlib, sys\n"
            "faltan = [o for o in sys.argv[2:] if not (pathlib.Path(o) / 'documentado').exists()]\n"
            "print(*(f'{pathlib.Path(o).name} no documenta el contrato' for o in faltan))\n"
            "sys.exit(1 if faltan else 0)\n", encoding="utf-8")
        for app in (api, web):
            repo.instalar(app, [grupos.CONTRATOS, "pruebas-demo"], cat=cat)
        proyectos.agregar([str(api), str(web)])
        with self.assertRaises(ValueError):
            grupos.guardar("Sistema", [str(api), str(web)])
        grupos.guardar("sistema", [str(api), str(web)])
        (web / "documentado").write_text("", encoding="utf-8")
        filas = {f["nombre"]: f for f in grupos.verificar("sistema")}
        self.assertEqual(filas["web"]["contratos"], "divergentes")
        self.assertIn("api no documenta", filas["web"]["contratos_salida"])
        self.assertEqual(filas["web"]["codigo"], 1)
        (api / "documentado").write_text("", encoding="utf-8")
        self.assertEqual({f["nombre"]: f["contratos"] for f in grupos.verificar("sistema")}, {"api": "alineados", "web": "alineados"})
        with mock.patch.dict(os.environ, {"UXYNGRAPHAR_CATALOGO": str(cat)}):
            informe = grupos.actualizar("sistema")
        self.assertEqual([f["error"] for f in informe], ["", ""])
        m = grupos.matriz("sistema")
        self.assertEqual(m["sistemas"], [grupos.CONTRATOS, "pruebas-demo"])
        self.assertTrue(all(c["integro"] for r in m["repos"] for c in r["sistemas"].values()))
        self.assertEqual(sorted(self.pedir("/api/grupos")), ["sistema"])
        self.pedir("/api/grupos/borrar", {"nombre": "sistema"})
        self.assertEqual(grupos.listar(), {})


class TestErroresConCodigo(ConServidor):
    """M-25: todos los errores 4xx llevan un código documentado y, si la hay, una acción."""

    def test_codigos(self):
        app = self.repo_git("app")
        casos = [("/api/repo/instalar", {"ids": ["pruebas-demo"]}, "campo_obligatorio", ""),
                 ("/api/repo/instalar", {"repo": str(app), "ids": ["pruebas-demo"]}, "proyecto_no_registrado", "registrar"),
                 ("/api/no-existe", {}, "ruta_desconocida", "")]
        for ruta, datos, codigo, accion in casos:
            self.error(ruta, datos)
            self.assertEqual((self.ultimo_error["codigo"], self.ultimo_error["accion"]), (codigo, accion), ruta)
        self.pedir("/api/proyectos/agregar", {"rutas": [str(app)]})
        self.error("/api/repo/desinstalar", {"repo": str(app), "con_trabajo": True})
        self.assertEqual(self.ultimo_error["codigo"], "falta_confirmacion")
        self.assertEqual(self.error("/api/sesion", token="otro")[0], 403)
        self.assertEqual(self.ultimo_error["codigo"], "sin_sesion")

    def test_codigos_documentados(self):
        import rutas_panel
        readme = (panel.WEB.parent / "README.md").read_text(encoding="utf-8")
        for _, codigo, _ in rutas_panel.CODIGOS:
            self.assertIn(f"`{codigo}`", readme)
        for codigo in ("ajustes_claude_invalidos", "codigo_caducado", "sin_sesion", "ruta_desconocida", "error_interno",
                       "host_no_permitido", "origen_no_permitido", "content_length_invalido", "pedido_demasiado_grande", "json_invalido"):
            self.assertIn(f"`{codigo}`", readme)


class TestRespaldosLigeros(unittest.TestCase):
    """M-10: instalar un sistema en un proyecto con muchos respalda solo ese; la vuelta atrás deja los demás intactos."""

    def setUp(self):
        import tempfile
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.app = Path(self._t.name).resolve() / "app"
        (self.app / ".git").mkdir(parents=True)
        self.diez = [f"pruebas-sistema-{n}" for n in ("uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez")]
        cat = catalogo_de_prueba(Path(self._t.name) / "catalogo", *self.diez, "pruebas-ultimo")
        parche = mock.patch.dict(os.environ, {"UXYNGRAPHAR_HOME": str(Path(self._t.name) / "casa"), "UXYNGRAPHAR_CATALOGO": str(cat)})
        parche.start()
        self.addCleanup(parche.stop)

    def archivos_respaldados(self, respaldo):
        return [q for q in (respaldo / "copia" / "uxyngraphar" / "sistemas-de-gobernanza").rglob("*") if q.is_file()]

    def test_respaldo_proporcional_y_vuelta_atras(self):
        import repo
        import transaccion
        diez = self.diez
        repo.instalar(self.app, diez)
        instalados = sum(1 for q in (self.app / "uxyngraphar" / "sistemas-de-gobernanza").rglob("*") if q.is_file())
        repo.instalar(self.app, ["pruebas-ultimo"])
        self.assertEqual(self.archivos_respaldados(transaccion.ultimo(self.app)), [], "el sistema nuevo no existía: nada que copiar")
        repo.actualizar(self.app, ["pruebas-ultimo"], forzar=True)
        uno = len(self.archivos_respaldados(transaccion.ultimo(self.app)))
        self.assertLess(uno * 5, instalados, "solo se respalda el sistema que se actualiza")
        antes = {q.relative_to(self.app).as_posix(): q.read_bytes() for q in (self.app / "uxyngraphar" / "sistemas-de-gobernanza").rglob("*") if q.is_file()}
        with mock.patch.object(repo.generar, "regenerar", side_effect=RuntimeError("fallo")):
            with self.assertRaises(RuntimeError):
                repo.actualizar(self.app, [diez[0]], forzar=True)
        despues = {q.relative_to(self.app).as_posix(): q.read_bytes() for q in (self.app / "uxyngraphar" / "sistemas-de-gobernanza").rglob("*") if q.is_file()}
        self.assertEqual(antes, despues)
        transaccion.deshacer(self.app)   # deshace la actualización de pruebas-ultimo
        self.assertTrue(all(e["integro"] for e in repo.estado(self.app)))


if __name__ == "__main__":
    unittest.main()
