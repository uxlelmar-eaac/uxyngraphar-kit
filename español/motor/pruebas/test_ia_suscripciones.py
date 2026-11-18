"""Suscripciones de IA en este equipo (ADR 0014): el kit usa la CLI oficial con tu sesión, nunca tus tokens."""

from __future__ import annotations

import os
import stat
import tempfile
import unittest
from pathlib import Path

import _rutas  # noqa: F401
import ia_local

CLAUDE = """#!/bin/sh
# Simula «claude -p» (rutas absolutas: el PATH de la prueba solo tiene las CLI simuladas).: responde con lo que recibe y comprueba que corre en una carpeta vacía.
entrada=$(/bin/cat)
[ -z "$(/bin/ls -A .)" ] || { echo "carpeta no vacía" >&2; exit 3; }
echo "eco: $(printf '%s' "$entrada" | /usr/bin/grep -c 'Persona')"
"""

CODEX = """#!/bin/sh
# Simula «codex exec … --output-last-message ARCHIVO -»: el registro va a stdout y la respuesta al archivo.
while [ $# -gt 0 ]; do
  if [ "$1" = "--output-last-message" ]; then shift; destino=$1; fi
  shift
done
/bin/cat > /dev/null
echo "registro ruidoso"
printf 'respuesta final' > "$destino"
"""

SIN_SESION = """#!/bin/sh
echo "Error: not logged in, please run login" >&2
exit 1
"""


class TestSuscripcionesLocales(unittest.TestCase):
    def setUp(self):
        self.bin = tempfile.TemporaryDirectory()
        self.path = os.environ.get("PATH", "")
        os.environ["PATH"] = self.bin.name

    def tearDown(self):
        os.environ["PATH"] = self.path
        self.bin.cleanup()

    def _cli(self, nombre: str, guion: str):
        ruta = Path(self.bin.name) / nombre
        ruta.write_text(guion)
        ruta.chmod(ruta.stat().st_mode | stat.S_IEXEC)

    def test_lista_con_avisos_y_sin_google(self):
        self._cli("claude", CLAUDE)
        r = ia_local.suscripciones()
        por_id = {s["proveedor"]: s for s in r["disponibles"]}
        self.assertTrue(por_id["claude"]["instalada"])
        self.assertFalse(por_id["codex"]["instalada"])
        self.assertTrue(all(s["aviso"] for s in r["disponibles"]))
        self.assertNotIn("gemini", por_id)
        self.assertEqual([n["id"] for n in r["no_permitidas"]], ["gemini"])
        self.assertEqual([m["proveedor"] for m in ia_local.modelos() if m.get("suscripcion")], ["claude"])

    def test_claude_por_la_entrada_estandar_en_carpeta_vacia(self):
        self._cli("claude", CLAUDE)
        r = ia_local.completar("claude", [{"role": "user", "content": "hola"},
                                          {"role": "assistant", "content": "¿sí?"},
                                          {"role": "user", "content": "mejóralo"}], "eres útil")
        self.assertEqual(r, {"texto": "eco: 2", "modelo": "Claude Code", "proveedor": "claude"})

    def test_codex_lee_solo_el_ultimo_mensaje(self):
        self._cli("codex", CODEX)
        r = ia_local.completar("codex", [{"role": "user", "content": "hola"}])
        self.assertEqual(r["texto"], "respuesta final")

    def test_sin_sesion_dice_como_iniciarla(self):
        self._cli("copilot", SIN_SESION)
        with self.assertRaisesRegex(ia_local.IaNoDisponible, "copilot login"):
            ia_local.completar("copilot", [{"role": "user", "content": "hola"}])

    def test_no_instalada(self):
        with self.assertRaisesRegex(ia_local.IaNoDisponible, "no está instalada"):
            ia_local.completar("qwen", [{"role": "user", "content": "hola"}])


if __name__ == "__main__":
    unittest.main()
