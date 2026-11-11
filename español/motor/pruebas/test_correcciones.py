"""Pruebas que reproducen los fallos de PLAN-CORRECCIONES (F1–F3 y los hallazgos C-36 en adelante): candado por
proyecto, actualización en segundo plano, proyectos que fallan, settings.json inválido, verificaciones colgadas, orden de
respaldos, pid del panel, API (carpetas, GET sin efectos, 500, Content-Length, permisos, campos) y la CLI."""

from __future__ import annotations

import contextlib
import http.client
import io
import json
import os
import stat
import subprocess
import sys
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

import _rutas  # noqa: F401
import casa
import cli
import flujos_guardados as guardados
import generar
import herramienta
import panel
import procesos
import proyectos
import repo
import rutas_panel
import transaccion
from test_panel_api import ConServidor
from test_proyectos import Entorno

MOTOR = Path(__file__).resolve().parents[1]


def tomar_candado_en_otro_proceso(raiz: Path, segundos: float = 30) -> subprocess.Popen:
    """Otro proceso (como el panel o una segunda CLI) que tiene el candado del proyecto mientras duerme."""
    codigo = ("import sys, time; sys.path[:0] = [sys.argv[1]]; import transaccion\n"
              "with transaccion.candado(sys.argv[2], 'otro proceso'):\n"
              "    print('listo', flush=True); time.sleep(float(sys.argv[3]))\n")
    proc = subprocess.Popen([sys.executable, "-c", codigo, str(MOTOR), str(raiz), str(segundos)],
                            stdout=subprocess.PIPE, text=True, env=dict(os.environ))
    assert proc.stdout.readline().strip() == "listo"
    return proc


class TestCandado(Entorno):
    """C-04: un proyecto solo lo cambia un proceso (o un hilo) a la vez."""

    def setUp(self):
        super().setUp()
        self.app = self.repo_git("app")

    def terminar(self, proc: subprocess.Popen) -> None:
        proc.terminate()
        proc.wait(10)
        proc.stdout.close()

    def test_otro_proceso_con_el_candado_da_error_claro_sin_perder_nada(self):
        repo.instalar(self.app, ["pruebas-demo"])
        proc = tomar_candado_en_otro_proceso(self.app)
        try:
            with self.assertRaises(transaccion.ProyectoOcupado) as ctx:
                repo.instalar(self.app, ["pruebas-otras"])
            self.assertIn("otro cambio en curso", str(ctx.exception))
            self.assertTrue(repo.carpeta_instalada(self.app, "pruebas-demo").is_dir())
            self.assertFalse(repo.carpeta_instalada(self.app, "pruebas-otras").exists())
        finally:
            self.terminar(proc)
        self.assertEqual(repo.instalar(self.app, ["pruebas-otras"]), ["pruebas-otras"], "el candado de un proceso muerto se retira")

    def test_reparar_no_toca_la_transaccion_viva_de_otro_proceso(self):
        repo.instalar(self.app, ["pruebas-demo"])
        transaccion.respaldar(self.app, "en curso en otro proceso")   # respaldo «en_curso», como el de una transacción viva
        proc = tomar_candado_en_otro_proceso(self.app)
        try:
            with self.assertRaises(transaccion.ProyectoOcupado):
                repo.reparar(self.app)
            self.assertIsNotNone(transaccion.interrumpida(self.app))
        finally:
            self.terminar(proc)
        self.assertTrue(any("interrumpido" in h for h in repo.reparar(self.app)))

    def test_dos_procesos_instalan_a_la_vez_y_uno_gana(self):
        orden = [sys.executable, str(MOTOR / "uxyngraphar.py"), "instalar", "pruebas-demo", "--repo", str(self.app)]
        env = dict(os.environ, PYTHONIOENCODING="utf-8", UXYNGRAPHAR_CATALOGO=str(self.cat))
        procs = [subprocess.Popen(orden, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env) for _ in range(2)]
        salidas = [p.communicate(timeout=120) for p in procs]
        codigos = sorted(p.returncode for p in procs)
        self.assertEqual(codigos, [0, 1], salidas)
        perdedor = next(s for p, s in zip(procs, salidas) if p.returncode == 1)
        self.assertRegex(perdedor[1], "otro cambio en curso|ya está instalado")
        self.assertEqual([e["id"] for e in repo.estado(self.app)], ["pruebas-demo"])
        self.assertTrue(all(e["integro"] for e in repo.estado(self.app)))

    def test_dos_hilos_del_panel_no_se_pisan(self):
        repo.instalar(self.app, ["pruebas-demo"])
        dentro, salir, errores = threading.Event(), threading.Event(), []

        def primero():
            with transaccion.transaccion(self.app, "primero"):
                dentro.set()
                salir.wait(10)

        hilo = threading.Thread(target=primero)
        hilo.start()
        dentro.wait(10)
        try:
            repo.instalar(self.app, ["pruebas-otras"])
        except transaccion.ProyectoOcupado as e:
            errores.append(e)
        salir.set()
        hilo.join(10)
        self.assertEqual(len(errores), 1, "un segundo hilo no se cuela como transacción anidada")

    def test_candado_abandonado_se_retira(self):
        ruta = transaccion.carpeta_respaldos(self.app) / transaccion.CANDADO
        ruta.parent.mkdir(parents=True)
        ruta.write_text(json.dumps({"pid": 999999999, "motivo": "proceso muerto"}), encoding="utf-8")
        self.assertIsNone(transaccion.ocupado(self.app))
        self.assertEqual(repo.instalar(self.app, ["pruebas-demo"]), ["pruebas-demo"])
        self.assertFalse(ruta.exists())


