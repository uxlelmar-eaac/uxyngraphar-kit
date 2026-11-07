"""Reglas de una ficha pregunta usadas por verificar-preguntas.py: tabla de decisiones, síntesis, antigüedad e instrucción enlazada."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

INSTRUCCIONES = "instrucciones-aprobadas"
SIN_RESPUESTA = {"", "…", "...", "?", "-", "—"}
COLUMNAS = ("#", "Pregunta", "Opciones", "Elegida", "Efecto")
SEPARADOR = re.compile(r"^:?-{3,}:?$")


def secciones(cuerpo: str) -> dict[str, str]:
    """{título de «## …»: texto} del cuerpo de la ficha."""
    salida: dict[str, str] = {}
    actual = None
    for linea in cuerpo.splitlines():
        if linea.startswith("## "):
            actual = linea[3:].strip()
            salida[actual] = ""
        elif actual is not None:
            salida[actual] += linea + "\n"
    return salida


def filas_decisiones(texto: str) -> list[dict[str, str]]:
    """Filas de la tabla de «Decisiones» como {columna: celda}, sin cabecera ni separador."""
    filas = []
    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea.startswith("|"):
            continue
        celdas = [c.strip() for c in linea.strip("|").split("|")]
        if celdas[:2] == list(COLUMNAS[:2]) or all(SEPARADOR.match(c) for c in celdas if c):
            continue
        filas.append(dict(zip(COLUMNAS, celdas + [""] * (len(COLUMNAS) - len(celdas)))))
    return filas


def problemas_completada(cuerpo: str) -> list[str]:
    """Lo que impide dar por cerrada una pregunta (vacío = todas las decisiones respondidas y síntesis escrita)."""
    partes = secciones(cuerpo)
    filas = filas_decisiones(partes.get("Decisiones", ""))
    if not filas:
        return ["sin decisiones en la tabla"]
    problemas = []
    for n, fila in enumerate(filas, 1):
        if fila["Pregunta"] in SIN_RESPUESTA:
            problemas.append(f"decisión {n} sin pregunta")
        elif fila["Elegida"] in SIN_RESPUESTA:
            problemas.append(f"decisión {n} sin «Elegida» de la persona")
    sintesis = [ln.strip()[2:].strip() for ln in partes.get("Síntesis", "").splitlines() if ln.strip().startswith("- ")]
    if not [s for s in sintesis if s not in SIN_RESPUESTA]:
        problemas.append("síntesis vacía")
    return problemas


def dias_desde(creada, hoy: date | None = None) -> int | None:
    try:
        return ((hoy or date.today()) - date.fromisoformat(str(creada)[:10])).days
    except ValueError:
        return None


def aviso_instruccion(trabajo_instrucciones: Path, iid) -> str | None:
    """Aviso si la instrucción enlazada no está en el trabajo de INSTRUCCIONES; None si cuadra o si ese trabajo no existe."""
    if iid in (None, "", "null") or not trabajo_instrucciones.is_dir():
        return None
    if not any(trabajo_instrucciones.rglob(f"{iid}.md")):
        return f"instruccion_id {iid} no está en {INSTRUCCIONES}"
    return None
