#!/usr/bin/env python3
"""Copias de seguridad de uxyngraphar: listar, ver, restaurar y limpiar. Guía: docs/10-guias/respaldos.md

Uso:  python3 docs/scripts/respaldos.py listar   [--docs docs]
      python3 docs/scripts/respaldos.py ver       ID [--docs docs]
      python3 docs/scripts/respaldos.py restaurar ID [--archivo RUTA …] [--docs docs] [--aplicar]
      python3 docs/scripts/respaldos.py limpiar   [--dias N] [--minimo N] [--docs docs] [--aplicar]
ID es el que muestra `listar` (p. ej. actualizacion/20261026-090000) o solo la fecha de la carpeta.
Sin --aplicar solo muestra lo que haría. Restaurar y limpiar con --aplicar exigen una persona en la terminal
(o UXYNGRAPHAR_HUMANO=1): los agentes no restauran ni borran copias. Salida: 0 · 1 nada que hacer · 2 error.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "nucleo"))

import respaldos as rs  # noqa: E402
from terminal import hay_terminal  # noqa: E402


def _es_humano() -> bool:
    return hay_terminal() or "1" in (os.environ.get("UXYNGRAPHAR_HUMANO"), os.environ.get("uxyngraphar_HUMANO"))  # minúsculas: alias antiguo


def _linea(r: rs.Respaldo) -> str:
    extra = f" · {r.info['version_antes']} → {r.info['version_despues']}" if r.info.get("version_antes") else ""
    motivo = f" · {r.info['motivo']}" if r.info.get("motivo") else ""
    return f"{r.id:<38} {r.fecha:%Y-%m-%d %H:%M}  {r.dias:>4} d  {len(r.archivos):>3} archivo(s){extra}{motivo}"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("accion", choices=("listar", "ver", "restaurar", "limpiar"))
    ap.add_argument("id", nargs="?")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--archivo", action="append", default=[], help="restaurar solo esta ruta (repetible; tal como la muestra `ver`)")
    ap.add_argument("--dias", type=int)
    ap.add_argument("--minimo", type=int)
    ap.add_argument("--aplicar", action="store_true")
    a = ap.parse_args(argv)
    repo, docs = Path(a.repo).resolve(), a.docs.strip("/")

    if a.accion == "listar":
        lista = rs.listar(repo, docs)
        pol = rs.politica(repo, docs)
        print(f"Política: conservar {pol['conservar_dias']} días · siempre las {pol['conservar_minimo']} más recientes de cada origen · "
              f"limpieza automática {'sí' if pol['limpieza_automatica'] else 'no'}")
        if not lista:
            print("No hay copias de seguridad.")
            return 1
        print("\n".join(_linea(r) for r in lista))
        return 0

    if a.accion == "limpiar":
        if a.aplicar and not _es_humano():
            print("RECHAZADO: borrar copias exige una persona en la terminal (o UXYNGRAPHAR_HUMANO=1).")
            return 2
        lista = rs.limpiar(repo, docs, a.dias, a.minimo, aplicar=a.aplicar)
        if not lista:
            print("Nada que limpiar: ninguna copia supera el plazo (las más recientes se conservan siempre).")
            return 1
        print(("Borradas:" if a.aplicar else "Se borrarían (añade --aplicar):") + "\n" + "\n".join(_linea(r) for r in lista))
        return 0

    if not a.id:
        print("Falta el ID de la copia (míralo con: respaldos.py listar).")
        return 2
    r = rs.buscar(repo, docs, a.id)
    if r is None:
        print(f"No existe la copia {a.id!r}. Usa: respaldos.py listar")
        return 2

    if a.accion == "ver":
        print(_linea(r))
        print(f"Carpeta: {r.carpeta}\nRutas relativas a: {r.base}")
        print("Guardados (vuelven a esta versión al restaurar):\n" + "\n".join(f"  {x}" for x in r.archivos))
        if r.añadidos:
            print("Creados por la operación (se retiran al restaurar la copia entera):\n" + "\n".join(f"  {x}" for x in r.añadidos))
        return 0

    plan = rs.plan_restaurar(r, a.archivo or None)
    if plan["desconocidos"]:
        print("Estas rutas no están en la copia: " + ", ".join(plan["desconocidos"]) + " (usa las que muestra `ver`)")
        return 2
    if not plan["restaurar"] and not plan["retirar"]:
        print("Nada que restaurar.")
        return 1
    if a.archivo and r.origen == "actualizacion":
        print("Aviso: restaurar solo parte de una actualización deja el núcleo distinto del lock; verificar-nucleo lo marcará. "
              "Para deshacer una actualización, restaura la copia entera.")
    print("\n".join([f"  vuelve: {x}" for x in plan["restaurar"]] + [f"  se retira: {x}" for x in plan["retirar"]]))
    if not a.aplicar:
        print("Simulación: añade --aplicar para hacerlo (antes se guarda el estado actual en una copia nueva).")
        return 0
    if not _es_humano():
        print("RECHAZADO: restaurar exige una persona en la terminal (o UXYNGRAPHAR_HUMANO=1).")
        return 2
    _plan, previa = rs.restaurar(repo, docs, r, a.archivo or None)
    print(f"Restaurado desde {r.id}. Estado anterior guardado en {previa} (deshacer: respaldos.py restaurar {r.origen}/{previa.name} --aplicar).")
    if r.origen == "depuracion":
        print("Recuerda quitar la línea correspondiente de 90-archivo/registro-eliminaciones.md si la ficha vuelve a estar viva.")
    print("Revisa con `git status` y haz commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
