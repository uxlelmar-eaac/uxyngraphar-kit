"""Conexiones: tus agentes de IA (Claude Code, Codex, Cursor, Gemini CLI, OpenCode, Grok, Copilot) y uxyngraphar.

Conectar un agente a un proyecto hace dos cosas, y desconectarlo las deshace:
1. **Instrucciones**: el bloque de uxyngraphar en el archivo que ese agente lee (CLAUDE.md, AGENTS.md, GEMINI.md o
   `.github/copilot-instructions.md`). Los tres primeros ya los escribe la instalación; GEMINI.md y el de Copilot se
   crean aquí y desde entonces las actualizaciones los mantienen.
2. **MCP**: registra `uxyngraphar mcp` (solo lectura, ver mcp_servidor.py) en la configuración MCP del agente para ese
   proyecto. Solo se toca la entrada «uxyngraphar»; el resto del archivo es de la persona. Si el archivo no es JSON
   válido, no se toca y se dice por qué.

Codex guarda su configuración MCP para todo el equipo (`~/.codex/config.toml`): ahí se añade un bloque marcado.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import casa
import generar
import herramienta

NOMBRE = "uxyngraphar"
ESTADO = "conexiones.json"
TOML_INI, TOML_FIN = "# >>> uxyngraphar (MCP)", "# <<< uxyngraphar (MCP)"

# id → nombre, cómo detectarlo, archivo de instrucciones y configuración MCP:
#   ("json", ruta en el proyecto, clave)  ·  ("opencode", ruta)  ·  ("codex", None)  ·  None (sin MCP automático)
AGENTES: dict[str, dict] = {
    "claude": {"nombre": "Claude Code", "carpetas": [".claude"], "programas": ["claude"],
               "instrucciones": "CLAUDE.md", "mcp": ("json", ".mcp.json", "mcpServers")},
    "codex": {"nombre": "Codex", "carpetas": [".codex"], "programas": ["codex"],
              "instrucciones": "AGENTS.md", "mcp": ("codex", None, None)},
    "cursor": {"nombre": "Cursor", "carpetas": [".cursor"], "programas": ["cursor", "cursor-agent"],
               "instrucciones": "AGENTS.md", "mcp": ("json", ".cursor/mcp.json", "mcpServers")},
    "gemini": {"nombre": "Gemini CLI", "carpetas": [".gemini"], "programas": ["gemini"],
               "instrucciones": "GEMINI.md", "mcp": ("json", ".gemini/settings.json", "mcpServers")},
    "opencode": {"nombre": "OpenCode", "carpetas": [".opencode", ".config/opencode"], "programas": ["opencode"],
                 "instrucciones": "AGENTS.md", "mcp": ("opencode", "opencode.json", "mcp")},
    "grok": {"nombre": "Grok CLI", "carpetas": [".grok"], "programas": ["grok"],
             "instrucciones": "AGENTS.md", "mcp": None},
    "copilot": {"nombre": "GitHub Copilot (VS Code)", "carpetas": [".vscode", ".config/Code"], "programas": ["code"],
                "instrucciones": ".github/copilot-instructions.md", "mcp": ("json", ".vscode/mcp.json", "servers")},
}


class ConfiguracionInvalida(ValueError):
    """Un archivo de configuración del agente no es JSON válido: no se toca."""


def _inicio() -> Path:
    return Path(os.environ.get("UXYNGRAPHAR_INICIO_AGENTES") or Path.home())


def _carpeta_propia(agente: str, carpeta: Path) -> bool:
    """True si la carpeta solo guarda lo que escribió uxyngraphar (~/.codex con nuestro bloque en config.toml): que
    exista no prueba que el agente esté instalado."""
    if agente != "codex" or carpeta != _toml_codex().parent:
        return False
    try:
        if any(h.name != "config.toml" for h in carpeta.iterdir()):
            return False
        toml = _toml_codex()
        return not toml.is_file() or not _sin_bloque_toml(toml.read_text(encoding="utf-8", errors="replace")).strip()
    except OSError:
        return False


def detectar(agente: str) -> bool:
    """True si el agente está en este equipo: su carpeta de configuración (si no la creamos nosotros) o su programa, en
    el PATH o dentro de su app de escritorio (Claude Code de Claude Desktop, ver `ia_local.ejecutable`)."""
    import ia_local
    datos = AGENTES[agente]
    if any((_inicio() / c).exists() and not _carpeta_propia(agente, _inicio() / c) for c in datos["carpetas"]):
        return True
    return any(ia_local.ejecutable(p) for p in datos["programas"])


def comando_mcp() -> tuple[str, list[str]]:
    """Cómo arranca un agente el servidor MCP: el lanzador instalado o, en la copia del repositorio, uxyngraphar.py."""
    lanzador = herramienta.lanzador() if herramienta.instalada() else ""
    guion = lanzador or str(Path(__file__).resolve().parent / "uxyngraphar.py")
    return sys.executable, [guion, "mcp"]


def _entrada(tipo: str) -> dict:
    exe, args = comando_mcp()
    if tipo == "opencode":
        return {"type": "local", "command": [exe, *args], "enabled": True}
    entrada = {"command": exe, "args": args}
    return {"type": "stdio", **entrada} if tipo == "vscode" else entrada


def _leer_json(ruta: Path) -> dict:
    if not ruta.is_file():
        return {}
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8") or "{}")
    except ValueError:
        raise ConfiguracionInvalida(f"{ruta} no es JSON válido: corrígelo y vuelve a conectar; uxyngraphar no lo toca") from None
    if not isinstance(datos, dict):
        raise ConfiguracionInvalida(f"{ruta} debe ser un objeto JSON; uxyngraphar no lo toca")
    return datos


def _escribir_json(ruta: Path, datos: dict) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_name(ruta.name + ".uxyn-tmp")
    temporal.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporal, ruta)


def _toml_codex() -> Path:
    return _inicio() / ".codex" / "config.toml"


def _bloque_toml() -> str:
    exe, args = comando_mcp()
    return (f"{TOML_INI}\n[mcp_servers.{NOMBRE}]\ncommand = {json.dumps(exe)}\nargs = {json.dumps(args)}\n{TOML_FIN}\n")


def _sin_bloque_toml(texto: str) -> str:
    if TOML_INI not in texto or TOML_FIN not in texto:
        return texto
    antes, _, resto = texto.partition(TOML_INI)
    _, _, despues = resto.partition(TOML_FIN)
    resto_texto = (antes.rstrip("\n") + "\n" + despues.lstrip("\n")).strip("\n")
    return resto_texto + "\n" if resto_texto else ""


def _mcp_conectado(agente: str, proyecto: Path) -> bool | None:
    mcp = AGENTES[agente]["mcp"]
    if not mcp:
        return None
    tipo, rel, clave = mcp
    if tipo == "codex":
        ruta = _toml_codex()
        return ruta.is_file() and TOML_INI in ruta.read_text(encoding="utf-8")
    try:
        datos = _leer_json(proyecto / rel)
    except ConfiguracionInvalida:
        return False
    return NOMBRE in (datos.get(clave) or {})


def _poner_mcp(agente: str, proyecto: Path) -> str | None:
    mcp = AGENTES[agente]["mcp"]
    if not mcp:
        return None
    tipo, rel, clave = mcp
    if tipo == "codex":
        ruta = _toml_codex()
        texto = ruta.read_text(encoding="utf-8") if ruta.is_file() else ""
        nuevo = _sin_bloque_toml(texto).rstrip("\n")
        nuevo = (nuevo + "\n\n" if nuevo else "") + _bloque_toml()
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(nuevo, encoding="utf-8")
        return str(ruta)
    ruta = proyecto / rel
    datos = _leer_json(ruta)
    seccion = datos.get(clave)
    if seccion is not None and not isinstance(seccion, dict):
        raise ConfiguracionInvalida(f"{ruta}: «{clave}» debe ser un objeto; uxyngraphar no lo toca")
    datos[clave] = {**(seccion or {}), NOMBRE: _entrada("vscode" if agente == "copilot" else tipo)}
    _escribir_json(ruta, datos)
    return str(ruta)


def _quitar_mcp(agente: str, proyecto: Path, quedan_otros: bool) -> None:
    mcp = AGENTES[agente]["mcp"]
    if not mcp:
        return
    tipo, rel, clave = mcp
    if tipo == "codex":
        ruta = _toml_codex()
        if not quedan_otros and ruta.is_file():
            resto = _sin_bloque_toml(ruta.read_text(encoding="utf-8"))
            if resto.strip():
                ruta.write_text(resto, encoding="utf-8")
            else:   # solo tenía nuestro bloque: no se deja un config.toml vacío (ni la carpeta, si quedó vacía)
                ruta.unlink()
                if not any(ruta.parent.iterdir()):
                    ruta.parent.rmdir()
        return
    ruta = proyecto / rel
    if not ruta.is_file():
        return
    datos = _leer_json(ruta)
    seccion = datos.get(clave)
    if isinstance(seccion, dict) and NOMBRE in seccion:
        del seccion[NOMBRE]
        if not seccion:
            del datos[clave]
        if datos:
            _escribir_json(ruta, datos)
        else:
            ruta.unlink()


def _poner_instrucciones(agente: str, proyecto: Path) -> str:
    rel = AGENTES[agente]["instrucciones"]
    ruta = proyecto / rel
    if ruta.is_symlink():
        return str(ruta)
    actual = ruta.read_text(encoding="utf-8") if ruta.is_file() else ""
    nuevo = generar.insertar_bloque(actual, generar.instalados(proyecto))
    if nuevo != actual:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(nuevo, encoding="utf-8")
    return str(ruta)


def _quitar_instrucciones(agente: str, proyecto: Path) -> None:
    rel = AGENTES[agente]["instrucciones"]
    if rel in generar.ARCHIVOS_AGENTE:
        return   # los mantiene la instalación de uxyngraphar (los usan varios agentes)
    ruta = proyecto / rel
    if ruta.is_file() and not ruta.is_symlink():
        resto = generar.quitar_bloque(ruta.read_text(encoding="utf-8"))
        if resto.strip():
            ruta.write_text(resto, encoding="utf-8")
        else:
            ruta.unlink()


def _estado() -> dict:
    datos = casa.leer_json(ESTADO, {})
    return datos if isinstance(datos, dict) else {}


def _comprobar(agente: str, proyectos: list[str]) -> list[Path]:
    if agente not in AGENTES:
        raise ValueError(f"agente desconocido: {agente}")
    salida = []
    for p in proyectos:
        ruta = Path(p).expanduser().resolve()
        if not (ruta / generar.base.CARPETA_RAIZ).is_dir():
            raise ValueError(f"{ruta}: no tiene uxyngraphar; instala algún sistema antes de conectar agentes")
        salida.append(ruta)
    return salida


def conectar(agente: str, proyectos: list[str]) -> list[dict]:
    hechos = []
    estado = _estado()
    for proyecto in _comprobar(agente, proyectos):
        instrucciones = _poner_instrucciones(agente, proyecto)
        mcp = _poner_mcp(agente, proyecto)
        conocidos = estado.setdefault(agente, [])
        if str(proyecto) not in conocidos:
            conocidos.append(str(proyecto))
        hechos.append({"proyecto": str(proyecto), "instrucciones": instrucciones, "mcp": mcp})
    casa.escribir_json(ESTADO, estado)
    return hechos


def desconectar(agente: str, proyectos: list[str]) -> list[str]:
    estado = _estado()
    conocidos = estado.get(agente, [])
    hechos = []
    for proyecto in _comprobar(agente, proyectos):
        restantes = [p for p in conocidos if p != str(proyecto)]
        _quitar_mcp(agente, proyecto, quedan_otros=bool(restantes))
        _quitar_instrucciones(agente, proyecto)
        conocidos = restantes
        hechos.append(str(proyecto))
    estado[agente] = conocidos
    casa.escribir_json(ESTADO, estado)
    return hechos


def retirar_proyecto(proyecto: Path) -> tuple[list[str], list[str]]:
    """Desconecta todos los agentes de un proyecto que se desinstala: la entrada MCP de cada configuración, los bloques
    de GEMINI.md y de Copilot, y el bloque global de Codex si ya no queda otro proyecto conectado. (hechos, problemas)."""
    proyecto = Path(proyecto).resolve()
    estado = _estado()
    hechos: list[str] = []
    problemas: list[str] = []
    for agente, datos in AGENTES.items():
        conocidos = [p for p in estado.get(agente, []) if p != str(proyecto)]
        mcp = datos["mcp"]
        try:
            if mcp and mcp[0] == "codex":
                if str(proyecto) in estado.get(agente, []) and not conocidos and _mcp_conectado(agente, proyecto):
                    _quitar_mcp(agente, proyecto, quedan_otros=False)
                    hechos.append(f"{datos['nombre']}: bloque MCP retirado de {_toml_codex()}")
            elif mcp and _mcp_conectado(agente, proyecto):
                _quitar_mcp(agente, proyecto, quedan_otros=bool(conocidos))
                hechos.append(f"{datos['nombre']}: MCP retirado de {mcp[1]}")
            inst = proyecto / datos["instrucciones"]
            if datos["instrucciones"] not in generar.ARCHIVOS_AGENTE and inst.is_file() and \
                    generar.INICIO in inst.read_text(encoding="utf-8", errors="replace"):
                _quitar_instrucciones(agente, proyecto)
                hechos.append(f"{datos['nombre']}: bloque retirado de {datos['instrucciones']}")
        except (ConfiguracionInvalida, OSError) as e:
            problemas.append(f"{datos['nombre']}: {e}")
        if agente in estado:
            estado[agente] = conocidos
    casa.escribir_json(ESTADO, estado)
    return hechos, problemas


def restos(proyecto: Path) -> list[str]:
    """Lo que aún conecta el proyecto con uxyngraphar a través de los agentes (comprobación final de la desinstalación)."""
    proyecto = Path(proyecto)
    salida = set()
    for agente, datos in AGENTES.items():
        mcp = datos["mcp"]
        if mcp and mcp[0] != "codex" and _mcp_conectado(agente, proyecto):
            salida.add(f"entrada MCP «{NOMBRE}» en {mcp[1]}")
        inst = proyecto / datos["instrucciones"]
        if inst.is_file() and not inst.is_symlink() and generar.INICIO in inst.read_text(encoding="utf-8", errors="replace"):
            salida.add(f"bloque de uxyngraphar en {datos['instrucciones']}")
    return sorted(salida)


def codex_huerfano() -> bool:
    """True si ~/.codex/config.toml conserva nuestro bloque MCP sin ningún proyecto conectado a Codex."""
    ruta = _toml_codex()
    return ruta.is_file() and TOML_INI in ruta.read_text(encoding="utf-8", errors="replace") and not _estado().get("codex")


def resumen(proyectos: list[str]) -> list[dict]:
    """Cada agente: si está en este equipo y en qué proyectos está conectado (mirando los archivos, no solo el estado)."""
    salida = []
    estado = _estado()
    for clave, datos in AGENTES.items():
        conectados = []
        for p in proyectos:
            ruta = Path(p).expanduser().resolve()
            if str(ruta) not in estado.get(clave, []) or not (ruta / generar.base.CARPETA_RAIZ).is_dir():
                continue
            inst = ruta / datos["instrucciones"]
            tiene_instr = inst.is_file() and generar.INICIO in inst.read_text(encoding="utf-8", errors="replace")
            if tiene_instr and _mcp_conectado(clave, ruta) is not False:
                conectados.append(str(ruta))
        salida.append({"id": clave, "nombre": datos["nombre"], "detectado": detectar(clave),
                       "instrucciones": datos["instrucciones"], "mcp": bool(datos["mcp"]),
                       "proyectos": conectados})
    return salida


def mcp_manual() -> dict:
    """Lo que hay que pegar en la configuración de un agente sin conexión automática."""
    exe, args = comando_mcp()
    return {"command": exe, "args": args}
