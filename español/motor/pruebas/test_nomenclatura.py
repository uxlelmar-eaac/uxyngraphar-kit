"""Pruebas de la nomenclatura del kit (NOMENCLATURA.md): una por regla, más el catálogo real y `crear`."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import _rutas  # noqa: F401
from _paquetes import completar
import catalogo
import nomenclatura as nom

base = catalogo.base

BUENO = {
    "manifiesto_formato": 2, "id": "pruebas-de-nombres", "version": "1.0.0", "titulo": "Pruebas de nombres",
    "descripcion": "Paquete de prueba", "familia": "proceso", "motor": ">=2.0",
    "activacion": ["pruebas-de-nombres", "pruebas de nombres"], "entrada": "README.md", "verificaciones": [],
    "fichas": {"prueba": {"carpeta": ".", "prefijo": "PRN", "plantilla": "plantillas/prueba.md", "inicial": "propuesta",
                          "estados": {"propuesta": "pendientes", "cerrada": "completadas"}}},
}
README = "# Pruebas de nombres\n\nActivado con «usa el paquete pruebas-de-nombres» / «sigue el protocolo pruebas de nombres».\n"


class TestNomenclatura(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / "pruebas-de-nombres"
        (self.dir / "plantillas").mkdir(parents=True)
        (self.dir / "scripts").mkdir()
        (self.dir / "plantillas" / "prueba.md").write_text("---\nid: {{id}}\n---\n", encoding="utf-8")
        (self.dir / "README.md").write_text(README, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def errores(self, **cambios) -> list[str]:
        m = copy.deepcopy(BUENO)
        m.update(cambios)
        return nom.problemas_paquete(self.dir, m)[0]

    def test_manifiesto_bueno_sin_errores(self):
        self.assertEqual(nom.problemas_paquete(self.dir, BUENO), ([], []))

    def test_forma_del_id(self):
        for malo in ("calidad", "Calidad-de-codigo", "calidad_de_codigo", "rutas-v2", "a-b-c-d-e-f", "contratos-entre-repos",
                     "revisar-secretos", "uxyn-reglas", "de-reglas", "reglas-de", "reglas-para-todo"):
            self.assertTrue(nom.problemas_id(malo), malo)
        for bueno in ("calidad-de-codigo", "paginas-de-aterrizaje-bento", "rutas-de-api", "notas-de-memoria"):
            self.assertEqual(nom.problemas_id(bueno), [], bueno)

    def test_titulo_equivale_al_id(self):
        self.assertEqual(nom.problemas_titulo("rutas-de-api", "Rutas de API"), [])
        self.assertEqual(nom.problemas_titulo("mapa-de-modulos", "Mapa de módulos"), [])
        self.assertTrue(nom.problemas_titulo("rutas-de-api", "Rutas API"))
        self.assertTrue(nom.problemas_titulo("rutas-de-api", "Rutas de API (backend)"))
        self.assertTrue(nom.problemas_titulo("rutas-de-api", "rutas de API"))

    def test_familia(self):
        self.assertTrue(any("familia" in e for e in self.errores(familia="varios")))
        self.assertTrue(any("familia" in e for e in self.errores(familia=None)))

    def test_prefijo_y_plantilla(self):
        for prefijo in ("PR", "PRUE", "prn", "FIC"):
            fichas = copy.deepcopy(BUENO["fichas"])
            fichas["prueba"]["prefijo"] = prefijo
            self.assertTrue(any("prefijo" in e for e in self.errores(fichas=fichas)), prefijo)
        fichas = copy.deepcopy(BUENO["fichas"])
        fichas["prueba"].update(plantilla="plantillas/otra.md", variantes={"corta": "plantillas/corta.md"})
        errores = self.errores(fichas=fichas)
        self.assertTrue(any("plantilla:" in e for e in errores))
        self.assertTrue(any("variantes.corta" in e for e in errores))

    def test_status_fuera_del_vocabulario_y_heredados(self):
        fichas = copy.deepcopy(BUENO["fichas"])
        fichas["prueba"]["estados"]["done"] = "completadas"
        self.assertTrue(any("«done»" in e for e in self.errores(fichas=fichas)))
        m = copy.deepcopy(BUENO)
        m["id"], m["titulo"] = "deuda-y-mejoras", "Deuda y mejoras"
        m["activacion"] = ["deuda-y-mejoras", "deuda y mejoras"]
        m["fichas"]["prueba"]["estados"] = {s: "pendientes" for s in nom.NORMA["status"]["heredados"]["deuda-y-mejoras"]}
        (self.dir / "README.md").write_text("# Deuda y mejoras\n", encoding="utf-8")
        errores, heredados = nom.problemas_paquete(self.dir, m)
        self.assertEqual(errores, [])
        self.assertEqual(len(heredados), len(nom.NORMA["status"]["heredados"]["deuda-y-mejoras"]))
        del m["fichas"]["prueba"]["estados"]["pending"]
        self.assertTrue(any("ya no usa" in e for e in nom.problemas_paquete(self.dir, m)[0]))

    def test_activacion(self):
        self.assertTrue(any("primera" in e for e in self.errores(activacion=["pruebas de nombres", "pruebas-de-nombres"])))
        self.assertTrue(any("con espacios" in e for e in self.errores(activacion=["pruebas-de-nombres"])))
        errores = self.errores(activacion=["pruebas-de-nombres", "pruebas de nombres", "nombres", "Revisión de nombres"])
        self.assertTrue(any("«nombres»" in e for e in errores))
        self.assertTrue(any("Revisión" in e for e in errores))
        self.assertEqual(self.errores(activacion=BUENO["activacion"] + ["adr"]), [])

    def test_readme(self):
        (self.dir / "README.md").write_text(README.replace("pruebas de nombres", "nombres raros").replace("# Pruebas", "# Otras"), encoding="utf-8")
        errores = self.errores()
        self.assertTrue(any("primera línea" in e for e in errores))
        self.assertTrue(any("«nombres raros»" in e for e in errores))

    def test_scripts_y_documentos(self):
        for nombre in ("revisar.py", "Calidad.py", "verificar_capas.py", "escanear_todo.py"):
            (self.dir / "scripts" / nombre).write_text("", encoding="utf-8")
        (self.dir / "scripts" / "secretos_patrones.py").write_text("", encoding="utf-8")
        (self.dir / "scripts" / "verificar-capas.py").write_text("", encoding="utf-8")
        (self.dir / "plantillas" / "Mi Plantilla.md").write_text("", encoding="utf-8")
        errores = self.errores()
        for nombre in ("revisar.py", "Calidad.py", "verificar_capas.py", "escanear_todo.py", "Mi Plantilla.md"):
            self.assertTrue(any(nombre in e for e in errores), nombre)
        self.assertFalse(any("secretos_patrones" in e or "verificar-capas" in e for e in errores))

    def test_reglas_que_cruzan_el_catalogo(self):
        otro = copy.deepcopy(BUENO)
        otro.update(id="pruebas-de-nombres-largos", titulo="Pruebas de nombres largos",
                    activacion=["pruebas-de-nombres-largos", "pruebas de nombres largos", "pruebas de nombres"])
        salida = nom.revisar_catalogo({"pruebas-de-nombres": (self.dir, BUENO), otro["id"]: (self.dir, otro)})
        propios = salida["pruebas-de-nombres"][0]
        self.assertTrue(any("es prefijo" in e for e in propios))
        self.assertTrue(any("ya lo usa" in e for e in salida[otro["id"]][0]))
        self.assertTrue(any("repetida" in e for e in salida[otro["id"]][0]))
        self.assertTrue(any("está dentro de" in e for e in propios))

    def test_ayudas_de_crear(self):
        self.assertEqual(nom.singular("decisiones"), "decision")
        self.assertEqual(nom.singular("reglas"), "regla")
        self.assertEqual(nom.singular("manuales"), "manual")
        self.assertEqual(nom.singular("calidad"), "calidad")
        self.assertEqual(nom.proponer_prefijo("contratos-de-pago", set()), "CON")
        self.assertNotIn(nom.proponer_prefijo("contratos-de-pago", {"CON"}), {"CON", "FIC"})


class TestCatalogoReal(unittest.TestCase):
    def test_catalogo_cumple_la_nomenclatura(self):
        for m in catalogo.listar():
            self.assertEqual([e for e in m["errores"] if e.startswith("nomenclatura")], [], m["id"])
            self.assertIn(m["familia"], nom.NORMA["familias"])

    def test_heredados_declarados_existen_en_el_catalogo(self):
        ids = {m["id"] for m in catalogo.listar()}
        self.assertLessEqual(set(nom.NORMA["status"]["heredados"]), ids)
        self.assertLessEqual(set(nom.NORMA["status"]["dominio"]), ids)


class TestCrear(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cat = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_crear_rechaza_nombres_fuera_de_la_norma(self):
        for pid, titulo, familia in (("demo", "Demo", "proceso"), ("contratos-de-pago", "Pagos", "proceso"),
                                     ("contratos-de-pago", "Contratos de pago", "varios")):
            with self.assertRaises(ValueError):
                catalogo.crear(pid, titulo, "", self.cat, familia=familia)
        catalogo.crear("contratos-de-pago", "Contratos de pago", "", self.cat)
        with self.assertRaises(ValueError):
            catalogo.crear("contratos-de-pago-externo", "Contratos de pago externo", "", self.cat)

    def test_crear_deja_un_paquete_que_cumple(self):
        completar(catalogo.crear("contratos-de-pago", "Contratos de pago", "", self.cat, familia="arquitectura"))
        completar(catalogo.crear("contratos-de-cobro", "Contratos de cobro", "", self.cat, familia="arquitectura"))
        filas = {m["id"]: m for m in catalogo.listar(self.cat)}
        for m in filas.values():
            self.assertEqual(m["errores"], [], m["id"])
        pago = json.loads((self.cat / "contratos-de-pago" / base.MANIFIESTO).read_text(encoding="utf-8"))
        self.assertEqual(list(pago)[:6], ["manifiesto_formato", "id", "version", "titulo", "descripcion", "familia"])
        self.assertEqual(pago["fichas"]["contrato"]["prefijo"], "CON")
        self.assertNotEqual(filas["contratos-de-cobro"]["fichas"]["contrato"]["prefijo"], "CON")
        self.assertTrue((self.cat / "contratos-de-pago" / "plantillas" / "contrato.md").is_file())


if __name__ == "__main__":
    unittest.main()
