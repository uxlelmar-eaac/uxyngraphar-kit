"""Agente del Creador desde el panel del kit: el mismo «uxyn» del servidor (protocolo creacion-agente).

uxyn vive en el servidor y trabaja sobre los borradores web de tu cuenta. Para que vea el sistema que tienes abierto
en el panel, antes de cada turno el panel sube ese sistema a su borrador (lo crea si no existe). Lo que uxyn cambia
queda como **propuesta**: la revisas aquí, puedes corregirla, aceptas o rechazas cada archivo y, al aceptar, se trae
el borrador a este equipo. Nada se escribe sin que la persona lo acepte. Las conversaciones se guardan en el servidor.
"""

from __future__ import annotations

import re
import urllib.parse

import remoto

SEGUNDOS_TURNO = 300
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# Identificador del progreso en vivo de un turno (lo genera el panel; el mismo formato que exige el servidor).
PROGRESO = re.compile(r"^[A-Za-z0-9-]{8,64}$")
# Archivos de referencia por mensaje (los mismos límites que el servidor).
MAX_ADJUNTOS = 80
MAX_CARACTERES_ADJUNTO = 100_000
MAX_CARACTERES_ADJUNTOS = 200_000


class AgenteNoDisponible(remoto.SinServidor):
    """El servidor no responde o rechazó la petición."""


def _slug(valor: str) -> str:
    if not isinstance(valor, str) or not SLUG.match(valor) or len(valor) > 80:
        raise ValueError("borrador: identificador no válido")
    return valor


def _respuesta(codigo: int, cuerpo: dict, que: str) -> dict:
    if codigo == 401:
        raise PermissionError(remoto._mensaje(cuerpo, "sin sesión: inicia sesión en «Herramienta y ajustes»"))
    if codigo >= 400:
        raise AgenteNoDisponible(remoto._mensaje(cuerpo, f"{que}: el servidor respondió HTTP {codigo}"))
    return cuerpo


def info() -> dict:
    codigo, r = remoto._pedir_json("/me/agente", metodo="GET", con_sesion=True)
    return _respuesta(codigo, r, "agente")


def _adjuntos(lista) -> list[dict]:
    """Valida los archivos de referencia: [{nombre, contenido}] de texto y dentro de los límites."""
    if not lista:
        return []
    if not isinstance(lista, list):
        raise ValueError("adjuntos: se esperaba una lista")
    if len(lista) > MAX_ADJUNTOS:
        raise ValueError(f"demasiados archivos adjuntos (máximo {MAX_ADJUNTOS})")
    salida, total = [], 0
    for a in lista:
        if not isinstance(a, dict):
            raise ValueError("adjuntos: cada archivo es {nombre, contenido}")
        nombre = str(a.get("nombre") or "").strip()[:200]
        contenido = a.get("contenido")
        if not nombre or not isinstance(contenido, str):
            raise ValueError("adjuntos: cada archivo necesita nombre y contenido de texto")
        if len(contenido) > MAX_CARACTERES_ADJUNTO:
            raise ValueError(f"«{nombre}» es demasiado grande (máximo {MAX_CARACTERES_ADJUNTO // 1000} mil caracteres)")
        total += len(contenido)
        salida.append({"nombre": nombre, "contenido": contenido})
    if total > MAX_CARACTERES_ADJUNTOS:
        raise ValueError(f"los adjuntos son demasiado grandes (máximo {MAX_CARACTERES_ADJUNTOS // 1000} mil caracteres en total)")
    return salida


def conversaciones(borrador: str | None = None) -> list[dict]:
    """Lista de conversaciones con uxyn: [{id, titulo, borrador, actualizada}]."""
    ruta = "/me/agente/conversaciones"
    if borrador:
        ruta += f"?borrador={urllib.parse.quote(_slug(borrador))}"
    codigo, r = remoto._pedir_json(ruta, metodo="GET", con_sesion=True)
    _respuesta(codigo, r if isinstance(r, dict) else {}, "conversaciones")
    return r if isinstance(r, list) else []


def conversacion(id_conversacion: int) -> dict:
    """Una conversación con uxyn: {id, borrador, mensajes: [{rol, texto, acciones?, adjuntos?}]}."""
    codigo, r = remoto._pedir_json(f"/me/agente/conversaciones/{int(id_conversacion)}", metodo="GET", con_sesion=True)
    return _respuesta(codigo, r, "conversación")


