"""uxyngraphar como servidor MCP (stdio) para tus agentes: Claude Code, Codex, Cursor, Gemini CLI, OpenCode, Copilot…

Solo lectura: buscar sistemas en el catálogo, ver los del proyecto, leer uno y consultar el flujo. Instalar, quitar o
cambiar el flujo lo decide la persona desde el panel (regla 4 del bloque de AGENTES.md), así que no hay herramientas
para eso. Se arranca con `uxyngraphar mcp` desde la carpeta del proyecto (los agentes lo hacen solos).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import especificacion as esp
import generar
import remoto

base = esp.base
PROTOCOLO = "2025-06-18"
MAX_TEXTO = 60_000
LECTURAS = ("README.md", "SISTEMA.md", "LIMITES.md", "PERMISOS.md", "MEMORIAS.md")

HERRAMIENTAS = [
    {"name": "buscar_sistemas", "description": "Busca sistemas de gobernanza en el catálogo de uxyngraphar por el problema que resuelven.",
     "inputSchema": {"type": "object", "properties": {"texto": {"type": "string", "description": "Qué problema quieres resolver"}},
                     "required": ["texto"]}},
    {"name": "sistemas_del_proyecto", "description": "Sistemas de gobernanza instalados en este proyecto, con sus frases de activación.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "leer_sistema", "description": "Lee un sistema instalado en el proyecto: README, alcance, límites, permisos y memorias.",
     "inputSchema": {"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]}},
    {"name": "flujo", "description": "Cómo quiere trabajar la persona en este proyecto (uxyngraphar/FLUJO.json).",
     "inputSchema": {"type": "object", "properties": {}}},
]


def raiz_proyecto(desde: Path | None = None) -> Path | None:
    """La carpeta más cercana (hacia arriba) que tiene `uxyngraphar/`."""
    actual = (desde or Path(os.environ.get("UXYNGRAPHAR_PROYECTO") or os.getcwd())).resolve()
    for carpeta in (actual, *actual.parents):
        if (carpeta / base.CARPETA_RAIZ).is_dir():
            return carpeta
    return None


def _proyecto() -> Path:
    raiz = raiz_proyecto()
    if not raiz:
        raise ValueError("Esta carpeta no tiene uxyngraphar: la persona puede instalar sistemas desde el panel.")
    return raiz


def llamar(nombre: str, argumentos: dict) -> str:
    if nombre == "buscar_sistemas":
        texto = str(argumentos.get("texto") or "")[:200]
        encontrados = remoto.buscar(texto)[:15]
        return json.dumps([{k: s.get(k) for k in ("editor", "id", "titulo", "descripcion", "familia", "version")} for s in encontrados],
                          ensure_ascii=False, indent=1)
    if nombre == "sistemas_del_proyecto":
        return json.dumps([{k: m.get(k) for k in ("id", "titulo", "descripcion", "version", "activacion")}
                           for m in generar.instalados(_proyecto())], ensure_ascii=False, indent=1)
    if nombre == "leer_sistema":
        pid = str(argumentos.get("id") or "")
        carpeta = _proyecto() / base.CARPETA_SISTEMAS_DE_GOBERNANZA / pid
        if not pid or "/" in pid or "\\" in pid or pid.startswith(".") or not (carpeta / base.MANIFIESTO).is_file():
            raise ValueError(f"No hay un sistema «{pid}» instalado en este proyecto.")
        partes = [f"=== {n} ===\n{(carpeta / n).read_text(encoding='utf-8')}" for n in LECTURAS if (carpeta / n).is_file()]
        return "\n\n".join(partes)[:MAX_TEXTO]
    if nombre == "flujo":
        return json.dumps(generar.leer_flujo(_proyecto()), ensure_ascii=False, indent=1)
    raise ValueError(f"Herramienta desconocida: {nombre}")


def responder(mensaje: dict) -> dict | None:
    """Una petición JSON-RPC → su respuesta (None para notificaciones)."""
    metodo, ident = mensaje.get("method"), mensaje.get("id")
    if ident is None:
        return None
    resultado: dict
    if metodo == "initialize":
        resultado = {"protocolVersion": (mensaje.get("params") or {}).get("protocolVersion") or PROTOCOLO,
                     "capabilities": {"tools": {}},
                     "serverInfo": {"name": "uxyngraphar", "version": esp.VERSION_MOTOR}}
    elif metodo == "ping":
        resultado = {}
    elif metodo == "tools/list":
        resultado = {"tools": HERRAMIENTAS}
    elif metodo == "tools/call":
        params = mensaje.get("params") or {}
        try:
            texto = llamar(str(params.get("name")), params.get("arguments") or {})
            resultado = {"content": [{"type": "text", "text": texto}], "isError": False}
        except (ValueError, OSError, remoto.SinServidor, LookupError) as e:
            resultado = {"content": [{"type": "text", "text": str(e)}], "isError": True}
    else:
        return {"jsonrpc": "2.0", "id": ident, "error": {"code": -32601, "message": f"método no soportado: {metodo}"}}
    return {"jsonrpc": "2.0", "id": ident, "result": resultado}


def servir(entrada=None, salida=None) -> int:
    entrada = entrada or sys.stdin
    salida = salida or sys.stdout
    for linea in entrada:
        if not linea.strip():
            continue
        respuesta: dict | None
        try:
            mensaje = json.loads(linea)
        except ValueError:
            respuesta = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "JSON no válido"}}
        else:
            respuesta = responder(mensaje) if isinstance(mensaje, dict) else None
        if respuesta is not None:
            salida.write(json.dumps(respuesta, ensure_ascii=False) + "\n")
            salida.flush()
    return 0
