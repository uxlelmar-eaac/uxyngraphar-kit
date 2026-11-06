"""Contratos de uxyngraphar 2.0 del lado del motor: paquete (fuente o construido) y FLUJO.json.

El manifiesto y la integridad se validan con la copia de `scripts/comun/uxyn_base.py` de `paquetes/!base/`, la base de
la que nacen los paquetes nuevos (no es un paquete: no se lista, no se construye ni se instala).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

MOTOR = Path(__file__).resolve().parent
KIT = MOTOR.parent
CATALOGO = KIT / "paquetes"
PLANTILLA = CATALOGO / "!base"
DESTINO_COMUN = "scripts/comun"
COMUN = PLANTILLA / DESTINO_COMUN
sys.path.insert(0, str(COMUN))

import uxyn_base as base  # noqa: E402

VERSION_MOTOR = "2.0.0"
FLUJO = "FLUJO.json"
INDICE = "INDICE.md"
FORMATO_FLUJO = 1
MODOS = ("manual", "leer_por_defecto", "trabajar_con", "secuencia")
CONFLICTOS = ("preguntar",)
OBLIGATORIOS = (base.ENTRADA,)
FLUJO_INICIAL = {"formato": FORMATO_FLUJO, "modo": "manual", "leer_por_defecto": [], "trabajar_con": None,
                 "secuencia": [], "conflictos": "preguntar"}


def version_tupla(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split("."))


def motor_compatible(requisito: str, version: str = VERSION_MOTOR) -> bool:
    minimo = version_tupla(requisito[2:])
    actual = version_tupla(version)[: len(minimo)]
    return actual >= minimo


def validar_paquete(carpeta: Path, construido: bool = False) -> list[str]:
    """Errores de un paquete del catálogo (`construido=False`) o ya construido/instalado (`True`)."""
    carpeta = Path(carpeta)
    try:
        m = base.leer_manifiesto(carpeta)
    except (OSError, ValueError) as e:
        return [f"{base.MANIFIESTO}: {e}"]
    errores = base.validar_manifiesto(m)
    if errores:
        return errores
    if carpeta.name != m["id"]:
        errores.append(f"la carpeta se llama «{carpeta.name}» pero el id es «{m['id']}»")
    if not motor_compatible(m["motor"]):
        errores.append(f"motor: requiere {m['motor']}, este motor es {VERSION_MOTOR}")
    for nombre in OBLIGATORIOS:
        if not (carpeta / nombre).is_file():
            errores.append(f"falta {nombre}")
    for v in m["verificaciones"]:
        if not (carpeta / v).is_file():
            errores.append(f"verificación inexistente: {v}")
    for tipo, d in m.get("fichas", {}).items():
        for donde, plantilla in [("plantilla", d["plantilla"]), *((f"variantes.{k}", v) for k, v in d.get("variantes", {}).items())]:
            if not (carpeta / plantilla).is_file():
                errores.append(f"fichas.{tipo}.{donde} inexistente: {plantilla}")
    for rel in base.archivos_del_paquete(carpeta):
        if not rel.isascii() or " " in rel:
            errores.append(f"nombre de archivo no ASCII o con espacios: {rel}")
    if construido:
        informe = base.comprobar_integridad(carpeta)
        if not base.integro(informe):
            errores.append(f"integridad: {json.dumps(informe, ensure_ascii=False)}")
    elif (carpeta / base.INTEGRIDAD).exists():
        errores.append(f"{base.INTEGRIDAD} no va en el catálogo: lo genera la construcción")
    return errores


def avisos_paquete(carpeta: Path) -> list[str]:
    """Avisos (no impiden validar): scripts de `scripts/comun/` que faltan o difieren de `paquetes/!base/`."""
    avisos = []
    for script in sorted(COMUN.glob("*.py")):
        propio = Path(carpeta) / DESTINO_COMUN / script.name
        if not propio.is_file():
            avisos.append(f"{DESTINO_COMUN}/{script.name}: no está (paquetes/!base lo trae)")
        elif base.sha256(propio) != base.sha256(script):
            avisos.append(f"{DESTINO_COMUN}/{script.name}: difiere de paquetes/!base")
    return avisos


def validar_flujo(flujo, instalados: set[str] | None = None) -> list[str]:
    """Errores de FLUJO.json. Con `instalados`, también comprueba que los paquetes citados existan."""
    if not isinstance(flujo, dict):
        return ["FLUJO.json debe ser un objeto JSON"]
    errores = []
    if flujo.get("formato") != FORMATO_FLUJO:
        errores.append(f"formato: debe ser {FORMATO_FLUJO}")
    modo = flujo.get("modo")
    if modo not in MODOS:
        errores.append(f"modo: uno de {', '.join(MODOS)}")
    if flujo.get("conflictos") not in CONFLICTOS:
        errores.append("conflictos: debe ser «preguntar»")
    citados: list[str] = []
    for campo in ("leer_por_defecto", "secuencia"):
        valor = flujo.get(campo)
        if not isinstance(valor, list) or not all(isinstance(x, str) and base.ID_VALIDO.match(x) for x in valor):
            errores.append(f"{campo}: lista de ids de paquete")
        else:
            citados += valor
            if len(set(valor)) != len(valor):
                errores.append(f"{campo}: ids repetidos")
    trabajar = flujo.get("trabajar_con")
    if trabajar is not None and (not isinstance(trabajar, str) or not base.ID_VALIDO.match(trabajar)):
        errores.append("trabajar_con: id de paquete o null")
    elif trabajar:
        citados.append(trabajar)
    if modo == "leer_por_defecto" and not flujo.get("leer_por_defecto"):
        errores.append("modo leer_por_defecto: «leer_por_defecto» no puede estar vacío")
    if modo == "trabajar_con" and not trabajar:
        errores.append("modo trabajar_con: falta «trabajar_con»")
    if modo == "secuencia" and not flujo.get("secuencia"):
        errores.append("modo secuencia: «secuencia» no puede estar vacía")
    if instalados is not None:
        for pid in sorted(set(citados) - instalados):
            errores.append(f"paquete no instalado: {pid}")
    return errores
