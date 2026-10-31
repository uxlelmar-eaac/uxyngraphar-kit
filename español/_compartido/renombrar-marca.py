#!/usr/bin/env python3
"""Renombra la marca del sistema en todo el repositorio fuente: contenido de archivos y nombres de rutas.

Para que un cambio global de marca sea una sola orden auditable, no una búsqueda manual.
Variantes de caso: minúscula y Capitalizado -> la marca tal cual (la marca se escribe siempre en
minúscula); MAYÚSCULAS (variables de entorno) -> la marca en mayúsculas. Con --capitalizar,
Capitalizado -> Marca capitalizada (por si una marca futura lo pide).

Uso:
  python3 renombrar-marca.py --desde <nombre-actual> --hacia <nombre-nuevo>             # simulacro
  python3 renombrar-marca.py --desde <nombre-actual> --hacia <nombre-nuevo> --aplicar   # escribe

Por defecto opera sobre la raíz del repositorio (../.. desde este archivo); --raiz lo cambia.
Excluye carpetas de soporte: .git, .atl, odd, __pycache__, node_modules, .venv, venv.
Salida: 0 = sin colisiones; 1 = colisiones de renombrado, argumentos inválidos o raíz inexistente.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

EXCLUIR_DIRS = (".git", ".atl", "odd", "__pycache__", "node_modules", ".venv", "venv")
BINARIOS = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".zip", ".pyc", ".woff", ".woff2", ".pdf", ".exe", ".dll"}
SLUG = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


def variantes(desde: str, hacia: str, capitalizar: bool = False) -> list[tuple[bytes, bytes]]:
    """Pares (buscar, reemplazar) en bytes: seguros ante codificación y fines de línea."""
    cap = hacia.capitalize() if capitalizar else hacia
    return [
        (desde.encode("utf-8"), hacia.encode("utf-8")),
        (desde.upper().encode("utf-8"), hacia.upper().encode("utf-8")),
        (desde.capitalize().encode("utf-8"), cap.encode("utf-8")),
    ]


def _caminar(raiz: Path):
    for dirpath, dirnames, filenames in os.walk(raiz, topdown=True):
        dirnames[:] = sorted(d for d in dirnames if d not in EXCLUIR_DIRS)
        yield Path(dirpath), dirnames, filenames


def planificar(raiz: Path, pares: list[tuple[bytes, bytes]]) -> dict:
    """Qué archivos cambian (recuento por variante) y qué rutas se renombran. No toca el disco."""
    cambios, renombrar, colisiones = [], [], []
    for dirpath, _, filenames in _caminar(raiz):
        for nombre in filenames:
            p = dirpath / nombre
            if p.suffix.lower() in BINARIOS:
                continue
            datos = p.read_bytes()
            conteos = {busca.decode(): n for busca, _ in pares if (n := datos.count(busca))}
            if conteos:
                cambios.append((p, conteos))
    candidatos = []
    for dirpath, dirnames, filenames in _caminar(raiz):
        for nombre in list(dirnames) + filenames:
            nuevo = nombre
            for busca, reemp in pares:
                nuevo = nuevo.replace(busca.decode(), reemp.decode())
            if nuevo != nombre:
                candidatos.append((dirpath / nombre, dirpath / nuevo))
    destinos = set()
    for origen, destino in sorted(candidatos, key=lambda par: len(par[0].parts), reverse=True):
        if destino.exists() or destino in destinos:
            colisiones.append((origen, destino))
        else:
            destinos.add(destino)
            renombrar.append((origen, destino))
    return {"cambios": cambios, "renombrar": renombrar, "colisiones": colisiones}


def aplicar(raiz: Path, pares: list[tuple[bytes, bytes]]) -> dict:
    """Escribe contenido y renombra rutas (lo más profundo primero). Con colisiones no escribe nada."""
    plan = planificar(raiz, pares)
    if plan["colisiones"]:
        return plan
    for p, _ in plan["cambios"]:
        datos = p.read_bytes()
        for busca, reemp in pares:
            datos = datos.replace(busca, reemp)
        p.write_bytes(datos)
    for origen, destino in plan["renombrar"]:
        origen.rename(destino)
    return plan


def imprimir(plan: dict, raiz: Path, aplicado: bool) -> None:
    modo = "APLICADO" if aplicado else "SIMULACRO (nada escrito; --aplicar para ejecutar)"
    total = sum(sum(c.values()) for _, c in plan["cambios"])
    print(f"[{modo}] {total} ocurrencias en {len(plan['cambios'])} archivos; {len(plan['renombrar'])} rutas renombradas")
    for p, conteos in plan["cambios"]:
        detalle = ", ".join(f"{v}×{n}" for v, n in sorted(conteos.items()))
        print(f"  {p.relative_to(raiz)}: {detalle}")
    for origen, destino in plan["renombrar"]:
        print(f"  renombrar: {origen.relative_to(raiz)} -> {destino.relative_to(raiz)}")
    for origen, destino in plan["colisiones"]:
        print(f"  COLISIÓN: {origen.relative_to(raiz)} -> {destino.relative_to(raiz)} (el destino ya existe)", file=sys.stderr)


def _error(msg: str) -> int:
    print(f"error: {msg}", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--desde", required=True, help="marca actual, slug en minúscula (p. ej. mimarca)")
    ap.add_argument("--hacia", required=True, help="marca nueva, slug en minúscula")
    ap.add_argument("--raiz", type=Path, default=None, help="carpeta a barrer (por defecto, la raíz del repo)")
    ap.add_argument("--aplicar", action="store_true", help="escribe los cambios (sin esto es un simulacro)")
    ap.add_argument("--capitalizar", action="store_true", help="Capitalizado -> Marca capitalizada")
    a = ap.parse_args(argv)

    if not SLUG.match(a.desde) or not SLUG.match(a.hacia):
        return _error("los nombres deben ser slugs en minúscula (letras, dígitos y guiones)")
    if a.desde == a.hacia:
        return _error("--desde y --hacia son iguales")
    if a.desde in a.hacia:
        return _error("--hacia no puede contener --desde (provocaría reemplazos recursivos)")
    raiz = (a.raiz or Path(__file__).resolve().parents[2]).resolve()
    if not raiz.is_dir():
        return _error(f"la raíz no existe: {raiz}")

    pares = variantes(a.desde, a.hacia, a.capitalizar)
    plan = aplicar(raiz, pares) if a.aplicar else planificar(raiz, pares)
    imprimir(plan, raiz, a.aplicar)
    return 1 if plan["colisiones"] else 0


if __name__ == "__main__":
    sys.exit(main())