class TestRespaldos(Entorno):
    """C-09: con más de 9 respaldos en el mismo segundo, «~10» va después de «~2»."""

    def test_doce_respaldos_en_el_mismo_segundo(self):
        app = self.repo_git("app")
        repo.instalar(app, ["pruebas-demo"])
        with mock.patch.object(transaccion.time, "strftime", return_value="29991231-000000"):
            hechos = []
            for i in range(12):
                r = transaccion.respaldar(app, f"r{i}")
                transaccion._cerrar(r)
                hechos.append(r)
            transaccion._podar(app)
        self.assertEqual(transaccion.respaldos(app), hechos[-3:])
        self.assertEqual(transaccion.ultimo(app), hechos[-1])
        self.assertEqual(json.loads((hechos[-1] / transaccion.MANIFIESTO).read_text(encoding="utf-8"))["motivo"], "r11")

    def test_nombres_antiguos_sin_ceros_se_ordenan_como_numeros(self):
        carpetas = [Path("20260101-000000"), Path("20260101-000000~10"), Path("20260101-000000~2"), Path("20260101-000001")]
        self.assertEqual([c.name for c in sorted(carpetas, key=transaccion._orden)],
                         ["20260101-000000", "20260101-000000~2", "20260101-000000~10", "20260101-000001"])


class TestHerramienta(Entorno):
    def test_actualizar_en_fondo_con_oserror_termina_en_error_y_se_puede_reintentar(self):   # C-05
        def esperar():
            for _ in range(200):
                if herramienta.progreso()["estado"] != "en_curso":
                    break
                time.sleep(0.05)
            return herramienta.progreso()

        with mock.patch.object(herramienta, "descargar_instalador", side_effect=OSError(28, "No queda espacio")) as descarga:
            herramienta.actualizar()
            p = esperar()
            self.assertEqual(p["estado"], "error")
            self.assertTrue(any("No queda espacio" in linea for linea in p["lineas"]), p["lineas"])
            herramienta.actualizar()
            self.assertEqual(esperar()["estado"], "error")
            self.assertEqual(descarga.call_count, 2, "se puede volver a intentar: no se queda «en_curso»")

    def test_actualizar_proyectos_sigue_tras_un_error_inesperado(self):   # C-06
        apps = [self.repo_git(n) for n in ("a", "b", "c")]
        for app in apps:
            repo.instalar(app, ["pruebas-demo"])
        proyectos.agregar([str(a) for a in apps])
        real = repo.actualizar

        def actualizar(raiz, *a, **k):
            if Path(raiz).name == "b":
                raise PermissionError(13, "Permiso denegado", str(raiz / "uxyngraphar" / "sistemas-de-gobernanza"))
            return real(raiz, *a, **k)

        with mock.patch.object(repo, "actualizar", side_effect=actualizar) as llamado:
            filas = {f["nombre"]: f for f in herramienta.actualizar_proyectos()}
        self.assertEqual(llamado.call_count, 3)
        self.assertEqual((filas["a"]["error"], filas["c"]["error"]), ("", ""))
        self.assertIn("PermissionError", filas["b"]["error"])


