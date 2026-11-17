"""Agente del Creador desde el panel del kit: el mismo «Asistente del Creador» del servidor (protocolo creacion-agente).

El agente vive en el servidor y trabaja sobre los borradores web de tu cuenta. Para que vea el sistema que tienes abierto
en el panel, antes de cada turno el panel sube ese sistema a su borrador (lo crea si no existe). Lo que el agente cambia
queda como **propuesta**: la revisas aquí, aceptas o rechazas cada archivo y, al aceptar, se trae el borrador a este
equipo. Nada se escribe sin que la persona lo acepte.
"""

from __future__ import annotations

import re
import urllib.parse

import remoto

SEGUNDOS_TURNO = 300
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


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


def turno(mensaje: str, conversacion: int | None = None, borrador: str | None = None, modelo: str = "") -> dict:
    """Un turno: {conversacion, respuesta, acciones, propuestas, borrador, modelo}."""
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
    codigo, r = remoto._pedir_json("/me/agente/turno", cuerpo, con_sesion=True, segundos=SEGUNDOS_TURNO)
    return _respuesta(codigo, r, "agente")


def propuestas(borrador: str) -> list[dict]:
    slug = urllib.parse.quote(_slug(borrador))
    codigo, r = remoto._pedir_json(f"/me/creador/borradores/{slug}/propuestas", metodo="GET", con_sesion=True)
    if codigo == 404:
        return []
    _respuesta(codigo, r if isinstance(r, dict) else {}, "propuestas")
    return r if isinstance(r, list) else []


def decidir(borrador: str, propuesta: int, aceptar: list[str], rechazar: list[str]) -> dict:
    slug = urllib.parse.quote(_slug(borrador))
    cuerpo = {"aceptar": [str(x) for x in aceptar], "rechazar": [str(x) for x in rechazar]}
    codigo, r = remoto._pedir_json(f"/me/creador/borradores/{slug}/propuestas/{int(propuesta)}", cuerpo, con_sesion=True)
    return _respuesta(codigo, r, "propuesta")
