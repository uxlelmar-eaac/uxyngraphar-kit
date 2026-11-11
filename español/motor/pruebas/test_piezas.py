"""Pruebas del protocolo de piezas: agregar y quitar, piezas declaradas frente a presentes, extensiones y avisos."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import _rutas  # noqa: F401
from _sistemas import completar
import catalogo
import entrada
import piezas

base = catalogo.base
esp = catalogo.esp


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cat = Path(self.tmp.name)
        self.c = completar(catalogo.crear("pruebas-piezas", "Pruebas piezas", "", self.cat))

    def tearDown(self):
        self.tmp.cleanup()

    def manifiesto(self, **cambios) -> dict:
        m = base.leer_manifiesto(self.c)
        m.update(cambios)
        (self.c / base.MANIFIESTO).write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
        entrada.actualizar(self.c)
        return m

    def errores(self) -> list[str]:
        return esp.validar_sistema(self.c)

    def avisos(self) -> list[str]:
        return esp.avisos_sistema(self.c)


class TestAgregarYQuitar(Base):
    def test_el_registro_cubre_todas_las_piezas(self):
        self.assertEqual(set(piezas.VALIDADORES), set(base.PIEZAS))
        self.assertEqual({d.name for d in catalogo.SEMILLAS.iterdir() if d.is_dir()}, set(base.PIEZAS))

    def test_cada_semilla_se_agrega_y_se_quita_sin_errores(self):
        for pieza in base.PIEZAS:
            if pieza in base.leer_manifiesto(self.c)["piezas"]:
                continue
            with self.subTest(pieza=pieza):
                self.assertEqual(catalogo.agregar_pieza("pruebas-piezas", pieza, self.cat), [])
                self.assertTrue((self.c / base.PIEZAS[pieza]).exists())
                self.assertTrue(entrada.al_dia(self.c))
                with self.assertRaises(FileExistsError):
                    catalogo.agregar_pieza("pruebas-piezas", pieza, self.cat)
        for pieza in ("proceso", "andamiaje", "skills", "componentes"):
            with self.subTest(quitar=pieza):
                self.assertEqual(catalogo.quitar_pieza("pruebas-piezas", pieza, self.cat), [])
                m = base.leer_manifiesto(self.c)
                self.assertNotIn(pieza, m["piezas"])
                self.assertNotIn(pieza, m)
                self.assertFalse((self.c / base.PIEZAS[pieza]).exists())

    def test_el_bloque_de_entrada_sigue_las_piezas(self):
        catalogo.agregar_pieza("pruebas-piezas", "componentes", self.cat)
        self.assertIn("COMPONENTES.md", (self.c / base.ENTRADA).read_text(encoding="utf-8"))
        catalogo.quitar_pieza("pruebas-piezas", "componentes", self.cat)
        self.assertNotIn("COMPONENTES.md", (self.c / base.ENTRADA).read_text(encoding="utf-8"))
        self.assertIn("LIMITES.md", (self.c / base.ENTRADA).read_text(encoding="utf-8"), "límites y permisos: paso fijo")

    def test_limites_ya_no_es_pieza(self):
        for accion in (catalogo.agregar_pieza, catalogo.quitar_pieza):
            with self.assertRaisesRegex(ValueError, "núcleo"):
                accion("pruebas-piezas", "limites", self.cat)

    def test_no_quita_plantillas_con_fichas(self):
        with self.assertRaises(ValueError):
            catalogo.quitar_pieza("pruebas-piezas", "plantillas", self.cat)
        with self.assertRaises(ValueError):
            catalogo.quitar_pieza("pruebas-piezas", "componentes", self.cat)

    def test_readme_libre_fuera_del_bloque(self):
        texto = (self.c / base.ENTRADA).read_text(encoding="utf-8") + "\n## Lo propio del sistema\n\nTexto libre.\n"
        self.assertEqual(catalogo.guardar_archivo("pruebas-piezas", base.ENTRADA, texto, self.cat), [])
        roto = texto.replace(entrada.FIN, "")
        self.assertTrue(catalogo.guardar_archivo("pruebas-piezas", base.ENTRADA, roto, self.cat))


class TestEstructura(Base):
    def test_carpeta_no_declarada_es_error_y_extension_la_admite(self):
        (self.c / "diagramas").mkdir()
        (self.c / "diagramas" / "flujo.md").write_text("# Flujo\n", encoding="utf-8")
        self.assertTrue(any(e.startswith("diagramas:") for e in self.errores()))
        self.manifiesto(extensiones={"diagramas/": "diagramas del flujo"})
        self.assertEqual(self.errores(), [])
        self.manifiesto(extensiones={"diagramas/": "diagramas del flujo", "otra/": "no existe"})
        self.assertTrue(any("extensiones.otra/" in e for e in self.errores()))

    def test_pieza_declarada_sin_ruta_y_ruta_sin_declarar(self):
        self.manifiesto(piezas=["plantillas", "componentes", "cambios"])
        self.assertTrue(any("declarada pero falta COMPONENTES.md" in e for e in self.errores()))
        self.manifiesto(piezas=["plantillas"])
        self.assertTrue(any(e.startswith("CHANGELOG.md: existe pero") for e in self.errores()))

    def test_marcadores_del_nucleo_son_error_y_de_las_piezas_aviso(self):
        catalogo.agregar_pieza("pruebas-piezas", "componentes", self.cat)
        self.assertEqual(self.errores(), [])
        self.assertTrue(any(a.startswith("COMPONENTES.md: marcadores") for a in self.avisos()))
        descripcion = self.c / base.DESCRIPCION
        descripcion.write_text(descripcion.read_text(encoding="utf-8") + "\n{{pendiente}}\n", encoding="utf-8")
        self.assertTrue(any(e.startswith("SISTEMA.md: marcadores") for e in self.errores()))

    def test_sistema_md_cita_los_problemas_y_tiene_sus_secciones(self):
        descripcion = self.c / base.DESCRIPCION
        texto = descripcion.read_text(encoding="utf-8")
        descripcion.write_text(texto.replace("`problema-principal`", "problema principal"), encoding="utf-8")
        self.assertTrue(any("problema-principal" in e for e in self.errores()))
        descripcion.write_text(texto.replace("## Fuera de alcance", "## Otra cosa"), encoding="utf-8")
        self.assertTrue(any("Fuera de alcance" in e for e in self.errores()))

    def test_formato_de_fase_y_de_skill(self):
        catalogo.agregar_pieza("pruebas-piezas", "skills", self.cat)
        catalogo.agregar_pieza("pruebas-piezas", "proceso", self.cat)
        self.assertEqual(self.errores(), [])
        skill = self.c / "skills" / "accion-principal" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace("name: accion-principal", "name: otra"), encoding="utf-8")
        self.assertTrue(any("«name» debe ser «accion-principal»" in e for e in self.errores()))
        (self.c / "proceso" / "sobrante.md").write_text("---\nfase: sobrante\n---\n# Sobrante\n", encoding="utf-8")
        self.assertTrue(any(e.startswith("proceso/sobrante.md: no está") for e in self.errores()))
        fase = self.c / "proceso" / "preparar.md"
        fase.write_text(fase.read_text(encoding="utf-8").replace("resuelve: [problema-principal]", "resuelve: [inventado]"),
                        encoding="utf-8")
        self.assertTrue(any("cita «inventado»" in e for e in self.errores()))


class TestAvisos(Base):
    def test_mas_de_cinco_problemas_avisa_de_generalista(self):
        m = base.leer_manifiesto(self.c)
        m["alcance"]["problemas"] = [{"id": f"problema-{n}", "descripcion": "x"} for n in "abcdef"]
        self.manifiesto(alcance=m["alcance"])
        self.assertTrue(any("posible sistema generalista" in a for a in self.avisos()))

    def test_problema_sin_cubrir_avisa(self):
        catalogo.agregar_pieza("pruebas-piezas", "proceso", self.cat)
        self.assertFalse(any("no lo cubre" in a for a in self.avisos()))
        m = base.leer_manifiesto(self.c)
        m["alcance"]["problemas"].append({"id": "problema-suelto", "descripcion": "x"})
        self.manifiesto(alcance=m["alcance"])
        self.assertTrue(any("«problema-suelto» no lo cubre" in a for a in self.avisos()))

    def test_recomendadas_por_familia_son_avisos(self):
        self.manifiesto(familia="arquitectura")
        self.assertEqual(self.errores(), [])
        faltan = catalogo.completitud("pruebas-piezas", self.cat)["faltan_recomendadas"]
        self.assertEqual(faltan, ["proceso", "componentes", "ejemplos"])
        self.assertTrue(any(a.startswith("completitud:") for a in self.avisos()))


if __name__ == "__main__":
    unittest.main()
