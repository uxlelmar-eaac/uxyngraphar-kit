#!/usr/bin/env python3
"""Escanea la app en busca de secretos (por contenido y por nombre de archivo). Código 0 = limpio; 1 = hallazgos.

  python3 uxyngraphar/paquetes/secretos-y-credenciales/scripts/escanear.py [--git] [--informe] [RUTA…]

Sin RUTA usa «raices» de los ajustes. --git: solo archivos versionados o preparados. Los valores siempre salen enmascarados.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import patrones_secretos as pat  # noqa: E402
import uxyn_base as base  # noqa: E402

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)


def excluido(rel: str, patrones: list[str]) -> bool:
    for p in patrones:
        if fnmatch.fnmatch(rel, p) or (p.startswith("**/") and fnmatch.fnmatch(rel, p[3:])):
            return True
    return False


def candidatos(raiz: Path, raices: list[str], excluir: list[str]) -> list[str]:
    salida = []
    for r in raices:
        inicio = (raiz / r).resolve()
        if inicio.is_file():
            salida.append(inicio.relative_to(raiz).as_posix())
            continue
        for actual, dirs, archivos in os.walk(inicio):
            rel_dir = Path(actual).relative_to(raiz).as_posix()
            rel_dir = "" if rel_dir == "." else rel_dir + "/"
            dirs[:] = [d for d in dirs if not excluido(f"{rel_dir}{d}/x", excluir)]
            salida += [f"{rel_dir}{a}" for a in archivos if not excluido(f"{rel_dir}{a}", excluir)]
    return sorted(set(salida))


def de_git(raiz: Path) -> list[str]:
    r = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=raiz, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("--git: no es un repositorio git")
    return sorted(set(r.stdout.split("\n")) - {""})


def escanear(raiz: Path, rutas: list[str], ajustes: dict) -> list[str]:
    hallazgos = []
    limite = int(ajustes.get("max_kb", 512)) * 1024
    for rel in rutas:
        if excluido(rel, ajustes.get("permitir", [])) or excluido(rel, ajustes.get("excluir", [])):
            continue
        if pat.archivo_prohibido(rel):
            hallazgos.append(f"{rel}: archivo de secretos (por nombre); no debe versionarse")
            continue
        ruta = raiz / rel
        try:
            if not ruta.is_file() or ruta.stat().st_size > limite:
                continue
            texto = ruta.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        hallazgos += [f"{h.ruta}:{h.linea}: {h.tipo} ({h.muestra})" for h in pat.escanear_texto(rel, texto)]
    return hallazgos


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rutas", nargs="*")
    ap.add_argument("--git", action="store_true")
    ap.add_argument("--informe", action="store_true")
    a = ap.parse_args(argv)
    raiz = base.raiz_app(PAQUETE)
    ajustes = base.leer_ajustes(PAQUETE)
    try:
        rutas = de_git(raiz) if a.git else candidatos(raiz, a.rutas or ajustes.get("raices", ["."]), ajustes.get("excluir", []))
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    hallazgos = escanear(raiz, rutas, ajustes)
    resumen = f"secretos: {len(rutas)} archivos revisados, {len(hallazgos)} hallazgos"
    for h in hallazgos:
        print(h)
    print(resumen)
    if a.informe:
        destino = base.carpeta_trabajo(PAQUETE) / "informes" / f"escaneo-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(f"# Escaneo de secretos\n\n{resumen}\n\n" + "".join(f"- {h}\n" for h in hallazgos), encoding="utf-8")
        print(f"informe: {destino}")
    return 1 if hallazgos else 0


if __name__ == "__main__":
    raise SystemExit(main())
