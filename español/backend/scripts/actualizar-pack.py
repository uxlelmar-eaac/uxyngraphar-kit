#!/usr/bin/env python3
"""Actualiza el núcleo de un proyecto desde un pack más nuevo (tres vías, con simulación por defecto).

Uso:  python3 actualizar-pack.py RUTA_PACK [--repo .] [--docs docs]            # simula
      python3 actualizar-pack.py RUTA_PACK --apply [--restaurar-nucleo] [--migracion-aprobada ID]
Nunca toca contenido del proyecto. Conflictos → «<archivo>.uxyngraphar-nuevo». Respaldo en .uxyngraphar-respaldo/.
Salida: 0 al día/aplicado sin conflictos · 1 hay cambios pendientes o conflictos · 2 error.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "nucleo"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "decisiones"))

import lock  # noqa: E402
from empaquetar import abrir_pack  # noqa: E402
from actualizar import ErrorActualizacion, aplicar, formatear, planificar  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent / "control"))
from uxyngraphar_config import normalizar  # noqa: E402



def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pack", help="carpeta del pack nuevo o .zip de empaquetar-pack.py")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--apply", action="store_true", help="escribir los cambios (por defecto solo simula)")
    ap.add_argument("--restaurar-nucleo", action="store_true", help="también sobrescribir archivos del núcleo editados en el proyecto")
    ap.add_argument("--migracion-aprobada", default="", help="id de la instrucción aprobada que autoriza un salto MAYOR")
    ap.add_argument("--evo", action="store_true", help="tras aplicar, crear la ficha EVO de adopción")
    a = ap.parse_args(argv)
    repo, a.docs = normalizar(Path(a.repo), a.docs)
    try:
        with abrir_pack(Path(a.pack).resolve()) as pack:
            return _actualizar(a, pack, repo)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


def _actualizar(a: argparse.Namespace, pack: Path, repo: Path) -> int:
    if not (pack / "VERSION.md").is_file():
        print(f"ERROR: {pack} no parece un pack (falta VERSION.md).", file=sys.stderr)
        return 2
    try:
        plan = planificar(pack, repo, a.docs, a.restaurar_nucleo)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"Comparando el núcleo de tu proyecto (versión {plan.adoptada}) con el pack ({plan.nueva}). Tu contenido (fichas, instrucciones, rutas) nunca se toca.\n")
    print(formatear(plan))
    pendientes = bool(plan.acciones) or plan.adoptada != plan.nueva
    if not a.apply:
        if pendientes:
            print("\nEsto fue solo una simulación: no se escribió nada.")
            print("Para aplicar estos cambios, ejecuta el mismo comando añadiendo --apply (se hace antes una copia de seguridad en .uxyngraphar-respaldo/).")
            if plan.de("conflicto"):
                print("Los archivos en conflicto no se pisan: la versión nueva quedará como «.uxyngraphar-nuevo» junto al tuyo para que decidas.")
        return 1 if pendientes else 0
    try:
        respaldo = aplicar(pack, repo, a.docs, plan, a.migracion_aprobada, probar=True)
    except ErrorActualizacion as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\nCancelado. La actualización se deshizo: el proyecto quedó como estaba.", file=sys.stderr)
        return 130
    for aviso in plan.avisos:
        print(f"! {aviso}")
    for ident, hecho in plan.hechas:
        print(f"Migración {ident}: " + ("; ".join(hecho) or "nada que cambiar"))
    print(f"\nListo, núcleo actualizado. Versión del núcleo: {lock.leer(repo, a.docs)['version']}" + (f" · respaldo: {respaldo}" if respaldo else ""))
    doctor = repo / a.docs / "scripts" / "doctor.py"
    if doctor.is_file():   # el doctor recién instalado conoce las protecciones nuevas (CI, deny, .gitignore, .gitattributes…)
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(doctor), "--fix", "--docs", a.docs], cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace")
        print("\nRevisión de protecciones tras actualizar (doctor --fix):\n" + "\n".join("  " + l for l in (r.stderr + "\n" + r.stdout).splitlines() if l.startswith("fix:") or "[ERROR]" in l or "[WARN]" in l or "Resumen" in l or "→" in l))
    if a.evo:
        from datetime import date
        import plantillas
        print("Ficha EVO:", plantillas.crear(repo / a.docs, "evo", "adopcion-" + plan.nueva.replace(".", "-"), date.today()))
    return 1 if plan.de("conflicto") else 0


if __name__ == "__main__":
    raise SystemExit(main())
