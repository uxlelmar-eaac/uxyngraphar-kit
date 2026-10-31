"""Instalación opt-in de ganchos git que ejecutan las verificaciones del pack (EVO ganchos-git).

Los ganchos se escriben en Python (sin shell) para que funcionen igual en Windows, macOS y Linux."""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
from pathlib import Path

MARCA = "# uxyngraphar-gancho"

PLANTILLA = """#!/usr/bin/env {interprete}
{marca} ({nombre}) — instalado por instalar-ganchos.py; quitar con: instalar-ganchos.py --quitar
# Ejecuta las verificaciones del pack. WARN no bloquea; un ERROR del validador sí. controlar.py bloquea según docs/uxyngraphar.config.json.
import subprocess
import sys
from pathlib import Path

DOCS_LIST="{docs}"
PASOS = {pasos}

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
ARG = sys.argv[1] if len(sys.argv) > 1 else ""
for DOCS in DOCS_LIST.split():
    if not Path(DOCS, "scripts", "verificar-nucleo.py").is_file():
        print(f"uxyngraphar: no encuentro {{DOCS}}/scripts (¿moviste o borraste el pack?). Repara el gancho con: python3 <carpeta-del-pack>/scripts/instalar-ganchos.py --docs <ruta-docs>. Solo si estás seguro, haz el commit con --no-verify.", file=sys.stderr)
        sys.exit(1)
    for paso in PASOS:
        args = [a.replace("$DOCS", DOCS).replace("$1", ARG) for a in paso]
        if subprocess.run([sys.executable, "-X", "utf8", *args]).returncode != 0:   # UTF-8 también en Windows
            sys.exit(1)
sys.exit(0)
"""
# Cada paso: argumentos tras el intérprete. $DOCS = carpeta del pack; $1 = primer argumento del gancho (commit-msg: archivo del mensaje).
COMANDOS = {
    "pre-commit": [["$DOCS/scripts/verificar-nucleo.py", "--docs", "$DOCS"],
                   ["$DOCS/scripts/validar-documentacion.py", "$DOCS"],
                   ["$DOCS/scripts/controlar.py", "--staged", "--docs", "$DOCS"]],
    "commit-msg": [["$DOCS/scripts/controlar.py", "--mensaje", "$1", "--docs", "$DOCS"]],
    "pre-push": [["$DOCS/scripts/controlar.py", "--base", "{base}", "--docs", "$DOCS"]],
}


def interprete() -> str:
    """Nombre del intérprete para la línea #! del gancho (git lo resuelve en el PATH; en Windows, con el sh de Git)."""
    if os.name == "nt":
        return "python"
    return "python3" if shutil.which("python3") or not shutil.which("python") else "python"


def dir_ganchos(repo: Path) -> Path:
    r = subprocess.run(["git", "rev-parse", "--git-path", "hooks"], cwd=repo, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("no es un repositorio git")
    ruta = Path(r.stdout.strip())
    return ruta if ruta.is_absolute() else (repo / ruta).resolve()


def docs_del_gancho(archivo: Path) -> list[str]:
    """Carpetas de pack que un gancho nuestro ya vigila (varios packs en un mismo repo)."""
    if not es_nuestro(archivo):
        return []
    for linea in archivo.read_text(encoding="utf-8", errors="replace").splitlines():
        if linea.startswith("DOCS_LIST="):
            return linea.split("=", 1)[1].strip().strip('"').split()
    return []


def contenido(nombre: str, docs: str, base: str = "origin/main") -> str:
    pasos = [[a.replace("{base}", base) for a in paso] for paso in COMANDOS[nombre]]
    return PLANTILLA.format(interprete=interprete(), marca=MARCA, nombre=nombre, docs=docs, pasos=json.dumps(pasos, ensure_ascii=False))


def es_nuestro(archivo: Path) -> bool:
    return archivo.is_file() and MARCA in archivo.read_text(encoding="utf-8", errors="replace")


def instalar(repo: Path, docs: str, con_pre_push: bool = False, base: str = "origin/main", force: bool = False) -> list[str]:
    carpeta = dir_ganchos(repo)
    carpeta.mkdir(parents=True, exist_ok=True)
    mensajes: list[str] = []
    for nombre in ("pre-commit", "commit-msg", "pre-push") if con_pre_push else ("pre-commit", "commit-msg"):
        destino = carpeta / nombre
        if destino.exists() and not es_nuestro(destino) and not force:
            raise FileExistsError(f"ya existe un gancho {nombre} que no es de uxyngraphar ({destino}); encadénalo a mano o usa --force")
        todos = [d for d in docs_del_gancho(destino) if (repo / d / "scripts").is_dir()]   # descarta rutas viejas que ya no existen
        todos = todos + [docs] if docs not in todos else todos
        destino.write_text(contenido(nombre, " ".join(todos), base), encoding="utf-8", newline="\n")
        destino.chmod(destino.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        mensajes.append(f"Instalado: {destino}")
    return mensajes


def quitar(repo: Path) -> list[str]:
    carpeta = dir_ganchos(repo)
    mensajes: list[str] = []
    for nombre in ("pre-commit", "commit-msg", "pre-push"):
        destino = carpeta / nombre
        if es_nuestro(destino):
            os.unlink(destino)
            mensajes.append(f"Quitado: {destino}")
    return mensajes or ["No había ganchos de uxyngraphar."]
