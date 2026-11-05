#!/usr/bin/env python3
"""Verifica las evaluaciones UX/UI: heurística y severidad válidas, evidencia, propuesta en severidad alta, métricas
y que nada figure implementado sin aprobación. Código 0 = sin errores.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
sys.path.insert(0, str(Path(__file__).resolve().parent))

import uxyn_base as base  # noqa: E402
import uxyn_fichas as fichas  # noqa: E402

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)
CON_PROBLEMAS = {"propuesta", "aprobada", "implementada", "validada"}
CON_METRICAS_ANTES = {"propuesta", "aprobada", "implementada", "validada"}
VACIO = {"", "-", "…", "..."}


def tabla(cuerpo: str, titulo: str) -> list[list[str]]:
    dentro, filas, cabecera = False, [], True
    for linea in cuerpo.splitlines():
        if linea.startswith("## "):
            dentro, cabecera = linea[3:].strip().lower() == titulo, True
            continue
        if dentro and linea.startswith("|"):
            c = [x.strip() for x in linea.strip().strip("|").split("|")]
            if cabecera or set("".join(c)) <= set("-: "):
                cabecera = False
                continue
            filas.append(c)
    return filas


def revisar(rel: str, status: str, cuerpo: str, aj: dict) -> tuple[list[str], list[str]]:
    errores, avisos = [], []
    heuristicas = {h.upper() for h in aj.get("heuristicas", [])}
    maxima, umbral = int(aj.get("severidad_max", 4)), int(aj.get("severidad_propuesta_obligatoria", 3))
    problemas = [(f + [""] * 7)[:7] for f in tabla(cuerpo, "problemas")]
    for num, heur, sev, problema, evidencia, propuesta, aprobada in problemas:
        if heur.upper() not in heuristicas:
            errores.append(f"{rel}: problema {num}: heurística «{heur}» no válida")
        if not sev.isdigit() or int(sev) > maxima:
            errores.append(f"{rel}: problema {num}: severidad «{sev}» (0–{maxima})")
        elif int(sev) >= umbral and propuesta in VACIO:
            errores.append(f"{rel}: problema {num}: severidad {sev} sin propuesta")
        if evidencia in VACIO:
            errores.append(f"{rel}: problema {num}: sin evidencia")
        if aprobada.lower() in ("si", "sí", "x") and status in ("abierta", "en-curso", "propuesta"):
            errores.append(f"{rel}: problema {num}: marcado como aprobado pero la evaluación está en «{status}» (aprueba una persona)")
    if status in CON_PROBLEMAS and not problemas:
        avisos.append(f"{rel}: en «{status}» sin problemas registrados")
    metricas = [(f + [""] * 5)[:5] for f in tabla(cuerpo, "métricas")]
    if status in CON_METRICAS_ANTES:
        if not metricas:
            errores.append(f"{rel}: en «{status}» sin métricas (al menos una con Antes, Objetivo y Fuente)")
        for nombre, antes, objetivo, despues, fuente in metricas:
            if VACIO & {antes, objetivo, fuente}:
                errores.append(f"{rel}: métrica «{nombre}» sin Antes, Objetivo o Fuente")
            if status == "validada" and despues in VACIO:
                errores.append(f"{rel}: métrica «{nombre}» sin Después en «validada»")
    if status in ("implementada", "validada") and not any(f[6].lower() in ("si", "sí", "x") for f in problemas):
        errores.append(f"{rel}: «{status}» sin ninguna fila con Aprobada = sí")
    return errores, avisos


def main() -> int:
    aj = base.leer_ajustes(PAQUETE)
    trabajo = base.carpeta_trabajo(PAQUETE, crear=False)
    errores, avisos = [], []
    for f in fichas.listar(PAQUETE, "evaluacion"):
        if f.status in ("archivada", "cancelada"):
            continue
        _, cuerpo = base.leer_frontmatter(f.ruta.read_text(encoding="utf-8"))
        e, a = revisar(f.ruta.relative_to(trabajo).as_posix(), f.status, cuerpo, aj)
        errores += e
        avisos += a
    for a in avisos:
        print(f"aviso: {a}")
    for e in errores:
        print(f"error: {e}", file=sys.stderr)
    print(f"ux: {len(errores)} errores, {len(avisos)} avisos")
    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main())
