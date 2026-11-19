"""1.5.22: «quitar todo» no deja carpetas vacías de uxyngraphar, el resumen no dice «quitado de la lista» si no estaba
y la CLI enseña el plan antes del error también con la salida redirigida (encontrado probando como usuario nuevo)."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

import _rutas  # noqa: F401
import quitar_proyecto as qp
import repo
from test_quitar_y_taller_1_5_21 import SISTEMAS, ConProyecto

MOTOR = Path(__file__).resolve().parents[1]
TRABAJO = Path("uxyngraphar") / "trabajo"


class TestQuitarSinRestos(ConProyecto):
    def test_quitar_todo_no_deja_carpetas_vacias(self):
        r = self.proyecto()
        (r / TRABAJO / "pruebas-demo" / "vacia").mkdir(parents=True, exist_ok=True)
        p = qp.plan(str(r))
        self.assertIn("uxyngraphar/trabajo/ (solo carpetas vacías)", p["borrar"])
        qp.quitar(str(r), todo=True)
        self.assertFalse((r / "uxyngraphar").exists(), sorted(x.as_posix() for x in r.rglob("*")))
        self.assertEqual((r / "src" / "main.py").read_text(encoding="utf-8"), "print('mío')\n")

    def test_conserva_el_trabajo_y_las_carpetas_ajenas(self):
        r = self.proyecto()
        (r / TRABAJO / "pruebas-demo").mkdir(parents=True, exist_ok=True)
        (r / TRABAJO / "pruebas-demo" / "ficha.md").write_text("mía\n", encoding="utf-8")
        (r / SISTEMAS / "mi-carpeta").mkdir()
        (r / SISTEMAS / "mi-carpeta" / "nota.md").write_text("nota\n", encoding="utf-8")
        p = qp.plan(str(r))
        self.assertIn("uxyngraphar/trabajo/ (tu trabajo con los sistemas)", p["conservar"])
        qp.quitar(str(r), todo=True)
        self.assertEqual((r / TRABAJO / "pruebas-demo" / "ficha.md").read_text(encoding="utf-8"), "mía\n")
        self.assertEqual((r / SISTEMAS / "mi-carpeta" / "nota.md").read_text(encoding="utf-8"), "nota\n")
        self.assertFalse((r / SISTEMAS / "pruebas-demo").exists())

    def test_no_dice_quitado_de_la_lista_si_no_estaba(self):
        r = self.repo_git("suelto")
        repo.instalar(r, ["pruebas-demo"])
        res = qp.quitar(str(r), todo=True)
        self.assertIn("no estaba en la lista del panel", res["hechos"])
        self.assertNotIn("quitado de la lista del panel", res["hechos"])

    def test_cli_ensena_el_plan_antes_del_error_con_salida_redirigida(self):
        r = self.repo_git("redirigido")
        repo.instalar(r, ["pruebas-demo"])
        entorno = {**os.environ, "UXYNGRAPHAR_HOME": str(self.t / "casa"), "UXYNGRAPHAR_CATALOGO": str(self.cat),
                   "PYTHONIOENCODING": "utf-8"}
        salida = subprocess.run([sys.executable, str(MOTOR / "uxyngraphar.py"), "proyectos", "quitar", str(r), "--todo"],
                                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=entorno,
                                check=False).stdout.decode("utf-8", errors="replace")
        self.assertIn("Quitar todo lo de uxyngraphar", salida)
        self.assertIn("añade --si", salida)
        self.assertLess(salida.index("Quitar todo lo de uxyngraphar"), salida.index("error:"), salida)
        self.assertTrue((r / SISTEMAS / "pruebas-demo").is_dir(), "sin --si no se toca nada")

    def test_sin_respuesta_no_revienta_aunque_parezca_una_terminal(self):
        # En Windows, la entrada NUL dice ser una terminal: input() acaba en EOFError y antes salía una traza.
        import contextlib
        import io
        from unittest import mock

        import cli
        r = self.repo_git("windows")
        repo.instalar(r, ["pruebas-demo"])
        err = io.StringIO()
        with mock.patch.object(cli.sys.stdin, "isatty", return_value=True), \
                mock.patch("builtins.input", side_effect=EOFError), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            codigo = cli.main(["proyectos", "quitar", str(r), "--todo"])
        self.assertNotEqual(codigo, 0)
        self.assertIn("añade --si", err.getvalue())
        self.assertTrue((r / SISTEMAS / "pruebas-demo").is_dir())


class TestSalidaCortada(unittest.TestCase):
    @unittest.skipIf(sys.platform == "win32", "tubería rota: en POSIX es EPIPE seguro")
    def test_lector_que_se_va_antes_no_deja_traza(self):
        # `uxyngraphar --version | head -1`: head cierra la tubería y lo que queda por escribir no debe dar una traza.
        import uxyngraphar
        leer, escribir = os.pipe()
        os.close(leer)
        flujo = os.fdopen(escribir, "w", encoding="utf-8")
        salida = uxyngraphar._SalidaPorLineas(flujo)
        try:
            self.assertEqual(salida.write("uxyngraphar 1.5.23\n"), len("uxyngraphar 1.5.23\n"))
            salida.write("más\n")
            salida.flush()
        finally:
            flujo.close()
        self.assertTrue(salida._rota)
