"""Archivado periódico de las colas acumulativas (EVO archivado-periodico).

`archivar`: 03-completadas → 04-archivadas. `limpiar`: 05-canceladas → 06-listas-para-eliminar.
Dry-run por defecto; **nunca borra archivos**: el borrado definitivo lo decide un humano.
La antigüedad se mide por la carpeta de fecha (creación; R-17), no por la de cierre.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

from common import estado_dest_rel, rebuild_content, split_frontmatter_parts, update_frontmatter_raw
from metricas import fichas

# tipo → (status al archivar). ADR aceptadas no se archivan solas: son decisiones vinculantes vigentes.
STATUS_ARCHIVADA = {"instruccion": "archivada", "mejora": "archivada", "evolucion": "archivada",
                    "herramienta": "archivada", "auditoria": "archivada"}
PLAN = {
    "archivar": ("03-completadas", "04-archivadas", STATUS_ARCHIVADA),
    "limpiar": ("05-canceladas", "06-listas-para-eliminar", {t: "para-eliminar" for t in ("instruccion", "mejora", "evolucion", "herramienta", "adr", "auditoria")}),
}


@dataclass
class Candidato:
    docs_root: Path
    path: str
    id: str
    tipo: str
    dias: int
    destino: str
    status_nuevo: str


def candidatos(accion: str, roots: list[tuple[Path, str]], dias: int, hoy: date | None = None) -> list[Candidato]:
    origen, destino_estado, status_por_tipo = PLAN[accion]
    hoy = hoy or datetime.now(timezone.utc).date()
    lista: list[Candidato] = []
    for docs_root, _label in roots:
        for f in fichas(docs_root):
            edad = (hoy - date.fromisoformat(f["fecha"])).days
            if f["estado"] != origen or edad <= dias or f["tipo"] not in status_por_tipo:
                continue
            lista.append(Candidato(docs_root, f["path"], f["id"], f["tipo"], edad,
                                   estado_dest_rel(f["path"], f["fm"], destino_estado), status_por_tipo[f["tipo"]]))
    return sorted(lista, key=lambda c: (-c.dias, c.id))


def aplicar(cands: list[Candidato], dry_run: bool = True) -> list[str]:
    """Mueve cada ficha y actualiza su `status`. Devuelve una línea por candidato."""
    lineas: list[str] = []
    for c in cands:
        origen, destino = c.docs_root / c.path, c.docs_root / c.destino
        if dry_run:
            lineas.append(f"[dry-run] {c.id} ({c.dias} d): {c.path} → {c.destino}")
            continue
        if destino.exists():
            lineas.append(f"OMITIDO {c.id}: ya existe {c.destino}")
            continue
        raw, _fm, cuerpo = split_frontmatter_parts(origen.read_text(encoding="utf-8"))
        if raw is not None:
            origen.write_text(rebuild_content(update_frontmatter_raw(raw, {"status": c.status_nuevo}), cuerpo), encoding="utf-8")
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(origen), str(destino))
        lineas.append(f"{c.id}: {c.path} → {c.destino} (status: {c.status_nuevo})")
    return lineas
