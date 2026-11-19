"""Hallazgos del informe de QA de la 1.5.15 (sección KIT): cada prueba reproduce el fallo que se vio."""

from __future__ import annotations

import contextlib
import http.client
import io
import json
import os
import urllib.error
from email.message import Message
from pathlib import Path
from unittest import mock

import _rutas  # noqa: F401
import casa
import catalogo
import cli
import conexiones
import desinstalacion
import herramienta
import nomenclatura
import panel
import proyectos
import remoto
import repo
import transaccion
import uxyngraphar
from test_instalador import VERSION
from test_instalador import Entorno as EntornoInstalador
from test_panel_api import ConServidor
from test_proyectos import Entorno

ar = casa.ar
WEB = Path(__file__).resolve().parents[1] / "web"


def salida(funcion, *args) -> tuple[object, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            codigo = funcion(*args)
        except SystemExit as e:
            codigo = e.code
    return codigo, out.getvalue(), err.getvalue()


def sistema_de_autor(carpeta: Path, pid: str, version: str = "1.0.0") -> Path:
    c = carpeta / pid
    c.mkdir(parents=True, exist_ok=True)
    (c / "sistema.json").write_text(json.dumps({"id": pid, "version": version}), encoding="utf-8")
    return c


class SinCatalogoElegido(Entorno):
    def setUp(self):
        super().setUp()
        parche = mock.patch.dict(os.environ)
        parche.start()
        self.addCleanup(parche.stop)
        os.environ.pop("UXYNGRAPHAR_CATALOGO", None)
        self.home = casa.carpeta()
        self.home.mkdir(parents=True, exist_ok=True)


# 1. ALTA: los sistemas del autor se perdían al reparar, actualizar, cambiar de versión, podar o desinstalar.
class TestCatalogoDelAutor(SinCatalogoElegido):
    def test_catalogo_fuera_de_versiones_y_configurable(self):
        home = str(self.home)
        self.assertEqual(ar.carpeta_catalogo_autor(home), os.path.join(home, "catalogo"))
        casa.escribir_json(Path(home) / "casa.json", {"catalogo_local": str(self.t / "desde-casa")})
        self.assertEqual(ar.carpeta_catalogo_autor(home), str(self.t / "desde-casa"))
        with mock.patch.dict(os.environ, {"UXYNGRAPHAR_CATALOGO": str(self.t / "elegido")}):
            self.assertEqual(ar.carpeta_catalogo_autor(home), str(self.t / "elegido"))
            self.assertEqual(catalogo.catalogo(), self.t / "elegido")
            codigo, _, err = salida(cli.main, ["crear", "revision-de-pagos", "--titulo", "Revisión de pagos", "--familia", nomenclatura.NORMA["familias"][0]])
            self.assertEqual(codigo, 0, err)
            self.assertTrue((self.t / "elegido" / "revision-de-pagos" / "sistema.json").is_file(), "crear respeta UXYNGRAPHAR_CATALOGO")

    def test_rescate_de_versiones_sin_perder_nada(self):
        cat_10 = self.home / "versiones" / "1.0.0" / "sistemas-de-gobernanza"
        cat_11 = self.home / "versiones" / "1.1.0" / "sistemas-de-gobernanza"
        sistema_de_autor(cat_10, "_base")
        sistema_de_autor(cat_10, "del-kit")
        (cat_10.parent / ar.ARCHIVOS).write_text("0" * 64 + "  sistemas-de-gobernanza/del-kit/sistema.json\n", encoding="utf-8")
        sistema_de_autor(cat_10, "mio", "1.0.0")
        sistema_de_autor(cat_11, "mio", "1.2.0")
        sistema_de_autor(cat_11, "otro")
        hechos, fallos = ar.rescatar_catalogo(str(self.home))
        self.assertEqual(fallos, [])
        self.assertEqual(len(hechos), 3, hechos)
        destino = self.home / "catalogo"
        self.assertEqual(sorted(p.name for p in destino.iterdir()), ["mio", "otro"])
        self.assertEqual(json.loads((destino / "mio" / "sistema.json").read_text())["version"], "1.2.0", "gana la más nueva")
        apartados = list((self.home / "respaldos" / "catalogo").iterdir())
        self.assertEqual(len(apartados), 1, "la otra copia se aparta, no se borra")
        self.assertTrue((cat_10 / "del-kit").is_dir() and (cat_10 / "_base").is_dir(), "lo que trae la versión se queda")
        self.assertEqual(ar.sistemas_de_autor_en_versiones(str(self.home)), [])

    def test_podar_rescata_antes_de_borrar(self):
        for v in ("1.0.0", "1.1.0", "1.2.0", "1.3.0", "1.4.0"):
            c = self.home / "versiones" / v
            c.mkdir(parents=True)
            (c / "motor").mkdir()
            (c / "motor" / "uxyngraphar.py").write_text("", encoding="utf-8")
            (c / ".completa").write_text(json.dumps({"linea": ar.LINEA, "version": v}), encoding="utf-8")
        sistema_de_autor(self.home / "versiones" / "1.0.0" / "sistemas-de-gobernanza", "mio")
        ar.podar_versiones(str(self.home), ["1.4.0"])
        self.assertFalse((self.home / "versiones" / "1.0.0").exists())
        self.assertTrue((self.home / "catalogo" / "mio" / "sistema.json").is_file())

    def test_desinstalar_avisa_y_pide_confirmar(self):
        sistema_de_autor(self.home / "catalogo", "mio")
        plan = desinstalacion.planificar("herramienta")
        self.assertEqual([Path(r).name for r in plan["catalogo"]], ["mio"])
        self.assertIn("mio", desinstalacion.texto_informe({**plan, "simulado": True}))
        with self.assertRaises(desinstalacion.CatalogoSinConfirmar):
            desinstalacion.ejecutar("herramienta")
        codigo, _, err = salida(uxyngraphar.main, ["desinstalar", "--alcance", "herramienta", "--si"])
        self.assertEqual(codigo, 2)
        self.assertIn("--con-catalogo", err)
        self.assertTrue((self.home / "catalogo" / "mio" / "sistema.json").is_file(), "no se borró nada")

    def test_alcances_del_lanzador_iguales_a_los_de_desinstalacion(self):
        self.assertEqual(tuple(uxyngraphar.ALCANCES), tuple(desinstalacion.ALCANCES))


class TestCatalogoSobreviveAReparar(EntornoInstalador):
    def test_crear_reparar_y_migrar(self):
        self.servir()
        self.assertEqual(self.por_tuberia(self.instalador()).returncode, 0)
        familia = nomenclatura.NORMA["familias"][0]
        r = self.uxyngraphar("crear", "revision-de-pagos", "--titulo", "Revisión de pagos", "--familia", familia)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.uxy / "catalogo" / "revision-de-pagos" / "sistema.json").is_file())
        # Uno escrito con la 1.5.15, todavía dentro de la carpeta de la versión.
        viejo = sistema_de_autor(self.uxy / "versiones" / VERSION / "sistemas-de-gobernanza", "de-antes")
        r = self.por_tuberia(self.instalador(), "--reparar")
        self.assertEqual(r.returncode, 0, r.stdout.decode() + r.stderr.decode())
        self.assertFalse(viejo.exists())
        self.assertTrue((self.uxy / "catalogo" / "de-antes" / "sistema.json").is_file(), "migrado fuera de versiones/")
        self.assertTrue((self.uxy / "catalogo" / "revision-de-pagos" / "sistema.json").is_file(), "reparar no lo borra")
        r = self.uxyngraphar("catalogo")
        self.assertIn("revision-de-pagos", r.stdout + r.stderr)


