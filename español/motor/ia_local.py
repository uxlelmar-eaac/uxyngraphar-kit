"""IA del Creador local (ADR 0013 y 0014): modelos de este equipo, tus suscripciones o la clave de tu cuenta.

- Locales: solo `http://127.0.0.1` / `localhost`. Nada sale del equipo y no hace falta clave.
- Suscripciones en este equipo (ADR 0014): el kit le pide la respuesta a la CLI oficial del proveedor (Claude Code,
  Codex, Copilot CLI, Qwen Code, Cursor CLI, Kimi Code CLI, OpenCode) con la sesión que ya tienes en ella. El kit nunca lee ni copia sus tokens: la
  suscripción no sale de tu ordenador. Cada una lleva su aviso honesto de términos (`SUSCRIPCIONES`).
  Gemini CLI se ofrece con riesgo alto: los términos de Google prohíben usarlo desde software de terceros.
- «servidor»: el kit pide `POST /me/ia/completar` con la sesión del equipo; el servidor usa tu clave o suscripción
  por defecto (cifrada allí, nunca llega a este equipo) y anota el uso en «IA y conexiones».

Las respuestas son texto: quien llama (panel) decide qué hacer con él; nunca se escribe nada sin que la persona acepte.
"""

from __future__ import annotations

import contextlib
import glob
import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import webbrowser

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
        "orden_login": ["claude", "auth", "login"],
        "url_claves": "https://console.anthropic.com/settings/keys",
        "url_instalar": "https://code.claude.com/docs/en/overview",
        "orden": ["claude", "-p", "--output-format", "text"], "salida": "stdout", "riesgo": "medio",
        "aviso": ("Anthropic solo permite el inicio de sesión de Pro y Max dentro de Claude Code y Claude.ai. Aquí es tu "
                  "Claude Code quien habla con Anthropic (en modo no interactivo, `claude -p`) y gasta de tu plan; el kit "
                  "nunca toca tus tokens. Si quieres evitar cualquier duda, usa una clave de API de Anthropic en tu cuenta."),
    },
    "codex": {
        "nombre": "Codex", "planes": "ChatGPT Go, Plus o Pro", "cli": "codex", "iniciar": "codex login",
        "orden_login": ["codex", "login"],
        "url_claves": "https://platform.openai.com/api-keys",
        "url_instalar": "https://developers.openai.com/codex/cli",
        "orden": ["codex", "exec", "--skip-git-repo-check", "--sandbox", "read-only", "--output-last-message",
                  "{salida}", "-"], "salida": "archivo", "riesgo": "bajo",
        "aviso": ("OpenAI deja usar tu plan de ChatGPT en proyectos locales con «Sign in with ChatGPT». Aquí es tu Codex "
                  "quien hace la llamada en tu equipo y gasta de los límites de tu plan."),
    },
    "copilot": {
        "nombre": "GitHub Copilot CLI", "planes": "Copilot Pro, Pro+ o Business", "cli": "copilot",
        "iniciar": "copilot login", "orden_login": ["copilot", "login"],
        "url_claves": "https://github.com/settings/copilot",
        "url_instalar": "https://docs.github.com/en/copilot/how-tos/copilot-cli",
        "orden": ["copilot", "-p", "{texto}", "--silent"], "salida": "stdout",
        "riesgo": "medio",
        "aviso": ("GitHub solo tiene un acuerdo formal para usar Copilot desde OpenCode. Aquí es tu Copilot CLI oficial quien "
                  "responde, con tu sesión y en tu equipo, y gasta tus peticiones premium. Si quieres evitar cualquier "
                  "duda, usa una clave de API."),
    },
    "qwen": {
        "nombre": "Qwen Code", "planes": "Alibaba Cloud Coding Plan", "cli": "qwen", "iniciar": "qwen  (luego /auth)",
        "orden_login": ["qwen"],
        "url_claves": "https://modelstudio.console.alibabacloud.com",
        "url_instalar": "https://github.com/QwenLM/qwen-code",
        "orden": ["qwen", "-p", "Responde a lo que llega por la entrada estándar."], "salida": "stdout",
        "riesgo": "bajo",
        "aviso": ("El acceso gratuito con Qwen OAuth cerró el 15 de abril de 2026: configura en Qwen Code la clave de tu "
                  "Coding Plan (empieza por «sk-sp-»), pensada para herramientas de programación."),
    },
    "cursor": {
        "nombre": "Cursor CLI", "planes": "Cursor Pro, Pro+, Ultra o Teams", "cli": "cursor-agent",
        "iniciar": "cursor-agent login", "orden_login": ["cursor-agent", "login"],
        "url_claves": "https://cursor.com/dashboard",
        "url_instalar": "https://docs.cursor.com/en/cli/overview",
        "orden": ["cursor-agent", "-p", "--output-format", "text", "{texto}"],
        "salida": "stdout", "riesgo": "bajo",
        "aviso": ("Cursor ofrece su CLI para usarla en scripts y en modo no interactivo (`-p`). Aquí es tu Cursor CLI oficial "
                  "quien responde, con tu sesión y en tu equipo, y gasta del uso incluido en tu plan."),
    },
    "kimi": {
        "nombre": "Kimi Code CLI", "planes": "Kimi Code (Plus, Pro o Max)", "cli": "kimi",
        "iniciar": "kimi  (luego /login)", "orden_login": ["kimi", "login"],
        "url_claves": "https://www.kimi.com/code",
        "url_instalar": "https://www.kimi.com/code",
        "orden": ["kimi", "-p", "{texto}", "--output-format", "text"],
        "salida": "stdout", "riesgo": "bajo",
        "aviso": ("El plan de Kimi Code está pensado para agentes de programación. Aquí es tu Kimi CLI oficial quien responde "
                  "en tu equipo y gasta de la cuota de tu plan."),
    },
    "opencode": {
        "nombre": "OpenCode", "planes": "Copilot (acuerdo formal), OpenCode Zen o tus planes con clave", "cli": "opencode",
        "iniciar": "opencode auth login", "orden_login": ["opencode", "auth", "login"],
        "url_claves": "https://opencode.ai/docs",
        "url_instalar": "https://opencode.ai/docs",
        "orden": ["opencode", "run", "{texto}"], "salida": "stdout", "riesgo": "bajo",
        "aviso": ("OpenCode es la vía que GitHub aprueba formalmente para usar Copilot, y también admite OpenCode Zen y los "
                  "planes con clave (GLM, Kimi, MiniMax, Qwen). Responde con el proveedor y modelo por defecto que "
                  "configuraste en OpenCode, en tu equipo y gastando de ese plan."),
    },
    "gemini": {
        "nombre": "Gemini CLI", "planes": "Google AI Pro o Ultra", "cli": "gemini", "iniciar": "gemini  (luego /auth)",
        "orden_login": ["gemini"],
        "url_claves": "https://aistudio.google.com/app/apikey",
        "url_instalar": "https://github.com/google-gemini/gemini-cli",
        "orden": ["gemini", "-p", "{texto}"], "salida": "stdout", "riesgo": "alto",
        "aviso": ("Los términos de Antigravity y Gemini CLI prohíben usarlos desde software de terceros, aunque sea "
                  "envolviendo su CLI, y Google ha suspendido cuentas de Google por ello. Aquí es tu Gemini CLI oficial quien "
                  "responde, con tu sesión y en tu equipo, pero úsalo bajo tu propio riesgo. Para evitarlo, usa una clave de "
                  "Google AI Studio en tu cuenta."),
    },
}
# Suscripciones y planes que se conectan abriendo la página del proveedor para obtener su clave (sin CLI propia).
SUSCRIPCIONES_WEB = (
    {"id": "deepseek", "nombre": "DeepSeek", "planes": "Saldo prepagado de DeepSeek Platform (la web es gratuita)",
     "riesgo": "bajo", "url_claves": "https://platform.deepseek.com/api_keys",
     "aviso": "DeepSeek no vende un plan mensual: abre DeepSeek Platform, copia tu clave y pégala en tu cuenta de uxyngraphar."},
    {"id": "glm", "nombre": "GLM (Z.ai)", "planes": "GLM Coding Plan Lite, Pro o Max",
     "riesgo": "bajo", "url_claves": "https://z.ai/manage-apikey/apikey-list",
     "aviso": "Tu plan de Z.ai incluye una clave para herramientas de programación. Ábrela y pégala en tu cuenta."},
    {"id": "minimax", "nombre": "MiniMax", "planes": "MiniMax Token Plan o M Plan",
     "riesgo": "bajo", "url_claves": "https://platform.minimax.io/user-center/basic-information",
     "aviso": "Copia la clave de tu plan en MiniMax y pégala en tu cuenta para usarla en el Creador."},
    {"id": "ollama", "nombre": "Ollama Cloud", "planes": "Ollama Free, Pro o Max (modelos en la nube)",
     "riesgo": "bajo", "url_claves": "https://ollama.com/settings/keys",
     "aviso": "Abre tus claves de Ollama Cloud y pégala en tu cuenta. Los modelos locales se usan aquí sin clave."},
    {"id": "supergrok", "nombre": "SuperGrok / xAI", "planes": "SuperGrok, X Premium+ o clave de xAI",
     "riesgo": "medio", "url_claves": "https://console.x.ai",
     "aviso": "Abre la consola de xAI para crear tu clave o conéctalo con OAuth desde tu cuenta web de uxyngraphar."},
    {"id": "openrouter", "nombre": "OpenRouter", "planes": "Un solo acceso a cientos de modelos (PKCE o clave)",
     "riesgo": "bajo", "url_claves": "https://openrouter.ai/keys",
     "aviso": "Puedes conectar OpenRouter en un clic desde tu cuenta web o copiando tu clave desde aquí."},
)
# Lo que no se ofrece y por qué (se muestra en el panel para que nadie lo busque).
NO_PERMITIDAS: dict[str, tuple[str, str]] = {}
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
    "  · Tu suscripción con su CLI oficial instalada y la sesión iniciada: Claude Code, Codex, GitHub Copilot CLI, "
    "Qwen Code, Cursor CLI, Kimi Code CLI, OpenCode o Gemini CLI.\n"
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


