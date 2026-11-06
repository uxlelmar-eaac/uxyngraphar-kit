"""Contratos de este repo y de los repos hermanos; compartido por contratos.py y verificar-contratos.py."""

from __future__ import annotations

import re
from pathlib import Path

import uxyn_base as base
import uxyn_fichas as fichas

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)
ID_COMPARTIDO = re.compile(r"^[a-z0-9-]+(?:\.[a-z0-9-]+)+$")
ROLES = ("proveedor", "consumidor", "bff")
VACIO = (None, "", "null")
RUTAS_API = "rutas-de-api"


def raiz() -> Path:
    return base.raiz_app(PAQUETE)


def propios() -> list[tuple[fichas.Ficha, dict]]:
    return [(f, base.leer_frontmatter(f.ruta.read_text(encoding="utf-8"))[0]) for f in fichas.listar(PAQUETE, "contrato")]


def _frontmatters(carpeta: Path) -> list[dict]:
    salida = []
    for md in sorted(carpeta.rglob("*.md")) if carpeta.is_dir() else []:
        if md.stem.isupper() or md.name.startswith("_"):
            continue
        fm, _ = base.leer_frontmatter(md.read_text(encoding="utf-8", errors="replace"))
        if fm:
            salida.append(fm)
    return salida


def otro_repo(ruta: Path) -> dict:
    """Contratos (por id_compartido) y rutas documentadas (método, path) de un repo hermano con uxyngraphar 2.0."""
    trabajo = ruta / base.CARPETA_TRABAJO
    contratos = {str(fm.get("id_compartido")): fm for fm in _frontmatters(trabajo / PAQUETE.name) if fm.get("id_compartido")}
    rutas = {(str(fm.get("method", "")).upper(), str(fm.get("path", ""))) for fm in _frontmatters(trabajo / RUTAS_API)
             if fm.get("method") and fm.get("path") and fm.get("status") not in ("retirada", "deprecada")}
    return {"contratos": contratos, "rutas": rutas}


def repos_hermanos(rutas: list[str] | None = None) -> list[Path]:
    return [(raiz() / r).resolve() for r in (rutas or base.leer_ajustes(PAQUETE).get("otros_repos", []))]


def problemas_propios() -> tuple[list[str], list[str]]:
    errores, avisos, vistos = [], [], {}
    for f, fm in propios():
        idc = fm.get("id_compartido")
        if not isinstance(idc, str) or not ID_COMPARTIDO.match(idc):
            errores.append(f"{f.id}: id_compartido «{idc}» debe ser modulo.recurso.accion (kebab-case con puntos)")
        elif idc in vistos and f.status != "retirado":
            errores.append(f"{f.id}: id_compartido «{idc}» repetido (también en {vistos[idc]})")
        vistos.setdefault(idc, f.id)
        if fm.get("rol") not in ROLES:
            errores.append(f"{f.id}: rol «{fm.get('rol')}» debe ser {' | '.join(ROLES)}")
        if f.status == "vigente" and (fm.get("method") in VACIO or fm.get("path") in VACIO):
            errores.append(f"{f.id}: vigente sin method o path")
        if f.status == "vigente" and fm.get("rol") == "consumidor" and fm.get("ficha_proveedor") in VACIO:
            avisos.append(f"{f.id}: consumidor vigente sin ficha_proveedor (cita la ficha del repo proveedor)")
    return errores, avisos


def comparar(rutas: list[str] | None = None) -> tuple[list[str], list[str]]:
    """(divergencias, avisos) de los contratos vigentes de este repo frente a los repos hermanos."""
    divergencias, avisos = [], []
    hermanos = {}
    for ruta in repos_hermanos(rutas):
        if not (ruta / base.CARPETA_TRABAJO).is_dir():
            avisos.append(f"{ruta}: no está o no tiene uxyngraphar/trabajo/ (no se compara)")
            continue
        hermanos[ruta.name] = otro_repo(ruta)
    for f, fm in propios():
        if f.status != "vigente" or fm.get("rol") != "consumidor":
            continue
        otro = hermanos.get(str(fm.get("proveedor")))
        if otro is None:
            continue
        clave = (str(fm.get("method", "")).upper(), str(fm.get("path", "")))
        suyo = otro["contratos"].get(str(fm.get("id_compartido")))
        if suyo is None and clave not in otro["rutas"]:
            divergencias.append(f"{f.id}: {fm.get('proveedor')} no documenta «{fm.get('id_compartido')}» ni {clave[0]} {clave[1]}")
        elif suyo is not None:
            for campo in ("method", "path", "version"):
                if str(suyo.get(campo, "")).upper() != str(fm.get(campo, "")).upper():
                    divergencias.append(f"{f.id}: {campo} «{fm.get(campo)}» aquí, «{suyo.get(campo)}» en {fm.get('proveedor')}")
            if suyo.get("status") in ("deprecado", "retirado"):
                avisos.append(f"{f.id}: el proveedor lo marca «{suyo.get('status')}»")
    return divergencias, avisos
