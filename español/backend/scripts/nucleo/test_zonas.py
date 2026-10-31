#!/usr/bin/env python3
"""Pruebas de las zonas del pack en archivos mixtos (README/INDICE), plantillas sin tocar y degradación de versión."""

from __future__ import annotations

import unittest

import zonas
from test_nucleo import Base, act, copiar_pack, lock  # noqa: F401 - Base no contiene pruebas propias

I, F = zonas.INICIO, zonas.FIN


class TestFusion(unittest.TestCase):
    def test_sustituye_solo_las_zonas(self) -> None:
        local = f"# T\n{I}\nviejo\n{F}\n| fila mía |\n{I}\nb\n{F}\nnota mía\n"
        nuevo = f"# T\n{I}\nnuevo\n{F}\n| fila pack |\n{I}\nB\n{F}\n"
        self.assertEqual(zonas.fusionar(local, nuevo), f"# T\n{I}\nnuevo\n{F}\n| fila mía |\n{I}\nB\n{F}\nnota mía\n")

    def test_sin_marcadores_o_distinto_numero_no_fusiona(self) -> None:
        self.assertIsNone(zonas.fusionar("# T\nsin zonas\n", f"# T\n{I}\nx\n{F}\n"))
        self.assertIsNone(zonas.fusionar(f"{I}a{F}{I}b{F}", f"{I}a{F}"))


class TestActualizarMixtos(Base):
    def setUp(self) -> None:
        super().setUp()
        self.instalar()
        self.nuevo = copiar_pack(self.tmp / "pack2")
        v = lock.version_de(self.pack)
        f = self.nuevo / "VERSION.md"
        f.write_text(f.read_text(encoding="utf-8").replace(f"version: {v}", f"version: {lock.mayor(v)}.99.0", 1), encoding="utf-8")

    def test_readme_sin_tocar_se_reemplaza_entero(self) -> None:
        (self.nuevo / "README.md").write_text((self.nuevo / "README.md").read_text(encoding="utf-8").replace("**Versión:**", "**Versión (nueva):**"), encoding="utf-8")
        p = act.planificar(self.nuevo, self.repo, "docs")
        self.assertIn("README.md", [a.rel for a in p.de("reemplazar")])

    def test_indice_editado_conserva_lo_del_proyecto_y_actualiza_la_zona(self) -> None:
        rel = "15-rutas/INDICE.md"
        local = self.repo / "docs" / rel
        local.write_text(local.read_text(encoding="utf-8") + "| usuarios | /u | GET | [f](u.md) |\n", encoding="utf-8")
        (self.nuevo / rel).write_text((self.nuevo / rel).read_text(encoding="utf-8").replace(zonas.INICIO, zonas.INICIO + "\nCatálogo NUEVO.", 1), encoding="utf-8")
        p = act.planificar(self.nuevo, self.repo, "docs")
        self.assertIn(rel, [a.rel for a in p.de("zona")])
        act.aplicar(self.nuevo, self.repo, "docs", p)
        texto = local.read_text(encoding="utf-8")
        self.assertIn("Catálogo NUEVO.", texto)
        self.assertIn("| usuarios | /u | GET |", texto)

    def test_plantilla_rellenada_no_se_pisa(self) -> None:
        rel = "00-nucleo/configuracion-proyecto.md"
        (self.repo / "docs" / rel).write_text("mi proyecto\n", encoding="utf-8")
        (self.nuevo / rel).write_text("plantilla nueva\n", encoding="utf-8")
        p = act.planificar(self.nuevo, self.repo, "docs")
        self.assertIn(rel, [a.rel for a in p.de("plantilla-cambiada")])
        act.aplicar(self.nuevo, self.repo, "docs", p)
        self.assertEqual((self.repo / "docs" / rel).read_text(encoding="utf-8"), "mi proyecto\n")


class TestDegradacion(Base):
    def test_comparacion(self) -> None:
        self.assertTrue(lock.es_degradacion("2.0.0", "1.0.9"))
        self.assertTrue(lock.es_degradacion("2.10.0", "2.9.0"))
        self.assertFalse(lock.es_degradacion("1.0.0", "1.0.0"))
        self.assertFalse(lock.es_degradacion("1.0.0", "1.0.1"))

    def test_pack_mas_antiguo_no_escribe(self) -> None:
        self.instalar()
        datos = lock.leer(self.repo, "docs")
        datos["version"] = f"{int(lock.mayor(datos['version'])) + 1}.0.0"
        lock.escribir(self.repo, "docs", datos)
        p = act.planificar(self.pack, self.repo, "docs")
        with self.assertRaises(act.ErrorActualizacion):
            act.aplicar(self.pack, self.repo, "docs", p, migracion="cualquiera")
        self.assertEqual(lock.leer(self.repo, "docs")["version"], datos["version"])


if __name__ == "__main__":
    unittest.main()
