"""Extensiones (1.6.5): «extensiones» como lista se acepta con aviso y se convierte en objeto; las carpetas propias sin
declarar son aviso en el borrador (se declaran solas al regenerar el índice) y error solo para publicar; el validador sigue
cuando el manifiesto solo falla por «extensiones»; «extension declarar» nunca toca la carpeta; importar acepta la lista."""

from __future__ import annotations

import hashlib
import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import _rutas  # noqa: F401
import catalogo
import cli
import especificacion as esp
import implementado
import importar
from test_nucleo_1_6_0 import sistema_implementado

base = esp.base


def _hashes(c: Path, carpetas: tuple[str, ...]) -> dict[str, str]:
    return {p.relative_to(c).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for d in carpetas for p in sorted((c / d).rglob("*")) if p.is_file()}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.c = sistema_implementado(self.tmp)   # trae prompts/ y config/ declaradas como objeto (las de _base)
        self.pid = self.c.name

    def manifiesto(self) -> dict:
        return base.leer_manifiesto(self.c)

    def escribir(self, m: dict) -> None:
        catalogo._escribir_manifiesto(self.c, m)


class Normalizacion(Base):
    def test_la_base_declara_prompts_y_config_como_objeto(self):
        self.assertEqual(set(base.extensiones_declaradas(self.manifiesto())), {"prompts", "config"})

    def test_lista_se_acepta_con_aviso_y_sin_error(self):
        m = self.manifiesto()
        m["extensiones"] = ["prompts", "config"]
        self.escribir(m)
        self.assertEqual(base.validar_manifiesto(m), [])
        self.assertEqual(esp.validar_sistema(self.c), [])
        avisos = esp.avisos_sistema(self.c)
        self.assertTrue(any(a.startswith("extensiones: es una lista") and '"prompts": "para qué sirve"' in a for a in avisos), avisos)

    def test_indice_convierte_la_lista_en_objeto_sin_tocar_carpetas(self):
        m = self.manifiesto()
        m["extensiones"] = ["prompts", "config"]
        self.escribir(m)
        antes = _hashes(self.c, ("prompts", "config"))
        self.assertTrue(catalogo.indice_sistema(self.pid, self.tmp))
        ext = self.manifiesto()["extensiones"]
        self.assertIsInstance(ext, dict)
        self.assertEqual(set(ext), {"prompts", "config"})
        self.assertTrue(all(v == base.EXTENSION_PROVISIONAL for v in ext.values()))
        self.assertEqual(_hashes(self.c, ("prompts", "config")), antes)
        self.assertFalse(catalogo.indice_sistema(self.pid, self.tmp), "segunda vez: ya está al día")

    def test_lista_bloquea_publicar(self):
        m = self.manifiesto()
        m["extensiones"] = ["prompts", "config"]
        self.escribir(m)
        r = implementado.evaluar(self.c)
        self.assertFalse(r["implementado"])
        self.assertTrue(any("«extensiones» es una lista" in e for e in r["errores"]), r["errores"])

    def test_frase_provisional_es_aviso_al_publicar(self):
        m = self.manifiesto()
        m["extensiones"] = {"prompts": base.EXTENSION_PROVISIONAL, "config": "Ajustes propios"}
        self.escribir(m)
        r = implementado.evaluar(self.c)
        self.assertTrue(r["implementado"], r["errores"])
        self.assertTrue(any("frase provisional" in a and "prompts" in a for a in r["avisos"]), r["avisos"])


class SinDeclarar(Base):
    def setUp(self):
        super().setUp()
        (self.c / "guias").mkdir()
        (self.c / "guias" / "a.md").write_text("# Guía\n\nAlgo propio.\n", encoding="utf-8")

    def test_carpeta_propia_sin_declarar_es_aviso_en_el_borrador(self):
        self.assertEqual(esp.validar_sistema(self.c), [])
        self.assertTrue(any(a.startswith("guias: carpeta propia sin declarar") for a in esp.avisos_sistema(self.c)))

    def test_y_error_al_publicar(self):
        r = implementado.evaluar(self.c)
        self.assertFalse(r["implementado"])
        self.assertTrue(any(e.startswith("guias: carpeta propia sin declarar") and "Nunca hace falta borrarla" in e
                            for e in r["errores"]), r["errores"])

    def test_indice_la_declara_sola(self):
        catalogo.indice_sistema(self.pid, self.tmp)
        self.assertEqual(self.manifiesto()["extensiones"]["guias"], base.EXTENSION_PROVISIONAL)
        self.assertTrue((self.c / "guias" / "a.md").is_file())
        self.assertTrue(implementado.evaluar(self.c)["implementado"])


class Validador(Base):
    def test_sigue_validando_si_solo_falla_extensiones(self):
        m = self.manifiesto()
        m["extensiones"] = "prompts, config"
        self.escribir(m)
        (self.c / base.LIMITES).unlink()
        errores = esp.validar_sistema(self.c)
        self.assertTrue(any(e.startswith("extensiones: debe ser un objeto") and "tus carpetas no se tocan" in e for e in errores), errores)
        self.assertIn(f"falta {base.LIMITES}", errores, "no se queda en el manifiesto: valida el resto")

    def test_otros_errores_del_manifiesto_siguen_cortando(self):
        m = self.manifiesto()
        m["version"] = "uno"
        self.escribir(m)
        self.assertEqual(esp.validar_sistema(self.c), ["version: semver X.Y.Z"])

    def test_entrada_reservada_da_ejemplo(self):
        m = self.manifiesto()
        m["extensiones"] = {"proceso": "x"}
        e = base.validar_manifiesto(m)
        self.assertTrue(e and e[0].startswith("extensiones.proceso:") and "p. ej." in e[0], e)


