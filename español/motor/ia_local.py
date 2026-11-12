"""IA del Creador local (ADR 0013): modelos de este equipo (Ollama, LM Studio) o la clave guardada en tu cuenta.

- Locales: solo `http://127.0.0.1` / `localhost`. Nada sale del equipo y no hace falta clave.
- «servidor»: el kit pide `POST /me/ia/completar` con la sesión del equipo; el servidor usa tu clave por defecto
  (cifrada allí, nunca llega a este equipo) y anota el uso en «Claves de IA».

Las respuestas son texto: quien llama (panel) decide qué hacer con él; nunca se escribe nada sin que la persona acepte.
"""

from __future__ import annotations

import json
import os
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
PROVEEDORES = ("servidor", *LOCALES)


class IaNoDisponible(remoto.SinServidor):
    """El proveedor elegido no responde o rechazó la petición."""


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
        raise IaNoDisponible(f"{url}: HTTP {e.code}") from None
    except (urllib.error.URLError, OSError, ValueError) as e:
        raise IaNoDisponible(f"{url}: no responde ({getattr(e, 'reason', e)})") from None


def modelos() -> list[dict]:
    """Modelos locales que responden ahora mismo: [{proveedor, modelo}]."""
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
    return salida


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
    if not modelo:
        raise ValueError("elige un modelo local")
    todos = _mensajes(sistema, mensajes)
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