class TestAjustesClaude(Entorno):
    """C-07: un .claude/settings.json inválido es de la persona: no se toca y el mensaje dice qué pasa."""

    def test_instalar_y_retirar_con_settings_invalido(self):
        app = self.repo_git("app")
        ruta = app / ".claude" / "settings.json"
        ruta.parent.mkdir()
        malo = '{\n  "permissions": {"deny": ["Read(.env)",]}\n}\n'
        ruta.write_text(malo, encoding="utf-8")
        with self.assertRaises(ValueError) as ctx:
            repo.instalar(app, ["pruebas-demo"])
        self.assertIn("no es JSON válido (línea 2)", str(ctx.exception))
        self.assertEqual(ruta.read_text(encoding="utf-8"), malo)
        self.assertFalse((app / "uxyngraphar").exists(), "la transacción deja el proyecto como estaba")
        ruta.write_text('["no es un objeto"]', encoding="utf-8")
        with self.assertRaises(ValueError):
            repo.instalar(app, ["pruebas-demo"])
        ruta.write_text("{}", encoding="utf-8")
        repo.instalar(app, ["pruebas-demo"])
        ruta.write_text(malo, encoding="utf-8")
        with self.assertRaises(ValueError):
            repo.desinstalar(app)
        self.assertEqual(ruta.read_text(encoding="utf-8"), malo)
        self.assertTrue(repo.carpeta_instalada(app, "pruebas-demo").is_dir())


class TestVerificar(Entorno):
    def test_verificacion_colgada_se_corta(self):   # C-08
        app = self.repo_git("app")
        script = repo.carpeta_instalada(app, "lento") / "scripts" / "lento.py"
        script.parent.mkdir(parents=True)
        script.write_text("import time\nprint('empiezo', flush=True)\ntime.sleep(10)\n", encoding="utf-8")
        inicio = time.time()
        r = repo.ejecutar_verificacion(app, "lento", "scripts/lento.py", segundos=1)
        self.assertLess(time.time() - inicio, 5)
        self.assertEqual(r["codigo"], repo.AGOTADO)
        self.assertIn("excedió 1 s", r["salida"])


class TestPidDelPanel(Entorno):
    """C-10: el pid de panel.json se comprueba sin excepciones ni falsos positivos."""

    def test_pids_raros(self):
        for pid in (0, -1, "x", None, "", 1.5e300):
            self.assertFalse(procesos.vivo(pid), pid)
        self.assertTrue(procesos.vivo(os.getpid()))
        for pid in (0, "x", None):
            casa.escribir_json(panel.ESTADO, {"puerto": 1, "token": "t", "pid": pid})
            self.assertIsNone(panel.panel_abierto())

    def test_proceso_lanzado_que_termina(self):
        proc = subprocess.Popen([sys.executable, "-c", "pass"])
        procesos.LANZADOS[proc.pid] = proc
        proc.wait(10)
        self.assertFalse(procesos.vivo(proc.pid))
        procesos.LANZADOS.pop(proc.pid)


