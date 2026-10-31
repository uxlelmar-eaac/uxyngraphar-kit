"""Pruebas de R-21 (alcance.py): fraccionar o ampliar 1.5–2× con aprobación humana."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import alcance  # noqa: E402

JUST = "Contrato compartido: a medias rompe la compilación entre entregas."


def fm(n: int = 3, **extra: object) -> dict:
    d: dict = {"anclas_codigo": [f"src/m{i}.py" for i in range(n)], "presupuesto_max_archivos_codigo": 5}
    d.update(extra)
    return d


class TestEstandar(unittest.TestCase):
    def test_dentro_del_estandar_no_molesta(self) -> None:
        self.assertEqual(alcance.problemas(fm(5)), [])
        self.assertEqual(alcance.bloqueos(fm(5)), [])
        self.assertEqual(alcance.resumen(fm(5)), "")
        self.assertEqual(alcance.leer(fm(5)).maximo, 5)

    def test_rangos_del_mismo_archivo_cuentan_una_vez(self) -> None:
        f = {"anclas_codigo": ["src/a.py:1-20", "src/a.py:40-60", "`src/b.py`", "src/c.py:7"]}
        self.assertEqual(alcance.leer(f).archivos, ["src/a.py", "src/b.py", "src/c.py"])

    def test_mas_de_cinco_sin_factor_obliga_a_fraccionar_o_ampliar(self) -> None:
        p = alcance.problemas(fm(7))
        self.assertEqual(len(p), 1)
        self.assertTrue(p[0].startswith("7 archivos de código > estándar 5"))
        self.assertIn("fracciona", p[0])

    def test_presupuesto_declarado_tambien_cuenta(self) -> None:
        self.assertTrue(alcance.problemas(fm(2, presupuesto_max_archivos_codigo=7)))

    def test_fraccion_que_excede_el_estandar(self) -> None:
        self.assertTrue(any("cada fracción" in m for m in alcance.problemas(fm(6, fraccion_de="20261028-001"))))

    def test_fracciones_validas(self) -> None:
        self.assertEqual(alcance.bloqueos(fm(4, fraccion_de="20261028-001", depende_de=["20261028-002"])), [])


class TestAmpliacion(unittest.TestCase):
    def test_ampliacion_justificada_pide_aprobacion(self) -> None:
        f = fm(7, ampliacion_factor="1.5", ampliacion_justificacion=JUST)
        self.assertEqual(alcance.problemas(f), [])   # se puede aprobar
        self.assertEqual(alcance.leer(f).maximo, 7)
        self.assertTrue(any("sin aprobación humana" in b for b in alcance.bloqueos(f)))   # pero no ejecutar aún
        self.assertTrue(alcance.resumen(f).startswith("R-21 pide ampliar a 7"))

    def test_aprobada_desbloquea(self) -> None:
        f = fm(10, ampliacion_factor=2, ampliacion_justificacion=JUST, ampliacion_aprobada_at="2026-10-28T20:00:00Z")
        self.assertEqual(alcance.bloqueos(f), [])
        self.assertEqual(alcance.leer(f).maximo, 10)

    def test_factor_fuera_de_rango(self) -> None:
        for malo in ("1.2", "2.5", "3", "mucho"):
            with self.subTest(malo=malo):
                p = alcance.problemas(fm(7, ampliacion_factor=malo, ampliacion_justificacion=JUST))
                self.assertTrue(p and "fuera de 1.5–2" in p[0])

    def test_sin_justificacion(self) -> None:
        self.assertTrue(any("sin ampliacion_justificacion" in m for m in alcance.problemas(fm(7, ampliacion_factor=1.5))))

    def test_excede_el_tope_del_factor(self) -> None:
        p = alcance.problemas(fm(8, ampliacion_factor=1.5, ampliacion_justificacion=JUST))
        self.assertTrue(any("tope 7" in m for m in p))

    def test_ampliacion_innecesaria(self) -> None:
        self.assertTrue(any("no hace falta ampliar" in m for m in alcance.problemas(fm(4, ampliacion_factor=1.5, ampliacion_justificacion=JUST))))

    def test_null_no_es_ampliacion(self) -> None:
        f = fm(3, ampliacion_factor=None, ampliacion_justificacion="", ampliacion_aprobada_at=None)
        self.assertEqual(alcance.bloqueos(f), [])
        self.assertEqual(alcance.resumen(f), "")


if __name__ == "__main__":
    unittest.main()
