"""Validación de fichas (colas por estado): status↔carpeta, enums, ids y fechas (R-17)."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from validar_comun import FECHA_RE, Opciones, Pack, Reporte, iter_md, leer_ficha  # añade decisiones/ al sys.path
from common_constantes import ENUMS_FICHA  # noqa: E402
import alcance  # noqa: E402  (R-21)

SECCIONES = {
    "05-instrucciones": "instruccion",
    "20-decisiones": "adr",
    "35-herramientas/propuestas": "herramienta",
    "40-auditorias": "auditoria",
    "45-mejoras-propuestas": "mejora",
    "46-evolucion-documentacion": "evolucion",
}
_COLA = {"01-pendientes": {"pending"}, "02-en-progreso": {"approved"}, "03-completadas": {"done"},
         "04-archivadas": {"archivada"}, "05-canceladas": {"rejected"}, "06-listas-para-eliminar": {"para-eliminar"}}
# Estado de carpeta → status admitidos, por tipo (fuente: 00-nucleo/frontmatter/<tipo>.md).
STATUS_POR_ESTADO: dict[str, dict[str, set[str]]] = {
    "instruccion": {"01-pendientes": {"draft", "awaiting_approval"}, "02-en-progreso": {"approved", "executing"},
                    "03-completadas": {"done"}, "04-archivadas": {"archivada"}, "05-canceladas": {"cancelled"},
                    "06-listas-para-eliminar": {"para-eliminar"}},
    "mejora": _COLA,
    "evolucion": _COLA,
    "adr": {"01-pendientes": {"propuesta"}, "02-en-progreso": set(), "03-completadas": {"aceptada"},
            "04-archivadas": {"reemplazada", "obsoleta"}, "05-canceladas": {"rechazada"},
            "06-listas-para-eliminar": {"para-eliminar"}},
    "auditoria": {"01-pendientes": {"pendiente", "draft"}, "02-en-progreso": {"activa", "active"},
                  "03-completadas": {"cerrada"}, "04-archivadas": {"archivada"}, "05-canceladas": {"cancelada"},
                  "06-listas-para-eliminar": {"para-eliminar"}},
    "herramienta": {"01-pendientes": {"pending"}, "02-en-progreso": {"en-evaluacion"}, "03-completadas": {"promovida"},
                    "04-archivadas": {"archivada"}, "05-canceladas": {"rejected"},
                    "06-listas-para-eliminar": {"para-eliminar"}},
}
ENUMS = ENUMS_FICHA
NOMBRE_IGUAL_ID = {"mejora", "evolucion", "auditoria", "adr"}
LIMITE_COLAS = {"mejoras_propuestas": 3, "evolucion_documentacion": 2}


@dataclass
class Ficha:
    path: Path
    rel: str
    tipo: str
    estado: str
    fecha: str
    fm: dict[str, Any]
    cuerpo: str = field(repr=False, default="")


def descubrir(pack: Pack, rep: Reporte) -> list[Ficha]:
    """Fichas con forma `<sección>/<estado>/YYYY-MM-DD/<slug>.md`; avisa de las sin frontmatter."""
    fichas: list[Ficha] = []
    for md in iter_md(pack.docs):
        rel = md.relative_to(pack.docs).as_posix()
        for sec, tipo in SECCIONES.items():
            m = re.match(rf"^{re.escape(sec)}/(0[1-6]-[a-z-]+)/(\d{{4}}-\d{{2}}-\d{{2}})/([^/]+\.md)$", rel)
            if not m or m.group(3) == "README.md" or m.group(3).startswith("_"):
                continue
            fm, cuerpo = leer_ficha(md)
            if fm is None:
                rep.fail(f"Ficha sin frontmatter: {rel}")
                break
            fichas.append(Ficha(md, rel, tipo, m.group(1), m.group(2), fm, cuerpo))
            break
    return fichas


def _fecha_ficha(fm: dict[str, Any]) -> str:
    for clave in ("proposed_at", "created", "fecha", "date"):
        v = str(fm.get(clave) or "")[:10]
        if FECHA_RE.match(v):
            return v
    return ""


def validar_ficha(f: Ficha, rep: Reporte, op: Opciones) -> None:
    if not f.fm.get("id"):
        rep.fail(f"Ficha sin id: {f.rel}")
        return
    status = str(f.fm.get("status", "")).lower()
    permitidos = STATUS_POR_ESTADO[f.tipo].get(f.estado, set())
    if status not in permitidos:
        rep.segun(op.estados, f"status «{status or '—'}» no corresponde a {f.estado} ({', '.join(sorted(permitidos)) or 'ninguno'}): {f.rel}")
    nombre = f.path.stem
    ident = str(f.fm["id"])
    if f.tipo in NOMBRE_IGUAL_ID and nombre != ident and not nombre.startswith(f"{ident}-"):
        rep.segun(op.ids, f"Nombre de archivo ≠ id ({ident}): {f.rel}")
    fecha = _fecha_ficha(f.fm)
    if fecha and fecha != f.fecha:
        rep.warn(f"Carpeta de fecha {f.fecha} ≠ fecha de la ficha {fecha}: {f.rel}")
    for clave, validos in ENUMS.get(f.tipo, {}).items():
        valor = f.fm.get(clave)
        if valor not in (None, "", []) and str(valor) not in validos:
            rep.warn(f"{clave}: «{valor}» fuera de {sorted(validos)} en {f.rel}")
    for clave, tope in LIMITE_COLAS.items():
        n = len(f.fm.get(clave) or []) if isinstance(f.fm.get(clave), list) else 0
        if n > tope:
            rep.warn(f"{clave} supera el máximo de {tope} ({n}) en {f.rel}")
    if f.estado == "03-completadas" and "PENDIENTE-" in str(f.fm.get("instruction_derivada", "")):
        rep.warn(f"instruction_derivada sin completar en ficha completada: {f.rel}")
    if f.tipo == "instruccion":
        validar_alcance(f, rep)


def validar_alcance(f: Ficha, rep: Reporte) -> None:
    """R-21: ampliación 1.5–2× con justificación y aprobación humana, o fraccionar. Error en colas activas."""
    if str(f.fm.get("status", "")).lower() == "plantilla":
        return
    activa = f.estado in ("01-pendientes", "02-en-progreso")
    mensajes = alcance.bloqueos(f.fm) if f.estado != "01-pendientes" else alcance.problemas(f.fm)
    for m in mensajes:
        (rep.fail if activa else rep.warn)(f"R-21 {m}: {f.rel}")


def ids_duplicados(fichas: list[Ficha], rep: Reporte, op: Opciones) -> None:
    por_id: dict[str, list[str]] = defaultdict(list)
    for f in fichas:
        if f.fm.get("id"):
            por_id[str(f.fm["id"])].append(f.rel)
    for ident, rutas in sorted(por_id.items()):
        if len(rutas) > 1:
            rep.segun(op.ids, f"id duplicado «{ident}»: {', '.join(rutas)}")


def validar(pack: Pack, rep: Reporte, op: Opciones) -> list[Ficha]:
    fichas = descubrir(pack, rep)
    for f in fichas:
        validar_ficha(f, rep, op)
    ids_duplicados(fichas, rep, op)
    return fichas
