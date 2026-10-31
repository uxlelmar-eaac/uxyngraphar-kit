#!/usr/bin/env python3
"""Garantías de actualización: todo o nada (también con Ctrl+C o un corte), prueba de humo, migraciones, lock dañado y contrato."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from unittest import mock

from test_nucleo import Base, copiar_pack

import actualizar as act  # noqa: E402
import ci  # noqa: E402
import contrato  # noqa: E402
import doctor  # noqa: E402
import lock  # noqa: E402
import migraciones  # noqa: E402
import respaldos  # noqa: E402
import transaccion  # noqa: E402

AQUI = Path(__file__).resolve().parent


class BaseActualizar(Base):
    def setUp(self) -> None:
        super().setUp()
        self.instalar()
        self.nuevo = copiar_pack(self.tmp / "pack2")
        self.version_nueva = f"{lock.mayor(lock.version_de(self.pack))}.99.0"
        f = self.nuevo / "VERSION.md"
        f.write_text(f.read_text(encoding="utf-8").replace(f"version: {lock.version_de(self.pack)}", f"version: {self.version_nueva}", 1), encoding="utf-8")
        (self.nuevo / "REGLAS.md").write_text("regla nueva", encoding="utf-8")
        (self.nuevo / "10-guias/guia-nueva.md").write_text("g", encoding="utf-8")
        self.reglas = self.repo / "docs/REGLAS.md"
        self.original = self.reglas.read_bytes()
        self.lock_original = lock.ruta_lock(self.repo, "docs").read_bytes()

    def plan(self) -> act.Plan:
        return act.planificar(self.nuevo, self.repo, "docs")

    def assert_como_antes(self) -> None:
        self.assertEqual(self.reglas.read_bytes(), self.original)
        self.assertFalse((self.repo / "docs/10-guias/guia-nueva.md").exists())
        self.assertEqual(lock.ruta_lock(self.repo, "docs").read_bytes(), self.lock_original)
        self.assertEqual(transaccion.interrumpidas(self.repo), [])


class TestTodoONada(BaseActualizar):
    def test_ctrl_c_a_mitad_deja_todo_como_estaba(self) -> None:
        real, llamadas = transaccion.Transaccion.copiar, []

        def copiar(tx, rel, origen):  # type: ignore[no-untyped-def]
            llamadas.append(rel)
            if len(llamadas) == 2:
                raise KeyboardInterrupt
            return real(tx, rel, origen)

        with mock.patch.object(transaccion.Transaccion, "copiar", copiar), self.assertRaises(KeyboardInterrupt):
            act.aplicar(self.nuevo, self.repo, "docs", self.plan())
        self.assert_como_antes()
        r = respaldos.listar(self.repo, "docs")[0]
        self.assertEqual(r.info.get("estado"), "deshecha")

    def test_corte_brusco_se_deshace_y_luego_se_aplica(self) -> None:
        tx = transaccion.Transaccion(self.repo, "docs", version_antes="x", version_despues="y")   # el proceso «muere» sin confirmar
        tx.copiar("docs/REGLAS.md", self.nuevo / "REGLAS.md")
        tx.escribir("docs/10-guias/guia-nueva.md", b"a medias")
        self.assertEqual(len(transaccion.interrumpidas(self.repo)), 1)
        self.assertIn("actualizacion-interrumpida", {c.id for c in doctor.estado_lock(self.repo, "docs")})
        p = self.plan()
        self.assertTrue(any("se cortó a mitad" in a for a in p.avisos))
        act.aplicar(self.nuevo, self.repo, "docs", p)
        self.assertEqual(transaccion.interrumpidas(self.repo), [])
        self.assertEqual(self.reglas.read_text(encoding="utf-8"), "regla nueva")
        self.assertEqual((self.repo / "docs/10-guias/guia-nueva.md").read_text(encoding="utf-8"), "g")
        self.assertEqual(lock.leer(self.repo, "docs")["version"], self.version_nueva)

    def test_doctor_fix_deshace_la_interrumpida(self) -> None:
        tx = transaccion.Transaccion(self.repo, "docs")
        tx.copiar("docs/REGLAS.md", self.nuevo / "REGLAS.md")
        tx.escribir("docs/10-guias/guia-nueva.md", b"x")
        hechas = doctor.arreglar(self.repo, "docs")
        self.assertTrue(any("interrumpida" in h for h in hechas))
        self.assert_como_antes()

    def test_una_interrumpida_no_se_poda(self) -> None:
        tx = transaccion.Transaccion(self.repo, "docs")
        tx.escribir("docs/x.md", b"x")
        self.assertEqual(respaldos.caducados(self.repo, "docs", dias=-1, minimo=0), [])


class TestPruebaDeHumo(BaseActualizar):
    def test_herramientas_instaladas_arrancan(self) -> None:
        self.assertEqual(contrato.probar(self.repo, "docs"), [])

    def test_version_que_rompe_las_herramientas_se_deshace(self) -> None:
        (self.nuevo / "scripts/controlar.py").write_text("import modulo_que_no_existe\n", encoding="utf-8")
        with self.assertRaises(act.ErrorActualizacion) as ctx:
            act.aplicar(self.nuevo, self.repo, "docs", self.plan(), probar=True)
        self.assertIn("controlar.py", str(ctx.exception))
        self.assert_como_antes()

    def test_version_que_quita_una_opcion_del_contrato_se_deshace(self) -> None:
        f = self.nuevo / "scripts/controlar.py"
        f.write_text(f.read_text(encoding="utf-8").replace('"--staged"', '"--preparados"'), encoding="utf-8")
        with self.assertRaises(act.ErrorActualizacion) as ctx:
            act.aplicar(self.nuevo, self.repo, "docs", self.plan(), probar=True)
        self.assertIn("--staged", str(ctx.exception))
        self.assert_como_antes()


def _renombrar_clave(ctx: migraciones.Contexto) -> list[str]:
    cfg = ctx.config()
    if cfg is None or "clave_vieja" not in cfg:
        return []
    cfg["clave_nueva"] = cfg.pop("clave_vieja")
    ctx.guardar_config(cfg)
    return ["clave_vieja → clave_nueva"]


class TestMigraciones(BaseActualizar):
    def _registro(self, *extra: migraciones.Migracion) -> mock._patch:  # type: ignore[name-defined]
        m = migraciones.Migracion(self.version_nueva, "M-clave", "renombra clave_vieja", _renombrar_clave)
        return mock.patch.object(migraciones, "REGISTRO", [m, *extra])

    def test_se_aplica_una_sola_vez(self) -> None:
        cfg = self.repo / "docs/uxyngraphar.config.json"
        datos = json.loads(cfg.read_text(encoding="utf-8"))
        datos["clave_vieja"] = 7
        cfg.write_text(json.dumps(datos), encoding="utf-8")
        with self._registro():
            p = self.plan()
            self.assertEqual([m.split(" ")[0] for m in p.migraciones], ["M-clave"])
            act.aplicar(self.nuevo, self.repo, "docs", p)
            self.assertEqual(p.hechas, [("M-clave", ["clave_vieja → clave_nueva"])])
            self.assertEqual(json.loads(cfg.read_text(encoding="utf-8"))["clave_nueva"], 7)
            self.assertEqual(lock.leer(self.repo, "docs")["migraciones"], ["M-clave"])
            self.assertEqual(self.plan().migraciones, [])

    def test_migracion_que_falla_deshace_todo(self) -> None:
        def rompe(ctx: migraciones.Contexto) -> list[str]:
            ctx.escribir("uxyngraphar.config.json", "{}")
            raise RuntimeError("fallo de prueba")
        cfg = (self.repo / "docs/uxyngraphar.config.json").read_bytes()
        with self._registro(migraciones.Migracion(self.version_nueva, "M-rompe", "x", rompe)), self.assertRaises(RuntimeError):
            act.aplicar(self.nuevo, self.repo, "docs", self.plan())
        self.assertEqual((self.repo / "docs/uxyngraphar.config.json").read_bytes(), cfg)
        self.assert_como_antes()

    def test_que_migraciones_tocan(self) -> None:
        # Versiones hipotéticas posteriores a la línea base 1.0.0.
        reg = [migraciones.Migracion(v, v, "", _renombrar_clave) for v in ("2.1.0", "2.5.0", "3.0.0")]
        ids = lambda a, n, h=set(): [m.id for m in migraciones.pendientes(a, n, h, reg)]  # noqa: E731
        self.assertEqual(ids("2.1.0", "2.9.0"), ["2.5.0"])
        self.assertEqual(ids("1.0.0", "3.0.0"), ["2.1.0", "2.5.0", "3.0.0"])
        self.assertEqual(ids("desconocida", "2.5.0"), ["2.1.0", "2.5.0"])
        self.assertEqual(ids("1.0.0", "3.0.0", {"2.5.0"}), ["2.1.0", "3.0.0"])

    def test_registro_real_bien_formado(self) -> None:
        ids = [m.id for m in migraciones.REGISTRO]
        self.assertEqual(len(ids), len(set(ids)), "ids de migración repetidos")
        self.assertEqual(migraciones.REGISTRO, sorted(migraciones.REGISTRO, key=lambda m: lock._tupla(m.version)))
        self.assertTrue(all(lock._tupla(m.version) <= lock._tupla(lock.version_de(self.pack)) for m in migraciones.REGISTRO))
        # Ninguna migración puede ser de la línea base o anterior: en 1.0.0 todo se instala ya en su forma final.
        self.assertTrue(all(lock._tupla(m.version) > lock._tupla("1.0.0") for m in migraciones.REGISTRO))

    def test_linea_base_sin_pendientes(self) -> None:
        self.assertEqual(migraciones.pendientes("1.0.0", "1.0.0", set()), [])


class TestLockDanado(BaseActualizar):
    def test_usa_la_copia_del_ultimo_respaldo(self) -> None:
        act.aplicar(self.nuevo, self.repo, "docs", self.plan())
        lock.ruta_lock(self.repo, "docs").write_text("{roto", encoding="utf-8")
        datos = lock.leer(self.repo, "docs")
        self.assertIn("copia del respaldo", datos["danado"])
        self.assertEqual(datos["version"], lock.version_de(self.pack))
        p = act.planificar(self.nuevo, self.repo, "docs")
        self.assertTrue(p.avisos)
        act.aplicar(self.nuevo, self.repo, "docs", p)
        self.assertNotIn("danado", json.loads(lock.ruta_lock(self.repo, "docs").read_text(encoding="utf-8")))

    def test_sin_copia_no_pisa_nada(self) -> None:
        self.reglas.write_text("mi versión", encoding="utf-8")
        lock.ruta_lock(self.repo, "docs").write_text("no es json", encoding="utf-8")
        p = self.plan()
        self.assertTrue(p.sin_lock)
        act.aplicar(self.nuevo, self.repo, "docs", p)
        self.assertEqual(self.reglas.read_text(encoding="utf-8"), "mi versión")
        self.assertEqual(lock.leer(self.repo, "docs")["version"], self.version_nueva)


class TestContrato(unittest.TestCase):
    """Lo que los ganchos y el CI de cualquier versión anterior llaman debe seguir existiendo."""

    SCRIPTS = AQUI.parent

    def test_entradas_existen(self) -> None:
        faltan = [s for s in contrato.ENTRADAS if not (self.SCRIPTS / s).is_file()]
        self.assertEqual(faltan, [], "una versión no puede quitar una entrada del contrato (deja un alias)")

    def test_ganchos_y_ci_solo_usan_entradas_del_contrato(self) -> None:
        sys_path = str(self.SCRIPTS / "ganchos")
        import sys
        sys.path.insert(0, sys_path)
        import instalar_ganchos
        usados = {Path(a).name for pasos in instalar_ganchos.COMANDOS.values() for paso in pasos for a in paso if a.endswith(".py")}
        usados |= set(re.findall(r"scripts/([a-z-]+\.py)", ci.PLANTILLA))
        self.assertTrue(usados)
        self.assertEqual(sorted(usados - set(contrato.ENTRADAS)), [])


if __name__ == "__main__":
    unittest.main()
