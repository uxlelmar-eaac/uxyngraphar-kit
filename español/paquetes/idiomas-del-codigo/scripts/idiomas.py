#!/usr/bin/env python3
"""Revisa el idioma del código: nombres de archivo en ASCII.

  python3 uxyngraphar/paquetes/idiomas-del-codigo/scripts/idiomas.py [ARCHIVO…]

Sin archivos revisa las «raices» de los ajustes. Código 0 = sin problemas; 1 = hay problemas.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import uxyn_base as base  # noqa: E402

PAQUETE = base.carpeta_paquete(AQUI)


def coincide(rel: str, patrones: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel, p) or (p.startswith("**/") and fnmatch.fnmatch(rel, p[3:])) for p in patrones)


def archivos_de_codigo(raiz: Path, ajustes: dict, explicitos: list[str]) -> list[str]:
    extensiones = set(ajustes.get("extensiones", []))
    excluir = ajustes.get("excluir", [])
    if explicitos:
        rels = [Path(a).resolve().relative_to(raiz).as_posix() for a in explicitos]
        return [r for r in rels if Path(r).suffix in extensiones and not coincide(r, excluir)]
    salida = []
    for r in ajustes.get("raices", ["src"]):
        for actual, dirs, archivos in os.walk(raiz / r):
            rel_dir = Path(actual).relative_to(raiz).as_posix()
            dirs[:] = [d for d in dirs if not coincide(f"{rel_dir}/{d}/x", excluir)]
            salida += [f"{rel_dir}/{a}" for a in archivos if Path(a).suffix in extensiones and not coincide(f"{rel_dir}/{a}", excluir)]
    return sorted(salida)


def revisar_nombres(rels: list[str]) -> list[str]:
    return [f"{rel}: nombre de archivo no ASCII; tradúcelo al inglés (referencia/idioma.md)" for rel in rels if not rel.isascii()]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("archivos", nargs="*")
    a = ap.parse_args(argv)
    raiz = base.raiz_app(PAQUETE)
    rels = archivos_de_codigo(raiz, base.leer_ajustes(PAQUETE), a.archivos)
    problemas = revisar_nombres(rels)
    for p in problemas:
        print(p)
    print(f"idiomas-del-codigo: {len(rels)} archivos revisados, {len(problemas)} problemas")
    return 1 if problemas else 0


if __name__ == "__main__":
    raise SystemExit(main())
