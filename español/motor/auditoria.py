"""Registro de auditoría: una línea JSON por cada operación que cambia algo (instalar, actualizar, quitar, retirar,
migrar, flujo, deshacer, desinstalar…), venga de la CLI o del panel, también cuando falla. Vive en
`registros/acciones.jsonl` de la carpeta de uxyngraphar y rota por tamaño (`acciones.jsonl.1`). Nunca hace fallar la
operación que registra."""

from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path

import casa

ARCHIVO = "registros/acciones.jsonl"
MAX_BYTES = 1024 * 1024
ORIGEN = {"valor": "cli"}   # el panel lo cambia a «panel» al arrancar
_candado = threading.Lock()


def ruta() -> Path:
    return casa.carpeta() / ARCHIVO


def registrar(accion: str, proyecto: str = "", ids: list[str] | None = None, error: str = "", **extra) -> None:
    linea = {"fecha": time.strftime("%Y-%m-%dT%H:%M:%S"), "origen": ORIGEN["valor"], "accion": accion, "proyecto": proyecto,
             "ids": list(ids or []), "resultado": "error" if error else "ok", **({"error": error} if error else {}), **extra}
    if not casa.carpeta().is_dir():   # p. ej. tras «desinstalar --alcance todo»: no se vuelve a crear la carpeta
        return
    try:
        with _candado:
            destino = ruta()
            destino.parent.mkdir(parents=True, exist_ok=True)
            if destino.is_file() and destino.stat().st_size > MAX_BYTES:
                os.replace(destino, destino.with_name(destino.name + ".1"))
            with open(destino, "a", encoding="utf-8") as f:
                f.write(json.dumps(linea, ensure_ascii=False) + "\n")
    except OSError:
        pass


def leer(limite: int = 100) -> list[dict]:
    """Las últimas `limite` acciones, de la más reciente a la más antigua."""
    salida = []
    for archivo in (ruta(), ruta().with_name(ruta().name + ".1")):
        try:
            lineas = archivo.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for texto in reversed(lineas):
            try:
                salida.append(json.loads(texto))
            except ValueError:
                continue
            if len(salida) >= limite:
                return salida
    return salida