# 2. MEDIA: --help ejecutaba el comando y las opciones desconocidas se ignoraban.
class TestAyudaNoEjecuta(Entorno):
    def test_help_y_opciones_desconocidas(self):
        with mock.patch.object(uxyngraphar, "_autoactualizar", return_value=0) as auto:
            codigo, out, _ = salida(uxyngraphar.main, ["autoactualizar", "--help"])
            self.assertEqual(codigo, 0)
            self.assertIn("uso:", out)
            codigo, _, err = salida(uxyngraphar.main, ["autoactualizar", "--verison", "1.0.0"])
            self.assertEqual(codigo, 2)
            self.assertIn("no reconocidos", err)
            auto.assert_not_called()
        import reparacion
        with mock.patch.object(reparacion, "reparar") as reparar:
            self.assertEqual(salida(uxyngraphar.main, ["reparar", "--help"])[0], 0)
            reparar.assert_not_called()
        for cmd in ("usar", "desinstalar"):
            codigo, out, _ = salida(uxyngraphar.main, [cmd, "--help"])
            self.assertEqual(codigo, 0, cmd)
            self.assertIn("muestra esta ayuda", out)


# 3. BAJA-MEDIA: un --repo inexistente pasaba por proyecto vacío (o se creaba).
class TestRepoInexistente(Entorno):
    def test_estado_verificar_e_instalar(self):
        no_hay = self.t / "no-existe" / "dir"
        self.assertEqual(salida(cli.main, ["estado", "--repo", str(no_hay)])[0], 1)
        codigo, _, err = salida(cli.main, ["verificar", "--repo", str(no_hay)])
        self.assertEqual(codigo, 2)
        self.assertIn("no existe la carpeta del proyecto", err)
        self.assertEqual(salida(cli.main, ["instalar", "pruebas-demo", "--repo", str(no_hay)])[0], 1)
        self.assertFalse((self.t / "no-existe").exists())


