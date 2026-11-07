#!/usr/bin/env python3
"""Verifica reglas y excepciones, y evalúa las reglas activas sobre el código. Código 0 = sin errores."""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import reglas_datos as datos  # noqa: E402


def main() -> int:
    errores, avisos = [], []
    reglas = {f.id: f.status for f, _, _ in datos.fichas_de("regla")}
    for f, fm, _ in datos.fichas_de("regla"):
        problemas = datos.problemas_regla(fm)
        (errores if f.status == "activa" else avisos).extend(f"{f.id}: {p}" for p in problemas)
    for f, fm, _ in datos.fichas_de("excepcion"):
        if fm.get("regla") not in reglas:
            (errores if f.status == "aprobada" else avisos).append(f"{f.id}: cita la regla «{fm.get('regla')}», que no existe")
        if f.status == "aprobada" and fm.get("aprobada_por") in datos.VACIO:
            avisos.append(f"{f.id}: aprobada sin «aprobada_por»")
    for h in datos.comprobar():
        texto = f"{h['archivo']}: {h['regla']} {h['motivo']}"
        if h["excusado"]:
            continue
        (errores if h["nivel"] == "bloqueante" else avisos).append(texto)
    for a in avisos:
        print(f"aviso: {a}")
    for e in errores:
        print(f"error: {e}", file=sys.stderr)
    print(f"reglas-del-proyecto: {len(errores)} errores, {len(avisos)} avisos")
    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main())
