#!/usr/bin/env python3
"""Verifica las fichas de rutas: campos obligatorios, clave única y archivos ancla existentes. Código 0 = sin errores.

Campos y clave se leen de los ajustes del paquete («campos_obligatorios», «clave_unica»).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import uxyn_base as base  # noqa: E402
import uxyn_fichas as fichas  # noqa: E402

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)
ANCLA = re.compile(r"`([^`…<>*]+\.[A-Za-z0-9]+)`")


def anclas(cuerpo: str) -> list[str]:
    dentro, salida = False, []
    for linea in cuerpo.splitlines():
        if linea.startswith("## "):
            dentro = "ancla" in linea.lower()
            continue
        if dentro and linea.lstrip().startswith("-"):
            salida += ANCLA.findall(linea)
    return salida


def main() -> int:
    ajustes = base.leer_ajustes(PAQUETE)
    obligatorios = ajustes.get("campos_obligatorios", [])
    clave = ajustes.get("clave_unica", [])
    raiz = base.raiz_app(PAQUETE)
    trabajo = base.carpeta_trabajo(PAQUETE, crear=False)
    errores, avisos, vistas = [], [], {}
    for f in fichas.listar(PAQUETE, "ruta"):
        fm, cuerpo = base.leer_frontmatter(f.ruta.read_text(encoding="utf-8"))
        rel = f.ruta.relative_to(trabajo).as_posix()
        if not fm:
            continue
        faltan = [c for c in obligatorios if fm.get(c) in (None, "", [])]
        if faltan:
            errores.append(f"{rel}: faltan campos {', '.join(faltan)}")
            continue
        firma = " ".join(str(fm.get(c)).upper() if c == "method" else str(fm.get(c)) for c in clave)
        if firma in vistas and f.status not in ("deprecada", "retirada"):
            errores.append(f"{rel}: «{firma}» ya está documentada en {vistas[firma]}")
        vistas.setdefault(firma, rel)
        for ancla in anclas(cuerpo):
            if not (raiz / ancla).exists():
                avisos.append(f"{rel}: archivo ancla inexistente {ancla}")
    for a in avisos:
        print(f"aviso: {a}")
    for e in errores:
        print(f"error: {e}", file=sys.stderr)
    print(f"rutas: {len(vistas)} documentadas, {len(errores)} errores, {len(avisos)} avisos")
    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main())