class ConAgentes(Entorno):
    def setUp(self):
        super().setUp()
        self.inicio = self.t / "inicio"
        self.inicio.mkdir()
        parche = mock.patch.dict(os.environ, {"UXYNGRAPHAR_INICIO_AGENTES": str(self.inicio)})
        parche.start()
        self.addCleanup(parche.stop)
        self.app = self.repo_git("app")
        repo.instalar(self.app, ["pruebas-demo"])


# 4. BAJA-MEDIA: detección de agentes.
class TestDeteccion(ConAgentes):
    def test_codex_no_se_detecta_por_nuestra_carpeta_ni_deja_restos(self):
        import ia_local
        with mock.patch.object(ia_local, "ejecutable", return_value=None):
            conexiones.conectar("codex", [str(self.app)])
            self.assertFalse(conexiones.detectar("codex"), "~/.codex solo con nuestro bloque no es Codex instalado")
            conexiones.desconectar("codex", [str(self.app)])
            self.assertFalse((self.inicio / ".codex" / "config.toml").exists(), "sin config.toml de 1 byte")
            self.assertFalse((self.inicio / ".codex").exists())

    def test_claude_de_claude_desktop(self):
        import ia_local
        with mock.patch.object(ia_local, "ejecutable", side_effect=lambda p: "/apps/Claude/claude" if p == "claude" else None):
            self.assertTrue(conexiones.detectar("claude"))
            self.assertFalse(conexiones.detectar("gemini"))


# 5. BAJA-MEDIA: desinstalar un proyecto dejaba sus conexiones y decía «no queda nada».
class TestDesinstalarConexiones(ConAgentes):
    def test_quita_mcp_instrucciones_y_bloque_codex(self):
        proyectos.agregar([str(self.app)])
        for agente in ("cursor", "gemini", "codex"):
            conexiones.conectar(agente, [str(self.app)])
        self.assertTrue(conexiones.restos(self.app))
        informe = desinstalacion.ejecutar("proyectos", [str(self.app)])
        self.assertEqual(conexiones.restos(self.app), [])
        self.assertFalse(conexiones.codex_huerfano())
        toml = self.inicio / ".codex" / "config.toml"
        self.assertFalse(toml.is_file() and conexiones.TOML_INI in toml.read_text(encoding="utf-8"))
        cursor = self.app / ".cursor" / "mcp.json"
        self.assertFalse(cursor.is_file() and conexiones.NOMBRE in cursor.read_text(encoding="utf-8"))
        self.assertEqual(informe["pendiente"], [])
        self.assertIn("no queda nada", desinstalacion.texto_informe(informe))

    def test_comprobacion_final_veraz(self):
        conexiones.conectar("cursor", [str(self.app)])
        with mock.patch.object(conexiones, "retirar_proyecto", return_value=([], [])):
            informe = desinstalacion.ejecutar("proyectos", [str(self.app)])
        self.assertTrue(informe["pendiente"], "si queda la entrada MCP, lo dice")
        self.assertNotIn("no queda nada", desinstalacion.texto_informe(informe))


# 6. BAJA: un tipo mal escrito en «accesos» borraba los accesos existentes.
class TestAccesos(Entorno):
    def test_tipo_desconocido_no_toca_nada(self):
        with mock.patch.object(ar, "quitar_accesos") as quitar:
            codigo, _, err = salida(cli.main, ["accesos", "fooo"])
            self.assertEqual(codigo, 1)
            self.assertIn("no he cambiado nada", err)
            with self.assertRaises(ValueError):
                herramienta.cambiar_accesos(["menu", "fooo"])
            quitar.assert_not_called()


