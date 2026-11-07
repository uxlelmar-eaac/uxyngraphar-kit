#!/usr/bin/env python3
"""Revisa mensajes de commit: Conventional Commits, en inglés ASCII y de 72 caracteres como máximo.

  python3 uxyngraphar/paquetes/mensajes-de-commit/scripts/commits.py [N]                 últimos N commits sin merges
  python3 uxyngraphar/paquetes/mensajes-de-commit/scripts/commits.py --mensaje "TEXTO"   un mensaje antes de hacer el commit

Sin N revisa los últimos «commits_revisar» de los ajustes. Código 0 = sin problemas; 1 = hay problemas.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import uxyn_base as base  # noqa: E402

PAQUETE = base.carpeta_paquete(AQUI)
CONVENCIONAL = re.compile(r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9._/-]+\))?!?: \S.*$")
MAXIMO = 72
MOTIVO = f"no cumple Conventional Commits en inglés ASCII (≤{MAXIMO} caracteres)"


def asunto_valido(asunto: str) -> bool:
    return bool(CONVENCIONAL.match(asunto)) and asunto.isascii() and len(asunto) <= MAXIMO


def ultimos_asuntos(raiz: Path, cantidad: int) -> list[tuple[str, str]] | None:
    r = subprocess.run(["git", "log", f"-n{cantidad}", "--no-merges", "--format=%h %s"], cwd=raiz, capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return [(sha, asunto) for sha, _, asunto in (linea.partition(" ") for linea in r.stdout.splitlines())]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cantidad", nargs="?", type=int, help="número de commits a revisar (por defecto, commits_revisar)")
    ap.add_argument("--mensaje", help="mensaje propuesto; solo se revisa su primera línea (el asunto)")
    a = ap.parse_args(argv)
    if a.mensaje is not None:
        asunto = a.mensaje.splitlines()[0] if a.mensaje.strip() else ""
        if asunto_valido(asunto):
            print("mensajes-de-commit: mensaje válido")
            return 0
        print(f"mensaje: «{asunto}» {MOTIVO}")
        return 1
    cantidad = a.cantidad if a.cantidad and a.cantidad > 0 else int(base.leer_ajustes(PAQUETE).get("commits_revisar", 20))
    commits = ultimos_asuntos(base.raiz_app(PAQUETE), cantidad)
    if commits is None:
        print("mensajes-de-commit: fuera de un repositorio git (o sin commits); nada que revisar")
        return 0
    problemas = [f"commit {sha}: «{asunto}» {MOTIVO}" for sha, asunto in commits if not asunto_valido(asunto)]
    for p in problemas:
        print(p)
    print(f"mensajes-de-commit: {len(commits)} commits revisados, {len(problemas)} problemas")
    return 1 if problemas else 0


if __name__ == "__main__":
    raise SystemExit(main())
