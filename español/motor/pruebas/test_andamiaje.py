"""Pruebas del andamiaje: el script portable de !base, el comando del motor y el andamiaje del piloto instalado."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import _rutas  # noqa: F401
from _paquetes import completar
import andamiaje
import andamiar
import catalogo
import repo

base = catalogo.base
PILOTO = "arquitectura-monolitica-por-capas"


class TestScriptPortable(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        raiz = Path(self.tmp.name)
        self.cat = raiz / "catalogo"
        self.cat.mkdir()
        self.app = raiz / "app"
        self.app.mkdir()
        self.paquete = completar(catalogo.crear("pruebas-andamio", "Pruebas andamio", "", self.cat, piezas=["andamiaje", "cambios"]))
        semilla = self.paquete / "andamiaje" / "estructura"
        (semilla / "__nombre__" / "__nombre__.ts").write_text(
            "export const {{nombreCamel}}Id = '{{nombre}}';\nexport class {{Nombre}} {}\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_semilla_valida(self):
        self.assertEqual(catalogo.esp.validar_paquete(self.paquete), [])
        self.assertIn("estructura", andamiar.variantes(self.paquete))

    def test_plan_no_escribe(self):
        plan = andamiar.plan(self.paquete, "estructura", "payment-methods", self.app)
        self.assertTrue(plan)
        self.assertTrue(all(not existe for _, _, existe in plan))
        self.assertEqual(list(self.app.iterdir()), [])

    def test_aplicar_sustituye_y_no_sobrescribe(self):
        creados, omitidos = andamiar.aplicar(self.paquete, "estructura", "payment-methods", self.app)
        self.assertEqual(omitidos, [])
        (ts,) = [f for f in creados if f.suffix == ".ts"]
        self.assertEqual(ts.name, "payment-methods.ts")
        texto = ts.read_text(encoding="utf-8")
        self.assertIn("paymentMethodsId = 'payment-methods'", texto)
        self.assertIn("class PaymentMethods", texto)
        self.assertNotIn("__nombre__", ts.as_posix())
        ts.write_text("propio\n", encoding="utf-8")
        creados, omitidos = andamiar.aplicar(self.paquete, "estructura", "payment-methods", self.app)
        self.assertEqual(creados, [])
        self.assertIn(ts, omitidos)
        self.assertEqual(ts.read_text(encoding="utf-8"), "propio\n")

    def test_rechaza_nombres_y_variantes_invalidos(self):
        for nombre in ("Orders", "1orders", "orders/../x", "orders-"):
            with self.assertRaises(ValueError, msg=nombre):
                andamiar.plan(self.paquete, "estructura", nombre, self.app)
        with self.assertRaises(ValueError):
            andamiar.plan(self.paquete, "otra", "orders", self.app)

    def test_destino_fuera_de_la_app(self):
        m = base.leer_manifiesto(self.paquete)
        m["andamiaje"]["estructura"]["destino"] = "../fuera/{nombre}"
        (self.paquete / base.MANIFIESTO).write_text(catalogo.json.dumps(m), encoding="utf-8")
        with self.assertRaises(ValueError):
            andamiar.plan(self.paquete, "estructura", "orders", self.app)


class TestComandoDelMotor(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = Path(self.tmp.name)
        repo.instalar(self.app, [PILOTO])

    def tearDown(self):
        repo.borrar_arbol(Path(self.tmp.name))
        self.tmp.cleanup()

    def test_variantes_del_piloto(self):
        self.assertEqual(set(andamiaje.variantes(self.app, PILOTO)), {"modulo-servidor", "modulo-cliente"})

    def test_simular_y_aplicar_respetan_el_paquete_inmutable(self):
        simulado = andamiaje.simular(self.app, PILOTO, "modulo-servidor", "orders")
        self.assertIn(("src/modules/orders/domain/orders.entity.ts", False), simulado)
        self.assertFalse((self.app / "src").exists())
        creados, omitidos = andamiaje.aplicar(self.app, PILOTO, "modulo-servidor", "orders")
        self.assertEqual(sorted(creados), sorted(r for r, _ in simulado))
        self.assertEqual(omitidos, [])
        self.assertTrue(repo.estado(self.app)[0]["integro"])
        self.assertEqual(andamiaje.aplicar(self.app, PILOTO, "modulo-servidor", "orders"), ([], creados))

    def test_paquete_no_instalado(self):
        with self.assertRaises(FileNotFoundError):
            andamiaje.variantes(self.app, "no-instalado")


if __name__ == "__main__":
    unittest.main()
