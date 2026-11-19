"""1.5.21: quitar un proyecto (solo desvincular o quitar todo), archivar en el Taller, «Por revisar» sin atascos
(propuestas desfasadas) y las rutas del editor de archivos (renombrar y borrar archivos y carpetas)."""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import unittest
from pathlib import Path
from unittest import mock

import _rutas  # noqa: F401
import agente
import catalogo
import cli
import grupos
import mis_sistemas as ms
import proyectos
import quitar_proyecto as qp
import remoto
import repo
from test_panel_api import ConServidor
from test_proyectos import Entorno

WEB = Path(__file__).resolve().parents[1] / "web"
SISTEMAS = Path("uxyngraphar") / "sistemas-de-gobernanza"


class ConProyecto(Entorno):
    def proyecto(self, nombre: str = "app") -> Path:
        r = self.repo_git(nombre)
        (r / "src").mkdir()
        (r / "src" / "main.py").write_text("print('mío')\n", encoding="utf-8")
        (r / "AGENTS.md").write_text("# Mis reglas\n\nNo toques esto.\n", encoding="utf-8")
        repo.instalar(r, ["pruebas-demo"])
        proyectos.agregar([str(r)])
        return r


def modificar(ruta: Path, texto: str) -> None:
    ruta.chmod(0o644)   # los sistemas instalados son de solo lectura
    ruta.write_text(texto, encoding="utf-8")


