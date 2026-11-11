"""Cambios en proyectos que nunca quedan a medias (transacción con respaldo), `reparar` de proyectos y la desinstalación
guiada por alcance."""

from __future__ import annotations

import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import _rutas  # noqa: F401
from _sistemas import completar
import casa
import catalogo
import desinstalacion
import generar
import proyectos
import repo
import transaccion
from test_motor import huella

base = catalogo.base


def escribible(ruta: Path) -> None:
    """Quita el solo lectura de los sistemas instalados para poder borrarlos o tocarlos en la prueba."""
    for p in [ruta, *ruta.rglob("*")] if ruta.is_dir() else [ruta]:
        if p.exists() and not p.is_symlink():
            os.chmod(p, p.stat().st_mode | stat.S_IWUSR | (stat.S_IXUSR if p.is_dir() else 0))


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        raiz = Path(self.tmp.name).resolve()
        self.cat = raiz / "catalogo"
        self.cat.mkdir()
        self.repo = raiz / "repo"
        self.repo.mkdir()
        self.casa = raiz / "casa"
        entorno = mock.patch.dict(os.environ, {"UXYNGRAPHAR_HOME": str(self.casa)})
        entorno.start()
        self.addCleanup(entorno.stop)
        for pid in ("pruebas-demo", "pruebas-otras"):
            completar(catalogo.crear(pid, pid.replace("-", " ").capitalize(), "Sistema de prueba", self.cat))
        repo.instalar(self.repo, ["pruebas-demo", "pruebas-otras"], self.cat)

    def tearDown(self):
        escribible(Path(self.tmp.name))
        self.tmp.cleanup()


class TestTransaccion(Base):
    def test_fallo_a_mitad_de_actualizar_deja_el_proyecto_como_estaba(self):
        for pid in ("pruebas-demo", "pruebas-otras"):
            catalogo.versionar(pid, "menor", self.cat)
        antes = huella(self.repo)
        original = repo._colocar
        llamadas = []

        def falla_en_la_segunda(*a, **k):
            llamadas.append(a[1])
            if len(llamadas) == 2:
                raise OSError("disco lleno (simulado)")
            return original(*a, **k)

        with mock.patch.object(repo, "_colocar", falla_en_la_segunda), self.assertRaises(OSError):
            repo.actualizar(self.repo, cat=self.cat)
        self.assertEqual(len(llamadas), 2, "el primer sistema sí llegó a cambiar antes del fallo")
        self.assertEqual(huella(self.repo), antes)
        self.assertIsNone(transaccion.interrumpida(self.repo))
        self.assertEqual(repo.actualizar(self.repo, cat=self.cat), ["pruebas-demo", "pruebas-otras"])

    def test_corte_brusco_se_deshace_con_reparar(self):
        antes = huella(self.repo)
        transaccion.respaldar(self.repo, "actualizar")   # el proceso murió aquí: el respaldo quedó «en curso»
        escribible(self.repo / base.CARPETA_SISTEMAS_DE_GOBERNANZA)
        repo.borrar_arbol(self.repo / base.CARPETA_SISTEMAS_DE_GOBERNANZA / "pruebas-otras")
        (self.repo / "AGENTES.md").write_text("a medias\n", encoding="utf-8")
        hechos = repo.reparar(self.repo, self.cat)
        self.assertTrue(any("interrumpido" in h for h in hechos), hechos)
        self.assertEqual(huella(self.repo), antes)
        self.assertIsNone(transaccion.interrumpida(self.repo))

    def test_respaldos_fuera_del_proyecto_y_podados(self):
        for _ in range(transaccion.GUARDADOS + 2):
            repo.actualizar(self.repo, cat=self.cat, forzar=True)
        respaldos = transaccion.carpeta_respaldos(self.repo)
        self.assertTrue(respaldos.is_relative_to(self.casa))
        self.assertEqual(len([d for d in respaldos.iterdir() if d.is_dir()]), transaccion.GUARDADOS)