_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[a-zA-Z]|\x1b\][^\x07]*\x07")
_URL_RE = re.compile(r"https://[^\s\"'<>)\]]+")
_CODIGO_RE = re.compile(r"\b[A-Z0-9]{4,5}-[A-Z0-9]{4,5}\b")
_BLOQUEO_LOGIN = threading.Lock()
_SESIONES_LOGIN: dict[str, dict] = {}
SEGUNDOS_LOGIN = 300


def _url_cuenta_ia() -> str:
    base_web = (os.environ.get("UXYNGRAPHAR_WEB") or "https://app.uxyngraphar.com").rstrip("/")
    return f"{base_web}/editor/cuenta/ia"


def suscripciones() -> dict:
    """Suscripciones de este equipo: si su CLI está instalada, cómo iniciar sesión, enlaces de clave y avisos."""
    return {
        "revisado": "2026-11-24",
        "url_cuenta_ia": _url_cuenta_ia(),
        "disponibles": [{"proveedor": p, "nombre": s["nombre"], "planes": s["planes"], "cli": s["cli"],
                         "instalada": ejecutable(s["cli"]) is not None, "iniciar_sesion": s["iniciar"],
                         "url_claves": s["url_claves"], "url_instalar": s["url_instalar"],
                         "riesgo": s["riesgo"], "aviso": s["aviso"]} for p, s in SUSCRIPCIONES.items()],
        "web": [dict(w) for w in SUSCRIPCIONES_WEB],
        "no_permitidas": [{"id": k, "nombre": n, "motivo": m} for k, (n, m) in NO_PERMITIDAS.items()],
    }


