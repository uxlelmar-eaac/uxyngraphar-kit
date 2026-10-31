#!/usr/bin/env python3
"""Construye los packs (backend, frontend, …) a partir de una fuente compartida + lo específico de cada rol.

Modelo:
  _compartido/base/…   archivos idénticos en todos los packs (scripts, guías, reglas comunes). SE EDITAN AQUÍ.
  <pack>/…             lo específico del rol (AGENTES.md, plantillas con redacción propia, …) y copias generadas.
  _compartido/generados.txt   manifiesto de lo generado (lo escribe este script; no se edita).
Añadir un rol nuevo = crear su carpeta con lo específico y añadirlo a PACKS.

Uso:  python3 español/_compartido/construir-packs.py              # genera/actualiza las copias
      python3 español/_compartido/construir-packs.py --verificar  # CI: falla (1) si hay deriva
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
BASE = RAIZ / "base"
MANIFIESTO = RAIZ / "generados.txt"
PACKS = ("backend", "frontend")
IGNORAR = ("__pycache__",)


def compartidos(base: Path = BASE) -> list[str]:
    return sorted(p.relative_to(base).as_posix() for p in base.rglob("*") if p.is_file() and not any(i in p.parts for i in IGNORAR) and p.suffix != ".pyc")


def _previos(manifiesto: Path) -> set[str]:
    return set(manifiesto.read_text(encoding="utf-8").split()) if manifiesto.is_file() else set()


def planificar(raiz_packs: Path, packs: tuple[str, ...] = PACKS, base: Path = BASE, manifiesto: Path = MANIFIESTO) -> dict[str, list]:
    """Qué hay que escribir, borrar o qué colisiona. No toca el disco."""
    files, previos = compartidos(base), _previos(manifiesto)
    plan: dict[str, list] = {"escribir": [], "borrar": [], "colisiones": []}
    for pack in packs:
        for rel in files:
            destino = raiz_packs / pack / rel
            origen = base / rel
            if not destino.exists():
                plan["escribir"].append((pack, rel))
            elif destino.read_bytes() != origen.read_bytes():
                (plan["escribir"] if rel in previos else plan["colisiones"]).append((pack, rel))
        for rel in sorted(previos - set(files)):
            if (raiz_packs / pack / rel).exists():
                plan["borrar"].append((pack, rel))
    return plan


def construir(raiz_packs: Path, packs: tuple[str, ...] = PACKS, base: Path = BASE, manifiesto: Path = MANIFIESTO) -> dict[str, list]:
    plan = planificar(raiz_packs, packs, base, manifiesto)
    if plan["colisiones"]:
        return plan   # no se escribe nada: un archivo específico de un pack coincide en ruta con uno compartido
    for pack, rel in plan["escribir"]:
        destino = raiz_packs / pack / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes((base / rel).read_bytes())
    for pack, rel in plan["borrar"]:
        (raiz_packs / pack / rel).unlink()
    manifiesto.write_text("\n".join(compartidos(base)) + "\n", encoding="utf-8", newline="\n")
    return plan


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verificar", action="store_true", help="no escribe; falla si algún pack difiere de la fuente compartida")
    a = ap.parse_args(argv)
    raiz_packs = RAIZ.parent
    plan = planificar(raiz_packs) if a.verificar else construir(raiz_packs)
    for pack, rel in plan["colisiones"]:
        print(f"COLISIÓN {pack}/{rel}: existe y difiere de _compartido/base; muévelo a base/ (si debe ser común) o renómbralo", file=sys.stderr)
    if a.verificar:
        pendientes = len(plan["escribir"]) + len(plan["borrar"]) + len(plan["colisiones"])
        for pack, rel in plan["escribir"] + plan["borrar"]:
            print(f"DERIVA {pack}/{rel}", file=sys.stderr)
        print("OK: los packs coinciden con _compartido/base." if not pendientes else f"{pendientes} diferencia(s): ejecuta construir-packs.py y confirma el resultado.")
        return 1 if pendientes else 0
    if plan["colisiones"]:
        return 1
    print(f"Escritos {len(plan['escribir'])}, borrados {len(plan['borrar'])} en {', '.join(PACKS)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
