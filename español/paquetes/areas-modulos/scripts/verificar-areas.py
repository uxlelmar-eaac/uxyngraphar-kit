#!/usr/bin/env python3
"""Verifica las áreas: sin ciclos de dependencias (error) y dependencias hacia áreas documentadas (aviso). Código 0 = sin errores."""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
sys.path.insert(0, str(Path(__file__).resolve().parent))

import uxyn_base as base  # noqa: E402
import uxyn_fichas as fichas  # noqa: E402

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)


def ciclos(grafo: dict[str, list[str]]) -> list[list[str]]:
    hallados, estado = [], {}

    def visitar(nodo: str, camino: list[str]) -> None:
        estado[nodo] = "en-curso"
        for siguiente in grafo.get(nodo, []):
            if estado.get(siguiente) == "en-curso":
                hallados.append(camino[camino.index(siguiente):] + [siguiente])
            elif siguiente in grafo and siguiente not in estado:
                visitar(siguiente, camino + [siguiente])
        estado[nodo] = "hecho"

    for nodo in grafo:
        if nodo not in estado:
            visitar(nodo, [nodo])
    return hallados


def main() -> int:
    raiz_areas = base.carpeta_trabajo(PAQUETE, crear=False) / fichas.definicion(PAQUETE, "area")["carpeta"]
    grafo: dict[str, list[str]] = {}
    for f in fichas.listar(PAQUETE, "area"):
        fm, _ = base.leer_frontmatter(f.ruta.read_text(encoding="utf-8"))
        if f.status is None:
            continue
        partes = f.ruta.relative_to(raiz_areas).parts
        nombre = partes[0] if len(partes) > 1 else str(fm.get("id") or f.ruta.stem)
        grafo[nombre] = [str(d) for d in (fm.get("depends_on") or []) if str(d).strip()]
    avisos = [f"{area}: depende de «{d}», que aún no está documentada" for area, deps in grafo.items() for d in deps if d not in grafo]
    errores = [f"ciclo de dependencias: {' → '.join(c)}" for c in ciclos(grafo)]
    for a in avisos:
        print(f"aviso: {a}")
    for e in errores:
        print(f"error: {e}", file=sys.stderr)
    print(f"areas: {len(grafo)} áreas, {len(errores)} errores, {len(avisos)} avisos")
    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main())
