"""Lectura y escritura de frontmatter YAML — revisión de pendientes.

Extraído de `common.py` (R-19). Depende solo de `common_constantes`.
"""

from __future__ import annotations

from typing import Any

from common_constantes import FM_KEY_RE, FRONTMATTER_RE


def _strip_yaml_scalar(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def _comment_start(text: str) -> int:
    """Índice del `#` que inicia un comentario inline (fuera de comillas, tras espacio); -1 si no hay."""
    quote = ""
    for i, ch in enumerate(text):
        if quote:
            if ch == quote:
                quote = ""
        elif ch in "\"'":
            quote = ch
        elif ch == "#" and i > 0 and text[i - 1] in " \t":
            return i
    return -1


def _strip_inline_comment(text: str) -> str:
    idx = _comment_start(text)
    return text[:idx].rstrip() if idx >= 0 else text


def parse_simple_yaml(yaml_text: str) -> dict[str, Any]:
    """Parser YAML mínimo para frontmatter (sin dependencias externas).

    Soporta escalares, listas inline `[a, b]`, listas `  - x` y bloques `|`/`>`.
    No soporta mapas anidados: una clave con hijos indentados no-lista se lee como `[]`.
    Los comentarios inline (` # ...` fuera de comillas) se descartan del valor.
    """
    result: dict[str, Any] = {}
    current_key: str | None = None
    lines = yaml_text.splitlines()
    i = 0
    while i < len(lines):
        raw_line = lines[i]
        line = raw_line.rstrip()
        i += 1
        if not line or line.strip().startswith("#"):
            continue
        if line.startswith("  - ") and current_key:
            item = _strip_yaml_scalar(line[4:].strip())
            if isinstance(result.get(current_key), list):
                result[current_key].append(item)
            else:
                result[current_key] = [item]
            continue
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            key = key.strip()
            value = _strip_inline_comment(value.strip())
            if value in {"", "[]"}:
                result[key] = []
            elif value == "null":
                result[key] = None
            elif value.startswith("[") and value.endswith("]"):
                inner = value[1:-1].strip()
                if not inner:
                    result[key] = []
                else:
                    result[key] = [
                        _strip_yaml_scalar(part.strip()) for part in inner.split(",") if part.strip()
                    ]
            elif value in {"|", ">"}:
                block: list[str] = []
                while i < len(lines) and (lines[i].startswith("  ") or lines[i].strip() == ""):
                    block.append(lines[i].strip())
                    i += 1
                result[key] = " ".join(part for part in block if part)
            else:
                result[key] = _strip_yaml_scalar(value)
            current_key = key
    return result


def split_frontmatter(content: str) -> tuple[dict[str, Any], str, str | None]:
    match = FRONTMATTER_RE.match(content)
    if not match:
        return {}, content, None
    raw_yaml = match.group(1)
    fm = parse_simple_yaml(raw_yaml)
    body = content[match.end() :]
    return fm, body, match.group(0)


def split_frontmatter_parts(content: str) -> tuple[str | None, dict[str, Any], str]:
    """Retorna (raw_yaml, fm_dict, body)."""
    match = FRONTMATTER_RE.match(content)
    if not match:
        return None, {}, content
    raw_yaml = match.group(1)
    return raw_yaml, parse_simple_yaml(raw_yaml), content[match.end() :]


def update_frontmatter_raw(raw_yaml: str, updates: dict[str, str]) -> str:
    """Actualiza claves en YAML raw preservando orden, comentarios y resto del bloque."""
    lines = raw_yaml.splitlines()
    result: list[str] = []
    updated: set[str] = set()

    for line in lines:
        m = FM_KEY_RE.match(line)
        if m and not line.startswith(" "):
            key = m.group(1)
            if key in updates:
                rest = line.split(":", 1)[1]
                idx = _comment_start(rest)
                comment = " " + rest[idx:] if idx >= 0 else ""
                result.append(f"{key}: {updates[key]}{comment}")
                updated.add(key)
                continue
        result.append(line)

    for key, value in updates.items():
        if key not in updated:
            result.append(f"{key}: {value}")

    # Siempre termina en salto de línea: `FRONTMATTER_RE` captura el YAML sin él y
    # `rebuild_content` pega el cierre `---` justo después.
    return "\n".join(result) + "\n"


def rebuild_content(raw_yaml: str | None, body: str) -> str:
    if raw_yaml is None:
        return body
    if not raw_yaml.endswith("\n"):
        raw_yaml += "\n"
    return f"---\n{raw_yaml}---\n{body}"


def serialize_frontmatter(fm: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in fm.items():
        if isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
            else:
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
        elif value is None:
            lines.append(f"{key}: null")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines) + "\n"
