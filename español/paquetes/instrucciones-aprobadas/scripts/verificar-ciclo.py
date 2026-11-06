#!/usr/bin/env python3
"""Verifica las instrucciones del trabajo: alcance, fechas de aprobación/cierre y anclas existentes. Código 0 = sin errores."""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import ciclo_reglas as reglas  # noqa: E402
import uxyn_base as base  # noqa: E402
import uxyn_fichas as fichas  # noqa: E402

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)
ACTIVAS = {"awaiting_approval", "approved"}


def main() -> int:
    raiz = base.raiz_app(PAQUETE)
    ajustes = base.leer_ajustes(PAQUETE)
    errores, avisos = [], []
    for f in fichas.listar(PAQUETE, "instruccion"):
        fm, _ = base.leer_frontmatter(f.ruta.read_text(encoding="utf-8"))
        rel = f.ruta.relative_to(raiz).as_posix()
        vacio = (None, "", "null")
        if f.status in ACTIVAS:
            errores += [f"{rel}: {p}" for p in reglas.problemas_alcance(fm, ajustes)]
            for ancla in reglas.lista(fm.get("anclas_codigo")):
                if not (raiz / reglas.separar_ancla(ancla)[0]).exists():
                    avisos.append(f"{rel}: ancla inexistente {ancla}")
        if f.status in ("approved", "done") and fm.get("approved_at") in vacio:
            (errores if f.status == "approved" else avisos).append(f"{rel}: {f.status} sin approved_at")
        if f.status == "done" and fm.get("executed_at") in vacio:
            avisos.append(f"{rel}: done sin executed_at")
    for a in avisos:
        print(f"aviso: {a}")
    for e in errores:
        print(f"error: {e}", file=sys.stderr)
    print(f"instrucciones-aprobadas: {len(errores)} errores, {len(avisos)} avisos")
    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main())