def _snapshot_login(sesion: dict) -> dict:
    return {
        "id": sesion["id"],
        "proveedor": sesion["proveedor"],
        "nombre": sesion["nombre"],
        "estado": sesion["estado"],
        "url": sesion["url"],
        "codigo": sesion["codigo"],
        "salida": list(sesion["salida"]),
        "comando": sesion["comando"],
        "url_claves": sesion["url_claves"],
        "error": sesion["error"],
    }


def _terminar_proceso(proc: subprocess.Popen | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    try:
        proc.terminate()
        proc.wait(timeout=2)
    except Exception:
        with contextlib.suppress(Exception):
            proc.kill()


def iniciar_sesion_cli(proveedor: str, abrir_navegador: bool = True) -> dict:
    """Lanza el inicio de sesión de la CLI oficial, captura el enlace/código y abre el navegador."""
    if proveedor not in SUSCRIPCIONES:
        raise ValueError(f"proveedor desconocido: {proveedor}")
    s = SUSCRIPCIONES[proveedor]
    exe = ejecutable(s["cli"])
    if exe is None:
        raise IaNoDisponible(f"{s['nombre']}: no está instalada en este equipo («{s['cli']}» no aparece en el PATH ni dentro de su app de escritorio)")
    orden = [exe if a == s["cli"] else a for a in s["orden_login"]]
    if os.name == "nt" and exe.lower().endswith((".cmd", ".bat")):
        orden = ["cmd.exe", "/c", *orden]
    carpeta = tempfile.mkdtemp(prefix="uxyngraphar-login-")
    sesion_id = uuid.uuid4().hex[:12]
    evento = threading.Event()
    sesion: dict = {
        "id": sesion_id,
        "proveedor": proveedor,
        "nombre": s["nombre"],
        "estado": "en_curso",
        "url": "",
        "codigo": "",
        "salida": [],
        "comando": s["iniciar"],
        "url_claves": s["url_claves"],
        "error": "",
        "proc": None,
        "carpeta": carpeta,
        "evento": evento,
    }
    with _BLOQUEO_LOGIN:
        for previa in list(_SESIONES_LOGIN.values()):
            if previa["proveedor"] == proveedor and previa["estado"] == "en_curso":
                previa["estado"] = "cancelado"
                _terminar_proceso(previa["proc"])
        _SESIONES_LOGIN[sesion_id] = sesion
    try:
        proc = subprocess.Popen(  # noqa: S603
            orden, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace", bufsize=1, cwd=carpeta,
        )
    except OSError as e:
        shutil.rmtree(carpeta, ignore_errors=True)
        with _BLOQUEO_LOGIN:
            sesion["estado"] = "error"
            sesion["error"] = str(e)
        raise IaNoDisponible(f"{s['nombre']}: no se pudo iniciar sesión ({e})") from None

    with _BLOQUEO_LOGIN:
        sesion["proc"] = proc

    def _vigilar() -> None:
        abierto = False
        limite = time.monotonic() + SEGUNDOS_LOGIN
        try:
            assert proc.stdout is not None
            for cruda in proc.stdout:
                limpia = _ANSI_RE.sub("", cruda).strip()
                if not limpia:
                    continue
                url_nueva = ""
                with _BLOQUEO_LOGIN:
                    sesion["salida"] = (sesion["salida"] + [limpia])[-25:]
                    if not sesion["url"]:
                        m_url = _URL_RE.search(limpia)
                        if m_url:
                            sesion["url"] = m_url.group(0).rstrip(".,;:")
                            url_nueva = sesion["url"]
                    if not sesion["codigo"]:
                        m_cod = _CODIGO_RE.search(limpia)
                        if m_cod:
                            sesion["codigo"] = m_cod.group(0)
                    if sesion["url"] or sesion["codigo"]:
                        evento.set()
                if url_nueva and abrir_navegador and not abierto:
                    abierto = True
                    with contextlib.suppress(Exception):
                        webbrowser.open(url_nueva)
                if time.monotonic() > limite:
                    _terminar_proceso(proc)
                    break
            rc = proc.wait(timeout=max(1.0, limite - time.monotonic()))
        except Exception as e:
            _terminar_proceso(proc)
            with _BLOQUEO_LOGIN:
                if sesion["estado"] == "en_curso":
                    sesion["estado"] = "error"
                    sesion["error"] = str(e)
        else:
            with _BLOQUEO_LOGIN:
                if sesion["estado"] == "en_curso":
                    if rc == 0:
                        sesion["estado"] = "listo"
                    else:
                        sesion["estado"] = "error"
                        sesion["error"] = sesion["salida"][-1] if sesion["salida"] else f"código {rc}"
        finally:
            if proc.stdout is not None:
                with contextlib.suppress(Exception):
                    proc.stdout.close()
            evento.set()
            shutil.rmtree(carpeta, ignore_errors=True)

    threading.Thread(target=_vigilar, daemon=True, name=f"login-{proveedor}").start()
    evento.wait(timeout=0.5)
    with _BLOQUEO_LOGIN:
        return _snapshot_login(sesion)


def estado_sesion_cli(sesion_id: str) -> dict:
    """Estado actual de un inicio de sesión lanzado desde el panel."""
    with _BLOQUEO_LOGIN:
        sesion = _SESIONES_LOGIN.get(sesion_id)
        if not sesion:
            raise ValueError("sesión de inicio no encontrada")
        return _snapshot_login(sesion)


def cancelar_sesion_cli(sesion_id: str) -> dict:
    """Detiene un inicio de sesión en curso."""
    with _BLOQUEO_LOGIN:
        sesion = _SESIONES_LOGIN.get(sesion_id)
        if not sesion:
            raise ValueError("sesión de inicio no encontrada")
        if sesion["estado"] == "en_curso":
            sesion["estado"] = "cancelado"
            proc = sesion["proc"]
        else:
            proc = None
        snap = _snapshot_login(sesion)
    _terminar_proceso(proc)
    return snap


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


INSTRUCCIONES_FRAGMENTO = (
    "Eres el asistente del Creador de uxyngraphar. Mejoras UN fragmento de un archivo de un sistema de gobernanza para "
    "agentes de IA: más claro, concreto y comprobable. Devuelve SOLO el texto que sustituye al fragmento, sin "
    "explicaciones, comillas ni bloques ```. Conserva el idioma, el formato Markdown o JSON del fragmento y su extensión "
    "aproximada; no repitas el resto del archivo.")


def mejorar_fragmento(proveedor: str, modelo: str, ruta: str, contenido: str, fragmento: str, instruccion: str) -> dict:
    """Reescribe solo `fragmento` (con el archivo como contexto). Devuelve {texto, modelo, proveedor, propuesta}."""
    if not fragmento.strip():
        raise ValueError("fragmento: selecciona el texto que quieres mejorar")
    pedido = (f"Archivo: {ruta}\nQué mejorar: {instruccion or 'claridad, precisión y lo que falte'}\n\n"
              f"=== Archivo completo (contexto) ===\n{contenido[:MAX_CARACTERES // 2]}\n\n"
              f"=== Fragmento que debes reescribir ===\n{fragmento}")
    r = completar(proveedor, [{"role": "user", "content": pedido}], INSTRUCCIONES_FRAGMENTO, modelo)
    propuesta = sin_cercas(r["texto"])
    # Conserva los saltos de línea del borde del fragmento original (la IA suele recortarlos).
    if not fragmento.endswith("\n"):
        propuesta = propuesta.rstrip("\n")
    return {**r, "propuesta": propuesta}


def revisar(proveedor: str, modelo: str, archivos: dict[str, str]) -> dict:
    cuerpo = "\n\n".join(f"=== {rel} ===\n{t}" for rel, t in sorted(archivos.items()))[:MAX_CARACTERES - 4000]
    return completar(proveedor, [{"role": "user", "content": cuerpo}], INSTRUCCIONES_REVISAR, modelo)
