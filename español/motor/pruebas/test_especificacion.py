"""Pruebas de los contratos del protocolo de sistemas v3: manifiesto, integridad y FLUJO.json."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import _rutas  # noqa: F401
from _sistemas import ALCANCE, DESCRIPCION, LIMITES, MEMORIAS, PERMISOS
import entrada
import especificacion as esp
import uxyn_permisos

base = esp.base

MANIFIESTO_VALIDO = {
    "manifiesto_formato": 1, "id": "demo", "version": "1.0.0", "titulo": "Demo", "descripcion": "Sistema de prueba",
    "motor": ">=1.0,<2", "activacion": ["demo"], "entrada": "README.md", "verificaciones": ["scripts/verificar.py"],
    "alcance": ALCANCE, "piezas": ["plantillas", "referencia"],
    "permisos": {"rutas": {"protegidas": [], "fuera_de_ia": []}, "acciones": {"agente": [], "solo_persona": []}},
    "fichas": {"nota": {"carpeta": "notas", "prefijo": "NOT", "plantilla": "plantillas/nota.md", "inicial": "abierta",
                        "estados": {"abierta": "pendientes", "cerrada": "completadas"}, "solo_humano": ["cerrada"]}},
}


def crear_sistema(raiz: Path, manifiesto: dict | None = None) -> Path:
    m = manifiesto or MANIFIESTO_VALIDO
    p = raiz / m["id"]
    (p / "plantillas").mkdir(parents=True)
    (p / "scripts").mkdir()
    (p / "referencia").mkdir()
    (p / base.MANIFIESTO).write_text(json.dumps(m), encoding="utf-8")
    (p / base.ENTRADA).write_text(entrada.con_bloque("# Demo\n", m), encoding="utf-8")
    (p / base.DESCRIPCION).write_text(DESCRIPCION.format(titulo="Demo"), encoding="utf-8")
    (p / base.MEMORIAS).write_text(MEMORIAS, encoding="utf-8")
    (p / base.LIMITES).write_text(LIMITES, encoding="utf-8")
    (p / base.PERMISOS).write_text(uxyn_permisos.con_bloque(PERMISOS, m), encoding="utf-8")
    (p / "referencia" / "guia.md").write_text("# Guía\n", encoding="utf-8")
    (p / "plantillas" / "nota.md").write_text("---\nid: {{id}}\nstatus: {{status}}\n---\n# {{titulo}}\n", encoding="utf-8")
    (p / "scripts" / "verificar.py").write_text("print('ok')\n", encoding="utf-8")
    return p


class TestManifiesto(unittest.TestCase):
    def test_valido(self):
        self.assertEqual(base.validar_manifiesto(MANIFIESTO_VALIDO), [])

    def test_campos_invalidos(self):
        casos = {"id": "Demo X", "version": "1.0", "motor": "2.0", "activacion": [], "entrada": "LEEME.md",
                 "verificaciones": ["otra/cosa.sh"], "manifiesto_formato": 2, "piezas": ["docs"],
                 "alcance": {"problemas": [], "fuera_de_alcance": []}}
        for campo, valor in casos.items():
            m = dict(MANIFIESTO_VALIDO, **{campo: valor})
            self.assertTrue(base.validar_manifiesto(m), campo)

    def test_activacion_incluye_id(self):
        m = dict(MANIFIESTO_VALIDO, activacion=["otra"])
        self.assertIn("activacion: debe incluir el id del sistema", base.validar_manifiesto(m))

    def test_fichas_estados_o_planas(self):
        m = copy.deepcopy(MANIFIESTO_VALIDO)
        m["fichas"]["nota"]["status_validos"] = ["abierta"]
        self.assertTrue(base.validar_manifiesto(m))
        m = copy.deepcopy(MANIFIESTO_VALIDO)
        m["fichas"]["nota"]["estados"] = {"abierta": "01-Pendientes/2026"}
        self.assertTrue(base.validar_manifiesto(m))
        m = copy.deepcopy(MANIFIESTO_VALIDO)
        m["fichas"]["nota"]["inicial"] = "otra"
        self.assertTrue(base.validar_manifiesto(m))


class TestSistemaEIntegridad(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_fuente_valida(self):
        self.assertEqual(esp.validar_sistema(crear_sistema(self.raiz)), [])

    def test_carpeta_distinta_del_id(self):
        p = crear_sistema(self.raiz)
        otra = p.rename(self.raiz / "otro")
        self.assertTrue(any("id es" in e for e in esp.validar_sistema(otra)))

    def test_integridad(self):
        p = crear_sistema(self.raiz)
        (p / base.INTEGRIDAD).write_text(json.dumps(base.calcular_integridad(p)), encoding="utf-8")
        self.assertTrue(base.integro(base.comprobar_integridad(p)))
        self.assertEqual(esp.validar_sistema(p, construido=True), [])
        (p / "referencia" / "guia.md").write_text("# Guía cambiada\n", encoding="utf-8")
        (p / "README.md").unlink()
        (p / "extra.md").write_text("x", encoding="utf-8")
        informe = base.comprobar_integridad(p)
        self.assertEqual(informe["alterados"], ["referencia/guia.md"])
        self.assertEqual(informe["faltantes"], ["README.md"])
        self.assertEqual(informe["añadidos"], ["extra.md"])

    def test_integridad_en_catalogo_es_error(self):
        p = crear_sistema(self.raiz)
        (p / base.INTEGRIDAD).write_text("{}", encoding="utf-8")
        self.assertTrue(esp.validar_sistema(p))

    def test_motor_compatible(self):
        self.assertTrue(esp.motor_compatible(">=1.0", "1.0.0"))
        self.assertTrue(esp.motor_compatible(">=1.0", "1.3.1"))
        self.assertFalse(esp.motor_compatible(">=1.1", "1.0.9"))
        self.assertFalse(esp.motor_compatible(">=2.0", "1.0.0"))
        self.assertTrue(esp.motor_compatible(">=2.0,<3", "2.4.1"))
        self.assertFalse(esp.motor_compatible(">=2.0,<3", "3.0.0"))
        self.assertEqual(esp.VERSION_MOTOR, (esp.MOTOR / "VERSION").read_text(encoding="utf-8").strip())


class TestFlujo(unittest.TestCase):
    def test_inicial(self):
        self.assertEqual(esp.validar_flujo(esp.FLUJO_INICIAL, set()), [])

    def test_modos(self):
        f = dict(esp.FLUJO_INICIAL, modo="secuencia")
        self.assertTrue(esp.validar_flujo(f))
        f["secuencia"] = ["a", "b"]
        self.assertEqual(esp.validar_flujo(f, {"a", "b"}), [])
        self.assertIn("sistema no instalado: b", esp.validar_flujo(f, {"a"}))
        f = dict(esp.FLUJO_INICIAL, modo="trabajar_con")
        self.assertTrue(esp.validar_flujo(f))
        f["trabajar_con"] = "a"
        self.assertEqual(esp.validar_flujo(f, {"a"}), [])
        self.assertTrue(esp.validar_flujo(dict(esp.FLUJO_INICIAL, modo="leer_por_defecto")))
        self.assertTrue(esp.validar_flujo(dict(esp.FLUJO_INICIAL, modo="otro")))
        self.assertTrue(esp.validar_flujo(dict(esp.FLUJO_INICIAL, conflictos="ignorar")))
        self.assertTrue(esp.validar_flujo(dict(esp.FLUJO_INICIAL, secuencia=["a", "a"], modo="secuencia")))


if __name__ == "__main__":
    unittest.main()