class TestApi(ConServidor):
    def setUp(self):
        super().setUp()
        self.app = self.repo_git("app")

    def crudo(self, cuerpo: bytes, cabeceras: dict) -> tuple[int, dict]:
        con = http.client.HTTPConnection("127.0.0.1", self.servidor.server_address[1], timeout=10)
        try:
            con.putrequest("POST", "/api/latido")
            for k, v in {"X-Uxyn-Token": self.token, **cabeceras}.items():
                con.putheader(k, v)
            con.endheaders()
            con.send(cuerpo)
            r = con.getresponse()
            return r.status, json.loads(r.read() or b"{}")
        finally:
            con.close()

    def test_carpetas_que_no_son_proyectos(self):   # C-11
        for ruta in (Path(Path.home().anchor or "/"), Path.home(), casa.carpeta()):
            casa.carpeta().mkdir(parents=True, exist_ok=True)
            codigo, _ = self.error("/api/repo/instalar", {"repo": str(ruta), "ids": ["pruebas-demo"]})
            self.assertEqual(codigo, 400, ruta)
            self.assertEqual(self.error("/api/proyectos/agregar", {"rutas": [str(ruta)]})[0], 400, ruta)
        codigo, mensaje = self.error("/api/repo/instalar", {"repo": str(self.app), "ids": ["pruebas-demo"]})
        self.assertEqual(codigo, 400)
        self.assertIn("uxyngraphar proyectos agregar", mensaje)
        self.assertFalse((self.app / "uxyngraphar").exists())
        sin_git = self.t / "suelta"
        sin_git.mkdir()
        self.assertIn("confirmar", self.error("/api/proyectos/agregar", {"rutas": [str(sin_git)]})[1])
        self.assertEqual(self.pedir("/api/proyectos/agregar", {"rutas": [str(sin_git)], "confirmar": "suelta"}), [str(sin_git)])

    def test_acciones_destructivas_piden_confirmar(self):   # C-11
        self.pedir("/api/proyectos/agregar", {"rutas": [str(self.app)]})
        self.pedir("/api/repo/instalar", {"repo": str(self.app), "ids": ["pruebas-demo"]})
        (self.app / "uxyngraphar" / "trabajo" / "pruebas-demo" / "mio.md").write_text("mío\n", encoding="utf-8")
        for ruta, datos in (("/api/repo/desinstalar", {"con_trabajo": True}), ("/api/repo/quitar", {"id": "pruebas-demo", "con_trabajo": True})):
            codigo, mensaje = self.error(ruta, {"repo": str(self.app), **datos})
            self.assertEqual(codigo, 400, ruta)
            self.assertIn("confirmar", mensaje)
        self.assertTrue((self.app / "uxyngraphar" / "trabajo" / "pruebas-demo" / "mio.md").is_file())
        self.pedir("/api/repo/desinstalar", {"repo": str(self.app), "con_trabajo": True, "confirmar": "app"})
        self.assertFalse((self.app / "uxyngraphar").exists())

    def test_get_no_escribe_en_el_proyecto(self):   # C-12
        self.pedir("/api/proyectos/agregar", {"rutas": [str(self.app)]})
        self.pedir("/api/repo/instalar", {"repo": str(self.app), "ids": ["pruebas-demo"]})
        generar.ruta_flujo(self.app).unlink()
        estado = self.pedir(f"/api/repo/estado?repo={self.app}")
        self.assertEqual(estado["flujo"]["modo"], "manual")
        self.assertEqual(self.pedir(f"/api/repo/flujo?repo={self.app}")["modo"], "manual")
        self.pedir("/api/flujos/desde-proyecto", {"repo": str(self.app), "nombre": "Solo leer"})
        self.assertFalse(generar.ruta_flujo(self.app).exists())

    def test_error_no_previsto_responde_500_con_registro(self):   # C-13
        with mock.patch.dict(rutas_panel.GET, {"/api/catalogo": mock.Mock(side_effect=RuntimeError("fallo raro"))}):
            codigo, _ = self.error("/api/catalogo")
        self.assertEqual(codigo, 500)
        with mock.patch.dict(rutas_panel.GET, {"/api/catalogo": mock.Mock(side_effect=KeyError("interno"))}):
            try:
                self.pedir("/api/catalogo")
            except Exception as e:  # noqa: BLE001
                with e:
                    datos = json.loads(e.read())
        self.assertEqual(datos["error"], {"codigo": "error_interno", "mensaje": "error interno", "accion": "ver_registro"})
        self.assertIn("KeyError", datos["detalle"], "un KeyError interno ya no se disfraza de error de usuario (C-17)")
        registro = Path(datos["registro"]).read_text(encoding="utf-8")
        self.assertIn("RuntimeError: fallo raro", registro)
        self.assertIn("Traceback", registro)

    def test_content_length_malo(self):   # C-14
        self.assertEqual(self.crudo(b"{}", {"Content-Length": "abc"})[0], 400)
        self.assertEqual(self.crudo(b"{}", {"Content-Length": "-1"})[0], 400)
        self.assertEqual(self.crudo(b"", {"Content-Length": str(10 ** 9)})[0], 413)
        self.assertTrue(self.pedir("/api/latido", {}), "el servidor sigue respondiendo")

    def test_campo_que_falta(self):   # C-17
        codigo, mensaje = self.error("/api/repo/instalar", {"ids": ["pruebas-demo"]})
        self.assertEqual((codigo, mensaje), (400, "falta el campo «repo»"))
        self.pedir("/api/proyectos/agregar", {"rutas": [str(self.app)]})
        self.assertEqual(self.error("/api/repo/instalar", {"repo": str(self.app)})[1], "falta el campo «ids»")
        self.assertIn("debe ser una lista", self.error("/api/repo/instalar", {"repo": str(self.app), "ids": "pruebas-demo"})[1])

    def test_settings_invalido_en_el_panel(self):   # C-07 por la API
        self.pedir("/api/proyectos/agregar", {"rutas": [str(self.app)]})
        (self.app / ".claude").mkdir()
        (self.app / ".claude" / "settings.json").write_text("{ // comentario\n}", encoding="utf-8")
        codigo, mensaje = self.error("/api/repo/instalar", {"repo": str(self.app), "ids": ["pruebas-demo"]})
        self.assertEqual(codigo, 400)
        self.assertIn("no es JSON válido", mensaje)

    def test_proyecto_ocupado_responde_409(self):   # C-04 por la API
        self.pedir("/api/proyectos/agregar", {"rutas": [str(self.app)]})
        proc = tomar_candado_en_otro_proceso(self.app)
        try:
            codigo, mensaje = self.error("/api/repo/instalar", {"repo": str(self.app), "ids": ["pruebas-demo"]})
        finally:
            proc.terminate()
            proc.wait(10)
            proc.stdout.close()
        self.assertEqual(codigo, 409)
        self.assertIn("otro cambio en curso", mensaje)


