#!/usr/bin/env python3
"""Revisa calidad de código: límite de líneas, nombres de archivo ASCII y (con --commits) mensajes de commit.

  python3 uxyngraphar/paquetes/calidad-de-codigo/scripts/revisar.py [ARCHIVO…] [--commits [N]]

Sin archivos revisa las «raices» de los ajustes. Código 0 = sin problemas; 1 = hay problemas.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import uxyn_base as base  # noqa: E402

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)
CONVENCIONAL = re.compile(r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9._/-]+\))?!?: \S.{0,70}$")


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
        inicio = raiz / r
        for actual, dirs, archivos in os.walk(inicio):
            rel_dir = Path(actual).relative_to(raiz).as_posix()
            dirs[:] = [d for d in dirs if not coincide(f"{rel_dir}/{d}/x", excluir)]
            salida += [f"{rel_dir}/{a}" for a in archivos if Path(a).suffix in extensiones and not coincide(f"{rel_dir}/{a}", excluir)]
    return sorted(salida)


def revisar_archivos(raiz: Path, ajustes: dict, rels: list[str]) -> list[str]:
    limite = int(ajustes.get("limite_lineas", 350))
    exentos = ajustes.get("exenciones_lineas", [])
    problemas = []
    for rel in rels:
        if not rel.isascii() or " " in rel:
            problemas.append(f"{rel}: nombre de archivo no ASCII o con espacios")
        try:
            lineas = len((raiz / rel).read_text(encoding="utf-8", errors="replace").splitlines())
        except OSError:
            continue
        if lineas > limite and not coincide(rel, exentos):
            problemas.append(f"{rel}: {lineas} líneas (límite {limite}); divide por responsabilidad (docs/limite-lineas.md)")
    return problemas


def revisar_commits(raiz: Path, cantidad: int) -> list[str]:
    r = subprocess.run(["git", "log", f"-n{cantidad}", "--no-merges", "--format=%h %s"], cwd=raiz, capture_output=True, text=True)
    if r.returncode != 0:
        return []
    problemas = []
    for linea in r.stdout.splitlines():
        sha, _, asunto = linea.partition(" ")
        if not CONVENCIONAL.match(asunto) or not asunto.isascii():
            problemas.append(f"commit {sha}: «{asunto}» no cumple Conventional Commits en inglés ASCII (≤72 caracteres)")
    return problemas


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("archivos", nargs="*")
    ap.add_argument("--commits", nargs="?", const=-1, type=int, default=None)
    a = ap.parse_args(argv)
    raiz = base.raiz_app(PAQUETE)
    ajustes = base.leer_ajustes(PAQUETE)
    rels = archivos_de_codigo(raiz, ajustes, a.archivos)
    problemas = revisar_archivos(raiz, ajustes, rels)
    if a.commits is not None:
        problemas += revisar_commits(raiz, a.commits if a.commits > 0 else int(ajustes.get("commits_revisar", 20)))
    for p in problemas:
        print(p)
    print(f"calidad-de-codigo: {len(rels)} archivos revisados, {len(problemas)} problemas")
    return 1 if problemas else 0


if __name__ == "__main__":
    raise SystemExit(main())
