#!/usr/bin/env python3
"""Mapa compacto del espejo y código sin espejo.

Uso:  python3 docs/scripts/espejo-mapa.py mapa [--escribir]            # tabla «código → qué hace»
      python3 docs/scripts/espejo-mapa.py faltantes --raices src,lib   # código sin ficha de espejo
`mapa --escribir` guarda docs/50-sistema-integral/mapa.md. Los resúmenes salen de `resumen:` en el frontmatter del espejo
(o de su primera línea de prosa). Salida de `faltantes`: 0 si no falta nada · 1 si hay faltantes.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "espejo"))

from mapa import faltantes, mapa  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("modo", choices=("mapa", "faltantes"))
    ap.add_argument("--repo", default=".")
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--escribir", action="store_true")
    ap.add_argument("--raices", default="src", help="carpetas de código separadas por comas (faltantes)")
    ap.add_argument("--excluir", default="", help="nombres de carpeta adicionales a excluir, separados por comas")
    a = ap.parse_args(argv)
    repo = Path(a.repo).resolve()
    docs = repo / a.docs
    if a.modo == "mapa":
        texto = mapa(docs)
        if a.escribir:
            destino = docs / "50-sistema-integral" / "mapa.md"
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(texto, encoding="utf-8", newline="\n")
            print(f"Escrito {destino}")
        else:
            print(texto)
        return 0
    from mapa import EXCLUIR
    falta = faltantes(docs, repo, [r for r in a.raices.split(",") if r], EXCLUIR + tuple(x for x in a.excluir.split(",") if x))
    print("\n".join(falta) or "Todo el código tiene espejo.")
    if falta:
        print(f"\n{len(falta)} archivo(s) sin espejo. Crea una instrucción `generar-espejo-integral` con estas rutas.", file=sys.stderr)
    return 1 if falta else 0


if __name__ == "__main__":
    raise SystemExit(main())
