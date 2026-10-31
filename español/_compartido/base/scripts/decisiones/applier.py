"""Aplicación de decisiones registradas a archivos markdown."""

from __future__ import annotations

import difflib
import re
import shutil
from pathlib import Path
from typing import Any

import alcance
from applier_promocion import _promote_herramienta, session_suffix
from applier_rutas import RutaInsegura, raices_permitidas, resolver_dentro
from common import (
    DECISION_GROUP_RE,
    DECISION_OPTION_RE,
    ELIMINAR_ESTADO,
    MOVE_ACTIONS,
    STATUS_MAP,
    estado_dest_rel,
    rebuild_content,
    split_frontmatter_parts,
    update_frontmatter_raw,
    utc_now_iso,
    validate_group_id,
)
from session_acciones import error_de_accion


def _estado_dest(file_path: Path, fm: dict[str, Any], estado: str) -> Path:
    """Destino al mover a <estado> conservando la carpeta de fecha (R-17)."""
    return Path(estado_dest_rel(file_path.as_posix(), fm, estado))


def _move_to_estado(file_path: Path, fm: dict[str, Any], estado: str, dry_run: bool) -> Path | None:
    dest = _estado_dest(file_path, fm, estado)
    if dry_run:
        return dest
    if dest.parent == file_path.parent and dest.name == file_path.name:
        return None
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest = dest.parent / f"{dest.stem}-{session_suffix()}{dest.suffix}"
    shutil.move(str(file_path), str(dest))
    return dest


class AlcanceInvalido(ValueError):
    """R-21: la instrucción declara un alcance de código que no se puede aprobar tal cual."""


def _aprobacion_alcance(fm: dict[str, Any], ahora: str) -> dict[str, str]:
    """R-21: aprobar una instrucción con `ampliacion_factor` autoriza expresamente esa ampliación."""
    errores = alcance.problemas(fm)
    if errores:
        raise AlcanceInvalido("R-21 — " + "; ".join(errores))
    return {"ampliacion_aprobada_at": ahora} if alcance.leer(fm).factor is not None else {}


def _status_updates(tipo: str, action: str) -> dict[str, str]:
    updates: dict[str, str] = {}
    new_status = STATUS_MAP.get(tipo, {}).get(action)
    if new_status:
        updates["status"] = new_status
    if tipo == "instruccion" and action == "aprobar":
        updates["approved_at"] = utc_now_iso()
    if tipo == "mejora" and action == "aprobar":
        updates["instruction_derivada"] = "PENDIENTE-YYYYMMDD-NNN"
    if tipo == "evolucion" and action == "aprobar":
        updates["instruction_derivada"] = "PENDIENTE-YYYYMMDD-NNN"
    return updates


def _apply_posponer(
    file_path: Path,
    tipo: str,
    action: str,
    session_id: str,
    group_id: str | None,
    dry_run: bool,
) -> tuple[str, str, list[str]] | None:
    content = file_path.read_text(encoding="utf-8")
    raw_yaml, fm, body = split_frontmatter_parts(content)
    if raw_yaml is None:
        return None

    doc_id = str(fm.get("id", file_path.stem))
    gid, id_ok = validate_group_id(body, doc_id)
    effective_group = group_id or gid
    notes: list[str] = []
    if not id_ok:
        notes.append(f"WARN: decision-group ({gid}) != id frontmatter ({doc_id})")

    note = f"decisiones-pendientes sesión {session_id}: posponer"
    new_body = _mark_checkbox_in_group(body, effective_group, action)
    new_body = _append_human_note(new_body, note)
    new_content = rebuild_content(raw_yaml, new_body)

    if new_content == content:
        return None
    if dry_run:
        return content, new_content, notes
    file_path.write_text(new_content, encoding="utf-8")
    return content, new_content, notes


def _mark_checkbox_in_group(body: str, group_id: str, action: str) -> str:
    lines = body.splitlines()
    result: list[str] = []
    in_block = False

    for line in lines:
        if "<!-- decision-group:" in line:
            m = DECISION_GROUP_RE.search(line)
            in_block = m is not None and m.group(1).strip() == group_id
            result.append(line)
            continue

        if in_block:
            if line.startswith("## ") and "Decisión" not in line:
                in_block = False
            elif in_block:
                m = DECISION_OPTION_RE.match(line.strip())
                if m and m.group(2) == action:
                    indent = line[: len(line) - len(line.lstrip())]
                    rest = re.sub(r"^-\s*\[[ xX]\]", "- [x]", line.strip())
                    result.append(indent + rest)
                    continue

        result.append(line)

    return "\n".join(result) + ("\n" if body.endswith("\n") else "")


def _append_human_note(body: str, note: str) -> str:
    marker = "### Notas del humano"
    if marker in body:
        return body.rstrip() + f"\n\n- [{utc_now_iso()}] {note}\n"
    return body.rstrip() + f"\n\n{marker}\n\n- [{utc_now_iso()}] {note}\n"


