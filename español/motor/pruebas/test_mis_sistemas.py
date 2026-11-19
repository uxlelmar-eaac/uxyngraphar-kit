"""«Mis sistemas» (1.5.20): carpetas y orden del catálogo local, papelera, duplicar y cambiar el nombre; CLI y API."""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import _rutas  # noqa: F401
from _sistemas import completar
import catalogo
import cli
import desinstalacion
import mis_sistemas as ms
import nomenclatura
import proyectos
import repo
from test_panel_api import ConServidor
from test_proyectos import Entorno

WEB = Path(__file__).resolve().parents[1] / "web"


def _errores(pid: str) -> list[str]:
    return next(m["errores"] for m in catalogo.listar() if m["id"] == pid)


class TestCarpetas(Entorno):
    def test_carpetas_anidadas_mover_ordenar_y_persistir(self):
        org = ms.crear_carpeta("Pruebas")
        a = org["carpetas"][0]["id"]
        org = ms.crear_carpeta("Dentro", a)
        b = next(c["id"] for c in org["carpetas"] if c["nombre"] == "Dentro")
        ms.mover(["pruebas-demo"], b)
        ms.mover(["pruebas-otras"], b, antes="pruebas-demo")
        v = ms.vista()
        self.assertEqual([s["id"] for s in v["sistemas"] if s["carpeta"] == b], ["pruebas-otras", "pruebas-demo"])
        # persistido en .organizacion.json dentro del catálogo y sin mover carpetas en el disco
        datos = json.loads((self.cat / ".organizacion.json").read_text(encoding="utf-8"))
        self.assertEqual(datos["sistemas"]["pruebas-demo"]["carpeta"], b)
        self.assertTrue((self.cat / "pruebas-demo" / "sistema.json").is_file())
        self.assertEqual(sorted(m["id"] for m in catalogo.listar()), ["pruebas-demo", "pruebas-otras"])
        self.assertEqual(ms.arbol()[:2], ["Pruebas/", "  Dentro/"])
        # de vuelta a la raíz
        ms.mover(["pruebas-demo"], None)
        self.assertIsNone(next(s for s in ms.vista()["sistemas"] if s["id"] == "pruebas-demo")["carpeta"])

    def test_nombres_ciclos_y_borrar(self):
        a = ms.crear_carpeta("Uno")["carpetas"][0]["id"]
        with self.assertRaises(FileExistsError):
            ms.crear_carpeta("uno")
        with self.assertRaises(ValueError):
            ms.crear_carpeta("   ")
        with self.assertRaises(ValueError):
            ms.crear_carpeta("x" * 41)
        b = ms.crear_carpeta("Dos", a)["carpetas"][1]["id"]
        with self.assertRaises(ValueError):
            ms.mover_carpeta(a, b)   # dentro de su propia hija
        ms.renombrar_carpeta(b, "Tres")
        ms.mover(["pruebas-demo"], b)
        with self.assertRaisesRegex(ValueError, "confírmalo"):
            ms.borrar_carpeta(a)
        org = ms.borrar_carpeta(a, confirmar=True)
        self.assertEqual(org["carpetas"], [])
        self.assertEqual(org["sistemas"], {})
        self.assertTrue((self.cat / "pruebas-demo").is_dir(), "borrar una carpeta no borra sistemas")

    def test_lo_que_falta_va_a_la_raiz_y_lo_viejo_se_olvida(self):
        (self.cat / ".organizacion.json").write_text(json.dumps({
            "carpetas": [{"id": "c-1", "nombre": "A", "padre": "c-2"}, {"id": "c-2", "nombre": "B", "padre": "c-1"},
                         {"id": "c-1", "nombre": "repetida"}, {"nombre": "sin id"}],
            "sistemas": {"ya-no-existe": {"carpeta": "c-1"}, "pruebas-demo": {"carpeta": "c-9"}},
            "orden": ["ya-no-existe", "pruebas-otras", 3]}), encoding="utf-8")
        org = ms.leer()
        self.assertEqual([c["id"] for c in org["carpetas"]], ["c-1", "c-2"])
        self.assertIn(None, [c["padre"] for c in org["carpetas"]], "el ciclo se rompe")
        self.assertEqual(org["sistemas"], {})
        self.assertEqual(org["orden"], ["pruebas-otras"])
        self.assertEqual(json.loads((self.cat / ".organizacion.json").read_text(encoding="utf-8")), org, "se guarda limpio")
        (self.cat / ".organizacion.json").write_text("{roto", encoding="utf-8")
        self.assertEqual(ms.vista()["carpetas"], [])

    def test_el_archivo_no_es_un_sistema(self):
        ms.crear_carpeta("A")
        self.assertNotIn(".organizacion.json", catalogo._sistemas(None))  # noqa: SLF001
        self.assertEqual(catalogo.versiones(), {"pruebas-demo": "0.1.0", "pruebas-otras": "0.1.0"})


