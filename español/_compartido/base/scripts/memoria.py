#!/usr/bin/env python3
"""Memoria del sistema (R-24): donde terminan las fichas en lugar de borrarse. Solo para personas.

Uso (desde la raíz del repo; en Windows: py -3 en lugar de python3):
  python3 docs/scripts/memoria.py buscar [TEXTO] [--seccion instrucciones]   busca en el catálogo (no abre fichas)
  python3 docs/scripts/memoria.py ver ID                                      muestra una memoria en la terminal
  python3 docs/scripts/memoria.py guardar RUTA --motivo "…"                  guarda una ficha (ruta relativa a docs/)
  python3 docs/scripts/memoria.py recuperar ID                                la devuelve a <sección>/04-archivadas/
  python3 docs/scripts/memoria.py purgar ID --confirmar ID --motivo "…"      borrado definitivo (dato sensible)
  python3 docs/scripts/memoria.py verificar                                   integridad (lo usan la puerta y doctor)
Todo salvo `verificar` exige una persona en la terminal (o UXYNGRAPHAR_HUMANO=1): un agente no consulta la memoria.
Cada consulta queda en 95-memoria/registro-accesos.jsonl. Guía: 10-guias/memoria.md.
Salida: 0 bien · 1 nada encontrado o problemas de integridad · 2 error o rechazado.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "memoria"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "control"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "nucleo"))

import almacen  # noqa: E402
from terminal import hay_terminal  # noqa: E402
from uxyngraphar_config import cargar, normalizar  # noqa: E402


def es_humano() -> bool:
    return hay_terminal() or os.environ.get("UXYNGRAPHAR_HUMANO") == "1"


def _docs(a: argparse.Namespace) -> tuple[Path, Path]:
    repo, docs = normalizar(Path(a.repo), a.docs)
    return repo, repo / docs


def main(argv: list[str] | None = None) -> int:
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--docs", default="docs")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("buscar", help="buscar en el catálogo")
    p.add_argument("texto", nargs="?", default="")
    p.add_argument("--seccion", default="", choices=["", *almacen.SECCIONES.values()])
    sub.add_parser("ver", help="mostrar una memoria").add_argument("id")
    p = sub.add_parser("guardar", help="guardar una ficha en la memoria")
    p.add_argument("ruta", help="ruta relativa a docs/ (p. ej. 05-instrucciones/04-archivadas/2026-01-10/tarea.md)")
    p.add_argument("--motivo", required=True)
    sub.add_parser("recuperar", help="devolver una memoria a 04-archivadas").add_argument("id")
    p = sub.add_parser("purgar", help="borrado definitivo")
    p.add_argument("id")
    p.add_argument("--confirmar", required=True, help="repite el id")
    p.add_argument("--motivo", required=True)
    sub.add_parser("verificar", help="comprobar la integridad")
    a = ap.parse_args(argv)
    repo, docs = _docs(a)
    if a.cmd == "verificar":
        problemas = almacen.verificar(docs)
        print("\n".join(problemas) if problemas else "Memoria íntegra.")
        return 1 if problemas else 0
    if not es_humano():
        print("RECHAZADO: la memoria solo la consulta una persona en la terminal (R-24). Si una tarea la necesita, pídela en la instrucción.", file=sys.stderr)
        return 2
    try:
        return _ejecutar(a, repo, docs)
    except almacen.ErrorMemoria as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


def _ejecutar(a: argparse.Namespace, repo: Path, docs: Path) -> int:
    if a.cmd == "buscar":
        res = almacen.buscar(docs, a.texto, a.seccion)
        almacen.registrar_acceso(docs, "buscar", detalle=f"{a.texto!r} · {len(res)} resultados")
        for m in res:
            print(f"{m.id} · {m.titulo}\n    guardada {m.guardada} · desde {m.desde} · {m.motivo}")
        print(f"\n{len(res)} memoria(s)." if res else "Nada encontrado.")
        return 0 if res else 1
    if a.cmd == "ver":
        print(almacen.leer(docs, a.id))
        almacen.registrar_acceso(docs, "ver", a.id)
        return 0
    if a.cmd == "guardar":
        m = almacen.guardar(docs, a.ruta.strip().removeprefix("docs/"), a.motivo)
        print(f"Guardada en memoria: {m.id} → {m.ruta}")
        return 0
    if a.cmd == "recuperar":
        destino = almacen.recuperar(docs, a.id)
        print(f"Recuperada: {a.id} → {destino}")
        return 0
    if a.confirmar != a.id:
        print("RECHAZADO: --confirmar debe repetir el id exacto.", file=sys.stderr)
        return 2
    if not cargar(repo, os.path.relpath(docs, repo))[0].get("memoria", {}).get("permitir_purgar", True):
        print("RECHAZADO: este proyecto no permite purgar (uxyngraphar.config.json → memoria.permitir_purgar).", file=sys.stderr)
        return 2
    almacen.purgar(docs, a.id, a.motivo)
    print(f"Purgada: {a.id}. Sigue en el historial de git: si era un dato sensible, límpialo también allí (guía 10-guias/memoria.md).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
