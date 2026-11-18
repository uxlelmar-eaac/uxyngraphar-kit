"""Suscripciones de IA en este equipo (ADR 0014): el kit usa la CLI oficial con tu sesión, nunca tus tokens.

Los stubs son Python (+ `.cmd` en Windows): `shutil.which` en Windows solo encuentra
ejecutables con extensión de PATHEXT, y los `#!/bin/sh` no sirven allí.
"""

from __future__ import annotations

import os
import stat
import sys
import tempfile
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

    def tearDown(self):
        os.environ["PATH"] = self.path
        self.bin.cleanup()

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

    def test_lista_con_avisos_y_sin_google(self):
        self._cli("claude", CLAUDE_PY)
        r = ia_local.suscripciones()
        por_id = {s["proveedor"]: s for s in r["disponibles"]}
        self.assertTrue(por_id["claude"]["instalada"])
        self.assertFalse(por_id["codex"]["instalada"])
        self.assertTrue(all(s["aviso"] for s in r["disponibles"]))
        self.assertNotIn("gemini", por_id)
        self.assertEqual([n["id"] for n in r["no_permitidas"]], ["gemini"])
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


if __name__ == "__main__":
    unittest.main()
