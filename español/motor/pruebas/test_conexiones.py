"""Conexiones (agentes ↔ proyectos) y el servidor MCP de solo lectura."""

from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import _rutas  # noqa: F401
import conexiones
import generar
import mcp_servidor


def proyecto(raiz: Path) -> Path:
    sis = raiz / "uxyngraphar" / "sistemas-de-gobernanza" / "demo"
    sis.mkdir(parents=True)
    (sis / "sistema.json").write_text(json.dumps({"id": "demo", "version": "1.0.0", "titulo": "Demo", "descripcion": "d",
                                                  "activacion": ["demo"]}), encoding="utf-8")
    (sis / "README.md").write_text("# Demo\n", encoding="utf-8")
    (sis / "LIMITES.md").write_text("límites\n", encoding="utf-8")
    (raiz / "uxyngraphar" / "FLUJO.json").write_text('{"modo": "manual"}', encoding="utf-8")
    return raiz


class PruebasConexiones(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.inicio = base / "inicio"
        self.inicio.mkdir()
        self.p = proyecto(base / "app")
        parche = mock.patch.dict(os.environ, {"UXYNGRAPHAR_INICIO_AGENTES": str(self.inicio)})
        parche.start()
        self.addCleanup(parche.stop)
        conexiones.casa.escribir_json(conexiones.ESTADO, {})

    def test_detectar_por_carpeta(self):
        (self.inicio / ".gemini").mkdir()
        with mock.patch.object(conexiones.shutil, "which", return_value=None):
            self.assertTrue(conexiones.detectar("gemini"))
            self.assertFalse(conexiones.detectar("cursor"))

    def test_conectar_y_desconectar_respeta_lo_de_la_persona(self):
        cfg = self.p / ".mcp.json"
        cfg.write_text(json.dumps({"mcpServers": {"otro": {"command": "x"}}, "extra": 1}), encoding="utf-8")
        r = conexiones.conectar("claude", [str(self.p)])
        self.assertTrue(r[0]["mcp"].endswith(".mcp.json"))
        datos = json.loads(cfg.read_text(encoding="utf-8"))
        self.assertEqual(datos["mcpServers"]["otro"], {"command": "x"})
        self.assertEqual(datos["mcpServers"]["uxyngraphar"]["args"][-1], "mcp")
        self.assertIn(generar.INICIO, (self.p / "CLAUDE.md").read_text(encoding="utf-8"))
        resumen = {a["id"]: a for a in conexiones.resumen([str(self.p)])}
        self.assertEqual(resumen["claude"]["proyectos"], [str(self.p.resolve())])
        self.assertEqual(resumen["cursor"]["proyectos"], [])
        conexiones.desconectar("claude", [str(self.p)])
        datos = json.loads(cfg.read_text(encoding="utf-8"))
        self.assertEqual(datos, {"mcpServers": {"otro": {"command": "x"}}, "extra": 1})

    def test_gemini_crea_y_quita_su_archivo_y_copilot_usa_servers(self):
        conexiones.conectar("gemini", [str(self.p)])
        conexiones.conectar("copilot", [str(self.p)])
        self.assertIn(generar.INICIO, (self.p / "GEMINI.md").read_text(encoding="utf-8"))
        self.assertIn("uxyngraphar", json.loads((self.p / ".gemini/settings.json").read_text())["mcpServers"])
        vscode = json.loads((self.p / ".vscode/mcp.json").read_text())
        self.assertEqual(vscode["servers"]["uxyngraphar"]["type"], "stdio")
        conexiones.desconectar("gemini", [str(self.p)])
        self.assertFalse((self.p / "GEMINI.md").exists())
        self.assertFalse((self.p / ".gemini/settings.json").exists())

    def test_codex_bloque_global_marcado(self):
        toml = self.inicio / ".codex" / "config.toml"
        toml.parent.mkdir()
        toml.write_text('model = "o3"\n', encoding="utf-8")
        conexiones.conectar("codex", [str(self.p)])
        conexiones.conectar("codex", [str(self.p)])
        texto = toml.read_text(encoding="utf-8")
        self.assertEqual(texto.count("[mcp_servers.uxyngraphar]"), 1)
        self.assertTrue(texto.startswith('model = "o3"'))
        conexiones.desconectar("codex", [str(self.p)])
        self.assertEqual(toml.read_text(encoding="utf-8"), 'model = "o3"\n')

    def test_json_invalido_no_se_toca(self):
        (self.p / ".mcp.json").write_text("{roto", encoding="utf-8")
        with self.assertRaises(conexiones.ConfiguracionInvalida):
            conexiones.conectar("claude", [str(self.p)])
        self.assertEqual((self.p / ".mcp.json").read_text(encoding="utf-8"), "{roto")

    def test_sin_uxyngraphar_o_agente_desconocido(self):
        with self.assertRaises(ValueError):
            conexiones.conectar("claude", [self.tmp.name])
        with self.assertRaises(ValueError):
            conexiones.conectar("nadie", [str(self.p)])

    def test_opencode_formato_local(self):
        conexiones.conectar("opencode", [str(self.p)])
        entrada = json.loads((self.p / "opencode.json").read_text())["mcp"]["uxyngraphar"]
        self.assertEqual(entrada["type"], "local")
        self.assertEqual(entrada["command"][-1], "mcp")


class PruebasMcp(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.p = proyecto(Path(self.tmp.name) / "app")
        sub = self.p / "src" / "dentro"
        sub.mkdir(parents=True)
        parche = mock.patch.dict(os.environ, {"UXYNGRAPHAR_PROYECTO": str(sub)})
        parche.start()
        self.addCleanup(parche.stop)

    def _servir(self, *mensajes):
        salida = io.StringIO()
        mcp_servidor.servir(io.StringIO("\n".join(json.dumps(m) for m in mensajes) + "\n"), salida)
        return [json.loads(x) for x in salida.getvalue().splitlines()]

    def test_dialogo_completo(self):
        r = self._servir(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26"}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "sistemas_del_proyecto", "arguments": {}}},
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "leer_sistema", "arguments": {"id": "demo"}}},
            {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "leer_sistema", "arguments": {"id": "../fuera"}}},
            {"jsonrpc": "2.0", "id": 6, "method": "otra/cosa"},
        )
        self.assertEqual([x["id"] for x in r], [1, 2, 3, 4, 5, 6])
        self.assertEqual(r[0]["result"]["protocolVersion"], "2025-03-26")
        self.assertEqual({t["name"] for t in r[1]["result"]["tools"]}, {"buscar_sistemas", "sistemas_del_proyecto", "leer_sistema", "flujo"})
        self.assertIn('"demo"', r[2]["result"]["content"][0]["text"])
        self.assertIn("=== LIMITES.md ===", r[3]["result"]["content"][0]["text"])
        self.assertTrue(r[4]["result"]["isError"])
        self.assertEqual(r[5]["error"]["code"], -32601)

    def test_json_mal_formado(self):
        salida = io.StringIO()
        mcp_servidor.servir(io.StringIO("{no json\n"), salida)
        self.assertEqual(json.loads(salida.getvalue())["error"]["code"], -32700)


if __name__ == "__main__":
    unittest.main()
