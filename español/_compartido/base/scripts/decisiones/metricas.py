"""Métricas del propio sistema documental — instrucciones por semana, antigüedad y colas.

Solo lectura. `calcular()` devuelve un dict serializable; `formatear()` lo muestra en tabla.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from common import DATE_FOLDER_RE, ESTADO_RE, ESTADOS, infer_tipo, split_frontmatter

TIPOS = ("instruccion", "mejora", "evolucion", "herramienta", "adr", "auditoria")


def _ubicacion(rel: str) -> tuple[str, str] | None:
    """(estado, fecha) si `rel` tiene forma `<sección>/<estado>/YYYY-MM-DD/<slug>.md`."""
    partes = rel.split("/")
    for i, parte in enumerate(partes):
        if ESTADO_RE.match(parte) and i + 3 == len(partes) and DATE_FOLDER_RE.match(partes[i + 1]):
            return parte, partes[i + 1]
    return None


def fichas(docs_root: Path) -> list[dict[str, Any]]:
    """Fichas de colas del pack: tipo, estado, fecha de carpeta, id y frontmatter."""
    salida: list[dict[str, Any]] = []
    for md in sorted(docs_root.rglob("*.md")):
        rel = md.relative_to(docs_root).as_posix()
        if md.name == "README.md" or md.name.startswith("_") or "/90-archivo/" in f"/{rel}" or rel.startswith("95-memoria/"):
            continue
        ubicacion = _ubicacion(rel)
        tipo = infer_tipo(rel, {})
        if not ubicacion or not tipo:
            continue
        fm, _, _ = split_frontmatter(md.read_text(encoding="utf-8"))
        salida.append({"tipo": tipo, "estado": ubicacion[0], "fecha": ubicacion[1], "id": str(fm.get("id", md.stem)),
                       "status": str(fm.get("status", "")), "path": rel, "fm": fm})
    return salida


def _semana(fecha: str) -> str:
    anio, semana, _ = date.fromisoformat(fecha).isocalendar()
    return f"{anio}-W{semana:02d}"


def _presupuesto_excedido(fm: dict[str, Any]) -> bool:
    try:
        maximo = int(str(fm.get("presupuesto_max_docs", "")))
    except ValueError:
        return False
    usados = sum(len(fm.get(k) or []) for k in ("lectura_minima", "espejo_leer") if isinstance(fm.get(k), list))
    return usados > maximo


def calcular(roots: list[tuple[Path, str]], hoy: date | None = None, max_dias: int = 30) -> dict[str, Any]:
    hoy = hoy or datetime.now(timezone.utc).date()
    por_cola: dict[str, Counter[str]] = defaultdict(Counter)
    semanas: Counter[str] = Counter()
    edades: list[int] = []
    antiguas: list[dict[str, Any]] = []
    excedidos: list[str] = []
    total = 0
    for docs_root, _label in roots:
        for f in fichas(docs_root):
            total += 1
            por_cola[f["tipo"]][f["estado"]] += 1
            if f["tipo"] == "instruccion":
                semanas[_semana(f["fecha"])] += 1
                if _presupuesto_excedido(f["fm"]):
                    excedidos.append(f["id"])
            if f["estado"] == "01-pendientes":
                dias = (hoy - date.fromisoformat(f["fecha"])).days
                edades.append(dias)
                if dias > max_dias:
                    antiguas.append({"id": f["id"], "tipo": f["tipo"], "dias": dias})
    return {
        "fecha": hoy.isoformat(),
        "total_fichas": total,
        "colas": {t: {e: por_cola[t].get(e, 0) for e in ESTADOS} for t in TIPOS if t in por_cola},
        "instrucciones_por_semana": dict(sorted(semanas.items())),
        "pendientes": {
            "cantidad": len(edades),
            "antiguedad_media_dias": round(sum(edades) / len(edades), 1) if edades else 0.0,
            "antiguedad_max_dias": max(edades) if edades else 0,
            "mas_antiguas_que": max_dias,
            "antiguas": sorted(antiguas, key=lambda a: -a["dias"]),
        },
        "presupuesto_excedido": sorted(excedidos),
    }


def formatear(m: dict[str, Any]) -> str:
    cab = ["pend", "prog", "compl", "arch", "canc", "elim"]
    lineas = [f"Métricas documentales al {m['fecha']} — {m['total_fichas']} fichas", "",
              f"{'COLA':<12}" + "".join(f"{c:>7}" for c in cab), "-" * (12 + 7 * len(cab))]
    for tipo, estados in m["colas"].items():
        lineas.append(f"{tipo:<12}" + "".join(f"{estados[e]:>7}" for e in ESTADOS))
    p = m["pendientes"]
    lineas += ["", f"Pendientes: {p['cantidad']} · antigüedad media {p['antiguedad_media_dias']} d · máxima {p['antiguedad_max_dias']} d"]
    for a in p["antiguas"][:10]:
        lineas.append(f"  > {p['mas_antiguas_que']} d: {a['id']} ({a['tipo']}, {a['dias']} d)")
    if m["instrucciones_por_semana"]:
        lineas += ["", "Instrucciones por semana (carpeta de fecha):"]
        lineas += [f"  {s}: {n}" for s, n in m["instrucciones_por_semana"].items()]
    if m["presupuesto_excedido"]:
        lineas += ["", f"WARN presupuesto de lectura excedido: {', '.join(m['presupuesto_excedido'])}"]
    return "\n".join(lineas)
