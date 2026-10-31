"""Utilidades compartidas — revisión de pendientes documentales.

Fachada pública del paquete `common*`: re-exporta las constantes, el frontmatter
y los bloques de decisión extraídos por R-19 (nomenclatura relacional
`<raiz>_<relacion>.py`), de modo que `from common import <nombre>` siga siendo la
única puerta de entrada para el resto de módulos.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from common_bloques import (
    extract_context,
    extract_title,
    find_group_id,
    has_decision_section,
    iter_decision_blocks,
    validate_group_id,
)
from common_constantes import (
    DATE_FOLDER_RE,
    DECISION_GROUP_RE,
    DECISION_OPTION_RE,
    DECISION_SECTION_RE,
    DEFAULT_OPTIONS,
    ELIMINAR_ESTADO,
    ESTADO_RE,
    ESTADOS,
    FM_KEY_RE,
    FRONTMATTER_RE,
    MOVE_ACTIONS,
    STATUS_MAP,
    TITLE_RE,
)
from common_frontmatter import (
    parse_simple_yaml,
    rebuild_content,
    serialize_frontmatter,
    split_frontmatter,
    split_frontmatter_parts,
    update_frontmatter_raw,
)


def date_from_fm(fm: dict[str, Any]) -> str:
    """Fecha YYYY-MM-DD del frontmatter (carpeta de fecha, R-17)."""
    for key in ("proposed_at", "created", "fecha", "date"):
        value = str(fm.get(key) or "").strip()
        m = re.match(r"^\d{4}-\d{2}-\d{2}", value)
        if m:
            return m.group(0)
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def estado_dest_rel(rel_path: str, fm: dict[str, Any], estado: str) -> str:
    """Nueva ruta relativa al mover el archivo a <estado> conservando la carpeta de fecha."""
    parts = rel_path.split("/")
    for i in range(len(parts) - 2, -1, -1):  # estado más cercano al archivo
        if ESTADO_RE.match(parts[i]):
            tiene_fecha = i + 1 < len(parts) - 1 and DATE_FOLDER_RE.match(parts[i + 1])
            fecha = parts[i + 1] if tiene_fecha else date_from_fm(fm)
            return "/".join(parts[:i] + [estado, fecha, parts[-1]])
    fecha = date_from_fm(fm)
    return "/".join(parts[:-1] + [estado, fecha, parts[-1]])


def estado_from_path(path: Path) -> str:
    """Carpeta de estado en la que vive el archivo ('' si no está bajo estados)."""
    for parent in path.parents:
        if ESTADO_RE.match(parent.name):
            return parent.name
    return ""


def find_section_root(path: Path, section_name: str) -> Path | None:
    """Raíz de una sección (p. ej. '35-herramientas') subiendo por los padres."""
    for parent in path.parents:
        if parent.name == section_name:
            return parent
    return None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def session_id_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def resolve_docs_roots(start: Path | None = None) -> list[tuple[Path, str]]:
    env = os.environ.get("DOCS_DIRS", "").strip()
    if env:
        roots: list[tuple[Path, str]] = []
        for part in env.split(","):
            part = part.strip()
            if not part:
                continue
            p = Path(part).resolve()
            label = p.name or "pack"
            roots.append((p, label))
        return roots

    if start is None:
        start = Path(__file__).resolve().parent

    candidate = start
    for _ in range(5):
        if (candidate / "PROTOCOLO.md").exists() or (candidate / "INDICE.md").exists():
            return [(candidate, candidate.name)]
        candidate = candidate.parent

    docs_env = os.environ.get("DOCS_DIR", "docs").strip()
    return [(Path(docs_env).resolve(), "docs")]


def session_paths(docs_root: Path) -> tuple[Path, Path]:
    base = docs_root / ".decisiones"
    active = base / "sesion-activa.json"
    history = base / "historial"
    return active, history


def should_skip_file(path: Path, fm: dict[str, Any]) -> bool:
    name = path.name
    parts = path.as_posix()
    if "90-archivo" in parts or "95-memoria" in parts:
        return True
    if name.startswith("_PLANTILLA") or name.startswith("_PROTOCOLO"):
        return True
    if name.startswith("_ejemplo"):
        return True
    for estado in ("04-archivadas", "05-canceladas", "06-listas-para-eliminar"):
        if f"/{estado}/" in f"/{parts}/":
            return True
    status = str(fm.get("status", "")).lower()
    if status in {
        "plantilla",
        "draft",
        "authorized",
        "done",
        "archived",
        "archivada",
        "cancelled",
        "cancelada",
        "rejected",
        "rechazada",
        "para-eliminar",
    }:
        return True
    return False


def infer_tipo(rel_path: str, fm: dict[str, Any]) -> str | None:
    if rel_path.startswith("05-instrucciones/"):
        return "instruccion"
    if rel_path.startswith("35-herramientas/propuestas/"):
        return "herramienta"
    if rel_path.startswith("45-mejoras-propuestas/"):
        return "mejora"
    if rel_path.startswith("20-decisiones/"):
        return "adr"
    if rel_path.startswith("40-auditorias/"):
        return "auditoria"
    if rel_path.startswith("46-evolucion-documentacion/"):
        return "evolucion"
    return None


def is_pending_tipo(tipo: str, status: str) -> bool:
    mapping = {
        "instruccion": {"awaiting_approval"},
        "herramienta": {"pending"},
        "mejora": {"pending"},
        "adr": {"propuesta"},
        "auditoria": {"active", "activa", "pendiente"},
        "evolucion": {"pending"},
    }
    return status in mapping.get(tipo, set())


def parse_item_date(proposed_at: str, created: str = "") -> datetime | None:
    for raw in (proposed_at, created):
        if not raw:
            continue
        text = raw.strip()
        for fmt, size in (("%Y-%m-%dT%H:%M:%S", 19), ("%Y-%m-%d", 10)):
            try:
                return datetime.strptime(text[:size], fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    return None


def is_stale_item(proposed_at: str, created: str, max_days: int) -> bool:
    dt = parse_item_date(proposed_at, created)
    if dt is None:
        return False
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_days)
    return dt < cutoff


@dataclass
class DecisionOption:
    action: str
    label: str
    checked: bool = False


@dataclass
class DecisionItem:
    id: str
    tipo: str
    title: str
    path: str
    docs_root: str
    pack_label: str
    status: str
    options: list[DecisionOption] = field(default_factory=list)
    context: str = ""
    proposed_at: str = ""
    areas: list[str] = field(default_factory=list)
    group_id_mismatch: bool = False

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["options"] = [asdict(o) for o in self.options]
        return d


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict[str, Any]) -> None:
    """Escritura atómica: archivo temporal + `os.replace`, para no dejar JSON truncado si el proceso muere."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    try:
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)
