#!/usr/bin/env python3
"""Puerta de control de construcción: ¿este cambio respeta cómo se construye sobre la aplicación?

Uso:  python3 docs/scripts/controlar.py [--staged | --base origin/main | --mensaje ARCHIVO] [--docs docs] [--estricto] [--config]
  --staged    lo preparado para commit (gancho pre-commit)      --base  rama base de un PR (CI; también revisa sus commits)
  --mensaje   solo el mensaje de commit y la rama (gancho commit-msg, R-22)
  --estricto  trata todos los avisos como bloqueantes          --config  muestra la configuración efectiva
Salida: 0 sin bloqueos · 1 con hallazgos bloqueantes. Niveles en docs/uxyngraphar.config.json (10-guias/control-de-construccion.md).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "control"))

from uxyngraphar_config import cargar  # noqa: E402
from puerta import control_commits, evaluar, lineas_anadidas  # noqa: E402
from idioma import archivos_nuevos, asuntos_commits, rama_actual  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent / "espejo"))
from verificar_espejo import cambiados_git, raiz_repo  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent / "control"))
from uxyngraphar_config import normalizar  # noqa: E402



def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", default=os.environ.get("ESPEJO_BASE", "origin/main"))
    ap.add_argument("--staged", action="store_true")
    ap.add_argument("--docs", default=os.environ.get("DOCS_DIR", "docs"))
    ap.add_argument("--estricto", action="store_true")
    ap.add_argument("--config", action="store_true")
    ap.add_argument("--mensaje", metavar="ARCHIVO", help="archivo con el mensaje de commit (gancho commit-msg)")
    a = ap.parse_args(argv)
    repo = raiz_repo(Path.cwd())
    if repo is not None:
        repo, a.docs = normalizar(Path.cwd(), a.docs)
    if repo is None:
        print("No es un repositorio git.", file=sys.stderr)
        return 2
    cfg, problemas = cargar(repo, a.docs)
    for p in problemas:
        print(f"WARN config: {p}", file=sys.stderr)
    if a.config:
        print(json.dumps(cfg, ensure_ascii=False, indent=2))
        return 0
    if a.mensaje:
        try:
            texto = Path(a.mensaje).read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"WARN: no pude leer el mensaje de commit ({e}); control omitido.", file=sys.stderr)
            return 0
        return _informar(control_commits([texto], rama_actual(repo), cfg), a.estricto)
    cambiados = cambiados_git(repo, a.base, a.staged)
    if cambiados is None:
        print(f"WARN: no se pudo resolver la base {a.base!r}; control omitido.", file=sys.stderr)
        return 0
    hallazgos = evaluar(repo, cambiados, lineas_anadidas(repo, a.base, a.staged), cfg, a.docs.strip("/"), archivos_nuevos(repo, a.base, a.staged))
    if not a.staged:   # CI / pre-push: los commits del PR y su rama
        hallazgos += control_commits(asuntos_commits(repo, a.base), rama_actual(repo), cfg)
    return _informar(hallazgos, a.estricto)


def _informar(hallazgos: list, estricto: bool) -> int:
    bloqueo = False
    for h in hallazgos:
        bloquea = h.nivel == "bloqueante" or estricto
        bloqueo |= bloquea
        print(f"{'ERROR' if bloquea else 'WARN'} [{h.control}] {h.mensaje}")
    print(f"controlar: {len(hallazgos)} hallazgo(s); " + ("BLOQUEADO" if bloqueo else "OK"))
    return 1 if bloqueo else 0


if __name__ == "__main__":
    raise SystemExit(main())
