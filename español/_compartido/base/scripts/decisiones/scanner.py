"""Escaneo de decisiones pendientes en documentación."""

from __future__ import annotations

from pathlib import Path

import alcance
from common import (
    DECISION_GROUP_RE,
    DECISION_OPTION_RE,
    DEFAULT_OPTIONS,
    DecisionItem,
    DecisionOption,
    extract_context,
    extract_title,
    has_decision_section,
    infer_tipo,
    is_pending_tipo,
    is_stale_item,
    iter_decision_blocks,
    resolve_docs_roots,
    should_skip_file,
    split_frontmatter,
    validate_group_id,
)


def _parse_decision_block(block_text: str, group_id: str) -> list[DecisionOption]:
    options: list[DecisionOption] = []
    in_block = "<!-- decision-group:" in block_text or "## Decisión" in block_text
    for line in block_text.splitlines():
        if "<!-- decision-group:" in line:
            m = DECISION_GROUP_RE.search(line)
            in_block = m is not None and m.group(1).strip() == group_id
            continue
        if not in_block:
            continue
        if line.startswith("## ") and "Decisión" not in line and "Decisiones" not in line:
            break
        m = DECISION_OPTION_RE.match(line.strip())
        if m:
            checked = m.group(1).lower() == "x"
            action = (m.group(2) or "").strip()
            label = m.group(3).strip()
            if not action:
                lower = label.lower()
                for candidate in (
                    "aprobar",
                    "rechazar",
                    "posponer",
                    "promover",
                    "cancelar",
                    "aceptar",
                    "obsoleta",
                ):
                    if candidate in lower:
                        action = candidate
                        break
                if not action:
                    action = label[:30].lower().replace(" ", "-")
            options.append(DecisionOption(action=action, label=label, checked=checked))
    return options


def scan_file_items(docs_root: Path, pack_label: str, file_path: Path) -> list[DecisionItem]:
    content = file_path.read_text(encoding="utf-8")
    rel = file_path.relative_to(docs_root).as_posix()

    if rel.startswith("10-guias/") and not has_decision_section(content) and "<!-- decision-group:" not in content:
        return []

    fm, body, _ = split_frontmatter(content)
    if should_skip_file(file_path, fm):
        return []

    tipo = infer_tipo(rel, fm)
    if not tipo:
        return []

    status = str(fm.get("status", "")).lower()
    if not is_pending_tipo(tipo, status):
        return []

    doc_id = str(fm.get("id", file_path.stem))
    blocks = iter_decision_blocks(body, doc_id)
    if not blocks:
        blocks = [(doc_id, body)]

    areas_raw = fm.get("areas", [])
    if isinstance(areas_raw, str):
        areas = [areas_raw] if areas_raw else []
    else:
        areas = list(areas_raw)

    proposed = str(fm.get("proposed_at") or fm.get("created") or fm.get("fecha") or fm.get("date") or "")
    title_base = extract_title(body, doc_id)
    context = extract_context(body)
    if tipo == "instruccion" and alcance.resumen(fm):   # R-21: que el revisor vea la ampliación que aprueba
        context = alcance.resumen(fm) + (f" · {context}" if context else "")

    items: list[DecisionItem] = []
    for group_id, block_text in blocks:
        _, id_ok = validate_group_id(block_text if "<!-- decision-group:" in block_text else body, doc_id)
        if "<!-- decision-group:" in block_text:
            m = DECISION_GROUP_RE.search(block_text)
            group_id = m.group(1).strip() if m else group_id
            id_ok = group_id == doc_id or group_id.startswith(f"{doc_id}-")

        options = _parse_decision_block(block_text, group_id)
        if not options:
            options = [
                DecisionOption(action=a, label=l) for a, l in DEFAULT_OPTIONS.get(tipo, [])
            ]

        pending_options = [o for o in options if not o.checked]
        if not pending_options and options:
            continue

        block_title = title_base
        if len(blocks) > 1:
            block_title = f"{title_base} · {group_id}"

        items.append(
            DecisionItem(
                id=group_id,
                tipo=tipo,
                title=block_title,
                path=rel,
                docs_root=str(docs_root),
                pack_label=pack_label,
                status=status,
                options=options if options else pending_options,
                context=context,
                proposed_at=proposed[:10] if proposed else "",
                areas=areas,
                group_id_mismatch=not id_ok,
            )
        )

    return items


def scan_file(docs_root: Path, pack_label: str, file_path: Path) -> DecisionItem | None:
    items = scan_file_items(docs_root, pack_label, file_path)
    return items[0] if items else None


def scan_all(roots: list[tuple[Path, str]] | None = None) -> list[DecisionItem]:
    if roots is None:
        roots = resolve_docs_roots()

    items: list[DecisionItem] = []
    seen: set[str] = set()

    for docs_root, pack_label in roots:
        if not docs_root.exists():
            continue
        for md in sorted(docs_root.rglob("*.md")):
            for item in scan_file_items(docs_root, pack_label, md):
                key = f"{item.docs_root}|{item.id}"
                if key in seen:
                    continue
                seen.add(key)
                items.append(item)

    items.sort(key=lambda x: (x.pack_label, x.tipo, x.proposed_at, x.id))
    return items


def filter_stale(items: list[DecisionItem], max_days: int) -> list[DecisionItem]:
    return [i for i in items if is_stale_item(i.proposed_at, "", max_days)]


def format_scan_table(items: list[DecisionItem]) -> str:
    if not items:
        return "Sin decisiones pendientes."
    lines = [
        f"{'ID':<28} {'TIPO':<12} {'PACK':<10} {'FECHA':<12} {'PATH'}",
        "-" * 100,
    ]
    for it in items:
        flag = "!" if it.group_id_mismatch else ("+" if it.context.startswith("R-21 pide") else " ")
        lines.append(
            f"{flag}{it.id:<27} {it.tipo:<12} {it.pack_label:<10} "
            f"{it.proposed_at or '—':<12} {it.path}"
        )
    if any(it.context.startswith("R-21 pide") for it in items):
        lines.append("\n+ = pide ampliar el alcance de código (R-21): aprobarla autoriza la ampliación; revisa la justificación.")
    lines.append(f"\nTotal: {len(items)}")
    return "\n".join(lines)