# 7. BAJA: comandos que no hacían nada y salían con 0.
class TestSinSilencios(Entorno):
    def test_construir_empaquetar_andamiar_y_validar(self):
        for cmd in ("construir", "empaquetar"):
            codigo, _, err = salida(cli.main, [cmd, "--destino", str(self.t / cmd)])
            self.assertEqual(codigo, 1, cmd)
            self.assertIn("--todos", err)
        app = self.repo_git("app")
        repo.instalar(app, ["pruebas-demo"])
        codigo, out, _ = salida(cli.main, ["andamiar", "pruebas-demo", "--repo", str(app)])
        self.assertEqual(codigo, 0)
        self.assertIn("no trae andamiaje", out)
        borrador = self.t / "borrador"
        salida(cli.main, ["creador", "nuevo", "--dir", str(borrador), "--id", "a-medias", "--titulo", "A medias"])
        self.assertEqual(salida(cli.main, ["creador", "validar", "--dir", str(borrador)])[0], 1)


# 8. BAJA: «reparar --proyectos» decía que todo estaba bien después de reconstruir algo.
class TestRepararMensaje(Entorno):
    def test_no_se_contradice(self):
        import reparacion
        informe = {"hechos": [], "problemas": [], "proyectos": [
            {"nombre": "nogit", "error": None, "hechos": ["revision-de-pagos: reconstruido (estaba alterado)"]}]}
        with mock.patch.object(reparacion, "reparar", return_value=informe):
            codigo, out, _ = salida(uxyngraphar.main, ["reparar", "--proyectos", "--sin-descargar"])
        self.assertEqual(codigo, 0)
        self.assertIn("reconstruido", out)
        self.assertNotIn("Todo estaba bien", out)
        self.assertIn("Reparación terminada", out)


# 9. BAJA: panel: estados HTTP, errores en español y métodos no admitidos.
class TestPanelErrores(ConServidor):
    def crudo(self, metodo: str, ruta: str) -> tuple[int, dict, dict]:
        con = http.client.HTTPConnection("127.0.0.1", self.servidor.server_address[1], timeout=10)
        try:
            con.request(metodo, ruta, headers={"X-Uxyn-Token": self.token})
            r = con.getresponse()
            cuerpo = r.read()
            return r.status, dict(r.getheaders()), json.loads(cuerpo) if cuerpo else {}
        finally:
            con.close()

    def test_metodos_no_admitidos_en_json(self):
        for metodo in ("PUT", "DELETE", "PATCH", "OPTIONS"):
            estado, cabeceras, cuerpo = self.crudo(metodo, "/api/proyectos")
            self.assertEqual(estado, 405, metodo)
            self.assertEqual(cabeceras.get("Allow"), "GET, POST")
            self.assertEqual(cuerpo["error"]["codigo"], "metodo_no_permitido")
            self.assertIn("método no permitido", cuerpo["error"]["mensaje"])
        estado, cabeceras, cuerpo = self.crudo("HEAD", "/")
        self.assertEqual((estado, cuerpo), (405, {}))
        self.assertIn("json", cabeceras.get("Content-Type", ""))

    def test_numero_mal_escrito_en_espanol(self):
        codigo, mensaje = self.error("/api/historial?limite=abc")
        self.assertEqual(codigo, 400)
        self.assertIn("número entero", mensaje)
        self.assertNotIn("invalid literal", mensaje)

    def test_estados_por_tipo_de_error(self):
        import rutas_panel
        self.assertEqual(rutas_panel.estado_http(PermissionError("sin sesión")), 401)
        self.assertEqual(rutas_panel.estado_http(PermissionError(13, "Permission denied", "/x")), 403)
        self.assertEqual(rutas_panel.estado_http(remoto.DePago("de pago")), 402)
        self.assertEqual(rutas_panel.estado_http(FileNotFoundError(2, "No such file or directory", "/x")), 404)
        self.assertEqual(rutas_panel.estado_http(ValueError("x")), 400)
        self.assertEqual(rutas_panel.codigo_error(PermissionError("sin sesión")), ("sin_sesion_cuenta", "iniciar_sesion"))

    def test_inicio_no_pide_rutas_de_sesion_sin_sesion(self):
        js = (WEB / "js" / "vistas" / "inicio.js").read_text(encoding="utf-8")
        self.assertIn('obtener("/api/cuenta")', js)
        for ruta in ("/api/creador/borradores", "/api/agente/propuestas"):
            antes = js[:js.index(ruta)]
            self.assertIn("if (sesion)", antes[-200:], ruta)

    def test_movil_sin_desbordar(self):
        css = (WEB / "estilos.css").read_text(encoding="utf-8")
        movil = css[css.index("@media (max-width: 820px)"):]
        self.assertIn(".marco { grid-template-columns: minmax(0, 1fr); }", movil)
        self.assertIn("minmax(0, 1fr) minmax(0, 1fr)", movil)


