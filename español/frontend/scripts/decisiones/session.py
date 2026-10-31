"""Gestión de sesiones de decisiones."""

from __future__ import annotations

import getpass
import os
from pathlib import Path
from typing import Any

from common import load_json, save_json, session_id_now, session_paths, utc_now_iso
from session_acciones import error_de_accion, opciones_de_item


def _primary_docs_root() -> Path:
    from common import resolve_docs_roots

    roots = resolve_docs_roots()
    return roots[0][0]


def get_active_session_path() -> Path:
    active, _ = session_paths(_primary_docs_root())
    return active


def load_active_session() -> dict[str, Any]:
    path = get_active_session_path()
    data = load_json(path)
    if not data:
        data = {
            "session_id": session_id_now(),
            "started_at": utc_now_iso(),
            "closed_at": None,
            "decisions": [],
        }
        save_active_session(data)
    return data


def save_active_session(data: dict[str, Any]) -> None:
    active, _ = session_paths(_primary_docs_root())
    save_json(active, data)


def register_decision(
    group_id: str,
    action: str,
    item: dict[str, Any] | None = None,
    *,
    registered_by: str | None = None,
) -> dict[str, Any]:
    if item is not None:
        error = error_de_accion(str(item.get("tipo") or ""), action, opciones_de_item(item))
        if error:
            raise ValueError(error)
    session = load_active_session()
    user = registered_by or os.environ.get("DECISIONES_USER") or getpass.getuser()

    # Reemplazar la decisión previa del mismo grupo *en el mismo pack*: con varios packs
    # (DOCS_DIRS) el mismo id puede existir en cada uno y no deben pisarse.
    docs_root = (item or {}).get("docs_root")
    session["decisions"] = [
        d
        for d in session.get("decisions", [])
        if not (d.get("id") == group_id and d.get("docs_root") == docs_root)
    ]

    entry = {
        "id": group_id,
        "group_id": group_id,
        "action": action,
        "registered_at": utc_now_iso(),
        "registered_by": user,
        "applied": False,
        "applied_at": None,
    }
    if item:
        entry.update(
            {
                "path": item.get("path"),
                "docs_root": item.get("docs_root"),
                "pack_label": item.get("pack_label"),
                "tipo": item.get("tipo"),
                "title": item.get("title"),
                "opciones": opciones_de_item(item),
            }
        )

    session["decisions"].append(entry)
    save_active_session(session)
    return entry


def close_session(archive: bool = True) -> dict[str, Any]:
    session = load_active_session()
    session["closed_at"] = utc_now_iso()
    if archive:
        _, history = session_paths(_primary_docs_root())
        history.mkdir(parents=True, exist_ok=True)
        archive_path = history / f"{session['session_id']}.json"
        save_json(archive_path, session)
    # Nueva sesión vacía
    new_session = {
        "session_id": session_id_now(),
        "started_at": utc_now_iso(),
        "closed_at": None,
        "decisions": [],
    }
    save_active_session(new_session)
    return session


def list_session_history(limit: int = 20) -> list[dict[str, Any]]:
    _, history = session_paths(_primary_docs_root())
    if not history.exists():
        return []
    entries: list[dict[str, Any]] = []
    for path in sorted(history.glob("*.json"), reverse=True):
        data = load_json(path)
        if not data:
            continue
        entries.append(
            {
                "session_id": data.get("session_id"),
                "started_at": data.get("started_at"),
                "closed_at": data.get("closed_at"),
                "decisions_count": len(data.get("decisions", [])),
            }
        )
        if len(entries) >= limit:
            break
    return entries
