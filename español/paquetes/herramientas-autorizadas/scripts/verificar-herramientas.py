#!/usr/bin/env python3
"""Verifica las herramientas autorizadas: quién y cuándo autorizó, y anclas existentes. Código 0 = sin errores."""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import uxyn_base as base  # noqa: E402
import uxyn_fichas as fichas  # noqa: E402

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)
SIN_VALOR = (None, "", "null", "<persona o equipo>")


def main() -> int:
    raiz = base.raiz_app(PAQUETE)
    trabajo = base.carpeta_trabajo(PAQUETE, crear=False)
    errores, avisos = [], []
    for f in fichas.listar(PAQUETE, "autorizada"):
        if f.status != "authorized":
            continue
        fm, _ = base.leer_frontmatter(f.ruta.read_text(encoding="utf-8"))
        rel = f.ruta.relative_to(trabajo).as_posix()
        if fm.get("authorized_by") in SIN_VALOR:
            errores.append(f"{rel}: authorized sin authorized_by (lo completa la persona que autoriza)")
        if fm.get("authorized_at") in SIN_VALOR:
            errores.append(f"{rel}: authorized sin authorized_at")
        if str(fm.get("source")) != "human":
            errores.append(f"{rel}: una herramienta autorizada debe tener source: human")
        for ancla in fm.get("anclas_codigo") or []:
            if not (raiz / str(ancla).split(":")[0]).exists():
                avisos.append(f"{rel}: ancla inexistente {ancla}")
    for a in avisos:
        print(f"aviso: {a}")
    for e in errores:
        print(f"error: {e}", file=sys.stderr)
    print(f"herramientas: {len(errores)} errores, {len(avisos)} avisos")
    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main())