class TestPapelera(Entorno):
    def test_eliminar_restaurar_y_vaciar(self):
        a = ms.crear_carpeta("Pruebas")["carpetas"][0]["id"]
        ms.mover(["pruebas-demo"], a)
        (hecho,) = ms.eliminar(["pruebas-demo"])
        self.assertFalse((self.cat / "pruebas-demo").exists())
        entrada = ms.carpeta_papelera() / hecho["entrada"]
        self.assertTrue((entrada / "pruebas-demo" / "sistema.json").is_file())
        (e,) = ms.papelera()
        self.assertEqual((e["id"], e["nombre_carpeta"], e["choca"]), ("pruebas-demo", "Pruebas", False))
        # 1.5.26: lo que está en la papelera sigue entre «mis sistemas» (en su carpeta, con estado «papelera»)
        self.assertEqual(ms.leer()["sistemas"]["pruebas-demo"]["carpeta"], a)
        (enpap,) = [s for s in ms.vista(con_web=False)["sistemas"] if s["id"] == "pruebas-demo"]
        self.assertEqual((enpap["estado"], enpap["entrada"]), ("papelera", hecho["entrada"]))
        r = ms.restaurar(hecho["entrada"])
        self.assertEqual(r["carpeta"], "Pruebas")
        self.assertEqual(ms.leer()["sistemas"]["pruebas-demo"]["carpeta"], a, "vuelve a su carpeta")
        self.assertEqual(ms.papelera(), [])
        self.assertEqual(_errores("pruebas-demo"), [])
        # vaciar una o todas
        h1, h2 = ms.eliminar(["pruebas-demo", "pruebas-otras"])
        self.assertEqual(ms.vaciar(h1["entrada"]), 1)
        self.assertEqual([x["id"] for x in ms.papelera()], ["pruebas-otras"])
        self.assertEqual(ms.vaciar(), 1)
        self.assertEqual(ms.papelera(), [])

    def test_restaurar_vuelve_a_su_sitio_en_la_carpeta(self):
        a = ms.crear_carpeta("Pruebas")["carpetas"][0]["id"]
        ms.duplicar("pruebas-demo", "copia-de-demo", "Copia de demo")
        ms.mover(["pruebas-otras", "pruebas-demo", "copia-de-demo"], a)
        (hecho,) = ms.eliminar(["pruebas-demo"])
        ms.restaurar(hecho["entrada"])
        self.assertEqual([s["id"] for s in ms.vista()["sistemas"]], ["pruebas-otras", "pruebas-demo", "copia-de-demo"])
        ms.borrar_carpeta(a, confirmar=True)
        (hecho,) = ms.eliminar(["pruebas-otras"])
        self.assertIsNone(ms.restaurar(hecho["entrada"])["carpeta"], "su carpeta ya no existe: vuelve a la raíz")

    def test_restaurar_con_el_id_ocupado_no_pisa(self):
        (hecho,) = ms.eliminar(["pruebas-demo"])
        completar(catalogo.crear("pruebas-demo", "Pruebas demo", "otro", self.cat))
        self.assertTrue(ms.papelera()[0]["choca"])
        with self.assertRaises(FileExistsError):
            ms.restaurar(hecho["entrada"])
        self.assertTrue((ms.carpeta_papelera() / hecho["entrada"] / "pruebas-demo").is_dir(), "no se pierde")

    def test_entradas_invalidas_y_todo_o_nada(self):
        for malo in ("../catalogo", "", "20260101-000000-x/../..", "nada"):
            with self.assertRaises((ValueError, FileNotFoundError)):
                ms.restaurar(malo)
        with self.assertRaises(FileNotFoundError):
            ms.eliminar(["pruebas-demo", "no-existe"])
        self.assertTrue((self.cat / "pruebas-demo").is_dir(), "si uno no existe no se mueve ninguno")
        self.assertEqual(ms.resolver_entrada(ms.eliminar(["pruebas-demo"])[0]["entrada"]), ms.papelera()[0]["entrada"])
        self.assertEqual(ms.resolver_entrada("pruebas-demo"), ms.papelera()[0]["entrada"])

    def test_avisa_donde_esta_instalado_y_no_toca_el_proyecto(self):
        r = self.repo_git("app")
        repo.instalar(r, ["pruebas-demo"])
        proyectos.agregar([str(r)])
        self.assertEqual(ms.avisos_eliminar("pruebas-demo")["proyectos"], ["app"])
        ms.eliminar(["pruebas-demo"])
        self.assertTrue((r / "uxyngraphar" / "sistemas-de-gobernanza" / "pruebas-demo").is_dir())

    def test_desinstalar_cuenta_lo_que_hay_en_la_papelera(self):
        ms.eliminar(["pruebas-demo"])
        rutas = desinstalacion.sistemas_de_autor(str(ms.casa.carpeta()))
        self.assertTrue(any(r.endswith("pruebas-demo") and "papelera" in r for r in rutas))


