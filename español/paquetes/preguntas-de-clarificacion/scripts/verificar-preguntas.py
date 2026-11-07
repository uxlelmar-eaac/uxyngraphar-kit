#!/usr/bin/env python3
"""Verifica las preguntas del trabajo: las completadas tienen todas sus decisiones elegidas por la persona y su síntesis;
avisa de las que llevan demasiado tiempo en curso y, si existe el trabajo de instrucciones-aprobadas, de la instrucción
enlazada que no está allí. Código 0 = sin errores."""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import preguntas_reglas as reglas  # noqa: E402
import uxyn_base as base  # noqa: E402
import uxyn_fichas as fichas  # noqa: E402

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)


def main() -> int:
    raiz = base.raiz_app(PAQUETE)
    dias_max = int(base.leer_ajustes(PAQUETE).get("dias_en_curso", 7))
    trabajo_instrucciones = raiz / base.CARPETA_TRABAJO / reglas.INSTRUCCIONES
    errores, avisos = [], []
    for f in fichas.listar(PAQUETE, "pregunta"):
        fm, cuerpo = base.leer_frontmatter(f.ruta.read_text(encoding="utf-8"))
        rel = f.ruta.relative_to(raiz).as_posix()
        if f.status == "completada":
            errores += [f"{rel}: {p}" for p in reglas.problemas_completada(cuerpo)]
        if f.status == "en-curso":
            dias = reglas.dias_desde(fm.get("created"))
            if dias is not None and dias > dias_max:
                avisos.append(f"{rel}: en-curso desde hace {dias} días (máximo {dias_max}): ciérrala o cancélala")
        aviso = reglas.aviso_instruccion(trabajo_instrucciones, fm.get("instruccion_id"))
        if aviso:
            avisos.append(f"{rel}: {aviso}")
    for a in avisos:
        print(f"aviso: {a}")
    for e in errores:
        print(f"error: {e}", file=sys.stderr)
    print(f"preguntas-de-clarificacion: {len(errores)} errores, {len(avisos)} avisos")
    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main())
