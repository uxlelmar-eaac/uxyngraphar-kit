"""IA del Creador local (ADR 0013 y 0014): modelos de este equipo, tus suscripciones o la clave de tu cuenta.

- Locales: solo `http://127.0.0.1` / `localhost`. Nada sale del equipo y no hace falta clave.
- Suscripciones en este equipo (ADR 0014): el kit le pide la respuesta a la CLI oficial del proveedor (Claude Code,
  Codex, Copilot CLI, Qwen Code) con la sesión que ya tienes en ella. El kit nunca lee ni copia sus tokens: la
  suscripción no sale de tu ordenador. Cada una lleva su aviso honesto de términos (`SUSCRIPCIONES`). Google AI
  Pro/Ultra no se ofrece: sus términos prohíben usarlo desde software de terceros, aunque sea envolviendo su CLI.
- «servidor»: el kit pide `POST /me/ia/completar` con la sesión del equipo; el servidor usa tu clave o suscripción
  por defecto (cifrada allí, nunca llega a este equipo) y anota el uso en «IA y conexiones».

Las respuestas son texto: quien llama (panel) decide qué hacer con él; nunca se escribe nada sin que la persona acepte.
"""

from __future__ import annotations

import glob
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request

import remoto

SEGUNDOS_SONDEO = 1.5
SEGUNDOS_RESPUESTA = 180
MAX_CARACTERES = 200_000
LOCALES = {
    "ollama": os.environ.get("UXYNGRAPHAR_OLLAMA_URL", "http://127.0.0.1:11434"),
    "lmstudio": os.environ.get("UXYNGRAPHAR_LMSTUDIO_URL", "http://127.0.0.1:1234"),
}
# Suscripciones que se usan en este equipo a través de la CLI oficial (revisado el 2026-11-18). `orden` recibe el
# texto por la entrada estándar; `salida` = "archivo" si la CLI escribe el último mensaje en un archivo aparte.
SUSCRIPCIONES = {
    "claude": {
        "nombre": "Claude Code", "planes": "Claude Pro o Max", "cli": "claude", "iniciar": "claude  (luego /login)",
        "orden": ["claude", "-p", "--output-format", "text"], "salida": "stdout", "riesgo": "medio",
        "aviso": ("Anthropic solo permite el inicio de sesión de Pro y Max dentro de Claude Code y Claude.ai. Aquí es tu "
                  "Claude Code quien habla con Anthropic (en modo no interactivo, `claude -p`) y gasta de tu plan; el kit "
                  "nunca toca tus tokens. Si quieres evitar cualquier duda, usa una clave de API de Anthropic en tu cuenta."),
    },
    "codex": {
        "nombre": "Codex", "planes": "ChatGPT Go, Plus o Pro", "cli": "codex", "iniciar": "codex login",
        "orden": ["codex", "exec", "--skip-git-repo-check", "--sandbox", "read-only", "--output-last-message",
                  "{salida}", "-"], "salida": "archivo", "riesgo": "bajo",
        "aviso": ("OpenAI deja usar tu plan de ChatGPT en proyectos locales con «Sign in with ChatGPT». Aquí es tu Codex "
                  "quien hace la llamada en tu equipo y gasta de los límites de tu plan."),
    },
    "copilot": {
        "nombre": "GitHub Copilot CLI", "planes": "Copilot Pro, Pro+ o Business", "cli": "copilot",
        "iniciar": "copilot login", "orden": ["copilot", "-p", "{texto}", "--silent"], "salida": "stdout",
        "riesgo": "medio",
        "aviso": ("GitHub solo tiene un acuerdo formal para usar Copilot desde OpenCode. Aquí es tu Copilot CLI oficial quien "
                  "responde, con tu sesión y en tu equipo, y gasta tus peticiones premium. Si quieres evitar cualquier "
                  "duda, usa una clave de API."),
    },
    "qwen": {
        "nombre": "Qwen Code", "planes": "Alibaba Cloud Coding Plan", "cli": "qwen", "iniciar": "qwen  (luego /auth)",
        "orden": ["qwen", "-p", "Responde a lo que llega por la entrada estándar."], "salida": "stdout",
        "riesgo": "bajo",
        "aviso": ("El acceso gratuito con Qwen OAuth cerró el 15 de abril de 2026: configura en Qwen Code la clave de tu "
                  "Coding Plan (empieza por «sk-sp-»), pensada para herramientas de programación."),
    },
}
# Lo que no se ofrece y por qué (se muestra en el panel para que nadie lo busque).
NO_PERMITIDAS = {
    "gemini": ("Google AI Pro o Ultra (Gemini CLI / Antigravity)",
               "Los términos de Antigravity prohíben entrar con software de terceros, aunque sea envolviendo su CLI, y "
               "Google ha suspendido cuentas por ello. Usa una clave de Google AI Studio en tu cuenta."),
}
PROVEEDORES = ("servidor", *LOCALES, *SUSCRIPCIONES)
# CLI que una app de escritorio trae dentro sin ponerla en el PATH. Claude Desktop instala Claude Code en su propia
# carpeta (`claude-code/<versión>/<id>/claude`); si solo tienes la app, `shutil.which("claude")` no la encuentra.
# Por orden de preferencia; dentro de cada patrón gana la versión más alta.
INCLUIDAS = {
    "claude": (
        "~/.config/Claude/claude-code/*/*/claude",
        "~/Library/Application Support/Claude/claude-code/*/*/claude",
        "~/AppData/Roaming/Claude/claude-code/*/*/claude.exe",
        "~/.claude/local/claude",
        "~/.config/Claude/claude-code-vm/*/claude",
    ),
}
SEGUNDOS_CLI = 300
MAX_ARGUMENTO = 100_000


