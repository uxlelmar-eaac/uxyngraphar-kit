"""Suscripciones de IA en este equipo (ADR 0014): el kit usa la CLI oficial con tu sesión, nunca tus tokens.

Los stubs son Python (+ `.cmd` en Windows): `shutil.which` en Windows solo encuentra
ejecutables con extensión de PATHEXT, y los `#!/bin/sh` no sirven allí.
"""

from __future__ import annotations

import os
import stat
import sys
import tempfile
import time
import unittest
from pathlib import Path

import _rutas  # noqa: F401
import ia_local

# Stubs en Python (portable). Claude: lee stdin, exige cwd vacío, cuenta «Persona».
CLAUDE_PY = r"""
import os, sys
entrada = sys.stdin.read()
if any(os.scandir(".")):
    print("carpeta no vacía", file=sys.stderr)
    sys.exit(3)
print(f"eco: {entrada.count('Persona')}")
"""

# Codex: escribe la respuesta en --output-last-message y tira basura a stdout.
CODEX_PY = r"""
import sys
destino = None
args = sys.argv[1:]
i = 0
while i < len(args):
    if args[i] == "--output-last-message" and i + 1 < len(args):
        destino = args[i + 1]
        i += 2
        continue
    i += 1
sys.stdin.read()
print("registro ruidoso")
if not destino:
    sys.exit(2)
open(destino, "w", encoding="utf-8").write("respuesta final")
"""

SIN_SESION_PY = r"""
import sys
print("Error: not logged in, please run login", file=sys.stderr)
sys.exit(1)
"""


