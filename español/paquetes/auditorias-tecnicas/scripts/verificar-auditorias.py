#!/usr/bin/env python3
"""Verifica hallazgos de auditorías: severidad válida, evidencia presente y findings_count correcto. Código 0 = sin errores."""

from __future__ import annotations

import re
import sys
from datetime import date, datetime
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import uxyn_base as base  # noqa: E402
import uxyn_fichas as fichas  # noqa: E402

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)


def _dias_sin_cambios(fm: dict, ruta: Path) -> int:
    """Días desde `actualizado` (o `fecha`) del frontmatter; si no hay, desde la última modificación del archivo."""
    for clave in ("actualizado", "fecha"):
        try:
            return (date.today() - date.fromisoformat(str(fm.get(clave))[:10])).days
        except ValueError:
            continue
    return (date.today() - datetime.fromtimestamp(ruta.stat().st_mtime).date()).days


LISTA = re.compile(r"^\s*(?:\d+[.)]|[-*])\s+\S")


def filas_hallazgos(cuerpo: str) -> tuple[list[list[str]], int]:
    """(filas de la tabla de hallazgos, elementos en formato lista del 1.x)."""
    dentro, filas, lista = False, [], 0
    for linea in cuerpo.splitlines():
        if linea.startswith("## "):
            dentro = linea.strip().lower() == "## hallazgos"
            continue
        if dentro and linea.startswith("|"):
            celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
            if celdas and celdas[0] not in ("#", "") and not set(celdas[0]) <= set("-: "):
                filas.append(celdas)
        elif dentro and LISTA.match(linea):
            lista += 1
    return filas, lista


def main() -> int:
    ajustes = base.leer_ajustes(PAQUETE)
    severidades = set(ajustes.get("severidades", []))
    trabajo = base.carpeta_trabajo(PAQUETE, crear=False)
    errores, avisos = [], []
    activas = []
    for f in fichas.listar(PAQUETE, "auditoria"):
        fm, cuerpo = base.leer_frontmatter(f.ruta.read_text(encoding="utf-8"))
        rel = f.ruta.relative_to(trabajo).as_posix()
        filas, lista = filas_hallazgos(cuerpo)
        for celdas in filas:
            if len(celdas) < 4 or celdas[1].lower() not in severidades:
                errores.append(f"{rel}: hallazgo {celdas[0]} sin severidad válida ({', '.join(sorted(severidades))})")
            elif not celdas[3]:
                errores.append(f"{rel}: hallazgo {celdas[0]} sin evidencia")
        if lista and not filas:
            avisos.append(f"{rel}: hallazgos en lista (formato 1.x); pásalos a la tabla con severidad y evidencia")
        contados = len(filas) or lista
        declarado = str(fm.get("findings_count", "0"))
        if declarado.isdigit() and int(declarado) != contados:
            (errores if f.status == "cerrada" else avisos).append(f"{rel}: findings_count={declarado} pero hay {contados} hallazgos")
        if f.status == "activa":
            activas.append(rel)
            dias = _dias_sin_cambios(fm, f.ruta)
            if dias > int(ajustes.get("dias_sin_cambios", 14)):
                avisos.append(f"{rel}: activa sin cambios hace {dias} días; propón cerrarla o pasarla a «pendiente»")
    if len(activas) > int(ajustes.get("max_activas", 5)):
        avisos.append(f"{len(activas)} auditorías activas (máximo {ajustes.get('max_activas', 5)}): cierra o pospón alguna")
    for a in avisos:
        print(f"aviso: {a}")
    for e in errores:
        print(f"error: {e}", file=sys.stderr)
    print(f"auditorias: {len(errores)} errores, {len(avisos)} avisos")
    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main())