_SIN_IA = re.compile(r"a[ñn]ade una clave de ia|sin (ninguna )?clave de ia|no hay ninguna ia", re.IGNORECASE)
AYUDA_SIN_IA = (
    "uxyn necesita una IA. Opciones (no se compra ni se guarda nada desde aquí):\n"
    "  · Clave de IA en tu cuenta: en la web de uxyngraphar, Cuenta → IA y conexiones (se guarda cifrada en el servidor).\n"
    "  · Un modelo en este equipo, sin clave: Ollama (http://127.0.0.1:11434) o LM Studio (http://127.0.0.1:1234) "
    "con un modelo descargado.\n"
    "  · Tu suscripción con su CLI oficial instalada y la sesión iniciada: Claude Code, Codex, GitHub Copilot CLI o "
    "Qwen Code.\n"
    "Qué hay disponible ahora en este equipo: «uxyngraphar creador modelos» (y, en el panel, Conexiones).")


def ayuda_sin_ia(mensaje: str) -> str:
    """Las opciones concretas cuando el error es que no hay ninguna IA; vacío si el error es otro."""
    return AYUDA_SIN_IA if _SIN_IA.search(str(mensaje or "")) else ""


class IaNoDisponible(remoto.SinServidor):
    """El proveedor elegido no responde o rechazó la petición."""


def _version_ruta(ruta: str) -> tuple[int, ...]:
    """La versión que aparece en la ruta (p. ej. `.../claude-code/2.1.325/...` → (2, 1, 325)); () si no hay."""
    for parte in reversed(re.split(r"[\\/]", ruta)):
        if re.fullmatch(r"\d+(\.\d+)+", parte):
            return tuple(int(n) for n in parte.split("."))
    return ()


def ejecutable(cli: str) -> str | None:
    """Ruta de la CLI: la del PATH o, si no está, la que trae dentro su app de escritorio (`INCLUIDAS`)."""
    exe = shutil.which(cli)
    if exe is not None:
        return exe
    for patron in INCLUIDAS.get(cli, ()):
        candidatos = [r for r in glob.glob(os.path.expanduser(patron))
                      if os.path.isfile(r) and (os.name == "nt" or os.access(r, os.X_OK))]
        if candidatos:
            return max(candidatos, key=lambda r: (_version_ruta(r), r))
    return None


def _url_local(proveedor: str) -> str:
    url = LOCALES[proveedor].rstrip("/")
    host = urllib.parse.urlparse(url).hostname
    if urllib.parse.urlparse(url).scheme != "http" or host not in ("127.0.0.1", "localhost", "::1"):
        raise ValueError(f"{proveedor}: solo se admiten direcciones locales (http://127.0.0.1:…)")
    return url


