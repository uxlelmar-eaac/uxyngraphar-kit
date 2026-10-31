#!/usr/bin/env python3
"""Imprime el paquete de contexto de una instrucción aprobada: ficha compacta, lectura mínima, espejo y rangos de código.

Uso:  python3 docs/scripts/contexto.py <id|slug|ruta> [--docs docs] [--max-tokens 12000] [--lista]
  --lista   solo el plan (qué incluiría y cuánto pesa), sin imprimir el contenido
  --max-tokens por defecto: UXYNGRAPHAR_MAX_TOKENS (alias de respaldo: uxyngraphar_MAX_TOKENS) o 12000
Lee `lectura_minima` (admite `ruta#seccion` para traer solo una sección), `espejo_leer` y `anclas_codigo` (con rango).
Lo que no cabe en el presupuesto se lista como OMITIDO. Salida: 0 · 2 si no encuentra la instrucción ·
3 si la instrucción incumple R-21 (alcance de código > estándar sin fraccionar o sin ampliación aprobada):
entonces solo imprime la ficha y el motivo, sin código.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "tokens"))

from paquete import construir, localizar_instruccion  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("instruccion")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--max-tokens", type=int, default=int(os.environ.get("UXYNGRAPHAR_MAX_TOKENS") or os.environ.get("uxyngraphar_MAX_TOKENS") or "12000"))
    ap.add_argument("--lista", action="store_true")
    a = ap.parse_args(argv)
    repo = Path(a.repo).resolve()
    docs = repo / a.docs
    ficha = localizar_instruccion(docs, a.instruccion)
    if ficha is None:
        print(f"ERROR: no se encontró la instrucción «{a.instruccion}» en {docs / '05-instrucciones'}", file=sys.stderr)
        return 2
    paq = construir(docs, ficha, a.max_tokens, repo)
    if paq.bloqueos:   # R-21: sin anclas de código hasta corregir la instrucción y tener aprobación
        paq.partes, paq.omitidas = paq.partes[:1], []
        print(paq.render() if not a.lista else "\n".join(f"BLOQUEADO (R-21): {b}" for b in paq.bloqueos))
        return 3
    if not a.lista:   # pedir el contexto abre la fase «Implementación» del costo en tokens (10-guias/costo-tokens.md)
        try:
            import costo
            from paquete import split_frontmatter
            fm, _, _ = split_frontmatter(ficha.read_text(encoding="utf-8"))
            costo.marcar(docs, str(fm.get("id") or ficha.stem), "implementacion", solo_si_falta=True)
        except Exception:  # noqa: BLE001 - medir nunca debe impedir trabajar
            pass
    if a.lista:
        for p in paq.partes:
            print(f"{p.tokens:>6}  {p.titulo}{' — ' + p.nota if p.nota else ''}")
        for p in paq.omitidas:
            print(f"{p.tokens:>6}  OMITIDO {p.titulo}")
        print(f"{paq.total:>6}  TOTAL (~tokens, presupuesto {a.max_tokens})")
        for av in paq.avisos:
            print(f"AVISO: {av}")
        return 0
    print(paq.render())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