class Declarar(Base):
    def setUp(self):
        super().setUp()
        (self.c / "guias").mkdir()
        (self.c / "guias" / "a.md").write_text("# Guía\n", encoding="utf-8")

    def test_declara_sin_tocar_la_carpeta(self):
        antes = _hashes(self.c, ("guias",))
        errores = catalogo.declarar_extension(self.pid, "guias/", "Guías de estilo del equipo", self.tmp)
        self.assertEqual(errores, [])
        self.assertEqual(self.manifiesto()["extensiones"]["guias"], "Guías de estilo del equipo")
        self.assertEqual(_hashes(self.c, ("guias",)), antes)

    def test_convierte_la_lista_al_declarar(self):
        m = self.manifiesto()
        m["extensiones"] = ["prompts", "config"]
        self.escribir(m)
        catalogo.declarar_extension(self.pid, "config", "Ajustes propios", self.tmp)
        ext = self.manifiesto()["extensiones"]
        self.assertEqual(ext["config"], "Ajustes propios")
        self.assertEqual(ext["prompts"], base.EXTENSION_PROVISIONAL)

    def test_rechazos(self):
        for nombre, para in (("proceso", "x"), ("no-existe", "x"), ("guias", "  "), ("a/b", "x"), ("../fuera", "x")):
            with self.assertRaises(ValueError, msg=nombre):
                catalogo.declarar_extension(self.pid, nombre, para, self.tmp)

    def test_cli_json(self):
        out = io.StringIO()
        with mock.patch.object(catalogo, "catalogo", return_value=self.tmp), redirect_stdout(out):
            codigo = cli.main(["extension", self.pid, "declarar", "guias", "Guías del equipo", "--json"])
        self.assertIn(codigo, (0, None))
        r = json.loads(out.getvalue())
        self.assertEqual((r["carpeta"], r["errores"]), ("guias", []))


class Importar(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.cat = self.tmp / "catalogo"
        self.cat.mkdir()

    def _origen(self) -> Path:
        origen = sistema_implementado(self.tmp / "fuente")
        shutil.rmtree(origen / "scripts")
        m = base.leer_manifiesto(origen)
        m["extensiones"] = ["prompts", "config"]   # como lo dejó uxyn en el borrador real
        catalogo._escribir_manifiesto(origen, m)
        return origen

    def test_adaptar_acepta_la_lista(self):
        r = importar.importar(importar.desde_carpeta(self._origen()), raiz=self.cat, modo="adaptar")
        ext = base.leer_manifiesto(Path(r["ruta"]))["extensiones"]
        self.assertIsInstance(ext, dict)
        self.assertEqual(set(ext), {"prompts", "config"})
        self.assertEqual(r["preservacion"]["perdidos"], [])

    def test_crear_acepta_la_lista(self):
        r = importar.importar(importar.desde_carpeta(self._origen()), raiz=self.cat, modo="crear")
        ext = base.leer_manifiesto(Path(r["ruta"]))["extensiones"]
        self.assertIsInstance(ext, dict)
        self.assertTrue({"prompts", "config"} <= set(ext))
        self.assertEqual(r["preservacion"]["perdidos"], [])


class PanelAvisoBorrado(unittest.TestCase):
    def test_tarjeta_de_cambios_avisa_en_rojo_si_borra(self):
        import subprocess
        if not shutil.which("node"):
            self.skipTest("sin node")
        programa = """
globalThis.document = { getElementById: () => null, createElement: () => ({}), createElementNS: () => ({ setAttribute() {}, append() {} }), addEventListener() {} };
globalThis.window = { addEventListener() {} };
globalThis.localStorage = { getItem: () => null, setItem() {} };
globalThis.location = { hash: '', pathname: '/' };
const m = await import('./vistas/agente-chat.js');
const acciones = [{ cambios: [{ ruta: 'config/ajustes.json', tipo: 'borrado', mas: 0, menos: 1 },
                              { ruta: 'sistema.json', tipo: 'cambiado', mas: 1, menos: 1 }] }];
console.log(JSON.stringify([m.archivosQueBorra(acciones), m.avisoBorrado(m.archivosQueBorra(acciones)),
                            m.archivosQueBorra([{ cambios: [{ ruta: 'a.md', tipo: 'nuevo' }] }])]));
"""
        web = Path(__file__).resolve().parent.parent / "web" / "js"
        r = subprocess.run(["node", "--input-type=module", "-e", programa], capture_output=True, text=True, encoding="utf-8",
                           cwd=web, check=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        borra, aviso, nada = json.loads(r.stdout)
        self.assertEqual(borra, ["config/ajustes.json"])
        self.assertIn("Esta propuesta borra archivos tuyos: config/ajustes.json", aviso)
        self.assertEqual(nada, [])
        chat = (web / "vistas" / "agente-chat.js").read_text(encoding="utf-8")
        self.assertIn('class: "aviso-borrado", role: "alert"', chat)


if __name__ == "__main__":
    unittest.main()