def apply_decision_to_file(
    file_path: Path,
    tipo: str,
    action: str,
    session_id: str,
    group_id: str | None = None,
    dry_run: bool = False,
) -> tuple[str, str, list[str]] | None:
    """Aplica decisión. Retorna (original, nuevo, notas) o None."""
    if action == "posponer":
        return _apply_posponer(file_path, tipo, action, session_id, group_id, dry_run)

    content = file_path.read_text(encoding="utf-8")
    raw_yaml, fm, body = split_frontmatter_parts(content)
    if raw_yaml is None:
        return None

    doc_id = str(fm.get("id", file_path.stem))
    gid, id_ok = validate_group_id(body, doc_id)
    effective_group = group_id or gid
    notes: list[str] = []
    if not id_ok:
        notes.append(f"WARN: decision-group ({gid}) != id frontmatter ({doc_id})")

    fm_updates = _status_updates(tipo, action)
    if tipo == "instruccion" and action == "aprobar":
        fm_updates.update(_aprobacion_alcance(fm, fm_updates["approved_at"]))
        if alcance.resumen(fm):
            notes.append(alcance.resumen(fm))
    new_body = _mark_checkbox_in_group(body, effective_group, action)
    note = f"decisiones-pendientes sesión {session_id}: {action}"
    if tipo in {"mejora", "herramienta", "instruccion", "adr", "auditoria", "evolucion"}:
        new_body = _append_human_note(new_body, note)
    if tipo == "mejora" and action == "aprobar":
        notes.append("Completar instruction_derivada en frontmatter y crear instrucción derivada")
    if tipo == "evolucion" and action == "aprobar":
        notes.append("Completar instruction_derivada y actualizar matriz-cobertura-proyectos.md")
        revision_hint = f"<!-- revision-pendientes-nota: actualizar matriz-cobertura-proyectos.md fila relacionada con EVO {doc_id} -->"
        if revision_hint not in new_body:
            new_body = new_body.rstrip() + "\n\n" + revision_hint + "\n"

    new_raw = update_frontmatter_raw(raw_yaml, fm_updates)
    new_content = rebuild_content(new_raw, new_body)

    side_effects: list[str] = []

    if action == "promover" and tipo == "herramienta":
        if not dry_run and new_content != content:
            file_path.write_text(new_content, encoding="utf-8")
        promoted = _promote_herramienta(file_path, fm, dry_run)
        if promoted:
            side_effects.append(f"Borrador autorizada: {promoted}")
        if not dry_run:
            moved = _move_to_estado(file_path, fm, "03-completadas", dry_run)
            if moved:
                side_effects.append(f"Propuesta movida a {moved}")
        return content, new_content, notes + side_effects

    estado = MOVE_ACTIONS.get((tipo, action))
    if action == "eliminar":
        estado = ELIMINAR_ESTADO

    if new_content == content and estado is None:
        return None

    if dry_run:
        return content, new_content, notes

    if new_content != content:
        file_path.write_text(new_content, encoding="utf-8")
    if estado:
        moved = _move_to_estado(file_path, fm, estado, dry_run)
        if moved:
            side_effects.append(f"Movido a {moved}")
    return content, new_content, notes + side_effects


def apply_session(
    session: dict[str, Any],
    dry_run: bool = False,
    permitidas: list[Path] | None = None,
) -> list[dict[str, Any]]:
    """Aplica las decisiones de la sesión. `permitidas`: raíces donde se puede escribir
    (por defecto, las de `resolve_docs_roots()`); toda ruta fuera de ellas se rechaza."""
    results: list[dict[str, Any]] = []
    session_id = session.get("session_id", "unknown")
    if permitidas is None:
        permitidas = raices_permitidas()

    for entry in session.get("decisions", []):
        if entry.get("applied"):
            continue

        action = entry.get("action", "")
        tipo = entry.get("tipo", "")
        rel = entry.get("path", "")
        group_id = entry.get("id") or entry.get("group_id")

        error_accion = error_de_accion(tipo, action, entry.get("opciones"))
        if error_accion:
            results.append({"id": entry.get("id"), "ok": False, "error": error_accion})
            continue
        try:
            file_path = resolver_dentro(entry.get("docs_root", ""), rel, permitidas)
        except RutaInsegura as exc:
            results.append({"id": entry.get("id"), "ok": False, "error": f"Ruta rechazada: {exc}"})
            continue
        docs_root = Path(entry["docs_root"]).resolve()

        if not file_path.exists():
            results.append(
                {
                    "id": entry.get("id"),
                    "ok": False,
                    "error": f"Archivo no encontrado: {file_path}",
                }
            )
            continue

        fm_pre: dict[str, Any] = {}
        try:
            _, fm_pre, _ = split_frontmatter_parts(file_path.read_text(encoding="utf-8"))
        except OSError:
            pass

        try:
            outcome = apply_decision_to_file(
                file_path,
                tipo,
                action,
                session_id,
                group_id=group_id,
                dry_run=dry_run,
            )
        except (OSError, AlcanceInvalido) as exc:
            results.append({"id": entry.get("id"), "ok": False, "error": str(exc)})
            continue

        if outcome is None and action == "posponer":
            results.append({"id": entry.get("id"), "ok": True, "note": "posponer sin cambios en markdown"})
            if not dry_run:
                entry["applied"] = True
                entry["applied_at"] = utc_now_iso()
            continue

        if outcome is None:
            results.append({"id": entry.get("id"), "ok": True, "note": "sin cambios"})
            if not dry_run:
                entry["applied"] = True
                entry["applied_at"] = utc_now_iso()
            continue

        original, new_content, extra_notes = outcome
        diff = "\n".join(
            difflib.unified_diff(
                original.splitlines(),
                new_content.splitlines(),
                fromfile=str(rel),
                tofile=str(rel) + " (applied)",
                lineterm="",
            )
        )
        note = "; ".join(extra_notes) if extra_notes else "aplicado"
        if not dry_run:
            entry["applied"] = True
            entry["applied_at"] = utc_now_iso()
            estado = MOVE_ACTIONS.get((tipo, action))
            if action == "eliminar":
                estado = ELIMINAR_ESTADO
            if estado and fm_pre:
                dest_rel = estado_dest_rel(rel, fm_pre, estado)
                dest = docs_root / dest_rel
                if dest.exists():
                    entry["path"] = dest_rel

        results.append({"id": entry.get("id"), "ok": True, "diff": diff, "note": note})

    return results
