"""Subcomando `depurar` de decisiones.py."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from common import resolve_docs_roots
from depurar import diagnosticar, informe_md, plan_desde
from depurar_aplicar import aplicar_plan


def _config_memoria(docs: Path) -> dict:
    """Plazos de la sección «memoria» de uxyngraphar.config.json (valores por defecto si no hay configuración)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "control"))
    import uxyngraphar_config as cfgmod
    return cfgmod.cargar(docs.parent, docs.name)[0]["memoria"]


def cmd_depurar(args: argparse.Namespace) -> int:
    docs = Path(args.docs).resolve() if args.docs else resolve_docs_roots()[0][0]
    if args.aplicar:
        plan = json.loads(Path(args.aplicar).read_text(encoding="utf-8"))
        lineas = aplicar_plan(docs, plan, dry_run=not args.apply)
        print("\n".join(lineas))
        if not args.apply:
            print("\n(simulación — usa --apply para ejecutar)")
        return 1 if any(l.startswith("RECHAZADO") for l in lineas) else 0
    mem = _config_memoria(docs)
    d = diagnosticar(docs, dias_archivar=args.dias_archivar, dias_limpiar=args.dias_limpiar,
                     dias_eliminar=mem["listas_a_memoria_dias"] if args.dias_eliminar is None else args.dias_eliminar,
                     dias_memoria=mem["archivadas_a_memoria_dias"] if args.dias_memoria is None else args.dias_memoria)
    print(informe_md(d))
    if args.plan:
        Path(args.plan).write_text(json.dumps(plan_desde(d), indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print(f"Plan escrito en {args.plan}: marca `aprobado: true` en lo que apruebes y ejecuta `depurar --aplicar {args.plan}`.", file=sys.stderr)
    return 0
