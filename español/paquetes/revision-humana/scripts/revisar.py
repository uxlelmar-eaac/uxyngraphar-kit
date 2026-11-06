#!/usr/bin/env python3
"""Revisión humana de pendientes de todos los paquetes instalados.

  python3 uxyngraphar/paquetes/revision-humana/scripts/revisar.py pendientes          lista, de la más antigua a la más nueva
  python3 uxyngraphar/paquetes/revision-humana/scripts/revisar.py preparar            escribe trabajo/revision-humana/REVISION.md
  python3 uxyngraphar/paquetes/revision-humana/scripts/revisar.py aplicar --humano    aplica las decisiones escritas en REVISION.md

En REVISION.md la persona escribe en «Decisión» uno de los status de «Opciones» (o «posponer», o lo deja vacío).
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import pendientes as pend  # noqa: E402
import uxyn_base as base  # noqa: E402

REVISION = "REVISION.md"
CABECERA = "| Paquete | Ficha | Status | Días | Título | Opciones | Decisión |"


def ruta_revision() -> Path:
    return base.carpeta_trabajo(pend.PAQUETE) / REVISION


def listar() -> None:
    lista = pend.recoger()
    if not lista:
        print("(nada espera una decisión)")
        return
    for p in lista:
        rel = f"{base.CARPETA_PAQUETES}/{p.paquete}/{' '.join(pend.comando(p, '<status>'))}"
        print(f"{p.id}\t{p.paquete}\t{p.status}\t{p.dias} días\t{p.titulo}\n    persona: python3 {rel}  (status: {', '.join(p.opciones)})")


def preparar() -> Path:
    filas = [f"| {p.paquete} | {p.id} | {p.status} | {p.dias} | {p.titulo} | {', '.join(p.opciones)} |  |" for p in pend.recoger()]
    texto = "\n".join([
        "# Revisión humana de pendientes", "",
        "Generado por `revisar.py preparar`. Una persona escribe en «Decisión» uno de los status de «Opciones» o «posponer»,",
        "y luego ejecuta `python3 uxyngraphar/paquetes/revision-humana/scripts/revisar.py aplicar --humano`.", "",
        CABECERA, "|---|---|---|---|---|---|---|", *(filas or ["| — | — | — | — | (nada espera una decisión) | — |  |"]), ""])
    destino = ruta_revision()
    destino.write_text(texto, encoding="utf-8")
    return destino


def decisiones() -> dict[tuple[str, str], str]:
    ruta = ruta_revision()
    if not ruta.is_file():
        raise FileNotFoundError(f"no hay {REVISION}: ejecuta antes «revisar.py preparar»")
    salida = {}
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if len(celdas) == 7 and celdas[1] not in ("Ficha", "—") and not set(celdas[1]) <= set("-: ") and celdas[6]:
            salida[(celdas[0], celdas[1])] = celdas[6]
    return salida


def aplicar() -> int:
    base.exigir_humano("aplicar decisiones")
    elegidas = decisiones()
    por_ficha = {(p.paquete, p.id): p for p in pend.recoger()}
    entorno = {**os.environ, base.VARIABLE_HUMANO: "1"}
    fallos = 0
    for clave, decision in elegidas.items():
        p = por_ficha.get(clave)
        if decision.lower() == "posponer":
            continue
        if p is None:
            print(f"{clave[1]}: ya no espera decisión (se omite)")
            continue
        if decision not in p.opciones:
            print(f"{p.id}: «{decision}» no es una opción ({', '.join(p.opciones)})", file=sys.stderr)
            fallos += 1
            continue
        args = pend.comando(p, decision)
        r = subprocess.run([sys.executable, "-B", str(p.carpeta / args[0]), *args[1:]], cwd=pend.raiz(), env=entorno,
                           capture_output=True, text=True, stdin=subprocess.DEVNULL)
        print(f"{p.id} → {decision}: {'hecho' if r.returncode == 0 else 'FALLÓ'} {(r.stdout + r.stderr).strip()}")
        fallos += r.returncode != 0
    preparar()
    return 1 if fallos else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("pendientes")
    sub.add_parser("preparar")
    sub.add_parser("aplicar").add_argument("--humano", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "pendientes":
            listar()
        elif a.cmd == "preparar":
            print(preparar())
        else:
            if not a.humano:
                raise PermissionError("aplicar decisiones es una acción de la persona (--humano)")
            return aplicar()
    except (ValueError, FileNotFoundError, PermissionError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
