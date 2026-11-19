"""1.5.26: esqueleto completo en todos los caminos de creación, importación que no descarta nada (zip, archivos,
carpeta), el editor y la sincronización ven TODOS los archivos (carpetas anidadas, cualquier extensión, binarios en
solo lectura) y Mis sistemas enseña los mismos sistemas que el Taller."""

from __future__ import annotations

import base64
import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

import _rutas  # noqa: F401
import artefacto
import catalogo
import creador
import generador
import importar
import mis_sistemas
from test_creador import ConServidor as ConWeb
from test_creador import Servidor
from test_panel_api import ConServidor as ConPanel

import uxyn_base as base

WEB = Path(__file__).resolve().parents[1] / "web"
PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
# Lo que todo sistema nuevo trae de serie (núcleo + prompts/ + config/ + piezas con contenido de arranque).
ESQUELETO = {"sistema.json", "README.md", "SISTEMA.md", "MEMORIAS.md", "LIMITES.md", "PERMISOS.md", "CHANGELOG.md",
             "HERRAMIENTAS.md", "prompts/README.md", "prompts/agente.md", "prompts/revision.md", "config/README.md",
             "config/ajustes.json", "proceso/preparar.md", "proceso/ejecutar.md", "proceso/cerrar.md",
             "skills/accion-principal/SKILL.md", "referencia/guia.md", "ejemplos/caso.md", "pruebas/test_sistema.py"}


def material() -> dict[str, bytes]:
    """Lo que alguien sube: carpeta raíz, docs/, prompts/, una carpeta desconocida anidada, un binario, un JSON de
    configuración que choca con el de la base, un manifiesto propio y basura de macOS."""
    return {
        "Mi Sistema/README.md": b"# Mi sistema\n\nMi texto.\n",
        "Mi Sistema/docs/manual.md": b"# Manual\n",
        "Mi Sistema/prompts/base.md": b"Eres un agente cuidadoso.\n",
        "Mi Sistema/kits/datos/anidado/tabla.yaml": b"clave: 1\n",
        "Mi Sistema/kits/script.sh": b"#!/bin/sh\necho hola\n",
        "Mi Sistema/recursos/logo.png": PNG,
        "Mi Sistema/ajustes.json": b'{"idioma": "en", "mio": true}',
        "Mi Sistema/notas de dise\xc3\xb1o.txt".encode("latin-1").decode("utf-8"): "ñ\n".encode(),
        "Mi Sistema/sistema.json": json.dumps({"version": "0.3.0", "activacion": ["pagos"], "ajustes": {"tono": "serio"},
                                               "permisos": {"rutas": {"protegidas": ["docs/"]}}}).encode(),
        "Mi Sistema/.DS_Store": b"\x00",
        "__MACOSX/Mi Sistema/._README.md": b"\x00",
    }