class TestPlanYQuitar(ConProyecto):
    def test_plan_lista_lo_que_se_borra_respalda_y_conserva(self):
        r = self.proyecto()
        modificar(r / SISTEMAS / "pruebas-demo" / "SISTEMA.md", "# cambiado por mí\n")
        (r / SISTEMAS / "notas-mias.md").write_text("mías\n", encoding="utf-8")
        p = qp.plan(str(r))
        self.assertTrue(p["existe"] and p["registrado"] and p["con_uxyngraphar"])
        self.assertEqual([s["id"] for s in p["sistemas"]], ["pruebas-demo"])
        self.assertIn("SISTEMA.md", p["sistemas"][0]["modificados"])
        self.assertIn(f"{SISTEMAS.as_posix()}/pruebas-demo/", p["borrar"])
        self.assertIn(f"{SISTEMAS.as_posix()}/pruebas-demo/SISTEMA.md", p["respaldar"])
        self.assertEqual(p["ajenos"], [f"{SISTEMAS.as_posix()}/notas-mias.md"])
        self.assertIn("AGENTS.md (solo el bloque de uxyngraphar)", p["editar"])
        self.assertTrue(any("tu código" in c for c in p["conservar"]))

    def test_quitar_todo_respalda_conserva_lo_ajeno_y_desvincula(self):
        r = self.proyecto()
        otro = self.proyecto("otro")
        tercero = self.proyecto("tercero")
        grupos.guardar("pareja", [str(r), str(otro)])
        grupos.guardar("trio", [str(r), str(otro), str(tercero)])
        modificar(r / SISTEMAS / "pruebas-demo" / "SISTEMA.md", "# cambiado por mí\n")
        (r / SISTEMAS / "notas-mias.md").write_text("mías\n", encoding="utf-8")
        res = qp.quitar(str(r), todo=True)
        self.assertFalse((r / SISTEMAS / "pruebas-demo").exists())
        self.assertEqual((r / SISTEMAS / "notas-mias.md").read_text(encoding="utf-8"), "mías\n", "lo ajeno se queda")
        self.assertEqual((r / "src" / "main.py").read_text(encoding="utf-8"), "print('mío')\n")
        agents = (r / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("No toques esto.", agents)
        self.assertNotIn("uxyngraphar:inicio", agents)
        respaldo = Path(res["respaldo"])
        self.assertEqual((respaldo / SISTEMAS / "pruebas-demo" / "SISTEMA.md").read_text(encoding="utf-8"), "# cambiado por mí\n")
        self.assertTrue(str(respaldo).startswith(str(self.t / "casa")))
        self.assertFalse(proyectos.registrado(str(r)))
        self.assertEqual(res["grupos_borrados"], ["pareja"])
        self.assertEqual(res["grupos_actualizados"], ["trio"])
        self.assertEqual(grupos.listar(), {"trio": [str(otro), str(tercero)]})
        self.assertEqual(res["conservados"], [f"{SISTEMAS.as_posix()}/notas-mias.md"])
        self.assertEqual(res["restos"], [])

    def test_solo_desvincular_no_toca_la_carpeta(self):
        r = self.proyecto()
        res = qp.quitar(str(r))
        self.assertFalse(res["todo"])
        self.assertTrue((r / SISTEMAS / "pruebas-demo").is_dir())
        self.assertFalse(proyectos.registrado(str(r)))

    def test_carpeta_que_ya_no_existe_solo_se_desvincula(self):
        r = self.proyecto()
        repo.borrar_arbol(r)
        p = qp.plan(str(r))
        self.assertFalse(p["existe"])
        self.assertEqual(p["borrar"], [])
        res = qp.quitar(str(r), todo=True)
        self.assertIn("la carpeta ya no existe: solo se quita de la lista", res["hechos"])
        self.assertEqual(proyectos.listar(), [])


class TestCliQuitar(ConProyecto):
    def correr(self, *argv: str) -> tuple[int, str]:
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(io.StringIO()):
            codigo = cli.main(list(argv))
        return codigo, salida.getvalue()

    def test_quitar_todo_pide_si_sin_terminal(self):
        r = self.proyecto()
        with mock.patch("sys.stdin", io.StringIO("")):
            codigo, _ = self.correr("proyectos", "quitar", str(r), "--todo")
        self.assertNotEqual(codigo, 0)
        self.assertTrue((r / SISTEMAS / "pruebas-demo").is_dir(), "sin --si no se toca nada")
        codigo, texto = self.correr("proyectos", "quitar", str(r), "--todo", "--si")
        self.assertEqual(codigo, 0, texto)
        self.assertIn("borrar  uxyngraphar/sistemas-de-gobernanza/pruebas-demo/", texto)
        self.assertFalse((r / SISTEMAS / "pruebas-demo").exists())
        self.assertFalse(proyectos.registrado(str(r)))

    def test_archivar_y_desarchivar(self):
        codigo, texto = self.correr("archivar", "pruebas-demo")
        self.assertEqual(codigo, 0)
        self.assertIn("archivado", texto)
        self.assertEqual(ms.archivados(), ["pruebas-demo"])
        self.assertIn("archivado", "\n".join(ms.arbol()))
        self.correr("desarchivar", "pruebas-demo")
        self.assertEqual(ms.archivados(), [])


class TestArchivar(Entorno):
    def test_archivar_no_borra_y_se_ve_en_mis_sistemas(self):
        self.assertEqual(ms.archivar(["pruebas-demo", "solo-en-la-web"]), ["pruebas-demo", "solo-en-la-web"])
        v = ms.vista()
        self.assertTrue(next(s for s in v["sistemas"] if s["id"] == "pruebas-demo")["archivado"])
        self.assertFalse(next(s for s in v["sistemas"] if s["id"] == "pruebas-otras")["archivado"])
        self.assertTrue((self.cat / "pruebas-demo" / "sistema.json").is_file())
        self.assertEqual(ms.archivar(["pruebas-demo"], False), ["solo-en-la-web"])
        with self.assertRaises(ValueError):
            ms.archivar(["../fuera"])
        with self.assertRaises(ValueError):
            ms.archivar([])
        datos = json.loads((self.t / "casa" / "archivados.json").read_text(encoding="utf-8"))
        self.assertEqual(datos, {"formato": 1, "ids": ["solo-en-la-web"]})


class TestArchivosDelSistema(Entorno):
    def test_renombrar_mover_y_borrar_archivos_y_carpetas(self):
        catalogo.guardar_archivo("pruebas-demo", "ejemplos/uno.md", "# uno\n")
        catalogo.guardar_archivo("pruebas-demo", "ejemplos/sub/dos.md", "# dos\n")
        self.assertEqual(catalogo.renombrar_archivo("pruebas-demo", "ejemplos/uno.md", "ejemplos/primero.md"), ["ejemplos/primero.md"])
        self.assertEqual(sorted(catalogo.renombrar_archivo("pruebas-demo", "ejemplos", "casos")), ["casos/primero.md", "casos/sub/dos.md"])
        self.assertFalse((self.cat / "pruebas-demo" / "ejemplos").exists(), "la carpeta vacía se recoge")
        with self.assertRaises(FileExistsError):
            catalogo.renombrar_archivo("pruebas-demo", "casos/primero.md", "casos/sub/dos.md")
        with self.assertRaises(ValueError):
            catalogo.renombrar_archivo("pruebas-demo", "SISTEMA.md", "otro.md")
        with self.assertRaises(ValueError):
            catalogo.renombrar_archivo("pruebas-demo", "casos/primero.md", "../fuera.md")
        with self.assertRaises(ValueError):
            catalogo.renombrar_archivo("pruebas-demo", "casos/primero.md", "con espacio.md")
        self.assertEqual(sorted(catalogo.borrar_carpeta_de_sistema("pruebas-demo", "casos")), ["casos/primero.md", "casos/sub/dos.md"])
        self.assertFalse((self.cat / "pruebas-demo" / "casos").exists())
        with self.assertRaises(FileNotFoundError):
            catalogo.borrar_carpeta_de_sistema("pruebas-demo", "casos")


class TestPropuestasSinAtascos(unittest.TestCase):
    def _con(self, respuestas):
        llamadas = []

        def falso(ruta, cuerpo=None, metodo="POST", con_sesion=False, segundos=0):
            llamadas.append((ruta, dict(cuerpo) if isinstance(cuerpo, dict) else cuerpo, metodo))
            return respuestas.pop(0)

        return mock.patch.object(remoto, "_pedir_json", side_effect=falso), llamadas

    def test_una_propuesta_desfasada_devuelve_las_rutas_en_vez_de_un_error(self):
        conflicto = {"message": "Estos archivos cambiaron después de la propuesta; si la aceptas, se pierden esos cambios.",
                     "details": {"rutas": ["SISTEMA.md"]}}
        parche, llamadas = self._con([(409, conflicto), (200, {"id": 9, "estado": "ACCEPTED"})])
        with parche:
            r = agente.decidir("gobernanza", 9, ["SISTEMA.md", "LIMITES.md"], [])
            self.assertEqual(r["rutas"], ["SISTEMA.md"])
            self.assertTrue(r["desfasada"])
            self.assertIn("cambiaron", r["mensaje"])
            agente.decidir("gobernanza", 9, ["SISTEMA.md"], [], forzar=True)
        self.assertNotIn("forzar", llamadas[0][1])
        self.assertTrue(llamadas[1][1]["forzar"])

    def test_cada_archivo_pendiente_dice_si_ya_esta_aplicado_o_cambio_despues(self):
        lista = [{"id": 11, "estado": "PENDING", "archivos": [
            {"ruta": "SISTEMA.md", "estado": "pendiente", "antes": "viejo", "despues": "actual"},
            {"ruta": "LIMITES.md", "estado": "pendiente", "antes": "otro", "despues": "nuevo"},
            {"ruta": "README.md", "estado": "pendiente", "antes": "igual", "despues": "mejor"},
            {"ruta": "MEMORIAS.md", "estado": "aceptado", "antes": "", "despues": ""}]}]
        web = {"revision": 4, "archivos": [{"ruta": "SISTEMA.md", "contenido": "actual"}, {"ruta": "LIMITES.md", "contenido": "cambió"},
                                           {"ruta": "README.md", "contenido": "igual"}]}
        parche, llamadas = self._con([(200, lista), (200, web)])
        with parche:
            r = agente.propuestas("gobernanza", con_situacion=True)
        situaciones = {a["ruta"]: a.get("situacion") for a in r[0]["archivos"]}
        self.assertEqual(situaciones, {"SISTEMA.md": "ya_aplicado", "LIMITES.md": "desfasado", "README.md": "aplicable", "MEMORIAS.md": None})
        self.assertEqual([m for _, _, m in llamadas], ["GET", "GET"], "solo lectura: no se acepta ni rechaza nada")

    def test_sin_el_borrador_web_las_propuestas_se_ven_igual(self):
        lista = [{"id": 1, "archivos": [{"ruta": "A.md", "estado": "pendiente", "antes": "a", "despues": "b"}]}]
        parche, _ = self._con([(200, lista), (500, {"message": "caído"})])
        with parche:
            r = agente.propuestas("x", con_situacion=True)
        self.assertNotIn("situacion", r[0]["archivos"][0])

    def test_el_panel_no_baja_el_borrador_si_la_propuesta_quedo_desfasada(self):
        import creador
        import rutas_panel
        with mock.patch.object(agente, "decidir", return_value={"desfasada": True, "rutas": ["SISTEMA.md"]}) as decidir, \
                mock.patch.object(creador, "bajar") as bajar:
            r = rutas_panel._agente_decidir({"slug": "gobernanza", "propuesta": 9, "aceptar": ["SISTEMA.md"], "forzar": True})
        self.assertTrue(r["desfasada"])
        bajar.assert_not_called()
        self.assertTrue(decidir.call_args.kwargs["forzar"])

    def test_uxyn_mejora_un_borrador_que_solo_esta_en_la_web(self):
        import creador
        import rutas_panel
        with mock.patch.object(agente, "turno", return_value={"conversacion": 1, "respuesta": "ok"}) as turno, \
                mock.patch.object(creador, "subir") as subir:
            rutas_panel._agente_turno({"mensaje": "mejora", "id": "solo-en-la-web-xyz"})
        subir.assert_not_called()
        turno.assert_called_once()


class TestApi(ConServidor):
    def test_rutas_de_quitar_archivar_y_archivos(self):
        r = self.repo_git("app")
        repo.instalar(r, ["pruebas-demo"])
        proyectos.agregar([str(r)])
        plan = self.pedir(f"/api/proyectos/plan-quitar?ruta={r}")
        self.assertEqual([s["id"] for s in plan["sistemas"]], ["pruebas-demo"])
        codigo, _ = self.error("/api/proyectos/quitar", {"ruta": str(r), "todo": True})
        self.assertEqual((codigo, self.ultimo_error.get("codigo")), (400, "falta_confirmacion"))
        self.assertTrue((r / SISTEMAS / "pruebas-demo").is_dir())
        res = self.pedir("/api/proyectos/quitar", {"ruta": str(r), "todo": True, "confirmar": True})
        self.assertTrue(res["todo"])
        self.assertFalse((r / SISTEMAS / "pruebas-demo").exists())
        self.assertEqual(self.pedir("/api/mis-sistemas/archivar", {"ids": ["pruebas-otras"]})["archivados"], ["pruebas-otras"])
        self.assertEqual(self.pedir("/api/mis-sistemas/archivados"), ["pruebas-otras"])
        self.assertEqual(self.pedir("/api/mis-sistemas/archivar", {"ids": ["pruebas-otras"], "archivar": False})["archivados"], [])
        self.pedir("/api/catalogo/archivo", {"id": "pruebas-demo", "rel": "notas/a.md", "contenido": "# a\n"})
        self.assertEqual(self.pedir("/api/catalogo/archivo/renombrar", {"id": "pruebas-demo", "de": "notas", "a": "apuntes"})["rutas"], ["apuntes/a.md"])
        self.assertEqual(self.pedir("/api/catalogo/archivo/borrar", {"id": "pruebas-demo", "rel": "apuntes", "carpeta": True})["borrados"], ["apuntes/a.md"])
        codigo, _ = self.error("/api/catalogo/archivo/borrar", {"id": "pruebas-demo", "rel": "SISTEMA.md"})
        self.assertEqual(codigo, 400)


class TestWeb(unittest.TestCase):
    def node(self, programa: str) -> str:
        if not shutil.which("node"):
            self.skipTest("sin node")
        r = subprocess.run(["node", "--input-type=module", "-e", programa], capture_output=True, text=True, encoding="utf-8",
                           cwd=WEB / "js", check=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_tokenizador_y_arbol_del_editor(self):
        # ui.js usa document al cargar: un DOM mínimo basta para importar los módulos puros.
        programa = """
globalThis.document = { getElementById: () => null, createElement: () => ({}), addEventListener() {} };
globalThis.window = { addEventListener() {} };
const ec = await import('./editor-codigo.js');
const t = (txt, l) => ec.tokenizar(txt, l).map((linea) => linea.filter(([c]) => c).map(([c, x]) => c + ':' + x));
console.log(JSON.stringify({
  json: t('{"a": "b", "n": 3, "v": true}', 'json'),
  py: t('def f(x):  # nota\\n    return "hola"', 'py'),
  md: t('# Título\\n- uno {{hueco}}\\n```\\ncódigo\\n```', 'md'),
  sh: t('echo "$HOME" # fin', 'sh'),
  yaml: t('clave: valor # c', 'yaml'),
  lenguajes: ['a.md', 'b.json', 'c.py', 'd.yml', 'e.sh', 'f.txt'].map(ec.lenguajeDe),
}));
"""
        datos = json.loads(self.node(programa))
        self.assertEqual(datos["json"][0], ['t-propiedad:"a"', 't-cadena:"b"', 't-propiedad:"n"', "t-numero:3", 't-propiedad:"v"', "t-clave:true"])
        self.assertEqual(datos["py"][0], ["t-clave:def", "t-comentario:# nota"])
        self.assertEqual(datos["py"][1], ["t-clave:return", 't-cadena:"hola"'])
        self.assertEqual(datos["md"][0], ["t-titulo:# Título"])
        self.assertEqual(datos["md"][1], ["t-lista:- ", "t-marcador:{{hueco}}"])
        self.assertEqual(datos["md"][3], ["t-codigo:código"])
        self.assertEqual(datos["sh"][0], ["t-clave:echo", 't-cadena:"$HOME"', "t-comentario:# fin"])
        self.assertEqual(datos["yaml"][0], ["t-propiedad:clave", "t-comentario:# c"])
        self.assertEqual(datos["lenguajes"], ["md", "json", "py", "yaml", "sh", "texto"])

    def test_el_editor_no_usa_cdn_ni_html_inyectado(self):
        for nombre in ("editor-codigo.js", "vistas/editor-archivos.js", "vistas/quitar-proyecto.js"):
            texto = (WEB / "js" / nombre).read_text(encoding="utf-8")
            self.assertNotIn("http://", texto.replace("https?:\\/\\/", ""))
            self.assertNotIn("cdn", texto.lower())
            self.assertNotIn("innerHTML", texto)

    def test_por_revisar_no_bloquea(self):
        js = (WEB / "js" / "vistas" / "creador.js").read_text(encoding="utf-8")
        self.assertNotIn("antes de seguir", js)
        for texto in ("Aceptar todo", "Descartar todo", "Aceptar igualmente (sobrescribe)", "Abrir en el editor", "forzar: true"):
            self.assertIn(texto, js)
        taller = (WEB / "js" / "vistas" / "creador-sistemas.js").read_text(encoding="utf-8")
        self.assertIn("Traer de la web para editar", taller)
        self.assertIn("Mostrar archivados", taller)


if __name__ == "__main__":
    unittest.main()
