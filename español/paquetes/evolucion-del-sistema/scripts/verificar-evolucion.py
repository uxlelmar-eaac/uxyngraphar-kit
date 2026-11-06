#!/usr/bin/env python3
"""Verifica las EVO: tipo válido, evidencia y propuesta presentes, paquete citado instalado. Código 0 = sin errores."""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import uxyn_base as base  # noqa: E402
import uxyn_fichas as fichas  # noqa: E402

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)


def seccion(cuerpo: str, titulo: str) -> str:
    dentro, lineas = False, []
    for linea in cuerpo.splitlines():
        if linea.startswith("## "):
            dentro = linea[3:].strip().lower() == titulo
            continue
        if dentro:
            lineas.append(linea)
    return "\n".join(lineas).strip()


def main() -> int:
    tipos = set(base.leer_ajustes(PAQUETE).get("tipos", []))
    instalados = base.raiz_app(PAQUETE) / base.CARPETA_PAQUETES
    errores, avisos = [], []
    for f in fichas.listar(PAQUETE, "evo"):
        fm, cuerpo = base.leer_frontmatter(f.ruta.read_text(encoding="utf-8"))
        if fm.get("tipo") not in tipos:
            errores.append(f"{f.id}: tipo «{fm.get('tipo')}» fuera de {', '.join(sorted(tipos))}")
        for titulo in ("evidencia", "propuesta"):
            texto = seccion(cuerpo, titulo)
            if f.status == "pending" and (not texto or texto.startswith(("Dónde se notó", "Qué cambiaría"))):
                avisos.append(f"{f.id}: sección «{titulo}» sin rellenar")
        paquete = fm.get("paquete")
        if paquete not in (None, "", "null") and not (instalados / str(paquete)).is_dir():
            avisos.append(f"{f.id}: cita el paquete «{paquete}», que no está instalado")
    for a in avisos:
        print(f"aviso: {a}")
    for e in errores:
        print(f"error: {e}", file=sys.stderr)
    print(f"evolucion-del-sistema: {len(errores)} errores, {len(avisos)} avisos")
    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main())