def como_zip(archivos: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for r, v in archivos.items():
            z.writestr(r, v)
    return buf.getvalue()


class ConCatalogo(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.t = Path(self._t.name)
        self.cat = self.t / "catalogo"
        self.cat.mkdir()

    def tearDown(self):
        self._t.cleanup()

    def archivos(self, pid: str) -> set[str]:
        return set(base.archivos_del_sistema(self.cat / pid))


class TestEsqueletoCompleto(ConCatalogo):
    def test_desde_cero(self):
        catalogo.crear("contratos-de-pago", "Contratos de pago", raiz=self.cat)
        self.assertLessEqual(ESQUELETO, self.archivos("contratos-de-pago"))
        m = base.leer_manifiesto(self.cat / "contratos-de-pago")
        self.assertEqual(set(m["extensiones"]), {"prompts", "config"})
        self.assertEqual(m["piezas"], list(catalogo.PIEZAS_AL_CREAR))
        errores = __import__("especificacion").validar_sistema(self.cat / "contratos-de-pago")
        self.assertTrue(errores and all("marcadores sin rellenar" in e for e in errores), errores)

    def test_el_contenido_de_arranque_no_esta_vacio(self):
        catalogo.crear("contratos-de-pago", "Contratos de pago", raiz=self.cat)
        for rel in ESQUELETO:
            self.assertGreater((self.cat / "contratos-de-pago" / rel).stat().st_size, 20, rel)

    def test_desde_especificacion_tambien_trae_prompts_y_config(self):
        r = generador.desde_spec(generador.plantilla_spec("contratos-de-pago"), aplicar=True, raiz=self.cat)
        self.assertEqual(r["errores"], [])
        self.assertLessEqual({"prompts/agente.md", "config/ajustes.json"}, self.archivos("contratos-de-pago"))

    def test_importar_zip(self):
        r = importar.importar(importar.desde_zip(como_zip(material())), pid="contratos-de-pago", raiz=self.cat)
        self.assertTrue(r["aplicado"])
        self.assertLessEqual(ESQUELETO, self.archivos("contratos-de-pago"))

    def test_importar_archivos_sueltos(self):
        lista = [{"ruta": "guia.md", "datos": base64.b64encode(b"# Guia\n").decode()},
                 {"ruta": "prompt-ventas.md", "contenido": "Vende con cuidado.\n"}]
        r = importar.importar(importar.desde_lista(lista), pid="contratos-de-pago", raiz=self.cat)
        hay = self.archivos("contratos-de-pago")
        self.assertLessEqual(ESQUELETO, hay)
        self.assertIn("referencia/guia.md", hay)
        self.assertIn("prompts/prompt-ventas.md", hay)
        self.assertEqual(r["total_importados"], 2)

    def test_importar_carpeta(self):
        origen = self.t / "mi-carpeta"
        for rel, datos in material().items():
            if rel.startswith("Mi Sistema/"):
                (origen / rel[len("Mi Sistema/"):]).parent.mkdir(parents=True, exist_ok=True)
                (origen / rel[len("Mi Sistema/"):]).write_bytes(datos)
        r = importar.importar(importar.desde_carpeta(origen), pid="contratos-de-pago", raiz=self.cat)
        self.assertTrue(r["aplicado"])
        self.assertLessEqual(ESQUELETO, self.archivos("contratos-de-pago"))


class TestImportarSinPerderNada(ConCatalogo):
    def setUp(self):
        super().setUp()
        self.r = importar.importar(importar.desde_zip(como_zip(material())), pid="contratos-de-pago", raiz=self.cat)
        self.c = self.cat / "contratos-de-pago"

    def test_ningun_archivo_del_usuario_se_pierde(self):
        destinos = {x["de"]: x["a"] for k in ("mapeados", "fusionados", "conservados") for x in self.r[k]}
        renombrados = {x["a"]: x["de"] for x in self.r["renombrados"]}
        for rel, datos in material().items():
            if importar.BASURA.search(rel):
                self.assertIn(rel, self.r["ignorados"])
                continue
            limpio = next((a for a, de in renombrados.items() if de == rel[len("Mi Sistema/"):]), rel[len("Mi Sistema/"):])
            self.assertIn(limpio, destinos, rel)
            if limpio == "README.md":   # el README recibe el bloque de entrada del kit, con el texto de la persona intacto
                self.assertIn("Mi texto.", (self.c / "README.md").read_text(encoding="utf-8"))
            elif limpio not in ("sistema.json", "ajustes.json"):
                self.assertEqual((self.c / destinos[limpio]).read_bytes(), datos, rel)

    def test_mapeo(self):
        hay = set(base.archivos_del_sistema(self.c))
        for rel in ("README.md", "referencia/manual.md", "prompts/base.md", "kits/datos/anidado/tabla.yaml", "kits/script.sh",
                    "referencia/logo.png", "referencia/notas-de-diseno.txt", "config/ajustes.json"):
            self.assertIn(rel, hay)
        self.assertIn("Mi texto.", (self.c / "README.md").read_text(encoding="utf-8"))
        self.assertIn({"de": "notas de diseño.txt", "a": "notas-de-diseno.txt"}, self.r["renombrados"])
        self.assertEqual(self.r["binarios"], ["referencia/logo.png"])
        self.assertIn("SISTEMA.md", self.r["de_la_base"])
        self.assertNotIn("README.md", self.r["de_la_base"])

    def test_carpetas_desconocidas_quedan_declaradas(self):
        m = base.leer_manifiesto(self.c)
        self.assertIn("kits", m["extensiones"])
        self.assertFalse([e for e in self.r["errores"] if "no es parte del núcleo" in e], self.r["errores"])

    def test_fusion_de_configuraciones(self):
        ajustes = json.loads((self.c / "config/ajustes.json").read_text(encoding="utf-8"))
        self.assertEqual(ajustes["idioma"], "en", "el valor de la persona manda")
        self.assertTrue(ajustes["mio"], "las claves nuevas de la persona se quedan")
        self.assertTrue(ajustes["revision_humana"], "las claves de la base que no tocó se quedan")
        m = base.leer_manifiesto(self.c)
        self.assertEqual(m["version"], "0.3.0")
        self.assertEqual(m["ajustes"], {"tono": "serio"})
        self.assertEqual(m["permisos"]["rutas"]["protegidas"], ["docs/"])
        self.assertIn("fuera_de_ia", m["permisos"]["rutas"], "lo que la persona no dijo sale de la base")
        self.assertEqual(m["activacion"][0], "contratos-de-pago")
        self.assertIn("pagos", m["activacion"])
        self.assertEqual(m["id"], "contratos-de-pago")

    def test_fusionar_manifiesto_unidad(self):
        m_base = {"manifiesto_formato": 1, "id": "x", "version": "0.1.0", "titulo": "X", "activacion": ["x"],
                  "permisos": {"rutas": {"protegidas": [], "fuera_de_ia": []}}, "piezas": ["cambios"]}
        m, avisos = importar.fusionar_manifiesto(m_base, {"id": "otro", "version": "nada", "permisos": {"rutas": {"protegidas": ["a/"]}},
                                                          "piezas": ["skills", "inventada"]}, "x", "X")
        self.assertEqual((m["id"], m["version"]), ("x", "0.1.0"))
        self.assertEqual(m["permisos"]["rutas"], {"protegidas": ["a/"], "fuera_de_ia": []})
        self.assertEqual(m["piezas"], ["skills", "cambios"])
        self.assertTrue(any("«id» era «otro»" in a for a in avisos))

    def test_vista_previa_no_crea_nada(self):
        r = importar.importar(importar.desde_zip(como_zip(material())), pid="pagos-de-prueba", raiz=self.cat, aplicar=False)
        self.assertFalse(r["aplicado"])
        self.assertFalse((self.cat / "pagos-de-prueba").exists())
        self.assertEqual([p.name for p in self.cat.iterdir() if p.name.startswith(".")], [])

    def test_no_pisa_un_sistema_existente(self):
        with self.assertRaises(FileExistsError):
            importar.importar(importar.desde_zip(como_zip(material())), pid="contratos-de-pago", raiz=self.cat)

    def test_zip_malicioso(self):
        with self.assertRaises(importar.ImportacionInvalida):
            importar.desde_zip(como_zip({"../fuera.md": b"x"}))
        with self.assertRaises(importar.ImportacionInvalida):
            importar.desde_zip(b"no es un zip")

    def test_lo_reservado_se_guarda_aparte(self):
        r = importar.importar({"INTEGRIDAD.json": b"{}", "scripts/comun/viejo.py": b"x = 1\n"}, pid="pagos-de-prueba", raiz=self.cat)
        hay = set(base.archivos_del_sistema(self.cat / "pagos-de-prueba"))
        self.assertLessEqual({"importado/INTEGRIDAD.json", "importado/scripts/comun/viejo.py"}, hay)
        self.assertEqual(r["total_importados"], 2)


class TestTodosLosArchivos(ConCatalogo):
    """Árbol, apertura, guardado, paquete: nada se queda fuera por no ser del núcleo."""

    def setUp(self):
        super().setUp()
        importar.importar(importar.desde_zip(como_zip(material())), pid="contratos-de-pago", raiz=self.cat)

    def test_listado_y_apertura(self):
        rutas = catalogo.archivos("contratos-de-pago", self.cat)
        self.assertIn("kits/datos/anidado/tabla.yaml", rutas)
        self.assertEqual(catalogo.abrir_archivo("contratos-de-pago", "kits/datos/anidado/tabla.yaml", self.cat), {"contenido": "clave: 1\n"})
        b = catalogo.abrir_archivo("contratos-de-pago", "referencia/logo.png", self.cat)
        self.assertEqual((b["binario"], b["tipo"], b["tamano"]), (True, "image/png", len(PNG)))
        self.assertEqual(base64.b64decode(b["datos"]), PNG)

    def test_editar_persiste_y_viaja_en_el_paquete(self):
        catalogo.guardar_archivo("contratos-de-pago", "kits/datos/anidado/tabla.yaml", "clave: 2\n", self.cat)
        catalogo.renombrar_archivo("contratos-de-pago", "kits/script.sh", "kits/bin/script.sh", self.cat)
        catalogo.guardar_archivo("contratos-de-pago", "plantillas/nueva/carta.txt", "Hola\n", self.cat)
        c = self.cat / "contratos-de-pago"
        from _sistemas import completar
        completar(c)
        for rel in ("proceso/preparar.md", "proceso/ejecutar.md", "proceso/cerrar.md", "skills/accion-principal/SKILL.md",
                    "referencia/guia.md", "HERRAMIENTAS.md", "ejemplos/caso.md"):
            texto = (c / rel).read_text(encoding="utf-8")
            (c / rel).write_text(__import__("re").sub(r"\{\{([^}]*)\}\}", lambda x: x.group(1).replace("{", "").strip() or "dato", texto), encoding="utf-8")
        self.assertEqual(__import__("especificacion").validar_sistema(c), [])
        z = artefacto.empaquetar("contratos-de-pago", self.t / "dist", self.cat)
        with zipfile.ZipFile(z) as zz:
            nombres = set(zz.namelist())
            self.assertEqual(zz.read("contratos-de-pago/kits/datos/anidado/tabla.yaml"), b"clave: 2\n")
        for rel in ("kits/bin/script.sh", "plantillas/nueva/carta.txt", "referencia/logo.png", "prompts/base.md", "config/ajustes.json"):
            self.assertIn(f"contratos-de-pago/{rel}", nombres)


class TestSincronizacionTodosLosArchivos(ConWeb):
    def test_subir_y_bajar_conservan_lo_anidado_y_no_borran_binarios(self):
        importar.importar(importar.desde_zip(como_zip(material())), pid="contratos-de-pago", raiz=self.cat)
        r = creador.subir("contratos-de-pago", cat=self.cat)
        self.assertEqual(r["solo_en_equipo"], ["referencia/logo.png"])
        web = Servidor.borradores["contratos-de-pago"]["archivos"]
        for rel in ("kits/datos/anidado/tabla.yaml", "kits/script.sh", "prompts/base.md", "config/ajustes.json", "referencia/notas-de-diseno.txt"):
            self.assertIn(rel, web)
        web["kits/datos/anidado/tabla.yaml"] = "clave: web\n"
        web["docs-nuevos/otro/leeme.txt"] = "nuevo en la web\n"
        Servidor.borradores["contratos-de-pago"]["revision"] += 1
        creador.bajar("contratos-de-pago", conservar="web", cat=self.cat)
        c = self.cat / "contratos-de-pago"
        self.assertEqual((c / "kits/datos/anidado/tabla.yaml").read_text(encoding="utf-8"), "clave: web\n")
        self.assertEqual((c / "docs-nuevos/otro/leeme.txt").read_text(encoding="utf-8"), "nuevo en la web\n")
        self.assertEqual((c / "referencia/logo.png").read_bytes(), PNG, "el binario que la web no puede guardar sigue aquí")


class TestPanel(ConPanel):
    def leer(self, ruta: str, **q):
        import urllib.parse
        import urllib.request
        pedido = urllib.request.Request(f"{self.url}{ruta}?{urllib.parse.urlencode(q)}", headers={"X-Uxyn-Token": self.token})
        with urllib.request.urlopen(pedido, timeout=10) as r:
            return json.loads(r.read())["ok"]

    def test_importar_por_el_panel_y_ver_todo(self):
        datos = base64.b64encode(como_zip(material())).decode()
        previa = self.pedir("/api/catalogo/importar", {"zip": datos, "id": "contratos-de-pago", "aplicar": False})
        self.assertFalse(previa["aplicado"])
        r = self.pedir("/api/catalogo/importar", {"zip": datos, "id": "contratos-de-pago"})
        self.assertTrue(r["aplicado"])
        rutas = self.leer("/api/catalogo/archivos", id="contratos-de-pago")
        self.assertIn("kits/datos/anidado/tabla.yaml", rutas)
        self.assertTrue(self.leer("/api/catalogo/archivo", id="contratos-de-pago", rel="referencia/logo.png")["binario"])
        self.assertEqual(self.leer("/api/catalogo/archivo", id="contratos-de-pago", rel="kits/script.sh")["contenido"], "#!/bin/sh\necho hola\n")

    def test_importar_archivos_sueltos_por_el_panel(self):
        r = self.pedir("/api/catalogo/importar", {"id": "pagos-de-prueba", "archivos": [
            {"ruta": "prompts/uno.md", "datos": base64.b64encode(b"uno\n").decode()}]})
        self.assertIn("prompts/uno.md", r["archivos"])

    def test_importar_sin_nada_es_400(self):
        codigo, mensaje = self.error("/api/catalogo/importar", {"id": "pagos-de-prueba"})
        self.assertEqual(codigo, 400, mensaje)


class TestMismosSistemasEnLosDosSitios(ConCatalogo):
    def setUp(self):
        super().setUp()
        catalogo.crear("contratos-de-pago", "Contratos de pago", raiz=self.cat)
        self.casa = mock.patch.dict(os.environ, {"UXYNGRAPHAR_HOME": str(self.t / "casa")})
        self.casa.start()

    def tearDown(self):
        self.casa.stop()
        super().tearDown()

    def test_borradores_solo_en_la_web_aparecen_y_se_organizan(self):
        filas = [{"slug": "revision-de-codigo", "titulo": "Revisión de código", "publicado": False}]
        with mock.patch.object(creador, "borradores", return_value=filas):
            v = mis_sistemas.vista(self.cat)
            mis_sistemas.crear_carpeta("Web", raiz=self.cat)
            cid = mis_sistemas.leer(self.cat)["carpetas"][0]["id"]
            mis_sistemas.mover(["revision-de-codigo"], cid, raiz=self.cat)
        ids = {s["id"]: s for s in v["sistemas"]}
        self.assertEqual(set(ids), {"contratos-de-pago", "revision-de-codigo"})
        self.assertEqual(ids["revision-de-codigo"]["estado"], "web")
        self.assertEqual(ids["contratos-de-pago"]["estado"], "local")
        # sin red, la carpeta del borrador web no se pierde: se usa lo recordado
        with mock.patch.object(creador, "borradores", side_effect=OSError("sin red")):
            v2 = mis_sistemas.vista(self.cat)
        self.assertEqual(v2["web"], "recordados")
        self.assertEqual({s["id"]: s["carpeta"] for s in v2["sistemas"]}["revision-de-codigo"], cid)

    def test_el_taller_lee_la_misma_fuente(self):
        js = (WEB / "js" / "vistas" / "creador-sistemas.js").read_text(encoding="utf-8")
        self.assertIn('obtener("/api/mis-sistemas")', js)
        self.assertIn("mios.sistemas", js)


class TestSesionCaducadaNoRompeProyectos(unittest.TestCase):
    def test_versiones_remotas_sin_sesion_son_vacias(self):
        import fuentes
        with mock.patch.object(fuentes.remoto, "versiones_disponibles", side_effect=PermissionError("sin sesión")):
            self.assertEqual(fuentes.remotas(), {})


class TestWeb1526(unittest.TestCase):
    def node(self, programa: str) -> str:
        if not shutil.which("node"):
            self.skipTest("sin node")
        r = subprocess.run(["node", "--input-type=module", "-e", programa], capture_output=True, text=True, encoding="utf-8",
                           cwd=WEB / "js", check=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_arbol_con_carpetas_anidadas_y_tamanos(self):
        programa = """
globalThis.document = { getElementById: () => null, createElement: () => ({}), createElementNS: () => ({ setAttribute() {}, append() {} }), addEventListener() {} };
globalThis.window = { addEventListener() {} };
globalThis.localStorage = { getItem: () => null, setItem() {} };
globalThis.location = { hash: '', pathname: '/' };
const { arbolDeRutas, tamanoLegible } = await import('./vistas/editor-archivos.js');
const a = arbolDeRutas(['README.md', 'kits/datos/anidado/tabla.yaml', 'recursos/logo.png']);
const kits = a.carpetas.get('kits').carpetas.get('datos').carpetas.get('anidado');
console.log(JSON.stringify([a.archivos, kits.archivos, [...a.carpetas.keys()], tamanoLegible(2048)]));
"""
        self.assertEqual(json.loads(self.node(programa)),
                         [["README.md"], ["kits/datos/anidado/tabla.yaml"], ["kits", "recursos"], "2,0 KB"])

    def test_iconos_con_tamano_propio_y_sin_tema_claro(self):
        ui = (WEB / "js" / "ui.js").read_text(encoding="utf-8")
        self.assertIn('svg.setAttribute("width", "18")', ui)
        css = (WEB / "estilos.css").read_text(encoding="utf-8")
        self.assertNotIn("prefers-color-scheme", css, "la app web es oscura siempre; el panel también")
        self.assertIn("--fondo: var(--color-ink);", css)
        self.assertIn("--foco: var(--color-tone);", css)
        self.assertIn("prefers-reduced-motion", css)


if __name__ == "__main__":
    unittest.main()
