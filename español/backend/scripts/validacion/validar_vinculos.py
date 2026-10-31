"""Vínculos y presupuesto de las instrucciones, y vínculos colgantes entre fichas."""

from __future__ import annotations

import re

from validar_comun import Opciones, Reporte, lista
from validar_fichas import Ficha

CLAVES_REF = ("mejoras_propuestas", "evolucion_documentacion", "herramientas_propuestas", "vinculos_entrada", "vinculos_salida")
ID_REF_RE = re.compile(r"\b((?:MEJ|EVO|AUD|ADR)-[A-Za-z0-9][A-Za-z0-9-]*)")


def _vinculos_instruccion(f: Ficha, rep: Reporte, op: Opciones) -> None:
    status = str(f.fm.get("status", ""))
    if status not in {"done", "approved"}:
        return
    if not f.fm.get("acto"):
        rep.segun(op.vinculos, f"Instrucción sin acto: {f.rel}")
    if status == "done" and not lista(f.fm, "vinculos_salida"):
        rep.segun(op.vinculos, f"Instrucción done sin vinculos_salida: {f.rel}")


def _presupuesto(f: Ficha, rep: Reporte, op: Opciones) -> None:
    if "presupuesto_max_docs" not in f.fm:
        return
    try:
        maximo = int(str(f.fm["presupuesto_max_docs"]))
    except ValueError:
        rep.warn(f"presupuesto_max_docs no numérico en {f.rel}")
        return
    total = len(lista(f.fm, "lectura_minima")) + len(lista(f.fm, "espejo_leer"))
    if total > maximo:
        rep.segun(op.presupuesto, f"Presupuesto docs excedido en {f.rel}: lectura_minima+espejo_leer={total} > presupuesto_max_docs({maximo})")


def _colgantes(fichas: list[Ficha], rep: Reporte, op: Opciones) -> None:
    existentes = {str(f.fm["id"]) for f in fichas if f.fm.get("id")}
    for f in fichas:
        for clave in CLAVES_REF:
            for ref in lista(f.fm, clave):
                for ident in ID_REF_RE.findall(ref):
                    if ident not in existentes:
                        rep.segun(op.vinculos, f"Vínculo colgante en {f.rel}: {clave} → {ident} (no existe ninguna ficha con ese id)")


def validar(fichas: list[Ficha], rep: Reporte, op: Opciones) -> None:
    for f in fichas:
        if f.tipo == "instruccion":
            _vinculos_instruccion(f, rep, op)
            _presupuesto(f, rep, op)
    _colgantes(fichas, rep, op)
