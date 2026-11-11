"""Pruebas del andamiaje: el script portable de _base y el comando del motor sobre un sistema instalado."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import _rutas  # noqa: F401
from _sistemas import completar
import andamiaje
import andamiar
import catalogo
import repo

base = catalogo.base
SISTEMA = "pruebas-andamio"


class TestScriptPortable(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        raiz = Path(self.tmp.name)
        self.cat = raiz / "catalogo"
        self.cat.mkdir()
        self.app = raiz / "app"
        self.app.mkdir()
        self.sistema = completar(catalogo.crear("pruebas-andamio", "Pruebas andamio", "", self.cat, piezas=["andamiaje", "cambios"]))
        semilla = self.sistema / "andamiaje" / "estructura"
        (semilla / "__nombre__" / "__nombre__.ts.plantilla").write_text(
            "export const {{nombreCamel}}Id = '{{nombre}}';\nexport class {{Nombre}} {}\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_semilla_valida(self):
        self.assertEqual(catalogo.esp.validar_sistema(self.sistema), [])
        self.assertIn("estructura", andamiar.variantes(self.sistema))

    def test_codigo_sin_sufijo_plantilla_no_valida(self):   # C-44
        (self.sistema / "andamiaje" / "estructura" / "suelto.ts").write_text("export {};\n", encoding="utf-8")
        errores = catalogo.esp.validar_sistema(self.sistema)
        self.assertTrue(any("suelto.ts" in e and ".plantilla" in e for e in errores), errores)

    def test_plan_no_escribe(self):
        plan = andamiar.plan(self.sistema, "estructura", "payment-methods", self.app)
        self.assertTrue(plan)
        self.assertTrue(all(not existe for _, _, existe in plan))
        self.assertEqual(list(self.app.iterdir()), [])

    def test_aplicar_sustituye_y_no_sobrescribe(self):
        creados, omitidos = andamiar.aplicar(self.sistema, "estructura", "payment-methods", self.app)
        self.assertEqual(omitidos, [])
        (ts,) = [f for f in creados if f.suffix == ".ts"]
        self.assertEqual(ts.name, "payment-methods.ts")
        texto = ts.read_text(encoding="utf-8")
        self.assertIn("paymentMethodsId = 'payment-methods'", texto)
        self.assertIn("class PaymentMethods", texto)
        self.assertNotIn("__nombre__", ts.as_posix())
        ts.write_text("propio\n", encoding="utf-8")
        creados, omitidos = andamiar.aplicar(self.sistema, "estructura", "payment-methods", self.app)
        self.assertEqual(creados, [])
        self.assertIn(ts, omitidos)
        self.assertEqual(ts.read_text(encoding="utf-8"), "propio\n")

    def test_rechaza_nombres_y_variantes_invalidos(self):
        for nombre in ("Orders", "1orders", "orders/../x", "orders-"):
            with self.assertRaises(ValueError, msg=nombre):
                andamiar.plan(self.sistema, "estructura", nombre, self.app)
        with self.assertRaises(ValueError):
            andamiar.plan(self.sistema, "otra", "orders", self.app)

    def test_destino_fuera_de_la_app(self):
        m = base.leer_manifiesto(self.sistema)
        m["andamiaje"]["estructura"]["destino"] = "../fuera/{nombre}"
        (self.sistema / base.MANIFIESTO).write_text(catalogo.json.dumps(m), encoding="utf-8")
        with self.assertRaises(ValueError):
            andamiar.plan(self.sistema, "estructura", "orders", self.app)


class TestComandoDelMotor(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        raiz = Path(self.tmp.name)
        cat = raiz / "catalogo"
        cat.mkdir()
        self.app = raiz / "app"
        self.app.mkdir()
        sistema = completar(catalogo.crear(SISTEMA, "Pruebas andamio", "", cat, piezas=["andamiaje", "cambios"]))
        (sistema / "andamiaje" / "estructura" / "__nombre__" / "__nombre__.ts.plantilla").write_text(
            "export class {{Nombre}} {}\n", encoding="utf-8")
        repo.instalar(self.app, [SISTEMA], cat)

    def tearDown(self):
        repo.borrar_arbol(Path(self.tmp.name))
        self.tmp.cleanup()

    def test_variantes_del_sistema_instalado(self):
        self.assertIn("estructura", andamiaje.variantes(self.app, SISTEMA))

    def test_simular_y_aplicar_respetan_el_sistema_inmutable(self):
        simulado = andamiaje.simular(self.app, SISTEMA, "estructura", "orders")
        self.assertTrue(any(r.endswith("orders/orders.ts") and not existe for r, existe in simulado), simulado)
        self.assertFalse(any((self.app / r).exists() for r, _ in simulado))
        creados, omitidos = andamiaje.aplicar(self.app, SISTEMA, "estructura", "orders")
        self.assertEqual(sorted(creados), sorted(r for r, _ in simulado))
        self.assertEqual(omitidos, [])
        self.assertTrue(repo.estado(self.app)[0]["integro"])
        self.assertEqual(andamiaje.aplicar(self.app, SISTEMA, "estructura", "orders"), ([], creados))

    def test_sistema_no_instalado(self):
        with self.assertRaises(FileNotFoundError):
            andamiaje.variantes(self.app, "no-instalado")


if __name__ == "__main__":
    unittest.main()