class TestRepararProyecto(Base):
    def test_sistema_alterado_se_reconstruye(self):
        archivo = self.repo / base.CARPETA_SISTEMAS_DE_GOBERNANZA / "pruebas-demo" / base.ENTRADA
        os.chmod(archivo, stat.S_IWUSR | stat.S_IREAD)
        archivo.write_text("editado a mano\n", encoding="utf-8")
        hechos = repo.reparar(self.repo, self.cat)
        self.assertIn("pruebas-demo: reconstruido (estaba alterado)", hechos)
        self.assertTrue(all(e["integro"] for e in repo.estado(self.repo, self.cat)))

    def test_cambio_de_sistema_cortado(self):
        sistemas = self.repo / base.CARPETA_SISTEMAS_DE_GOBERNANZA
        escribible(sistemas)
        (sistemas / "pruebas-demo").rename(sistemas / ".pruebas-demo.anterior")
        (sistemas / ".construyendo-x").mkdir()
        hechos = repo.reparar(self.repo, self.cat)
        self.assertTrue((sistemas / "pruebas-demo" / base.MANIFIESTO).is_file(), hechos)
        self.assertFalse((sistemas / ".construyendo-x").exists())

    def test_flujo_invalido_vuelve_al_ultimo_bueno(self):
        bueno = {**generar.leer_flujo(self.repo), "modo": "trabajar_con", "trabajar_con": "pruebas-demo"}
        self.assertEqual(generar.guardar_flujo(self.repo, bueno), [])
        repo.actualizar(self.repo, cat=self.cat, forzar=True)   # deja un respaldo con ese FLUJO.json
        generar.ruta_flujo(self.repo).write_text("{roto", encoding="utf-8")
        hechos = repo.reparar(self.repo, self.cat)
        self.assertIn("FLUJO.json: inválido; restaurado del último respaldo", hechos)
        self.assertEqual(generar.leer_flujo(self.repo)["trabajar_con"], "pruebas-demo")

    def test_proyecto_sano_no_cambia(self):
        antes = huella(self.repo)
        self.assertEqual(repo.reparar(self.repo, self.cat), [])
        self.assertEqual(huella(self.repo), antes)


class TestDesinstalacion(Base):
    def setUp(self):
        super().setUp()
        (self.repo / base.CARPETA_TRABAJO / "pruebas-demo" / "nota.md").parent.mkdir(parents=True, exist_ok=True)
        (self.repo / base.CARPETA_TRABAJO / "pruebas-demo" / "nota.md").write_text("mi trabajo\n", encoding="utf-8")
        (self.repo / "codigo.py").write_text("x = 1\n", encoding="utf-8")
        self.otro = Path(self.tmp.name).resolve() / "otro"
        self.otro.mkdir()
        (self.otro / "README.md").write_text("# Otro\n", encoding="utf-8")
        repo.instalar(self.otro, ["pruebas-otras"], self.cat)
        proyectos.agregar([str(self.repo), str(self.otro)])
        self.casa.joinpath("bin").mkdir(parents=True, exist_ok=True)
        temporal = Path(self.tmp.name) / "temporal"   # el informe de la desinstalación va a la carpeta temporal
        temporal.mkdir()
        parche = mock.patch.object(desinstalacion.tempfile, "gettempdir", return_value=str(temporal))
        parche.start()
        self.addCleanup(parche.stop)

    def test_simular_no_toca_nada(self):
        antes = (huella(self.repo), huella(self.otro), huella(self.casa))
        for alcance in desinstalacion.ALCANCES:
            plan = desinstalacion.ejecutar(alcance, simular=True)
            self.assertTrue(plan["simulado"])
            self.assertIn("simulación", desinstalacion.texto_informe(plan))
        self.assertEqual((huella(self.repo), huella(self.otro), huella(self.casa)), antes)
        plan = desinstalacion.planificar("todo")
        tipos = {Path(p["ruta"]).name: p["tipo"] for p in plan["proyectos"]}
        self.assertEqual(tipos, {"repo": "actual", "otro": "actual"})
        otro = next(p for p in plan["proyectos"] if Path(p["ruta"]).name == "otro")
        self.assertIn(f"{base.CARPETA_SISTEMAS_DE_GOBERNANZA}/pruebas-otras/", otro["quitar"])
        self.assertIn(f"{base.CARPETA_TRABAJO}/", otro["conservar"])

    def test_proyectos_quita_de_todos_y_conserva_lo_propio(self):
        informe = desinstalacion.ejecutar("proyectos")
        self.assertEqual(informe["pendiente"], [], desinstalacion.texto_informe(informe))
        self.assertFalse((self.repo / base.CARPETA_SISTEMAS_DE_GOBERNANZA).exists())
        self.assertFalse((self.repo / base.CARPETA_RAIZ / "FLUJO.json").exists())
        self.assertEqual((self.repo / base.CARPETA_TRABAJO / "pruebas-demo" / "nota.md").read_text(), "mi trabajo\n")
        self.assertTrue((self.repo / "codigo.py").is_file())
        self.assertFalse((self.otro / base.CARPETA_SISTEMAS_DE_GOBERNANZA).exists())
        self.assertEqual((self.otro / "README.md").read_text(), "# Otro\n")
        self.assertEqual(proyectos.listar(), [], "salen de la lista los proyectos desinstalados")
        self.assertTrue(self.casa.is_dir(), "la herramienta se queda")

    def test_proyectos_elegidos_con_trabajo(self):
        elegido = self.repo.parent / "enlace-al-repo"   # otra forma de escribir la misma carpeta que la registrada
        try:
            elegido.symlink_to(self.repo, target_is_directory=True)
        except OSError:   # Windows sin permiso para crear enlaces
            elegido = self.repo
        desinstalacion.ejecutar("proyectos", [str(elegido)], con_trabajo=True)
        self.assertFalse((self.repo / base.CARPETA_RAIZ).exists())
        self.assertTrue((self.otro / base.CARPETA_SISTEMAS_DE_GOBERNANZA / "pruebas-otras").is_dir(), "el otro proyecto no se toca")
        self.assertEqual(proyectos.listar(), [str(self.otro)])

    def test_herramienta_no_toca_proyectos(self):
        antes = (huella(self.repo), huella(self.otro))
        informe = desinstalacion.ejecutar("herramienta")
        self.assertEqual(informe["pendiente"], [], desinstalacion.texto_informe(informe))
        if os.name != "nt":   # en Windows la carpeta se borra al salir el proceso
            self.assertFalse(self.casa.exists())
        self.assertEqual((huella(self.repo), huella(self.otro)), antes)

    def test_un_proyecto_que_falla_no_impide_el_resto(self):
        original = repo.desinstalar
        with mock.patch.object(repo, "desinstalar", side_effect=OSError("permiso denegado (simulado)")):
            informe = desinstalacion.ejecutar("todo")
        self.assertTrue(any("permiso denegado" in p for p in informe["pendiente"]))
        self.assertTrue((self.repo / base.CARPETA_SISTEMAS_DE_GOBERNANZA / "pruebas-demo").is_dir(), "el proyecto que falló sigue entero")
        if os.name != "nt":   # en Windows la carpeta se borra al salir el proceso
            self.assertFalse(self.casa.exists())
        self.assertIs(repo.desinstalar, original)

    def test_retirar_un_proyecto(self):
        r = desinstalacion.retirar_de_proyecto(str(self.otro))
        self.assertEqual(r["tipo"], "actual")
        self.assertFalse((self.otro / base.CARPETA_SISTEMAS_DE_GOBERNANZA).exists())
        self.assertTrue((self.otro / "README.md").is_file())
        with self.assertRaises(FileNotFoundError):
            desinstalacion.retirar_de_proyecto(str(self.otro / "no-existe"))

    def test_menu_de_la_cli(self):
        respuestas = iter(["3", "1", "s"])
        eleccion = desinstalacion.preguntar(lambda _: next(respuestas), lambda *_: None)
        self.assertEqual(eleccion, ("proyectos", proyectos.listar()[:1], True))
        self.assertIsNone(desinstalacion.preguntar(lambda _: "0", lambda *_: None))


