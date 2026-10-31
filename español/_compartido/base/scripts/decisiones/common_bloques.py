"""Bloques de decisión y extracción de título/contexto — revisión de pendientes.

Extraído de `common.py` (R-19). Depende solo de `common_constantes`.
"""

from __future__ import annotations

from common_constantes import DECISION_GROUP_RE, DECISION_SECTION_RE, TITLE_RE


def extract_title(body: str, fallback: str) -> str:
    m = TITLE_RE.search(body)
    return m.group(1).strip() if m else fallback


def extract_context(body: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith(">"):
            if stripped.startswith("- "):
                return stripped[2:][:120]
            return stripped[:120]
    return ""


def has_decision_section(body: str) -> bool:
    return DECISION_SECTION_RE.search(body) is not None


def iter_decision_blocks(body: str, fm_id: str) -> list[tuple[str, str]]:
    """Retorna [(group_id, block_text), ...] incluyendo alias sin decision-group."""
    blocks: list[tuple[str, str]] = []
    lines = body.splitlines()

    group_starts: list[tuple[int, str]] = []
    for idx, line in enumerate(lines):
        m = DECISION_GROUP_RE.search(line)
        if m:
            group_starts.append((idx, m.group(1).strip()))

    if group_starts:
        for gi, (start_idx, group_id) in enumerate(group_starts):
            end_idx = group_starts[gi + 1][0] if gi + 1 < len(group_starts) else len(lines)
            block_lines: list[str] = []
            for ln in lines[start_idx:end_idx]:
                if block_lines and ln.startswith("## ") and "Decisión" not in ln and "Decisiones" not in ln:
                    break
                block_lines.append(ln)
            blocks.append((group_id, "\n".join(block_lines)))
        return blocks

    i = 0
    while i < len(lines):
        line = lines[i]
        if DECISION_SECTION_RE.match(line.strip()):
            block_lines = [line]
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if nxt.startswith("## ") and "Decisión" not in nxt and "Decisiones" not in nxt:
                    break
                block_lines.append(nxt)
                i += 1
            blocks.append((fm_id, "\n".join(block_lines)))
            continue
        i += 1
    return blocks


def find_group_id(body: str, fm_id: str) -> str:
    blocks = iter_decision_blocks(body, fm_id)
    if blocks:
        return blocks[0][0]
    m = DECISION_GROUP_RE.search(body)
    if m:
        return m.group(1).strip()
    return fm_id


def validate_group_id(body: str, fm_id: str) -> tuple[str, bool]:
    group_id = find_group_id(body, fm_id)
    ok = group_id == fm_id or group_id.startswith(f"{fm_id}-")
    return group_id, ok