def borrar_conversacion(id_conversacion: int) -> None:
    codigo, r = remoto._pedir_json(
        f"/me/agente/conversaciones/{int(id_conversacion)}",
        metodo="DELETE",
        con_sesion=True,
    )
    if codigo not in (200, 204):
        _respuesta(codigo, r if isinstance(r, dict) else {}, "borrar conversación")


def _progreso(valor) -> str:
    if not isinstance(valor, str) or not PROGRESO.match(valor):
        raise ValueError("progreso: identificador no válido")
    return valor


def progreso(id_progreso: str) -> dict:
    """Qué está haciendo el agente en un turno en curso: {fase, pasos: [{herramienta, etiqueta, estado}]}."""
    codigo, r = remoto._pedir_json(f"/me/agente/progreso/{_progreso(id_progreso)}", metodo="GET", con_sesion=True,
                                   segundos=10)
    return _respuesta(codigo, r, "progreso")


def turno(mensaje: str, conversacion: int | None = None, borrador: str | None = None, modelo: str = "",
          adjuntos: list | None = None, progreso_id: str | None = None) -> dict:
    """Un turno: {conversacion, respuesta, acciones, propuestas, borrador, modelo}. `adjuntos`: archivos de referencia.
    `progreso_id`: identificador para seguir en vivo lo que hace el agente (GET progreso)."""
    texto = str(mensaje or "").strip()
    if not texto:
        raise ValueError("escribe un mensaje")
    cuerpo: dict = {"mensaje": texto[:8000]}
    if conversacion:
        cuerpo["conversacion"] = int(conversacion)
    if borrador:
        cuerpo["borrador"] = _slug(borrador)
    if modelo:
        cuerpo["modelo"] = modelo
    archivos = _adjuntos(adjuntos)
    if archivos:
        cuerpo["adjuntos"] = archivos
    if progreso_id:
        cuerpo["progreso"] = _progreso(progreso_id)
    codigo, r = remoto._pedir_json("/me/agente/turno", cuerpo, con_sesion=True, segundos=SEGUNDOS_TURNO)
    # Servidores antiguos rechazan «progreso» (forbidNonWhitelisted): reintenta sin él; el turno sigue, sin pasos en vivo.
    if codigo == 400 and cuerpo.get("progreso") and "progreso" in str(remoto._mensaje(r, "")).lower():
        sin = {k: v for k, v in cuerpo.items() if k != "progreso"}
        codigo, r = remoto._pedir_json("/me/agente/turno", sin, con_sesion=True, segundos=SEGUNDOS_TURNO)
    return _respuesta(codigo, r, "agente")


def propuestas(borrador: str) -> list[dict]:
    slug = urllib.parse.quote(_slug(borrador))
    codigo, r = remoto._pedir_json(f"/me/creador/borradores/{slug}/propuestas", metodo="GET", con_sesion=True)
    if codigo == 404:
        return []
    _respuesta(codigo, r if isinstance(r, dict) else {}, "propuestas")
    return r if isinstance(r, list) else []


def corregir(borrador: str, propuesta: int, ruta: str, contenido: str) -> dict:
    """Corrige el contenido propuesto de un archivo pendiente antes de aceptarlo."""
    slug = urllib.parse.quote(_slug(borrador))
    cuerpo = {"ruta": str(ruta), "contenido": str(contenido)}
    codigo, r = remoto._pedir_json(
        f"/me/creador/borradores/{slug}/propuestas/{int(propuesta)}",
        cuerpo,
        metodo="PATCH",
        con_sesion=True,
    )
    return _respuesta(codigo, r, "corregir propuesta")


def decidir(borrador: str, propuesta: int, aceptar: list[str], rechazar: list[str]) -> dict:
    slug = urllib.parse.quote(_slug(borrador))
    cuerpo = {"aceptar": [str(x) for x in aceptar], "rechazar": [str(x) for x in rechazar]}
    codigo, r = remoto._pedir_json(f"/me/creador/borradores/{slug}/propuestas/{int(propuesta)}", cuerpo, con_sesion=True)
    return _respuesta(codigo, r, "propuesta")