class TestSuscripcionesLocales(unittest.TestCase):
    def setUp(self):
        self.bin = tempfile.TemporaryDirectory()
        self.path = os.environ.get("PATH", "")
        os.environ["PATH"] = self.bin.name
        # Sin las CLI que traen las apps de escritorio de este equipo (p. ej. Claude Desktop): solo el PATH de la prueba.
        self.incluidas = ia_local.INCLUIDAS
        ia_local.INCLUIDAS = {}

    def tearDown(self):
        ia_local.INCLUIDAS = self.incluidas
        os.environ["PATH"] = self.path
        self.bin.cleanup()

    def test_claude_de_claude_desktop_fuera_del_path(self):
        # Claude Desktop instala Claude Code en su carpeta y no en el PATH: el Creador también debe verlo.
        app = Path(self.bin.name) / "app"
        for version in ("2.1.9", "2.1.325"):
            ruta = app / "claude-code" / version / "abc123" / ("claude.exe" if os.name == "nt" else "claude")
            ruta.parent.mkdir(parents=True)
            ruta.write_text(f"#!{sys.executable}\n" + CLAUDE_PY.lstrip("\n"), encoding="utf-8")
            ruta.chmod(ruta.stat().st_mode | stat.S_IEXEC)
        patron = str(app / "claude-code" / "*" / "*" / ("claude.exe" if os.name == "nt" else "claude"))
        ia_local.INCLUIDAS = {"claude": (patron,)}
        self.assertIn("2.1.325", ia_local.ejecutable("claude") or "")
        por_id = {s["proveedor"]: s for s in ia_local.suscripciones()["disponibles"]}
        self.assertTrue(por_id["claude"]["instalada"])
        self.assertEqual([m["proveedor"] for m in ia_local.modelos() if m.get("suscripcion")], ["claude"])
        ia_local.INCLUIDAS = {}
        self.assertIsNone(ia_local.ejecutable("claude"))

    def _cli(self, nombre: str, cuerpo_py: str):
        """Deja `nombre` en el PATH vacío de la prueba (con `.cmd` en Windows)."""
        py = Path(self.bin.name) / f"_{nombre}.py"
        py.write_text(cuerpo_py.lstrip("\n"), encoding="utf-8")
        if os.name == "nt":
            cmd = Path(self.bin.name) / f"{nombre}.cmd"
            cmd.write_text(
                f'@echo off\r\n"{sys.executable}" "{py}" %*\r\n',
                encoding="utf-8",
            )
        else:
            ruta = Path(self.bin.name) / nombre
            ruta.write_text(f"#!{sys.executable}\n" + cuerpo_py.lstrip("\n"), encoding="utf-8")
            ruta.chmod(ruta.stat().st_mode | stat.S_IEXEC)

    def test_lista_con_avisos_y_gemini_riesgo_alto(self):
        self._cli("claude", CLAUDE_PY)
        r = ia_local.suscripciones()
        por_id = {s["proveedor"]: s for s in r["disponibles"]}
        self.assertTrue(por_id["claude"]["instalada"])
        self.assertFalse(por_id["codex"]["instalada"])
        self.assertTrue(all(s["aviso"] for s in r["disponibles"]))
        self.assertEqual(por_id["gemini"]["riesgo"], "alto")
        self.assertEqual(r["no_permitidas"], [])
        self.assertEqual([m["proveedor"] for m in ia_local.modelos() if m.get("suscripcion")], ["claude"])

    def test_claude_por_la_entrada_estandar_en_carpeta_vacia(self):
        self._cli("claude", CLAUDE_PY)
        r = ia_local.completar("claude", [{"role": "user", "content": "hola"},
                                          {"role": "assistant", "content": "¿sí?"},
                                          {"role": "user", "content": "mejóralo"}], "eres útil")
        self.assertEqual(r, {"texto": "eco: 2", "modelo": "Claude Code", "proveedor": "claude"})

    def test_codex_lee_solo_el_ultimo_mensaje(self):
        self._cli("codex", CODEX_PY)
        r = ia_local.completar("codex", [{"role": "user", "content": "hola"}])
        self.assertEqual(r["texto"], "respuesta final")

    def test_sin_sesion_dice_como_iniciarla(self):
        self._cli("copilot", SIN_SESION_PY)
        with self.assertRaisesRegex(ia_local.IaNoDisponible, "copilot login"):
            ia_local.completar("copilot", [{"role": "user", "content": "hola"}])

    def test_no_instalada(self):
        with self.assertRaisesRegex(ia_local.IaNoDisponible, "no está instalada"):
            ia_local.completar("qwen", [{"role": "user", "content": "hola"}])

    def test_iniciar_sesion_cli_captura_url_codigo_y_completa(self):
        login_py = (
            "import sys, time\n"
            "print('Abre https://github.com/login/device e introduce ABCD-1234', flush=True)\n"
            "time.sleep(0.05)\n"
            "print('Sesión iniciada', flush=True)\n"
        )
        self._cli("copilot", login_py)
        abiertas = []
        original_open = ia_local.webbrowser.open
        ia_local.webbrowser.open = lambda u: (abiertas.append(u), True)[1]
        try:
            est = ia_local.iniciar_sesion_cli("copilot", abrir_navegador=True)
            for _ in range(40):
                if est["estado"] != "en_curso":
                    break
                time.sleep(0.05)
                est = ia_local.estado_sesion_cli(est["id"])
        finally:
            ia_local.webbrowser.open = original_open
        self.assertEqual(est["estado"], "listo")
        self.assertEqual(est["url"], "https://github.com/login/device")
        self.assertEqual(est["codigo"], "ABCD-1234")
        self.assertEqual(abiertas, ["https://github.com/login/device"])

    def test_suscripciones_incluye_web_y_enlaces_de_claves(self):
        r = ia_local.suscripciones()
        self.assertTrue(r["url_cuenta_ia"].endswith("/editor/cuenta/ia"))
        self.assertTrue(all(s["url_claves"].startswith("https://") for s in r["disponibles"]))
        ids_web = {w["id"] for w in r["web"]}
        self.assertTrue({"deepseek", "glm", "minimax", "ollama", "supergrok", "openrouter"}.issubset(ids_web))


if __name__ == "__main__":
    unittest.main()
