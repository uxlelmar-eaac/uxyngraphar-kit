"""Enlaces markdown relativos rotos y secretos reales en los .md."""

from __future__ import annotations

import re
from pathlib import Path

from validar_comun import Pack, Reporte, iter_md, sin_codigo

ENLACE_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
SECRETO_RE = re.compile(
    r"(api[_-]?key|secret|password|passwd|token|bearer|authorization|client[_-]?secret)\s*[:=]\s*[A-Za-z0-9/+=_-]{12,}"
    r"|Bearer\s+[A-Za-z0-9._-]{20,}",
    re.IGNORECASE,
)
# Líneas que mencionan secretos sin serlo: placeholders, `<VARIABLE>` o referencias al gestor de secretos.
PERMITIDO_RE = re.compile(r"PLACEHOLDER|<[A-Za-z_]+>|gestor de secretos", re.IGNORECASE)
MAX_SECRETOS = 10


def enlaces_rotos(pack: Pack) -> list[tuple[Path, str]]:
    rotos: list[tuple[Path, str]] = []
    for md in iter_md(pack.docs):
        for m in ENLACE_RE.finditer(sin_codigo(md.read_text(encoding="utf-8"))):
            destino = m.group(1)
            if re.match(r"^(https?:|mailto:|#)", destino) or any(c in destino for c in "<{"):
                continue
            ruta = destino.split("#", 1)[0].split("?", 1)[0]
            if not ruta or ruta in {".", ".."}:
                continue
            resuelto = (md.parent / ruta).resolve()
            if pack.docs not in resuelto.parents and resuelto != pack.docs:
                continue  # apunta fuera del pack (p. ej. código del repo): no verificable aquí
            if resuelto.parent == pack.docs and resuelto.name in ("AGENTES.md", "AGENTS.md") and (pack.docs.parent / resuelto.name).exists():
                continue  # instalado: el punto de entrada de agentes vive en la raíz del repo, no en docs/
            if not resuelto.exists():
                rotos.append((md, destino))
    return rotos


def secretos_posibles(pack: Pack) -> list[str]:
    hallazgos: list[str] = []
    for md in iter_md(pack.docs):
        for n, linea in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            if SECRETO_RE.search(linea) and not PERMITIDO_RE.search(linea):
                hallazgos.append(f"{md.relative_to(pack.docs).as_posix()}:{n}: {linea.strip()[:100]}")
                if len(hallazgos) >= MAX_SECRETOS:
                    return hallazgos
    return hallazgos


def validar(pack: Pack, rep: Reporte) -> None:
    for md, destino in enlaces_rotos(pack):
        rep.warn(f"Link posiblemente roto en {md.relative_to(pack.docs).as_posix()} → {destino}")
    hallazgos = secretos_posibles(pack)
    if hallazgos:
        for h in hallazgos:
            rep.warn(f"  {h}")
        rep.warn("Posibles secretos en docs — revisar manualmente")
