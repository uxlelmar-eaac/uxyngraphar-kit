"""Verificación en el servidor: genera el workflow de GitHub Actions y diagnostica si hay CI que ejecute uxyngraphar.

El gancho pre-commit es local y `git commit --no-verify` lo salta: solo un check del servidor, marcado como requerido en la
protección de rama, hace cumplir el protocolo. GitHub únicamente lee `.github/workflows/` de la RAÍZ del repositorio.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import clasificacion as cl

MARCAS_uxyngraphar = ("verificar-nucleo", "controlar.py", "uxyngraphar")
OTROS_CI = (".gitlab-ci.yml", "azure-pipelines.yml", "Jenkinsfile", "bitbucket-pipelines.yml", ".circleci/config.yml")

PLANTILLA = """# Generado por uxyngraphar. Verifica en el servidor lo que el gancho local no puede garantizar (git commit --no-verify lo salta).
# Para que obligue de verdad: Settings → Branches → regla de protección → «Require status checks» → «{job}».
name: {nombre}

on:
  pull_request:
  push:
    branches: [main, master]

permissions:
  contents: read

concurrency:
  group: {grupo}-${{{{ github.ref }}}}
  cancel-in-progress: true

jobs:
  {job}:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Documentación válida
        run: python3 {docs}/scripts/validar-documentacion.py {docs}
      - name: Núcleo íntegro (R-20)
        run: python3 {docs}/scripts/verificar-nucleo.py --docs {docs}
      - name: Credenciales en el árbol (R-12)
        run: python3 {docs}/scripts/escanear-secretos.py --docs {docs}
      - name: Puerta de control del cambio
        if: github.event_name == 'pull_request'
        run: python3 {docs}/scripts/controlar.py --docs {docs} --base origin/${{{{ github.base_ref }}}}
"""


def nombre_archivo(docs: str) -> str:
    app = cl.padre(docs)
    return "uxyngraphar.yml" if not app else "uxyngraphar-" + re.sub(r"[^a-z0-9]+", "-", app.lower()).strip("-") + ".yml"


def workflow(repo: Path, docs: str, dry_run: bool = False) -> tuple[Path, bool]:
    """Crea `.github/workflows/uxyngraphar*.yml` en la raíz del repo. No sobrescribe: devuelve (ruta, creado)."""
    docs = docs.strip("/")
    f = repo / ".github" / "workflows" / nombre_archivo(docs)
    if f.exists():
        return f, False
    if not dry_run:
        slug = nombre_archivo(docs)[:-4]
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(PLANTILLA.format(nombre="uxyngraphar" + (f" ({cl.padre(docs)})" if cl.padre(docs) else ""), job=slug.replace("-", "_"),
                                      grupo=slug, docs=docs), encoding="utf-8", newline="\n")
    return f, True


def git_lineas(repo: Path, *a: str) -> list[str]:
    r = subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True)
    return r.stdout.splitlines() if r.returncode == 0 else []


def _ejecuta_uxyngraphar(repo: Path) -> bool:
    candidatos = list((repo / ".github" / "workflows").glob("*.y*ml")) + [repo / n for n in OTROS_CI]
    for f in candidatos:
        try:
            if f.is_file() and any(m in f.read_text(encoding="utf-8", errors="replace") for m in MARCAS_uxyngraphar):
                return True
        except OSError:
            continue
    return False


def chequeos(repo: Path, docs: str) -> list[tuple[str, str, str, str]]:
    """(id, nivel, mensaje, arreglo) para el doctor."""
    out: list[tuple[str, str, str, str]] = []
    if _ejecuta_uxyngraphar(repo):
        out.append(("ci", "OK", "Hay CI que ejecuta uxyngraphar en el servidor", ""))
    else:
        out.append(("ci", "WARN", "Ningún workflow ejecuta uxyngraphar: la protección solo existe en tu máquina (git commit --no-verify la salta)",
                    "instalar-pack.py --proteger crea .github/workflows/uxyngraphar.yml; o copia los pasos de 10-guias/ci-validacion-documentacion.md"))
    mal = [p for p in git_lineas(repo, "ls-files", "--", "*/.github/workflows/*.yml", "*/.github/workflows/*.yaml") if not p.startswith(".github/")]
    if mal:
        out.append(("ci-ubicacion", "WARN", f"{len(mal)} workflow(s) en subcarpetas que GitHub NO ejecuta (solo lee .github/workflows/ de la raíz del repo): {', '.join(mal[:3])}",
                    "Muévelos a .github/workflows/ en la raíz (en un monorepo usa working-directory en cada paso)"))
    return out