def _pedir(url: str, cuerpo: dict | None, segundos: float) -> dict:
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    pedido = urllib.request.Request(url, data=datos, method="POST" if datos else "GET",  # noqa: S310 - solo localhost
                                    headers={"Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(pedido, timeout=segundos) as r:  # noqa: S310 - solo localhost
            return json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        e.close()
        raise IaNoDisponible(f"{url}: HTTP {e.code}") from None
    except (urllib.error.URLError, OSError, ValueError) as e:
        raise IaNoDisponible(f"{url}: no responde ({getattr(e, 'reason', e)})") from None


def modelos() -> list[dict]:
    """Modelos locales que responden ahora mismo y suscripciones con su CLI instalada: [{proveedor, modelo, ...}]."""
    salida = []
    try:
        for m in _pedir(_url_local("ollama") + "/api/tags", None, SEGUNDOS_SONDEO).get("models", []):
            if isinstance(m, dict) and isinstance(m.get("name"), str):
                salida.append({"proveedor": "ollama", "modelo": m["name"]})
    except (IaNoDisponible, ValueError):
        pass
    try:
        for m in _pedir(_url_local("lmstudio") + "/v1/models", None, SEGUNDOS_SONDEO).get("data", []):
            if isinstance(m, dict) and isinstance(m.get("id"), str):
                salida.append({"proveedor": "lmstudio", "modelo": m["id"]})
    except (IaNoDisponible, ValueError):
        pass
    salida += [{"proveedor": p, "modelo": "", "nombre": s["nombre"], "suscripcion": True, "riesgo": s["riesgo"]}
               for p, s in SUSCRIPCIONES.items() if ejecutable(s["cli"]) is not None]
    return salida


def suscripciones() -> dict:
    """Suscripciones de este equipo: si su CLI está instalada, cómo iniciar sesión y su aviso de términos."""
    return {
        "revisado": "2026-11-18",
        "disponibles": [{"proveedor": p, "nombre": s["nombre"], "planes": s["planes"], "cli": s["cli"],
                         "instalada": ejecutable(s["cli"]) is not None, "iniciar_sesion": s["iniciar"],
                         "riesgo": s["riesgo"], "aviso": s["aviso"]} for p, s in SUSCRIPCIONES.items()],
        "no_permitidas": [{"id": k, "nombre": n, "motivo": m} for k, (n, m) in NO_PERMITIDAS.items()],
    }


def _plano(todos: list[dict]) -> str:
    """Una conversación en texto para las CLI (solo aceptan una instrucción)."""
    partes = []
    for m in todos:
        titulo = {"system": "Instrucciones", "user": "Persona", "assistant": "Tú (antes)"}[m["role"]]
        partes.append(f"## {titulo}\n{m['content']}")
    partes.append("Responde ahora solo con tu siguiente mensaje para la persona, en texto, sin usar herramientas.")
    return "\n\n".join(partes)


def _cli(proveedor: str, texto: str) -> str:
    """Ejecuta la CLI oficial en una carpeta vacía y temporal (no ve tus proyectos) y devuelve su respuesta."""
    s = SUSCRIPCIONES[proveedor]
    exe = ejecutable(s["cli"])
    if exe is None:
        raise IaNoDisponible(f"{s['nombre']}: no está instalada en este equipo («{s['cli']}» no aparece en el PATH ni dentro de su app de escritorio)")
    usa_argumento = "{texto}" in s["orden"]
    if usa_argumento and len(texto) > MAX_ARGUMENTO:
        raise ValueError(f"{s['nombre']}: la conversación es demasiado larga para pasarla a la CLI")
    with tempfile.TemporaryDirectory(prefix="uxyngraphar-ia-") as carpeta:
        salida = os.path.join(carpeta, "respuesta.txt")
        # Ruta absoluta de la CLI: en Windows las de npm suelen ser `.cmd` y CreateProcess
        # no las lanza sin `cmd /c` (WinError 2).
        orden = [exe if a == s["cli"] else salida if a == "{salida}" else texto if a == "{texto}" else a
                 for a in s["orden"]]
        if os.name == "nt" and exe.lower().endswith((".cmd", ".bat")):
            orden = ["cmd.exe", "/c", *orden]
        try:
            r = subprocess.run(orden, input=None if usa_argumento else texto, capture_output=True, text=True,  # noqa: S603
                               cwd=carpeta, timeout=SEGUNDOS_CLI, check=False)
        except subprocess.TimeoutExpired:
            raise IaNoDisponible(f"{s['nombre']}: no respondió en {SEGUNDOS_CLI} s") from None
        except OSError as e:
            raise IaNoDisponible(f"{s['nombre']}: no se pudo ejecutar ({e})") from None
        respuesta = r.stdout
        if s["salida"] == "archivo" and os.path.exists(salida):
            with open(salida, encoding="utf-8") as f:
                respuesta = f.read()
    if r.returncode != 0:
        detalle = (r.stderr or r.stdout or "").strip().splitlines()[-1:] or [f"código {r.returncode}"]
        pista = f" ¿Iniciaste sesión? Ejecuta: {s['iniciar']}" if any(
            w in detalle[0].lower() for w in ("login", "auth", "sesión", "401", "403", "credential")) else ""
        raise IaNoDisponible(f"{s['nombre']}: {detalle[0][:200]}{pista}")
    if not respuesta.strip():
        raise IaNoDisponible(f"{s['nombre']}: respuesta vacía")
    return respuesta.strip()


def _mensajes(sistema: str, mensajes: list[dict]) -> list[dict]:
    limpios = [{"role": m["role"], "content": str(m["content"])} for m in mensajes
               if isinstance(m, dict) and m.get("role") in ("user", "assistant") and m.get("content")]
    if not limpios:
        raise ValueError("falta el mensaje")
    if sum(len(m["content"]) for m in limpios) + len(sistema) > MAX_CARACTERES:
        raise ValueError("la conversación es demasiado larga")
    return ([{"role": "system", "content": sistema}] if sistema else []) + limpios


def completar(proveedor: str, mensajes: list[dict], sistema: str = "", modelo: str = "") -> dict:
    """Respuesta completa del modelo: {texto, modelo, proveedor}."""
    if proveedor not in PROVEEDORES:
        raise ValueError(f"proveedor: uno de {', '.join(PROVEEDORES)}")
    if proveedor == "servidor":
        cuerpo = {"mensajes": [{"rol": m["role"], "contenido": m["content"]} for m in _mensajes("", mensajes)],
                  **({"sistema": sistema} if sistema else {}), **({"modelo": modelo} if modelo else {}),
                  "proposito": "creador-local"}
        codigo, r = remoto._pedir_json("/me/ia/completar", cuerpo, con_sesion=True, segundos=SEGUNDOS_RESPUESTA)
        if codigo == 401:
            raise PermissionError(remoto._mensaje(r, "sin sesión: uxyngraphar iniciar-sesion"))
        if codigo >= 400:
            raise IaNoDisponible(remoto._mensaje(r, f"el servidor respondió HTTP {codigo}"))
        return {"texto": str(r.get("texto", "")), "modelo": str(r.get("modelo", "")), "proveedor": "servidor"}
    todos = _mensajes(sistema, mensajes)
    if proveedor in SUSCRIPCIONES:
        return {"texto": _cli(proveedor, _plano(todos)), "modelo": SUSCRIPCIONES[proveedor]["nombre"],
                "proveedor": proveedor}
    if not modelo:
        raise ValueError("elige un modelo local")
    if proveedor == "ollama":
        r = _pedir(_url_local("ollama") + "/api/chat", {"model": modelo, "messages": todos, "stream": False},
                   SEGUNDOS_RESPUESTA)
        texto = (r.get("message") or {}).get("content", "")
    else:
        r = _pedir(_url_local("lmstudio") + "/v1/chat/completions", {"model": modelo, "messages": todos, "stream": False},
                   SEGUNDOS_RESPUESTA)
        texto = ((r.get("choices") or [{}])[0].get("message") or {}).get("content", "")
    if not isinstance(texto, str) or not texto.strip():
        raise IaNoDisponible(f"{proveedor}: respuesta vacía")
    return {"texto": texto, "modelo": modelo, "proveedor": proveedor}


INSTRUCCIONES_MEJORAR = (
    "Eres el asistente del Creador de uxyngraphar. Mejoras un archivo de un sistema de gobernanza (protocolo del kit). "
    "Devuelve SOLO el contenido completo del archivo mejorado, sin explicaciones ni bloques ```. Conserva el formato "
    "(Markdown o JSON válido), los identificadores, los marcadores de fichas y el frontmatter.")

INSTRUCCIONES_REVISAR = (
    "Eres revisor de sistemas de gobernanza de uxyngraphar. Lee los archivos y devuelve un informe breve en Markdown: "
    "«Problemas» (lo que impide usarlo bien) y «Sugerencias» (mejoras), cada punto con el archivo afectado.")


def sin_cercas(texto: str) -> str:
    """Quita una cerca ``` envolvente si el modelo la añadió pese a las instrucciones."""
    t = texto.strip()
    if t.startswith("```") and t.endswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else ""
        t = t.rsplit("```", 1)[0]
    return t.rstrip() + "\n"


def mejorar(proveedor: str, modelo: str, ruta: str, contenido: str, instruccion: str) -> dict:
    pedido = f"Archivo: {ruta}\nQué mejorar: {instruccion or 'claridad, precisión y completitud'}\n\n---\n{contenido}"
    r = completar(proveedor, [{"role": "user", "content": pedido}], INSTRUCCIONES_MEJORAR, modelo)
    return {**r, "propuesta": sin_cercas(r["texto"])}


def revisar(proveedor: str, modelo: str, archivos: dict[str, str]) -> dict:
    cuerpo = "\n\n".join(f"=== {rel} ===\n{t}" for rel, t in sorted(archivos.items()))[:MAX_CARACTERES - 4000]
    return completar(proveedor, [{"role": "user", "content": cuerpo}], INSTRUCCIONES_REVISAR, modelo)
