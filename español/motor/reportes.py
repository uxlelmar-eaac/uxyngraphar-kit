"""Reportes al autor de un sistema (`uxyngraphar reportar`, botón «Reportar al autor» del panel).

Quien usa un sistema cuenta qué falla o qué falta y el autor lo ve en «Sugerencias» del Creador, donde la IA puede
convertirlo en una propuesta de mejora. Antes de enviar siempre se enseña la vista previa: lo que sale del equipo es
exactamente `armar(...)` (tipo, texto, sistema, versión, versión del kit, sistema operativo y Python). Nunca rutas,
nombres de proyectos ni código.
"""

from __future__ import annotations

import platform
from pathlib import Path

import especificacion as esp
import generar
import remoto

TIPOS = {"problema": "PROBLEMA", "mejora": "MEJORA", "duda": "DUDA"}
NOMBRES = {"PROBLEMA": "Problema", "MEJORA": "Mejora", "DUDA": "Duda"}
MINIMO, MAXIMO = 10, 4000


def contexto() -> dict:
    return {"kit": esp.VERSION_MOTOR, "sistema_operativo": platform.system() or "desconocido",
            "python": ".".join(platform.python_version_tuple()[:2])}


def _version_instalada(pid: str, repo: Path | None) -> str | None:
    if not repo:
        return None
    return next((m.get("version") for m in generar.instalados(Path(repo).resolve()) if m.get("id") == pid), None)


def armar(ref: str, tipo: str, texto: str, repo: Path | None = None) -> dict:
    """Lo que se enviaría: {editor, id, version, tipo, texto, contexto}. No usa la red salvo para saber el editor."""
    m = remoto.REFERENCIA.match((ref or "").strip())
    if not m:
        raise ValueError(f"sistema inválido «{ref}» (usa id, editor/id o editor/id@versión)")
    clave = (tipo or "").strip().lower()
    if clave not in TIPOS:
        raise ValueError(f"tipo: uno de {', '.join(TIPOS)}")
    limpio = (texto or "").replace("\r\n", "\n").strip()
    if len(limpio) < MINIMO:
        raise ValueError(f"cuenta un poco más (al menos {MINIMO} caracteres)")
    if len(limpio) > MAXIMO:
        raise ValueError(f"el reporte admite hasta {MAXIMO} caracteres")
    pid = m["id"]
    editor = m["editor"] or (remoto.versiones_disponibles().get(pid) or {}).get("editor")
    if not editor:
        raise ValueError(f"no sé de quién es «{pid}»: indica editor/{pid} (lo ves en «uxyngraphar info {pid}»)")
    return {"editor": editor, "id": pid, "version": m["version"] or _version_instalada(pid, repo),
            "tipo": TIPOS[clave], "texto": limpio, "contexto": contexto()}


def vista_previa(datos: dict) -> str:
    c = datos["contexto"]
    lineas = [f"Para: @{datos['editor']} (autor de «{datos['id']}»)",
              f"Sistema: {datos['editor']}/{datos['id']}" + (f"@{datos['version']}" if datos.get("version") else ""),
              f"Tipo: {NOMBRES[datos['tipo']]}",
              f"Equipo: uxyngraphar {c['kit']} · {c['sistema_operativo']} · Python {c['python']}",
              "Texto:"]
    lineas += [f"  {linea}" for linea in datos["texto"].splitlines()]
    lineas.append("No se envían rutas, nombres de proyectos ni código. El autor verá tu @usuario.")
    return "\n".join(lineas)


def enviar(datos: dict) -> dict:
    """Envía el reporte con la sesión del kit. Devuelve {id, repetido}."""
    if not remoto.token():
        raise PermissionError("sin sesión: uxyngraphar iniciar-sesion")
    codigo, cuerpo = remoto._pedir_json(  # noqa: SLF001 - cliente HTTP del propio kit
        f"/sistemas/{datos['editor']}/{datos['id']}/reportes",
        {"tipo": datos["tipo"], "texto": datos["texto"], "version": datos.get("version"), "contexto": datos["contexto"]},
        con_sesion=True)
    if codigo == 401:
        raise PermissionError("la sesión caducó o se revocó: uxyngraphar iniciar-sesion")
    if codigo == 403:
        raise PermissionError(remoto._mensaje(cuerpo, "solo puedes reportar sistemas de tu biblioteca"))  # noqa: SLF001
    if codigo == 404:
        raise remoto.NoEncontrado(remoto._mensaje(cuerpo, f"«{datos['editor']}/{datos['id']}» no existe"))  # noqa: SLF001
    if codigo >= 400:
        raise remoto.SinServidor(remoto._mensaje(cuerpo, f"el servidor respondió HTTP {codigo}"))  # noqa: SLF001
    return {"id": cuerpo.get("id"), "repetido": bool(cuerpo.get("repetido"))}
