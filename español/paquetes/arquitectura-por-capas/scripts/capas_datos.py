"""Capas e imports del código; compartido por capas.py y verificar-capas.py."""

from __future__ import annotations

import fnmatch
import os
import posixpath
import re
from dataclasses import dataclass
from pathlib import Path

import uxyn_base as base

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)
JS = re.compile(r"""(?:\bfrom\s*|\bimport\s*\(?\s*|\brequire\(\s*)['"]([^'"]+)['"]""")
PY = re.compile(r"^\s*(?:from\s+(\.*[\w.]*)\s+import|import\s+([\w.]+))", re.M)


@dataclass
class Lugar:
    modulo: str | None
    capa: str | None
    comun: bool


@dataclass
class Infraccion:
    archivo: str
    linea: int
    destino: str
    motivo: str


def raiz() -> Path:
    return base.raiz_app(PAQUETE)


def ajustes() -> dict:
    a = base.leer_ajustes(PAQUETE)
    perfil = a.get("perfiles", {}).get(a.get("perfil", "servidor"), {})
    return {**a, "capas": perfil.get("capas", {}), "cruce": perfil.get("cruce", "integrations")}


def lugar(rel: str, a: dict) -> Lugar:
    partes = rel.split("/")
    comun = any(rel == c or rel.startswith(c.rstrip("/") + "/") for c in a.get("comun", []))
    for patron in a.get("modulos", []):
        n = len(patron.split("/"))
        if len(partes) > n and fnmatch.fnmatch("/".join(partes[:n]), patron):
            capa = partes[n] if len(partes) > n + 1 and partes[n] in a["capas"] else None
            return Lugar(partes[n - 1], capa, comun)
    return Lugar(None, None, comun)


def archivos(a: dict, rutas: list[str] | None = None) -> list[str]:
    extensiones, excluir = set(a.get("extensiones", [])), set(a.get("excluir", []))
    salida = []
    for r in rutas or a.get("raices", ["src"]):
        p = raiz() / r
        if p.is_file():
            salida.append(p)
        for actual, dirs, nombres in os.walk(p) if p.is_dir() else []:
            dirs[:] = [d for d in dirs if d not in excluir]
            salida += [Path(actual) / n for n in nombres]
    return sorted({p.relative_to(raiz()).as_posix() for p in salida if p.suffix in extensiones})


def _resolver_js(origen: str, spec: str, a: dict) -> str | None:
    for alias, destino in a.get("alias", {}).items():
        if spec.startswith(alias):
            return posixpath.normpath(destino + spec[len(alias):])
    if spec.startswith("."):
        return posixpath.normpath(posixpath.join(posixpath.dirname(origen), spec))
    if any(spec.startswith(r.rstrip("/") + "/") for r in a.get("raices", [])):
        return posixpath.normpath(spec)
    return None


def _resolver_py(origen: str, spec: str) -> str | None:
    puntos = len(spec) - len(spec.lstrip("."))
    resto = spec[puntos:].replace(".", "/")
    if puntos:
        carpeta = posixpath.dirname(origen)
        for _ in range(puntos - 1):
            carpeta = posixpath.dirname(carpeta)
        return posixpath.normpath(posixpath.join(carpeta, resto)) if resto else carpeta
    return resto if (raiz() / resto).exists() or (raiz() / (resto + ".py")).exists() else None


def imports(rel: str, texto: str, a: dict) -> list[tuple[int, str]]:
    """(línea, ruta resuelta relativa a la raíz) de los imports internos del archivo."""
    salida = []
    if rel.endswith(".py"):
        for m in PY.finditer(texto):
            destino = _resolver_py(rel, m.group(1) or m.group(2))
            if destino:
                salida.append((texto.count("\n", 0, m.start()) + 1, destino))
    else:
        for m in JS.finditer(texto):
            destino = _resolver_js(rel, m.group(1), a)
            if destino:
                salida.append((texto.count("\n", 0, m.start()) + 1, destino))
    return salida


def revisar(rutas: list[str] | None = None) -> list[Infraccion]:
    a = ajustes()
    salida = []
    for rel in archivos(a, rutas):
        try:
            texto = (raiz() / rel).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        desde = lugar(rel, a)
        for n, destino in imports(rel, texto, a):
            motivo = _motivo(desde, lugar(destino + "/x", a), a)
            if motivo:
                salida.append(Infraccion(rel, n, destino, motivo))
    return salida


def _motivo(desde: Lugar, hacia: Lugar, a: dict) -> str:
    if desde.comun and hacia.modulo:
        return f"el código común no importa módulos de negocio (→ {hacia.modulo})"
    if desde.modulo and hacia.modulo and desde.modulo != hacia.modulo:
        if desde.capa and desde.capa != a["cruce"]:   # sin capa: archivo raíz del módulo (registro en el framework)
            return f"cruce de módulo {desde.modulo} → {hacia.modulo} fuera de «{a['cruce']}/»"
        return ""
    if desde.capa and hacia.capa and desde.capa != hacia.capa and hacia.capa not in a["capas"].get(desde.capa, []):
        return f"«{desde.capa}» no puede importar «{hacia.capa}» (permitidas: {', '.join(a['capas'][desde.capa]) or 'ninguna'})"
    return ""


def mapa() -> dict[str, set[str]]:
    a = ajustes()
    salida: dict[str, set[str]] = {}
    for rel in archivos(a):
        l = lugar(rel, a)
        if l.modulo:
            salida.setdefault(l.modulo, set()).update({l.capa} if l.capa else set())
    return salida