class TestDuplicarYRenombrar(Entorno):
    def test_duplicar_cambia_id_titulo_prefijos_y_queda_detras(self):
        a = ms.crear_carpeta("Pruebas")["carpetas"][0]["id"]
        ms.mover(["pruebas-demo", "pruebas-otras"], a)
        r = ms.duplicar("pruebas-demo", "copia-de-demo", "Copia de demo")
        m = catalogo.base.leer_manifiesto(self.cat / "copia-de-demo")
        original = catalogo.base.leer_manifiesto(self.cat / "pruebas-demo")
        self.assertEqual((m["id"], m["titulo"], m["version"]), ("copia-de-demo", "Copia de demo", original["version"]))
        self.assertEqual(m["activacion"][:2], ["copia-de-demo", "copia de demo"])
        prefijos = {d["prefijo"] for d in original["fichas"].values()}
        self.assertFalse(prefijos & {d["prefijo"] for d in m["fichas"].values()})
        self.assertEqual(r["prefijos"], {t: d["prefijo"] for t, d in m["fichas"].items()})
        readme = (self.cat / "copia-de-demo" / "README.md").read_text(encoding="utf-8")
        self.assertIn("# Copia de demo", readme)
        self.assertNotIn("pruebas-demo", readme)
        self.assertEqual(_errores("copia-de-demo"), [])
        self.assertEqual(_errores("pruebas-demo"), [], "el original sigue validando")
        v = ms.vista()
        self.assertEqual([s["id"] for s in v["sistemas"] if s["carpeta"] == a], ["pruebas-demo", "copia-de-demo", "pruebas-otras"])
        self.assertEqual(ms._errores_nombres(None), {p: [] for p in ("copia-de-demo", "pruebas-demo", "pruebas-otras")})  # noqa: SLF001

    def test_duplicar_rechaza_sin_crear_nada(self):
        casos = [("pruebas-otras", "Pruebas otras"), ("pruebas", "Pruebas"), ("pruebas-demo-mas", "Pruebas demo mas"),
                 ("revisar-algo", "Revisar algo"), ("copia-buena", "Otro titulo"), ("Mal_Id", "Mal id")]
        for pid, titulo in casos:
            with self.assertRaises(ValueError, msg=pid):
                ms.duplicar("pruebas-demo", pid, titulo)
        self.assertEqual(sorted(p.name for p in self.cat.iterdir() if p.is_dir()), ["pruebas-demo", "pruebas-otras"])

    def test_frases_propias_que_chocarian_no_se_copian(self):
        c = self.cat / "pruebas-demo"
        m = catalogo.base.leer_manifiesto(c)
        m["activacion"].append("revisar pagos")
        catalogo._escribir_manifiesto(c, m)  # noqa: SLF001
        r = ms.duplicar("pruebas-demo", "copia-de-demo", "Copia de demo")
        self.assertEqual(r["frases_quitadas"], ["revisar pagos"])
        self.assertNotIn("revisar pagos", catalogo.base.leer_manifiesto(self.cat / "copia-de-demo")["activacion"])

    def test_renombrar_titulo_solo_tildes(self):
        with self.assertRaisesRegex(ValueError, "cambia también el id"):
            ms.renombrar("pruebas-demo", "Otra cosa")
        r = ms.renombrar("pruebas-demo", "Prúebas demo")
        self.assertIsNone(r["anterior"])
        self.assertEqual(catalogo.base.leer_manifiesto(self.cat / "pruebas-demo")["titulo"], "Prúebas demo")
        self.assertIn("# Prúebas demo", (self.cat / "pruebas-demo" / "README.md").read_text(encoding="utf-8"))

    def test_renombrar_id_conserva_posicion_prefijos_y_frases_y_es_recuperable(self):
        a = ms.crear_carpeta("Pruebas")["carpetas"][0]["id"]
        ms.mover(["pruebas-demo", "pruebas-otras"], a)
        antes = catalogo.base.leer_manifiesto(self.cat / "pruebas-demo")
        r = ms.renombrar("pruebas-demo", "Ensayos de demo", "ensayos-de-demo")
        self.assertFalse((self.cat / "pruebas-demo").exists())
        m = catalogo.base.leer_manifiesto(self.cat / "ensayos-de-demo")
        self.assertEqual({t: d["prefijo"] for t, d in m["fichas"].items()}, {t: d["prefijo"] for t, d in antes["fichas"].items()})
        self.assertEqual(_errores("ensayos-de-demo"), [])
        self.assertEqual([s["id"] for s in ms.vista()["sistemas"] if s["carpeta"] == a and s["estado"] == "local"], ["ensayos-de-demo", "pruebas-otras"])
        self.assertIn(("pruebas-demo", "papelera"), [(s["id"], s["estado"]) for s in ms.vista()["sistemas"]], "el id anterior queda en la papelera")
        self.assertEqual(ms.papelera()[0]["id"], "pruebas-demo")
        self.assertEqual(r["anterior"]["id"], "pruebas-demo")

    def test_renombrar_que_falla_deja_el_original(self):
        with self.assertRaises(ValueError):
            ms.renombrar("pruebas-demo", "Pruebas otras", "pruebas-otras")
        self.assertTrue((self.cat / "pruebas-demo" / "sistema.json").is_file())
        self.assertEqual(ms.papelera(), [])


