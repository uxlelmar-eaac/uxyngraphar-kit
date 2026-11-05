"""Correspondencia código ↔ espejo, compartida por espejo.py y verificar-espejo.py."""

from __future__ import annotations

import fnmatch
import os
from pathlib import Path

import uxyn_base as base


def coincide(rel: str, patrones: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel, p) or (p.startswith("**/") and fnmatch.fnmatch(rel, p[3:])) for p in patrones)


def carpeta_espejo(paquete: Path) -> Path:
    return base.carpeta_trabajo(paquete, crear=False)


def ruta_espejo(paquete: Path, rel_codigo: str, es_carpeta: bool) -> Path:
    destino = carpeta_espejo(paquete) / rel_codigo
    return destino / "README.md" if es_carpeta else destino.with_suffix(".md")


def codigo(paquete: Path, ajustes: dict) -> tuple[list[str], list[str]]:
    """(archivos, carpetas) de código bajo las raíces, relativos a la raíz de la app."""
    raiz = base.raiz_app(paquete)
    extensiones, excluir = set(ajustes.get("extensiones", [])), ajustes.get("excluir", [])
    archivos, carpetas = [], []
    for r in ajustes.get("raices", ["src"]):
        for actual, dirs, nombres in os.walk(raiz / r):
            rel_dir = Path(actual).relative_to(raiz).as_posix()
            dirs[:] = sorted(d for d in dirs if not coincide(f"{rel_dir}/{d}/x", excluir))
            carpetas.append(rel_dir)
            archivos += [f"{rel_dir}/{n}" for n in sorted(nombres)
                         if Path(n).suffix in extensiones and not coincide(f"{rel_dir}/{n}", excluir)]
    return archivos, carpetas


def huerfanos(paquete: Path, ajustes: dict) -> list[str]:
    """Espejos bajo una raíz de código cuyo archivo o carpeta ya no existe."""
    raiz = base.raiz_app(paquete)
    espejo = carpeta_espejo(paquete)
    salida = []
    for r in ajustes.get("raices", ["src"]):
        for md in sorted((espejo / r).rglob("*.md")) if (espejo / r).is_dir() else []:
            rel = md.relative_to(espejo)
            if md.name.startswith("_"):
                continue
            if md.name == "README.md":
                existe = (raiz / rel.parent).is_dir()
            else:
                carpeta = raiz / rel.parent
                existe = carpeta.is_dir() and any(p.stem == md.stem and p.is_file() for p in carpeta.iterdir())
            if not existe:
                salida.append(rel.as_posix())
    return salida
