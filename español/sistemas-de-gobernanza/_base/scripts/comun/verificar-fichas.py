#!/usr/bin/env python3
"""Verifica las fichas de un sistema según sus ajustes: campos obligatorios («campos_obligatorios»), clave única entre
fichas vigentes («clave_unica») y archivos ancla existentes. Código 0 = sin errores.

Sirve a cualquier sistema con fichas: recorre todos sus tipos de ficha. Una ficha reemplazada o retirada no cuenta como
duplicada. En la clave, `method` se compara en mayúsculas.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el sistema es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import uxyn_base as base  # noqa: E402
import uxyn_fichas as fichas  # noqa: E402

SISTEMA = base.carpeta_sistema(AQUI)
ANCLA = re.compile(r"`([^`…<>*]+\.[A-Za-z0-9]+)`")
FUERA_DE_USO = {"reemplazada", "reemplazado", "retirada", "retirado"}


def anclas(cuerpo: str) -> list[str]:
    """Rutas entre comillas invertidas en las viñetas de las secciones cuyo título menciona «ancla»."""
    dentro, salida = False, []
    for linea in cuerpo.splitlines():
        if linea.startswith("## "):
            dentro = "ancla" in linea.lower()
            continue
        if dentro and linea.lstrip().startswith("-"):
            salida += ANCLA.findall(linea)
    return salida


def revisar(tipo: str, obligatorios: list[str], clave: list[str], raiz: Path, trabajo: Path) -> tuple[list[str], list[str], int]:
    errores: list[str] = []
    avisos: list[str] = []
    vistas: dict[str, str] = {}
    for f in fichas.listar(SISTEMA, tipo):
        fm, cuerpo = base.leer_frontmatter(f.ruta.read_text(encoding="utf-8"))
        rel = f.ruta.relative_to(trabajo).as_posix()
        if not fm:
            continue
        faltan = [c for c in obligatorios if fm.get(c) in (None, "", [])]
        if faltan:
            errores.append(f"{rel}: faltan campos {', '.join(faltan)}")
            continue
        if clave:
            firma = " ".join(str(fm.get(c)).upper() if c == "method" else str(fm.get(c)) for c in clave)
            if firma in vistas and f.status not in FUERA_DE_USO:
                errores.append(f"{rel}: «{firma}» ya está documentada en {vistas[firma]}")
            vistas.setdefault(firma, rel)
        for ancla in anclas(cuerpo):
            if not (raiz / ancla).exists():
                avisos.append(f"{rel}: archivo ancla inexistente {ancla}")
    return errores, avisos, len(vistas)


def main() -> int:
    ajustes = base.leer_ajustes(SISTEMA)
    raiz = base.raiz_app(SISTEMA)
    trabajo = base.carpeta_trabajo(SISTEMA, crear=False)
    codigo = 0
    for tipo in fichas.tipos(SISTEMA):
        errores, avisos, n = revisar(tipo, ajustes.get("campos_obligatorios", []), ajustes.get("clave_unica", []), raiz, trabajo)
        for a in avisos:
            print(f"aviso: {a}")
        for e in errores:
            print(f"error: {e}", file=sys.stderr)
        print(f"{tipo}s: {n} documentadas, {len(errores)} errores, {len(avisos)} avisos")
        codigo = codigo or (1 if errores else 0)
    return codigo


if __name__ == "__main__":
    raise SystemExit(main())