class TestCli(Entorno):
    def correr(self, *argv: str) -> tuple[int, str, str]:
        salida, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(err):
            codigo = cli.main(list(argv))
        return codigo, salida.getvalue(), err.getvalue()

    def test_ciclo_completo_en_espanol(self):
        codigo, texto, _ = self.correr("mis-sistemas")
        self.assertEqual(codigo, 0)
        self.assertIn("- pruebas-demo", texto)
        codigo, texto, _ = self.correr("duplicar", "pruebas-demo", "copia-de-demo", "--titulo", "Copia de demo")
        self.assertEqual(codigo, 0, texto)
        self.assertIn("copia de pruebas-demo", texto)
        codigo, texto, _ = self.correr("eliminar", "copia-de-demo")
        self.assertEqual(codigo, 0)
        self.assertIn("en la papelera", texto)
        self.assertIn("no se tocan", texto)
        codigo, texto, _ = self.correr("papelera")
        self.assertIn("copia-de-demo", texto)
        codigo, texto, _ = self.correr("restaurar", "copia-de-demo")
        self.assertEqual(codigo, 0)
        self.assertIn("de vuelta en el catálogo", texto)
        codigo, texto, _ = self.correr("renombrar", "copia-de-demo", "copia-de-ensayo", "--titulo", "Copia de ensayo")
        self.assertEqual(codigo, 0, texto)
        self.assertIn("el anterior está en la papelera", texto)
        codigo, _, err = self.correr("papelera", "vaciar")
        self.assertEqual(codigo, 1)
        self.assertIn("--si", err)
        codigo, texto, _ = self.correr("papelera", "vaciar", "--si")
        self.assertEqual(codigo, 0)
        self.assertIn("Borrado para siempre: 1 entrada", texto)
        codigo, _, err = self.correr("eliminar", "no-existe")
        self.assertEqual(codigo, 1)
        self.assertIn("el catálogo no tiene el sistema «no-existe»", err)
        codigo, _, err = self.correr("renombrar", "pruebas-demo", "--titulo", "Otra cosa")
        self.assertEqual(codigo, 1)
        self.assertIn("cambia también el id", err)

    def test_eliminar_instalado_sin_terminal_pide_si(self):
        r = self.repo_git("app")
        repo.instalar(r, ["pruebas-demo"])
        proyectos.agregar([str(r)])
        with unittest.mock.patch("sys.stdin", io.StringIO("")):
            codigo, texto, err = self.correr("eliminar", "pruebas-demo")
        self.assertEqual(codigo, 1)
        self.assertIn("está instalado en app", texto)
        self.assertIn("--si", err)
        self.assertTrue((self.cat / "pruebas-demo").is_dir())
        codigo, texto, _ = self.correr("eliminar", "pruebas-demo", "--si")
        self.assertEqual(codigo, 0)


