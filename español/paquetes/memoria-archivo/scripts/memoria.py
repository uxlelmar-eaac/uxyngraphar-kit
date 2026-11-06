#!/usr/bin/env python3
"""Memoria y archivo.

  python3 uxyngraphar/paquetes/memoria-archivo/scripts/memoria.py buscar <texto>          (solo si el pedido lo pide)
  python3 uxyngraphar/paquetes/memoria-archivo/scripts/memoria.py archivar <ruta> --humano   (copia al archivo histórico)
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import date
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import uxyn_base as base  # noqa: E402

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)


def buscar(texto: str) -> list[str]:
    trabajo = base.carpeta_trabajo(PAQUETE, crear=False)
    aguja = texto.lower()
    hallazgos = []
    for sub in ("memoria", "archivo"):
        for p in sorted((trabajo / sub).rglob("*.md")) if (trabajo / sub).is_dir() else []:
            for n, linea in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if aguja in linea.lower():
                    hallazgos.append(f"{p.relative_to(trabajo).as_posix()}:{n}: {linea.strip()[:160]}")
    return hallazgos


def archivar(ruta: str) -> Path:
    raiz = base.raiz_app(PAQUETE)
    origen = Path(ruta).resolve()
    if not origen.is_file():
        raise FileNotFoundError(f"no existe {ruta}")
    if raiz in origen.parents and origen.relative_to(raiz).as_posix().startswith(base.CARPETA_PAQUETES + "/"):
        raise ValueError("no se archivan archivos de paquetes")
    destino = base.carpeta_trabajo(PAQUETE) / "archivo" / date.today().isoformat() / origen.name
    if destino.exists():
        raise FileExistsError(f"ya está archivado hoy: {destino}")
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(origen, destino)
    return destino


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("buscar").add_argument("texto")
    ar = sub.add_parser("archivar")
    ar.add_argument("ruta")
    ar.add_argument("--humano", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "buscar":
            for h in buscar(a.texto):
                print(h)
        else:
            if not a.humano:
                raise PermissionError("archivar es una acción de la persona (--humano)")
            print(archivar(a.ruta))
    except (ValueError, FileNotFoundError, FileExistsError, PermissionError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
