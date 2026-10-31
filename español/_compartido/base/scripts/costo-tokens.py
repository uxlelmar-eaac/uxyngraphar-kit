#!/usr/bin/env python3
"""Costo en tokens de cada instrucción, por fases. Guía: docs/10-guias/costo-tokens.md

Uso:  python3 docs/scripts/costo-tokens.py fase <id> <analisis|instruccion|implementacion|verificacion|cierre>
      python3 docs/scripts/costo-tokens.py registrar <id> <fase> --entrada N --salida N [--cache-lectura N] [--cache-escritura N]
      python3 docs/scripts/costo-tokens.py medir <id> [--transcripciones DIR]   # escribe la tabla en la sección «Costo en tokens»
      python3 docs/scripts/costo-tokens.py ver <id>                             # muestra sin escribir
      python3 docs/scripts/costo-tokens.py resumen [--json]                     # todas las instrucciones medidas, con medias por fase
`instruccion` se marca solo al crear la ficha (decisiones.py new) e `implementacion` al pedir el contexto (contexto.py);
`decisiones.py cerrar` cierra la medición y escribe la tabla. <id> admite id, slug o ruta. Opciones comunes: --repo . --docs docs
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI / "tokens"))
sys.path.insert(0, str(AQUI / "decisiones"))

import costo  # noqa: E402
from common_frontmatter import split_frontmatter  # noqa: E402

SECCIONES = ("05-instrucciones",)


def localizar(docs: Path, ref: str) -> Path | None:
    directa = Path(ref)
    if directa.is_file():
        return directa.resolve()
    for seccion in SECCIONES:
        for md in sorted((docs / seccion).rglob("*.md")):
            if md.name.startswith("_") or md.name == "README.md":
                continue
            fm, _, _ = split_frontmatter(md.read_text(encoding="utf-8", errors="replace"))
            ident = str(fm.get("id", ""))
            if ref in (ident, md.stem) or ident.endswith("-" + ref):
                return md
    return None


def ident_de(ficha: Path) -> str:
    fm, _, _ = split_frontmatter(ficha.read_text(encoding="utf-8", errors="replace"))
    return str(fm.get("id") or ficha.stem)


def resumen(docs: Path) -> list[dict]:
    filas = []
    for seccion in SECCIONES:
        for md in sorted((docs / seccion).rglob("*.md")):
            if md.name.startswith("_"):
                continue
            d = costo.leer_datos(md)
            if d:
                filas.append({"id": d["id"], "ruta": md.relative_to(docs).as_posix(), "total": sum(costo.total(v) for v in d["fases"].values()),
                              "fases": {f: costo.total(v) for f, v in d["fases"].items()}, "fuente": d.get("fuente", "")})
    return filas


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("accion", choices=("fase", "registrar", "medir", "ver", "resumen"))
    ap.add_argument("id", nargs="?")
    ap.add_argument("fase", nargs="?", choices=costo.FASES)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--transcripciones")
    ap.add_argument("--json", action="store_true")
    for c in ("entrada", "salida", "cache-lectura", "cache-escritura"):
        ap.add_argument(f"--{c}", type=int, default=0)
    a = ap.parse_args(argv)
    repo = Path(a.repo).resolve()
    docs = repo / a.docs.strip("/")

    if a.accion == "resumen":
        filas = resumen(docs)
        if a.json:
            print(json.dumps(filas, ensure_ascii=False, indent=2))
            return 0 if filas else 1
        if not filas:
            print("Ninguna instrucción tiene todavía su costo medido.")
            return 1
        for r in filas:
            print(f"{r['total']:>10,}  {r['id']}  ({r['fuente']})".replace(",", " "))
        print("\nMedia por fase (tokens):")
        for f in costo.FASES:
            print(f"  {costo.NOMBRES[f]:<28} {round(sum(r['fases'].get(f, 0) for r in filas) / len(filas)):>10,}".replace(",", " "))
        print(f"  {'Total por instrucción':<28} {round(sum(r['total'] for r in filas) / len(filas)):>10,}".replace(",", " "))
        return 0

    if not a.id:
        print("Falta el id de la instrucción.", file=sys.stderr)
        return 2
    ficha = localizar(docs, a.id)
    ident = ident_de(ficha) if ficha else a.id
    if a.accion in ("fase", "registrar"):
        if not a.fase:
            print(f"Falta la fase: {', '.join(costo.FASES)}", file=sys.stderr)
            return 2
        if a.accion == "fase":
            costo.marcar(docs, ident, a.fase)
            print(f"{ident}: fase «{costo.NOMBRES[a.fase]}» desde ahora.")
        else:
            costo.registrar(docs, ident, a.fase, entrada=a.entrada, salida=a.salida, cache_lectura=a.cache_lectura, cache_escritura=a.cache_escritura)
            print(f"{ident}: registrado en «{costo.NOMBRES[a.fase]}».")
        return 0
    if ficha is None:
        print(f"No encuentro la instrucción «{a.id}».", file=sys.stderr)
        return 2
    m = costo.medir(repo, docs, ident, ficha, a.transcripciones)
    if a.accion == "medir":
        costo.escribir(ficha, m)
        print(f"Tabla escrita en {ficha.relative_to(repo).as_posix()} (sección «Costo en tokens»).")
    print(costo.render(m).split(costo.FIN)[0].replace(costo.INI, "").split("<!-- tokens:datos")[0].strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