class TestApi(ConServidor):
    def test_rutas_de_mis_sistemas(self):
        v = self.pedir("/api/mis-sistemas")
        self.assertEqual([s["id"] for s in v["sistemas"]], ["pruebas-demo", "pruebas-otras"])
        org = self.pedir("/api/mis-sistemas/carpeta", {"accion": "crear", "nombre": "Pruebas"})
        cid = org["carpetas"][0]["id"]
        self.pedir("/api/mis-sistemas/mover", {"ids": ["pruebas-demo"], "carpeta": cid})
        self.assertEqual(self.error("/api/mis-sistemas/carpeta", {"accion": "borrar", "id": cid})[0], 400)
        self.assertEqual(self.ultimo_error.get("codigo"), "falta_confirmacion")
        self.error("/api/mis-sistemas/carpeta", {"accion": "crear", "nombre": "pruebas"})
        self.assertEqual(self.ultimo_error.get("codigo"), "ya_existe")
        r = self.pedir("/api/mis-sistemas/duplicar", {"id": "pruebas-demo", "nuevo_id": "copia-de-demo", "titulo": "Copia de demo"})
        self.assertEqual(r["id"], "copia-de-demo")
        self.assertEqual(self.pedir("/api/mis-sistemas/avisos?id=pruebas-demo")["proyectos"], [])
        (h,) = self.pedir("/api/mis-sistemas/eliminar", {"ids": ["copia-de-demo"]})
        self.assertEqual(self.pedir("/api/mis-sistemas")["papelera"], 1)
        self.assertEqual(self.pedir("/api/mis-sistemas/papelera")[0]["entrada"], h["entrada"])
        self.pedir("/api/mis-sistemas/restaurar", {"entrada": h["entrada"]})
        self.assertEqual(self.error("/api/mis-sistemas/restaurar", {"entrada": "../../x"})[0], 400)
        self.assertEqual(self.error("/api/mis-sistemas/vaciar", {})[0], 400)
        self.assertEqual(self.pedir("/api/mis-sistemas/vaciar", {"confirmar": True})["borradas"], 0)
        r = self.pedir("/api/mis-sistemas/renombrar", {"id": "copia-de-demo", "titulo": "Copia de ensayo", "nuevo_id": "copia-de-ensayo"})
        self.assertEqual(r["anterior"]["id"], "copia-de-demo")
        self.pedir("/api/mis-sistemas/carpeta", {"accion": "borrar", "id": cid, "confirmar": True})
        self.assertTrue((self.cat / "pruebas-demo").is_dir())
        historial = self.pedir("/api/historial")
        self.assertTrue(any("papelera" in json.dumps(x, ensure_ascii=False) for x in historial))


class TestWeb(unittest.TestCase):
    def test_seccion_en_la_navegacion_y_en_las_vistas(self):
        self.assertIn('href="#/mis-sistemas" data-seccion="mis-sistemas"', (WEB / "index.html").read_text(encoding="utf-8"))
        app = (WEB / "js" / "app.js").read_text(encoding="utf-8")
        self.assertIn('import * as misSistemas from "./vistas/mis-sistemas.js"', app)
        self.assertIn('"mis-sistemas": misSistemas', app)
        js = (WEB / "js" / "vistas" / "mis-sistemas.js").read_text(encoding="utf-8")
        for ruta in ("/api/mis-sistemas/mover", "/api/mis-sistemas/eliminar", "/api/mis-sistemas/restaurar", "/api/mis-sistemas/duplicar",
                     "/api/mis-sistemas/renombrar", "/api/mis-sistemas/vaciar", "Deshacer", "Mover a…"):
            self.assertIn(ruta, js)

    def test_js_valido_y_slug_cumple_la_nomenclatura(self):
        if not shutil.which("node"):
            self.skipTest("sin node")
        js = (WEB / "js" / "vistas" / "mis-sistemas.js").read_text(encoding="utf-8")
        for archivo in ("vistas/mis-sistemas.js", "ui.js", "app.js"):
            subprocess.run(["node", "--check", str(WEB / "js" / archivo)], check=True, capture_output=True)
        inicio = js.index("const sinTildes = ")
        fin = js.index("const porTitulo = ")
        programa = js[inicio:fin].replace("export const", "const") + (
            'console.log(JSON.stringify(["Revisión de diseño", "Guía  de estilo 2", "Ñandú y pingüino"].map(slugDe)));')
        with tempfile.TemporaryDirectory() as t:
            guion = Path(t) / "slug.js"
            guion.write_text(programa, encoding="utf-8")
            r = subprocess.run(["node", str(guion)], capture_output=True, text=True, encoding="utf-8", check=True)
        ids = json.loads(r.stdout)
        self.assertEqual(ids, ["revision-de-diseno", "guia-de-estilo", "nandu-y-pinguino"])
        self.assertTrue(all(not nomenclatura.problemas_id(i) for i in ids))


if __name__ == "__main__":
    unittest.main()
