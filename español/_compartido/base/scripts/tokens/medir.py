"""Medición de costo en tokens: arranque del agente, una instrucción o los archivos más pesados de un pack."""

from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from estimar import tokens  # noqa: E402

# Lo que un agente lee al empezar cualquier tarea (AGENTES.md vive en la raíz del repo; ESTADO.md en docs/).
ARRANQUE = ("AGENTES.md", "docs/ESTADO.md")
ARRANQUE_MAX = 1500


def archivo(ruta: Path) -> int:
    return tokens(ruta.read_text(encoding="utf-8", errors="replace")) if ruta.is_file() else 0


def arranque(repo: Path, docs: str = "docs") -> list[tuple[str, int]]:
    filas = []
    for rel in ARRANQUE:
        rel = rel.replace("docs/", docs.strip("/") + "/", 1) if rel.startswith("docs/") else rel
        f = repo / rel
        if not f.is_file() and rel == "AGENTES.md":
            f = repo / docs / "AGENTES.md"   # dentro del propio pack
        filas.append((rel, archivo(f)))
    return filas


def pesados(raiz: Path, top: int = 15) -> list[tuple[str, int]]:
    filas = [(p.relative_to(raiz).as_posix(), archivo(p)) for p in raiz.rglob("*.md") if "scripts/" not in p.as_posix() and "95-memoria/" not in p.as_posix()]
    return sorted(filas, key=lambda x: -x[1])[:top]
