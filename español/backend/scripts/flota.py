#!/usr/bin/env python3
"""Tablero de proyectos: ejecuta el doctor en varios repos y muestra una tabla comparativa.

Uso:  python3 scripts/flota.py RUTA_REPO [RUTA_REPO …] [--docs docs] [--pack RUTA_PACK] [--json]
      python3 scripts/flota.py --lista repos.txt         # un repo por línea
Solo lectura. Usa el doctor de cada proyecto (docs/scripts/doctor.py). Salida: 1 si algún proyecto tiene errores.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def revisar(repo: Path, docs: str, pack: str) -> dict:
    doctor = repo / docs / "scripts" / "doctor.py"
    if not doctor.is_file():
        return {"repo": repo.name, "version": "—", "error": "sin doctor.py (¿no tiene uxyngraphar?)", "errores": -1, "avisos": 0, "motivos": []}
    cmd = [sys.executable, "-X", "utf8", "-I", str(doctor), "--repo", str(repo), "--docs", docs, "--json"] + (["--pack", pack] if pack else [])
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        cs = json.loads(r.stdout)
    except ValueError:
        return {"repo": repo.name, "version": "—", "error": "salida del doctor ilegible", "errores": -1, "avisos": 0, "motivos": []}
    lockc = next((c["mensaje"] for c in cs if c["id"] == "lock"), "")
    version = lockc.split("pack ")[-1].split(" ·")[0] if "pack " in lockc else "—"
    return {"repo": repo.name, "version": version, "errores": sum(c["nivel"] == "ERROR" for c in cs), "avisos": sum(c["nivel"] == "WARN" for c in cs),
            "motivos": [c["id"] for c in cs if c["nivel"] in ("ERROR", "WARN")]}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repos", nargs="*")
    ap.add_argument("--lista", default="")
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--pack", default="")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    rutas = list(a.repos)
    if a.lista:
        rutas += [l.strip() for l in Path(a.lista).read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    if not rutas:
        ap.error("indica al menos un repositorio")
    filas = [revisar(Path(r).resolve(), a.docs, str(Path(a.pack).resolve()) if a.pack else "") for r in rutas]
    if a.json:
        print(json.dumps(filas, ensure_ascii=False, indent=2))
    else:
        print(f"{'Proyecto':<24}{'Pack':<10}{'Err':>4}{'Avi':>5}  Motivos")
        for f in filas:
            print(f"{f['repo']:<24}{f['version']:<10}{f['errores'] if f['errores'] >= 0 else '?':>4}{f['avisos']:>5}  {f.get('error') or ', '.join(f['motivos']) or 'sano'}")
    return 1 if any(f["errores"] != 0 for f in filas) else 0


if __name__ == "__main__":
    raise SystemExit(main())
