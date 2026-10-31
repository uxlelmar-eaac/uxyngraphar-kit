"""Escaneo de credenciales sobre el árbol de trabajo y sobre todo el historial git (auditoría, R-12)."""

from __future__ import annotations

import fnmatch
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import secretos as sec  # noqa: E402

MAX_BYTES = 2_000_000


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", "-c", "core.quotepath=false", *args], cwd=repo, capture_output=True)


def _permitido(ruta: str, permitir: list[str]) -> bool:
    return any(fnmatch.fnmatch(ruta, p) for p in permitir)


def arbol(repo: Path, permitir: list[str] | None = None) -> list[sec.Hallazgo]:
    """Archivos versionados + nuevos no ignorados."""
    r = _git(repo, "ls-files", "-co", "--exclude-standard", "-z")
    salida: list[sec.Hallazgo] = []
    for rel in (p for p in r.stdout.decode("utf-8", "replace").split("\0") if p):
        if _permitido(rel, permitir or []):
            continue
        if sec.archivo_prohibido(rel):
            salida.append(sec.Hallazgo(rel, 0, "archivo de credenciales", Path(rel).name))
            continue
        f = repo / rel
        try:
            if not f.is_file() or f.stat().st_size > MAX_BYTES:
                continue
            datos = f.read_bytes()
        except OSError:
            continue
        if b"\0" in datos[:4096]:
            continue
        salida += sec.escanear_texto(rel, datos.decode("utf-8", "replace"))
    return salida


def historia(repo: Path, limite: int = 0, permitir: list[str] | None = None) -> list[tuple[str, sec.Hallazgo]]:
    """(commit, hallazgo) para líneas añadidas en cualquier commit de cualquier rama; y archivos prohibidos que alguna vez existieron."""
    args = ["log", "--all", "-p", "-U0", "--no-color", "--format=@@COMMIT %h", "--diff-filter=ACMR"]
    if limite:
        args.append(f"-{limite}")
    r = _git(repo, *args)
    commit, archivo, n = "", "", 0
    salida: list[tuple[str, sec.Hallazgo]] = []
    vistos: set[tuple[str, str, str]] = set()
    for linea in r.stdout.decode("utf-8", "replace").splitlines():
        if linea.startswith("+++ b/") and _permitido(linea[6:], permitir or []):
            archivo = ""
            continue
        if not archivo and linea.startswith("+") and not linea.startswith("+++"):
            continue
        if linea.startswith("@@COMMIT "):
            commit = linea[9:]
        elif linea.startswith("+++ b/"):
            archivo = linea[6:]
            if sec.archivo_prohibido(archivo) and (commit, archivo, "") not in vistos:
                vistos.add((commit, archivo, ""))
                salida.append((commit, sec.Hallazgo(archivo, 0, "archivo de credenciales", Path(archivo).name)))
        elif linea.startswith("+") and not linea.startswith("+++"):
            h = sec.en_linea(linea[1:], archivo)
            if h and (commit, archivo, h[1]) not in vistos:
                vistos.add((commit, archivo, h[1]))
                salida.append((commit, sec.Hallazgo(archivo, 0, h[0], h[1])))
    return salida
