"""Memorias del proyecto para un sistema: lo que el agente y la persona acuerdan recordar mientras trabajan con él.

Parte del propio sistema (`scripts/comun/`). Viven en `uxyngraphar/trabajo/<id>/memorias/MEM-AAAAMMDD-slug.md`.
El agente solo crea propuestas; «vigente» y «archivada» los pone una persona (`--humano`). `MEMORIAS.md` del sistema
dice qué conviene recordar y qué no.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import uxyn_base as base

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
INICIAL_AGENTE = "propuesta"
INICIAL_PERSONA = "vigente"
STATUS = ("propuesta", "vigente", "archivada")
SOLO_HUMANO = ("vigente", "archivada")
AUTORES = ("persona", "agente")
PLANTILLA = """---
id: {id}
status: {status}
fecha: {fecha}
autor: {autor}
fuente: "{fuente}"
valida_hasta: {valida_hasta}
---

# {titulo}

## Qué hay que recordar
{texto}

## Por qué importa
{motivo}
"""


@dataclass
class Memoria:
    ruta: Path
    id: str
    status: str | None
    autor: str | None
    fecha: str | None
    valida_hasta: str | None
    titulo: str
    datos: dict


def carpeta(sistema: Path, crear: bool = False) -> Path:
    destino = base.carpeta_trabajo(sistema, crear=crear) / base.CARPETA_MEMORIAS
    if crear:
        destino.mkdir(parents=True, exist_ok=True)
    return destino


def _titulo(cuerpo: str, defecto: str) -> str:
    for linea in cuerpo.splitlines():
        if linea.startswith("# "):
            return linea[2:].strip()
    return defecto


def leer(ruta: Path) -> Memoria:
    fm, cuerpo = base.leer_frontmatter(ruta.read_text(encoding="utf-8"))
    return Memoria(ruta, str(fm.get("id") or ruta.stem), fm.get("status"), fm.get("autor"), fm.get("fecha"),
                   fm.get("valida_hasta"), _titulo(cuerpo, ruta.stem), fm)


def listar(sistema: Path, status: str | None = None) -> list[Memoria]:
    raiz = carpeta(sistema)
    if not raiz.is_dir():
        return []
    salida = []
    for p in sorted(raiz.rglob("*.md")):
        if p.name.startswith("_") or (p.stem.isupper() and not p.stem.startswith(base.PREFIJO_MEMORIA + "-")):
            continue   # INDICE.md, _borradores…
        m = leer(p)
        if status is None or m.status == status:
            salida.append(m)
    return salida


def caducada(m: Memoria, hoy: date | None = None) -> bool:
    return bool(m.valida_hasta) and FECHA.match(str(m.valida_hasta)) is not None \
        and str(m.valida_hasta) < (hoy or date.today()).isoformat()


def vigentes(sistema: Path, hoy: date | None = None) -> list[Memoria]:
    """Las que el agente aplica: vigentes y no caducadas."""
    return [m for m in listar(sistema, "vigente") if not caducada(m, hoy)]


def crear(sistema: Path, slug: str, titulo: str, texto: str = "", motivo: str = "", fuente: str = "",
          valida_hasta: str | None = None, por_humano: bool = False, hoy: date | None = None,
          persona_verificada: bool = False) -> Path:
    """Nueva memoria: propuesta si la crea el agente; vigente si la crea una persona (`por_humano`).

    `persona_verificada`: quien llama ya comprobó que es una persona (el panel del motor, con su sesión de un solo uso)."""
    if not SLUG.match(slug):
        raise ValueError("slug: kebab-case ASCII (a-z, 0-9, guiones)")
    if not titulo.strip():
        raise ValueError("titulo: obligatorio")
    if valida_hasta and not FECHA.match(valida_hasta):
        raise ValueError("valida_hasta: fecha AAAA-MM-DD")
    if por_humano and not persona_verificada:
        base.exigir_humano("crear una memoria vigente")
    hoy = hoy or date.today()
    mid = f"{base.PREFIJO_MEMORIA}-{hoy.strftime('%Y%m%d')}-{slug}"
    destino = carpeta(sistema, crear=True) / f"{mid}.md"
    if destino.exists() or any(m.id == mid for m in listar(sistema)):
        raise FileExistsError(f"ya existe la memoria {mid}")
    contenido = PLANTILLA.format(
        id=mid, status=INICIAL_PERSONA if por_humano else INICIAL_AGENTE, fecha=hoy.isoformat(),
        autor="persona" if por_humano else "agente", fuente=fuente.replace('"', "'"),
        valida_hasta=valida_hasta or "null", titulo=titulo.strip(), texto=texto.strip() or "…", motivo=motivo.strip() or "…")
    destino.write_text(contenido, encoding="utf-8")
    return destino


def buscar(sistema: Path, mid: str) -> Memoria:
    hallazgos = [m for m in listar(sistema) if mid in (m.id, m.ruta.stem)]
    if not hallazgos:
        raise FileNotFoundError(f"no encuentro la memoria «{mid}»")
    if len(hallazgos) > 1:
        raise ValueError(f"id ambiguo «{mid}»: {', '.join(str(m.ruta) for m in hallazgos)}")
    return hallazgos[0]


def cambiar_estado(sistema: Path, mid: str, nuevo: str, por_humano: bool = False, persona_verificada: bool = False) -> Path:
    """`vigente` (aprobar) y `archivada` (archivar) solo los pone una persona."""
    if nuevo not in STATUS:
        raise ValueError(f"status inválido «{nuevo}»; válidos: {', '.join(STATUS)}")
    if nuevo in SOLO_HUMANO:
        if not por_humano:
            raise PermissionError(f"«{nuevo}» solo lo pone una persona (usa --humano si eres tú)")
        if not persona_verificada:
            base.exigir_humano(f"poner «{nuevo}» a una memoria")
    m = buscar(sistema, mid)
    texto = base.escribir_campo(m.ruta.read_text(encoding="utf-8"), "status", nuevo)
    if nuevo == "vigente" and m.autor == "agente":
        texto = base.escribir_campo(texto, "aprobada_por", "persona")
    m.ruta.write_text(texto, encoding="utf-8")
    return m.ruta


def validar(sistema: Path, hoy: date | None = None) -> tuple[list[str], list[str]]:
    """(errores, avisos) de las memorias del proyecto."""
    errores, avisos = [], []
    trabajo = base.carpeta_trabajo(sistema, crear=False)
    vistos: dict[str, Path] = {}
    for m in listar(sistema):
        rel = m.ruta.relative_to(trabajo).as_posix()
        if not m.datos:   # notas libres: no se aplican hasta que una persona las pase a memoria
            avisos.append(f"{rel}: sin frontmatter de memoria (id, status, autor); no se aplica")
            continue
        if not m.id.startswith(base.PREFIJO_MEMORIA + "-"):
            errores.append(f"{rel}: el id debe empezar por «{base.PREFIJO_MEMORIA}-»")
        if m.id in vistos:
            errores.append(f"{rel}: id repetido (también en {vistos[m.id].relative_to(trabajo).as_posix()})")
        vistos[m.id] = m.ruta
        if m.status not in STATUS:
            errores.append(f"{rel}: status «{m.status}» no válido; válidos: {', '.join(STATUS)}")
        if m.autor not in AUTORES:
            errores.append(f"{rel}: autor «{m.autor}» no válido; válidos: {', '.join(AUTORES)}")
        elif m.autor == "agente" and m.status == "vigente" and m.datos.get("aprobada_por") != "persona":
            errores.append(f"{rel}: memoria del agente vigente sin aprobar por una persona (aprobada_por: persona)")
        if not m.fecha or not FECHA.match(str(m.fecha)):
            avisos.append(f"{rel}: sin «fecha» AAAA-MM-DD")
        if m.status == "vigente" and caducada(m, hoy):
            avisos.append(f"{rel}: caducada desde {m.valida_hasta}; la persona debería archivarla o renovarla")
    return errores, avisos