# 10. BAJA: las respuestas de error (HTTPError) quedaban abiertas (ResourceWarning en Python 3.15).
class TestHTTPErrorCerrado(Entorno):
    def error_http(self, codigo: int) -> urllib.error.HTTPError:
        return urllib.error.HTTPError("http://x/a", codigo, "error", Message(), io.BytesIO(b'{"message": "no"}'))

    def test_pedir_y_pedir_json_cierran(self):
        for funcion in (lambda: remoto._pedir("/a"), lambda: remoto._pedir_json("/a")):
            e = self.error_http(500)
            with mock.patch.object(remoto, "servidor", return_value="http://x"), \
                    mock.patch.object(remoto.urllib.request, "urlopen", side_effect=e):
                with contextlib.suppress(Exception):
                    funcion()
            self.assertTrue(e.fp.closed)


# 11. Listas vacías, argparse y errores crudos en inglés.
class TestTextosEnEspanol(Entorno):
    def test_listas_vacias_dicen_algo(self):
        for args in (["proyectos"], ["grupos"], ["flujos-guardados"]):
            codigo, out, _ = salida(cli.main, args)
            self.assertEqual(codigo, 0, args)
            self.assertTrue(out.strip(), args)

    def test_argparse_y_comando_desconocido(self):
        codigo, out, _ = salida(cli.main, ["estado", "--help"])
        self.assertEqual(codigo, 0)
        self.assertIn("uso:", out)
        self.assertNotIn("usage:", out)
        self.assertNotIn("show this help", out)
        codigo, _, err = salida(cli.main, ["etsado"])
        self.assertEqual(codigo, 2)
        self.assertIn("comando desconocido", err)
        self.assertIn("estado", err, "propone el parecido")

    def test_errores_del_sistema_en_espanol(self):
        e = FileNotFoundError(2, "No such file or directory", "/x/y")
        self.assertEqual(casa.mensaje_de_error(e), "no existe: /x/y")
        try:
            json.loads('{"a" 1}')
        except json.JSONDecodeError as j:
            texto = casa.mensaje_de_error(j)
        self.assertIn("no es JSON válido", texto)
        self.assertNotIn("Expecting", texto)
        spec = self.t / "spec.json"
        spec.write_text('{"id": ', encoding="utf-8")
        codigo, _, err = salida(cli.main, ["generar", "desde", str(spec)])
        self.assertEqual(codigo, 1)
        self.assertNotIn("Expecting", err)
        self.assertNotIn("Errno", salida(cli.main, ["generar", "desde", str(self.t / "no-hay.json")])[2])


# 12. Menores.
class TestMenores(Entorno):
    def test_mensaje_de_macos_pide_310(self):
        with mock.patch.object(ar.sys, "platform", "darwin"):
            texto = ar.problema_python((3, 8))
        self.assertIn("Instala Python 3.10 o superior desde https://www.python.org", texto)
        self.assertNotIn("3.12", texto)

    def test_version_parche_anota_el_changelog(self):
        c = self.cat / "pruebas-demo"
        if not (c / "CHANGELOG.md").is_file():
            (c / "CHANGELOG.md").write_text("# Cambios\n", encoding="utf-8")
        nueva = catalogo.versionar("pruebas-demo", "parche", self.cat, nota="Arreglo de prueba.")
        texto = (c / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn(f"## {nueva}", texto)
        self.assertIn("Arreglo de prueba.", texto)

    def test_proyectos_agregar_dos_veces(self):
        app = self.repo_git("app")
        self.assertIn("añadido", salida(cli.main, ["proyectos", "agregar", str(app)])[1])
        codigo, out, _ = salida(cli.main, ["proyectos", "agregar", str(app)])
        self.assertEqual(codigo, 0)
        self.assertIn("ya estaba en la lista", out)
        self.assertNotIn("añadido", out)

    def test_deshacer_no_guarda_fallidos_ni_sin_cambios(self):
        app = self.repo_git("app")
        repo.instalar(app, ["pruebas-demo"])
        antes = len(transaccion.respaldos(app))
        repo.actualizar(app)   # no cambia nada
        self.assertEqual(len(transaccion.respaldos(app)), antes)
        with mock.patch.object(repo, "_colocar", side_effect=OSError("fallo a propósito")):
            with self.assertRaises(OSError):
                repo.actualizar(app, forzar=True)
        self.assertEqual(len(transaccion.respaldos(app)), antes)
