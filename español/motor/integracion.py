"""Integración opcional de `uxyngraphar verificar` en un proyecto (M-16): un workflow de GitHub Actions y un gancho
pre-commit. Nada se instala por defecto (nada se ejecuta sin que la persona lo pida): se añaden y se quitan desde el
panel o con `uxyngraphar integracion`, y `retirar` los quita. Solo se tocan archivos con la marca de uxyngraphar."""

from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

MARCA = "uxyngraphar-integracion"
WORKFLOW = ".github/workflows/uxyngraphar-verificar.yml"
TIPOS = ("workflow", "precommit")
INSTALADOR = "https://github.com/uxlelmar-eaac/uxyngraphar-kit/releases/latest/download/instalar-uxyngraphar.py"

TEXTO_WORKFLOW = f"""# {MARCA}: lo añadió uxyngraphar a petición de la persona; se quita desde el panel o con «uxyngraphar integracion quitar workflow».
# Ejecuta las verificaciones de los sistemas de uxyngraphar/ en cada push y PR. Salida: 0 bien, 1 problemas, 2 error.
name: uxyngraphar verificar

on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  verificar:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0 # v7.1.0
        with:
          python-version: "3.13"
      - name: Instalar uxyngraphar
        env:
          UXYNGRAPHAR_CONSOLA: "1"
          UXYNGRAPHAR_SIN_ACCESOS: "1"
          UXYNGRAPHAR_SIN_PATH: "1"
        run: curl -fsSL {INSTALADOR} | python3 -
      - name: Verificaciones de los sistemas
        run: ~/.uxyngraphar/bin/uxyngraphar verificar --repo . --formato json --trabajos 4
"""

TEXTO_PRECOMMIT = f"""#!/bin/sh
# {MARCA}: lo añadió uxyngraphar a petición de la persona; se quita desde el panel o con «uxyngraphar integracion quitar precommit».
# Antes de cada commit, las verificaciones de los sistemas de uxyngraphar/ (si uxyngraphar no está instalado, no hace nada).
command -v uxyngraphar >/dev/null 2>&1 || exit 0
exec uxyngraphar verificar --repo "$(git rev-parse --show-toplevel)" --trabajos 4
"""


def _gancho(raiz: Path) -> Path | None:
    r = subprocess.run(["git", "rev-parse", "--git-path", "hooks"], cwd=raiz, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        return None
    ruta = Path(r.stdout.strip())
    return (ruta if ruta.is_absolute() else (raiz / ruta)).resolve() / "pre-commit"


def _ruta(raiz: Path, tipo: str) -> Path:
    if tipo not in TIPOS:
        raise ValueError(f"tipo de integración: uno de {', '.join(TIPOS)}")
    if tipo == "workflow":
        return Path(raiz) / WORKFLOW
    gancho = _gancho(Path(raiz))
    if gancho is None:
        raise ValueError("el proyecto no es un repositorio git: no hay ganchos que añadir")
    return gancho


def _nuestra(ruta: Path) -> bool:
    try:
        return ruta.is_file() and MARCA in ruta.read_text(encoding="utf-8", errors="replace")[:400]
    except OSError:
        return False


def estado(raiz: Path) -> dict[str, bool]:
    salida = {}
    for tipo in TIPOS:
        try:
            salida[tipo] = _nuestra(_ruta(raiz, tipo))
        except ValueError:
            salida[tipo] = False
    return salida


def agregar(raiz: Path, tipo: str) -> str:
    ruta = _ruta(raiz, tipo)
    if ruta.exists() and not _nuestra(ruta):
        raise FileExistsError(f"ya existe {ruta} y no es de uxyngraphar: no lo sobrescribo")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(TEXTO_WORKFLOW if tipo == "workflow" else TEXTO_PRECOMMIT, encoding="utf-8", newline="\n")
    if tipo == "precommit" and os.name != "nt":
        ruta.chmod(ruta.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return str(ruta)


def quitar(raiz: Path, tipo: str) -> bool:
    ruta = _ruta(raiz, tipo)
    if not _nuestra(ruta):
        return False
    ruta.unlink()
    return True


def quitar_todas(raiz: Path) -> list[str]:
    return [tipo for tipo in TIPOS if estado(raiz).get(tipo) and quitar(raiz, tipo)]