class TestCasa(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        entorno = mock.patch.dict(os.environ, {"UXYNGRAPHAR_HOME": self.tmp.name})
        entorno.start()
        self.addCleanup(entorno.stop)
        self.addCleanup(self.tmp.cleanup)

    def test_legado_sin_formato_se_migra(self):
        casa.escribir_json("proyectos.json", ["/a", 3, "/b"])
        self.assertEqual(casa.migrar()[0], 0)
        self.assertEqual(casa.leer_json("proyectos.json", None), {"proyectos": ["/a", "/b"]})
        self.assertEqual(casa.formato(), casa.FORMATO_CASA)

    def test_formato_mas_nuevo_sin_respaldo_no_toca_nada(self):
        casa.escribir_json("casa.json", {"formato": casa.FORMATO_CASA + 1})
        casa.escribir_json("proyectos.json", {"proyectos": ["/x"], "nuevo": True})
        codigo, mensaje = casa.migrar()
        self.assertEqual(codigo, casa.ar.DATOS_INCOMPATIBLES, mensaje)
        self.assertTrue(casa.leer_json("proyectos.json", {})["nuevo"])

    def test_formato_mas_nuevo_con_respaldo_compatible(self):
        casa.escribir_json("proyectos.json", {"proyectos": ["/viejo"]})
        casa.migrar()
        casa.ar.respaldar_casa(self.tmp.name)
        casa.escribir_json("casa.json", {"formato": casa.FORMATO_CASA + 1})
        casa.escribir_json("proyectos.json", {"proyectos": ["/nuevo"]})
        self.assertEqual(casa.migrar()[0], 0)
        self.assertEqual(casa.leer_json("proyectos.json", {})["proyectos"], ["/viejo"])


if __name__ == "__main__":
    unittest.main()
