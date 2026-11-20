"""Propuestas de mejora del sistema: el sistema instalado es inmutable; si se queda corto, se propone al autor.

Parte del propio sistema (`scripts/comun/`). Viven en `uxyngraphar/trabajo/<id>/propuestas-de-mejora/PMS-AAAAMMDD-slug.md`.
El agente las escribe («borrador»); una persona las envía al autor con `uxyngraphar reportar <id> --mejora PMS-…`
(con vista previa) y el autor las acepta o rechaza en uxyn. Pueden llevar un diff **de archivos del sistema**,
nunca código del proyecto.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import uxyn_base as base

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
STATUS = ("borrador", "enviada", "descartada")
MAX_DIFF = 6000
CABECERA_DIFF = re.compile(r"^(?:---|\+\+\+) (?:a/|b/)?(\S+)", re.M)
PLANTILLA = """---
id: {id}
status: borrador
fecha: {fecha}
sistema: {sistema}
version: {version}
archivo: {archivo}
---

# {titulo}

## Qué falla o qué falta
{que}

## Por qué importa
{porque}

## Evidencia
{evidencia}
{diff}"""


@dataclass
class Mejora:
    ruta: Path
    id: str
    status: str | None
    titulo: str
    datos: dict
    cuerpo: str


def carpeta(sistema: Path, crear: bool = False) -> Path:
    destino = base.carpeta_trabajo(sistema, crear=crear) / base.CARPETA_MEJORAS
    if crear:
        destino.mkdir(parents=True, exist_ok=True)
    return destino


def leer(ruta: Path) -> Mejora:
    fm, cuerpo = base.leer_frontmatter(ruta.read_text(encoding="utf-8"))
    titulo = next((x[2:].strip() for x in cuerpo.splitlines() if x.startswith("# ")), ruta.stem)
    return Mejora(ruta, str(fm.get("id") or ruta.stem), fm.get("status"), titulo, fm, cuerpo)


def listar(sistema: Path) -> list[Mejora]:
    raiz = carpeta(sistema)
    if not raiz.is_dir():
        return []
    return [leer(p) for p in sorted(raiz.glob(f"{base.PREFIJO_MEJORA}-*.md"))]


def buscar(sistema: Path, mid: str) -> Mejora:
    hallazgos = [m for m in listar(sistema) if mid in (m.id, m.ruta.stem)]
    if not hallazgos:
        raise FileNotFoundError(f"no encuentro la propuesta de mejora «{mid}»")
    return hallazgos[0]


def comprobar_diff(sistema: Path, diff: str) -> str:
    """El diff solo puede tocar archivos del propio sistema (nunca código del proyecto)."""
    texto = (diff or "").replace("\r\n", "\n").strip()
    if not texto:
        return ""
    if len(texto) > MAX_DIFF:
        raise ValueError(f"el diff admite hasta {MAX_DIFF} caracteres; resume o divide la propuesta")
    rutas = {r for r in CABECERA_DIFF.findall(texto) if r != "/dev/null"}
    if not rutas:
        raise ValueError("el diff no tiene cabeceras «--- a/<archivo>» / «+++ b/<archivo>»")
    propios = set(base.archivos_del_sistema(sistema))
    fuera = sorted(r for r in rutas if r.removeprefix(f"{base.CARPETA_SISTEMAS_DE_GOBERNANZA}/{sistema.name}/") not in propios)
    if fuera:
        raise ValueError(f"el diff solo puede tocar archivos del sistema «{sistema.name}»; no: {', '.join(fuera[:5])}")
    return texto


def crear(sistema: Path, slug: str, titulo: str, que: str, porque: str = "", evidencia: str = "", archivo: str = "",
          diff: str = "", hoy: date | None = None) -> Path:
    if not SLUG.match(slug):
        raise ValueError("slug: kebab-case ASCII (a-z, 0-9, guiones)")
    if not titulo.strip() or len(que.strip()) < 10:
        raise ValueError("titulo y «que» (al menos 10 caracteres) son obligatorios")
    if archivo and archivo not in base.archivos_del_sistema(sistema):
        raise ValueError(f"archivo: «{archivo}» no es un archivo del sistema")
    diff = comprobar_diff(sistema, diff)
    m = base.leer_manifiesto(sistema)
    hoy = hoy or date.today()
    mid = f"{base.PREFIJO_MEJORA}-{hoy.strftime('%Y%m%d')}-{slug}"
    destino = carpeta(sistema, crear=True) / f"{mid}.md"
    if destino.exists():
        raise FileExistsError(f"ya existe la propuesta {mid}")
    destino.write_text(PLANTILLA.format(
        id=mid, fecha=hoy.isoformat(), sistema=m.get("id", sistema.name), version=m.get("version", ""),
        archivo=archivo or "null", titulo=titulo.strip(), que=que.strip(), porque=porque.strip() or "…",
        evidencia=evidencia.strip() or "…", diff=f"\n## Diff propuesto (archivos del sistema)\n\n```diff\n{diff}\n```\n" if diff else ""),
        encoding="utf-8")
    return destino


def texto_para_enviar(m: Mejora) -> str:
    """Lo que viaja al autor: el cuerpo de la propuesta (título, qué, por qué, evidencia y diff del sistema)."""
    return m.cuerpo.strip()


def marcar_enviada(m: Mejora) -> None:
    m.ruta.write_text(base.escribir_campo(m.ruta.read_text(encoding="utf-8"), "status", "enviada"), encoding="utf-8")
