"""Mapa compacto del espejo (`50-sistema-integral/`) y detección de código sin espejo."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "decisiones"))

from common_frontmatter import split_frontmatter  # noqa: E402

EXT_CODIGO = (".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".java", ".kt", ".go", ".rs", ".rb", ".php", ".cs", ".swift", ".vue", ".svelte", ".sql", ".sh")
EXCLUIR = ("node_modules", "dist", "build", ".git", "coverage", "__pycache__", ".venv", "venv", "docs", "vendor", "target")
RESUMEN_MAX = 110


def resumen_de(md: Path) -> str:
    """`resumen:` del frontmatter o, si no existe, la primera línea de prosa (sin encabezados ni tablas)."""
    fm, cuerpo, _ = split_frontmatter(md.read_text(encoding="utf-8", errors="replace"))
    r = str(fm.get("resumen", "")).strip()
    if not r:
        for l in cuerpo.splitlines():
            l = l.strip()
            if l and not re.match(r"^(#|>|\||-{3}|<!--|```|[-*]\s*\[)", l):
                r = re.sub(r"[`*_]", "", l)
                break
    return (r[: RESUMEN_MAX - 1] + "…") if len(r) > RESUMEN_MAX else r


def mapa(docs: Path) -> str:
    base = docs / "50-sistema-integral"
    filas = []
    for md in sorted(base.rglob("*.md")) if base.is_dir() else []:
        rel = md.relative_to(base)
        if len(rel.parts) < 2 or md.name.startswith("_") or rel.as_posix() == "mapa.md":
            continue
        nombre = (rel.parent.as_posix() + "/") if md.name == "README.md" else rel.with_suffix("").as_posix()
        filas.append(f"| `{nombre}` | {resumen_de(md).replace('|', '/')} |")
    cab = ["# Mapa del espejo", "", "_Generado por `espejo-mapa.py mapa --escribir`. Léelo en lugar de recorrer `50-sistema-integral/`; abre solo el archivo que necesites._", "",
           "| Código | Qué hace |", "|--------|----------|"]
    return "\n".join(cab + (filas or ["| — | (espejo vacío) |"])) + "\n"


def faltantes(docs: Path, repo: Path, raices: list[str], excluir: tuple[str, ...] = EXCLUIR, ext: tuple[str, ...] = EXT_CODIGO) -> list[str]:
    """Archivos de código de `raices` que no tienen su `.md` en el espejo."""
    base = docs / "50-sistema-integral"
    salida = []
    for raiz in raices:
        for f in sorted((repo / raiz).rglob("*")):
            rel = f.relative_to(repo)
            if not f.is_file() or f.suffix not in ext or any(p in excluir for p in rel.parts):
                continue
            if not (base / rel.with_suffix(".md")).is_file():
                salida.append(rel.as_posix())
    return salida