@unittest.skipIf(os.name == "nt", "permisos POSIX; en Windows vale la ACL del perfil")
class TestPermisosDelToken(Entorno):
    def test_panel_json_solo_para_su_dueno(self):   # C-15
        casa.carpeta().mkdir(parents=True)
        os.chmod(casa.carpeta(), 0o755)
        ruta = casa.escribir_json(panel.ESTADO, {"puerto": 1, "token": "secreto", "pid": 1}, privado=True)
        self.assertEqual(stat.S_IMODE(ruta.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(casa.carpeta().stat().st_mode), 0o700)


class TestHallazgosNuevos(Entorno):
    def cli(self, *args: str) -> tuple[int, str]:
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            codigo = cli.main(list(args))
        return codigo, err.getvalue()

    def test_cli_sin_traceback_ante_oserror(self):   # C-36
        app = self.repo_git("app")
        with mock.patch.object(repo, "instalar", side_effect=PermissionError(13, "Permiso denegado", str(app))):
            codigo, err = self.cli("instalar", "pruebas-demo", "--repo", str(app))
        self.assertEqual(codigo, 1)
        self.assertIn("error: Permiso denegado", err)

    def test_flujos_guardados_sin_id(self):   # C-37
        for accion in ("borrar", "exportar", "aplicar", "importar", "guardar"):
            codigo, err = self.cli("flujos-guardados", accion)
            self.assertEqual(codigo, 1, accion)
            self.assertIn("falta", err)

    def test_aplicar_flujo_sigue_tras_un_error_inesperado(self):   # C-38
        a, b = self.repo_git("a"), self.repo_git("b")
        fid = guardados.guardar({"nombre": "Demo", "sistemas": ["pruebas-demo"], "flujo": {}})
        real = repo.instalar
        with mock.patch.object(repo, "instalar", side_effect=lambda r, *x, **k: (_ for _ in ()).throw(PermissionError("sin permiso"))
                               if Path(r).name == "a" else real(r, *x, **k)):
            filas = guardados.aplicar(fid, [str(a), str(b)])
        self.assertIn("PermissionError", filas[0]["error"])
        self.assertEqual((filas[1]["error"], filas[1]["instalados"]), ("", ["pruebas-demo"]))

    def test_resumenes_con_un_proyecto_ilegible(self):   # C-39
        a, b = self.repo_git("a"), self.repo_git("b")
        proyectos.agregar([str(a), str(b)])
        real = proyectos.resumen
        with mock.patch.object(proyectos, "resumen", side_effect=lambda r, v=None: (_ for _ in ()).throw(OSError("roto"))
                               if Path(r).name == "a" else real(r, v)):
            filas = {f["nombre"]: f for f in proyectos.resumenes()}
        self.assertIn("roto", filas["a"]["error"])
        self.assertNotIn("error", filas["b"])


class TestClaudeMd(Entorno):
    """C-23: instalar crea CLAUDE.md con el mismo bloque que AGENTES.md; retirar lo quita sin tocar lo propio."""

    def test_repo_vacio(self):
        app = self.repo_git("app")
        repo.instalar(app, ["pruebas-demo"])
        textos = {n: (app / n).read_text(encoding="utf-8") for n in generar.ARCHIVOS_AGENTE}
        self.assertIn(generar.INICIO, textos["CLAUDE.md"])
        self.assertEqual(len(set(textos.values())), 1, "el mismo bloque completo en los tres archivos")
        repo.desinstalar(app)
        self.assertFalse(any((app / n).exists() for n in generar.ARCHIVOS_AGENTE))

    def test_claude_md_propio(self):
        app = self.repo_git("app")
        (app / "CLAUDE.md").write_text("# Mis normas\n\nUsa tabuladores.\n", encoding="utf-8")
        repo.instalar(app, ["pruebas-demo"])
        texto = (app / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertTrue(texto.startswith("# Mis normas\n\nUsa tabuladores.\n"))
        self.assertEqual(texto.count(generar.INICIO), 1)
        repo.desinstalar(app)
        self.assertEqual((app / "CLAUDE.md").read_text(encoding="utf-8"), "# Mis normas\n\nUsa tabuladores.\n")

    def test_un_fallo_restaura_claude_md(self):
        app = self.repo_git("app")
        (app / "CLAUDE.md").write_text("propio\n", encoding="utf-8")
        with mock.patch.object(generar, "flujo_inicial", side_effect=RuntimeError("fallo")):
            with self.assertRaises(RuntimeError):
                repo.instalar(app, ["pruebas-demo"])
        self.assertEqual((app / "CLAUDE.md").read_text(encoding="utf-8"), "propio\n")
        self.assertFalse((app / "uxyngraphar").exists(), "tampoco queda la carpeta de trabajo vacía (C-40)")


class TestNormaDelCatalogo(unittest.TestCase):
    """C-28, C-30, C-31 y C-41 sobre sistemas de prueba."""

    def setUp(self):
        import tempfile
        from test_especificacion import crear_sistema
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.n = 0

        def crear(m=None):
            self.n += 1
            destino = Path(self._t.name) / str(self.n)
            destino.mkdir()
            return crear_sistema(destino, m)
        self.crear = crear

    def test_descripcion_plantilla(self):   # C-28
        import especificacion as esp
        from test_especificacion import MANIFIESTO_VALIDO as MANIFIESTO
        errores = esp.validar_sistema(self.crear({**MANIFIESTO, "descripcion": "Plantilla"}))
        self.assertTrue(any("texto de la base" in e for e in errores), errores)

    def test_rango_del_motor(self):   # C-31
        import especificacion as esp
        self.assertTrue(esp.motor_compatible(">=1.0,<2", "1.9.3"))
        self.assertFalse(esp.motor_compatible(">=1.0,<2", "2.0.0"))
        self.assertFalse(esp.motor_compatible(">=1.2,<2", "1.1.0"))
        self.assertFalse(esp.motor_compatible(">=2.0", "1.0.0"))
        from test_especificacion import MANIFIESTO_VALIDO as MANIFIESTO
        self.assertTrue(any("sin techo" in e for e in esp.validar_sistema(self.crear({**MANIFIESTO, "motor": ">=1.0"}))))
        with mock.patch.dict(esp.PIEZA_DESDE, {"referencia": (1, 1)}):
            errores = esp.validar_sistema(self.crear())
        self.assertTrue(any("hace falta >=1.1" in e for e in errores), errores)

    def test_status_validos_cuentan_para_la_norma(self):   # C-41
        import nomenclatura
        m = {"id": "pruebas-norma", "titulo": "Pruebas norma", "familia": "proceso", "activacion": ["pruebas-norma", "pruebas norma"],
             "fichas": {"cosa": {"prefijo": "PNO", "plantilla": "plantillas/cosa.md", "status_validos": ["vigente", "authorized"]}}}
        errores, _ = nomenclatura.problemas_sistema(Path(self._t.name), m)
        self.assertTrue(any("«authorized» fuera del vocabulario" in e for e in errores), errores)

    def test_aviso_scripts_sin_pruebas(self):   # C-30
        import especificacion as esp
        c = self.crear()
        (c / "scripts").mkdir(exist_ok=True)
        (c / "scripts" / "cosa.py").write_text("print(1)\n", encoding="utf-8")
        self.assertTrue(any("no tiene pieza «pruebas»" in a for a in esp.avisos_sistema(c)))


if __name__ == "__main__":
    unittest.main()
