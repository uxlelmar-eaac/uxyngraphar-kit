#!/usr/bin/env python3
"""Exporta las fichas EVO del proyecto a un informe para el repo fuente de uxyngraphar (la cola 46 es un buzón hacia el pack).

Uso:  python3 docs/scripts/exportar-evo.py [--docs docs] [--salida propuestas.md] [--estados pending,approved] [--todas] [--marcar]
  --salida   escribe el informe en un archivo (por defecto lo imprime)
  --todas    incluye las ya exportadas
  --marcar   añade `exportada_al_pack: AAAA-MM-DD` a cada ficha exportada (para no repetirlas). Sin esta opción no escribe nada en docs/.
Salida: 0 · 1 si no hay fichas que exportar.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "evolucion"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "nucleo"))

import exportar  # noqa: E402
import lock  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--salida")
    ap.add_argument("--estados", default=",".join(exportar.POR_DEFECTO))
    ap.add_argument("--todas", action="store_true")
    ap.add_argument("--marcar", action="store_true")
    a = ap.parse_args(argv)
    repo = Path(a.repo).resolve()
    docs = repo / a.docs
    items = exportar.fichas(docs, tuple(e.strip() for e in a.estados.split(",") if e.strip()), a.todas)
    if not items:
        print("No hay fichas EVO que exportar.")
        return 1
    datos = lock.leer(repo, a.docs) or {}
    texto = exportar.informe(docs, items, repo.name, datos.get("version", lock.version_de(docs)))
    if a.salida:
        Path(a.salida).write_text(texto, encoding="utf-8", newline="\n")
        print(f"Informe escrito: {a.salida} ({len(items)} ficha(s)). Envíalo a quien mantiene uxyngraphar.")
    else:
        print(texto, end="")
    if a.marcar:
        print(f"Marcadas como exportadas: {exportar.marcar(items)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
