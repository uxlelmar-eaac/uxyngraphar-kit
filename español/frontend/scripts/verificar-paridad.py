#!/usr/bin/env python3
"""Verifica la paridad entre packs declarada en PARIDAD-PACKS.md (raíz del pack).

Vive dentro de cada pack. Solo opera cuando el pack hermano está junto a este
(proyecto plantilla). En un repo adoptado (pack aislado) se desactiva solo.
Soporta carpetas hermanas: cliente/servidor o frontend/backend.

Uso:  python3 scripts/verificar-paridad.py      (sale con 1 si hay errores de paridad)
"""

from __future__ import annotations

import fnmatch
import glob
import os
import sys
from pathlib import Path

HERMANOS = {"cliente": "servidor", "servidor": "cliente", "frontend": "backend", "backend": "frontend"}
EXT_ESPEJO = (".md", ".py")


def _filas(texto: str) -> list[tuple[str, str]]:
    """(ruta, tipo) de cada fila de la matriz que empieza por una ruta entre comillas invertidas."""
    out = []
    for linea in texto.splitlines():
        if not linea.startswith("|") or not linea[1:].lstrip(" ").startswith("`"):
            continue
        campos = linea.split("|")
        ruta = campos[1].replace("`", "").replace(" ", "") if len(campos) > 1 else ""
        tipo = campos[2].replace(" ", "") if len(campos) > 2 else ""
        out.append((ruta, tipo))
    return out


def _identicos(texto: str) -> list[str]:
    """Rutas de las filas marcadas «identico» (cualquier columna)."""
    out = []
    for linea in texto.splitlines():
        campos = linea.split("|")
        if any(c.strip(" ") == "identico" for c in campos[1:-1]):
            out.append(campos[1].replace("`", "").replace(" ", ""))
    return out


def _iguales(a: Path, b: Path) -> bool:
    return a.read_bytes() == b.read_bytes()


def _archivos(raiz: Path, ext: tuple[str, ...] | None = None) -> list[str]:
    """Rutas relativas («./x») de los archivos regulares bajo raiz, sin __pycache__."""
    out = []
    for d, dirs, files in os.walk(raiz):
        for f in files:
            p = Path(d) / f
            if p.is_symlink() or not p.is_file():
                continue
            rel = "./" + p.relative_to(raiz).as_posix()
            if "__pycache__" in rel or (ext and not f.endswith(ext)):
                continue
            out.append(rel)
    return sorted(out)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    pack = Path(__file__).resolve().parent.parent
    hermano = HERMANOS.get(pack.name)
    sib = pack.parent / hermano if hermano else None
    if sib is None or not sib.is_dir():
        print("AVISO: pack aislado (sin pack hermano junto a esta carpeta); nada que verificar.")
        return 0
    c, s = (pack, sib) if pack.name in ("cliente", "frontend") else (sib, pack)
    matriz = pack / "PARIDAD-PACKS.md"
    if not matriz.is_file():
        print("ERROR: falta PARIDAD-PACKS.md en la raíz del pack")
        return 1
    texto = matriz.read_text(encoding="utf-8")
    err = 0

    # Archivos «identico»: byte a byte iguales en ambos packs (admite patrones con *)
    for rel in _identicos(texto):
        if not rel:
            continue
        if "*" in rel:
            coincidencias = sorted(glob.glob(glob.escape(str(c)) + "/" + rel))
            for f in coincidencias:
                r = Path(f).relative_to(c).as_posix()
                if not (s / r).is_file():
                    print(f"ERROR: '{r}' (identico) falta en el pack hermano")
                    err = 1
                    continue
                if not _iguales(Path(f), s / r):
                    print(f"ERROR: divergencia en archivo 'identico': {r}")
                    err = 1
            if not coincidencias:
                print(f"ERROR: patrón 'identico' sin coincidencias: {rel}")
                err = 1
            continue
        if not (c / rel).is_file() or not (s / rel).is_file():
            print(f"ERROR: '{rel}' (identico) falta en un pack")
            err = 1
            continue
        if not _iguales(c / rel, s / rel):
            print(f"ERROR: divergencia en archivo 'identico': {rel}")
            err = 1

    # Estructura espejo: mismos paths .md/.py en ambos packs (aviso, no error)
    en_c, en_s = set(_archivos(c, EXT_ESPEJO)), set(_archivos(s, EXT_ESPEJO))
    for rel in sorted(en_c ^ en_s):
        print(f"  solo-cliente: {rel}" if rel in en_c else f"  solo-servidor: {rel}")

    # Cobertura de la matriz (aviso): cada archivo del pack debe tener fila, directa o por patrón con *
    filas = _filas(texto)
    rutas = {r for r, _ in filas}
    patrones = [r for r, _ in filas if "*" in r]
    for rel in _archivos(c):
        if rel.startswith("./.decisiones/"):
            continue
        rel = rel[2:]
        if rel in rutas or any(fnmatch.fnmatchcase(rel, p) for p in patrones):
            continue
        print(f"AVISO: sin fila en PARIDAD-PACKS.md: {rel}")

    # Filas «adaptado»/«especifico» cuyo archivo es idéntico en ambos packs (aviso: reclasificar a «identico»)
    for prel, ptipo in filas:
        if ptipo not in ("adaptado", "especifico") or not prel or "*" in prel:
            continue
        if (c / prel).is_file() and (s / prel).is_file() and _iguales(c / prel, s / prel):
            print(f"AVISO: '{prel}' figura como {ptipo} pero es idéntico en ambos packs")

    print("OK: paridad verificada." if err == 0 else "FALLÓ paridad.")
    return err


if __name__ == "__main__":
    raise SystemExit(main())
