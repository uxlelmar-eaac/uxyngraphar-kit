#!/usr/bin/env python3
"""CLI — revisión de pendientes documentales."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from applier import apply_session
from archivado import aplicar as aplicar_archivado, candidatos as candidatos_archivado
from common import resolve_docs_roots
from cerrar import cmd_cerrar
from depurar_cli import cmd_depurar
from estado import cmd_estado
from metricas import calcular as calcular_metricas, formatear as formatear_metricas
from scanner import filter_stale, format_scan_table, scan_all
from session import close_session, load_active_session, register_decision, save_active_session


def cmd_scan(args: argparse.Namespace) -> int:
    items = scan_all()
    stale: list = []
    if args.max_days:
        stale = filter_stale(items, args.max_days)
        if stale:
            print(
                f"\nWARN: {len(stale)} pendiente(s) con más de {args.max_days} días:",
                file=sys.stderr,
            )
            for it in stale:
                print(f"  - {it.id} ({it.proposed_at or 'sin fecha'})", file=sys.stderr)

    display = stale if (args.max_days and args.strict) else items
    print(format_scan_table(display))

    if args.strict:
        check = stale if args.max_days else items
        if check:
            print("\nWARN: condición --strict no cumplida", file=sys.stderr)
            return 1
    return 0


def cmd_register(args: argparse.Namespace) -> int:
    items = [i for i in scan_all() if i.id == args.id and (not args.pack or i.pack_label == args.pack)]
    if not items:
        print(f"ERROR: id '{args.id}' no encontrado en el escaneo actual", file=sys.stderr)
        return 2
    if len(items) > 1:
        packs = ", ".join(sorted(i.pack_label for i in items))
        print(f"ERROR: id '{args.id}' existe en varios packs ({packs}); indica --pack <nombre>", file=sys.stderr)
        return 2
    match = items[0]
    try:
        entry = register_decision(args.id, args.action, match.to_dict())
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(entry, indent=2, ensure_ascii=False))
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    session = load_active_session()
    if not session.get("decisions"):
        print("Sesión activa sin decisiones registradas.")
        return 0

    results = apply_session(session, dry_run=args.dry_run)
    for r in results:
        print(f"\n=== {r.get('id')} ===")
        if r.get("error"):
            print(f"ERROR: {r['error']}")
        elif r.get("diff"):
            print(r["diff"])
        else:
            print(r.get("note", "OK"))

    if not args.dry_run:
        save_active_session(session)
        print(f"\nAplicadas {sum(1 for r in results if r.get('ok'))} decisiones.")
    else:
        print("\n(dry-run — sin escribir archivos)")
    return 1 if any(not r.get("ok") for r in results) else 0


def cmd_close_session(_args: argparse.Namespace) -> int:
    archived = close_session()
    print(
        f"Sesión {archived['session_id']} archivada "
        f"con {len(archived.get('decisions', []))} decisiones."
    )
    return 0


def cmd_metricas(args: argparse.Namespace) -> int:
    datos = calcular_metricas(resolve_docs_roots(), max_dias=args.max_days)
    print(json.dumps(datos, indent=2, ensure_ascii=False) if args.json else formatear_metricas(datos))
    return 0


def cmd_archivado(args: argparse.Namespace) -> int:
    cands = candidatos_archivado(args.command, resolve_docs_roots(), args.dias)
    if not cands:
        print(f"Nada que {args.command} (umbral: más de {args.dias} días).")
        return 0
    for linea in aplicar_archivado(cands, dry_run=not args.apply):
        print(linea)
    if not args.apply:
        print(f"\n{len(cands)} candidata(s). Revisa y ejecuta de nuevo con --apply para mover (nunca se borra nada).")
    elif args.command == "limpiar":
        print("\nLas fichas quedaron en 06-listas-para-eliminar/: pasarlas a la memoria (95-memoria/, R-24) es decisión humana con «depurar».")
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass

    if len(sys.argv) > 1 and sys.argv[1] == "new":   # andamiaje: delega en plantillas.py (sus propias opciones)
        from plantillas import main as main_plantillas
        return main_plantillas(sys.argv[1:])

    parser = argparse.ArgumentParser(
        description="Revisión de pendientes documentales"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("new", help="Crear una ficha desde plantilla: new {instruccion|mejora|evo|auditoria|propuesta|adr} --slug <slug> [--plantilla compacta]")

    p_scan = sub.add_parser("scan", help="Listar decisiones pendientes")
    p_scan.add_argument("--strict", action="store_true", help="Exit 1 si hay pendientes (o stale con --max-days)")
    p_scan.add_argument(
        "--max-days",
        type=int,
        default=0,
        help="Días máximos; con --strict falla solo si hay pendientes más antiguas",
    )
    p_scan.set_defaults(func=cmd_scan)

    p_reg = sub.add_parser("register", help="Registrar decisión en sesión activa")
    p_reg.add_argument("--id", required=True, help="decision-group id")
    p_reg.add_argument("--pack", default="", help="nombre del pack (obligatorio si el id existe en varios, p. ej. con DOCS_DIRS)")
    p_reg.add_argument(
        "--action",
        required=True,
        help="aprobar|rechazar|posponer|promover|cancelar|aceptar|obsoleta (válidas según el tipo de ficha)",
    )
    p_reg.set_defaults(func=cmd_register)

    p_apply = sub.add_parser("apply", help="Aplicar sesión activa a archivos .md")
    p_apply.add_argument("--dry-run", action="store_true", help="Mostrar diff sin escribir")
    p_apply.set_defaults(func=cmd_apply)

    p_close = sub.add_parser("close-session", help="Archivar sesión activa")
    p_close.set_defaults(func=cmd_close_session)

    p_met = sub.add_parser("metricas", help="Métricas del sistema documental (tabla o JSON)")
    p_met.add_argument("--json", action="store_true", help="Salida JSON para dashboards")
    p_met.add_argument("--max-days", type=int, default=30, help="Umbral de antigüedad de pendientes (default 30)")
    p_met.set_defaults(func=cmd_metricas)

    for nombre, ayuda, por_defecto in (
        ("archivar", "Mover completadas antiguas a 04-archivadas (dry-run por defecto)", 90),
        ("limpiar", "Mover canceladas antiguas a 06-listas-para-eliminar (dry-run por defecto; no borra)", 180),
    ):
        p_arc = sub.add_parser(nombre, help=ayuda)
        p_arc.add_argument("--dias", type=int, default=por_defecto, help=f"Antigüedad mínima en días (default {por_defecto})")
        p_arc.add_argument("--apply", action="store_true", help="Aplicar el movimiento (sin esto solo lista)")
        p_arc.set_defaults(func=cmd_archivado)

    p_dep = sub.add_parser("depurar", help="Diagnóstico y depuración del contenido (informe, plan, aplicar)")
    p_dep.add_argument("--docs", default="", help="raíz del pack (default: autodetectada)")
    p_dep.add_argument("--dias-archivar", type=int, default=90)
    p_dep.add_argument("--dias-limpiar", type=int, default=180)
    p_dep.add_argument("--dias-eliminar", type=int, default=None, help="días en 06 antes de proponer la memoria (config: memoria.listas_a_memoria_dias)")
    p_dep.add_argument("--dias-memoria", type=int, default=None, help="días en 04-archivadas antes de proponer la memoria (config: memoria.archivadas_a_memoria_dias)")
    p_dep.add_argument("--plan", default="", help="escribir aquí el plan editable (JSON)")
    p_dep.add_argument("--aplicar", default="", help="ejecutar un plan con ítems `aprobado: true`")
    p_dep.add_argument("--apply", action="store_true", help="con --aplicar: escribir (sin esto solo simula)")
    p_dep.set_defaults(func=cmd_depurar)

    p_cer = sub.add_parser("cerrar", help="Cerrar una instrucción: status done + mover a 03-completadas + enlaces")
    p_cer.add_argument("ref", help="id o slug de la instrucción (en 02-en-progreso)")
    p_cer.add_argument("--docs", default="")
    p_cer.add_argument("--dry-run", action="store_true")
    p_cer.set_defaults(func=cmd_cerrar)

    p_est = sub.add_parser("estado", help="Resumen vivo (en curso, esperan aprobación, colas, cerradas)")
    p_est.add_argument("--docs", default="")
    p_est.add_argument("--escribir", action="store_true", help="actualizar el bloque autogenerado de docs/ESTADO.md")
    p_est.set_defaults(func=cmd_estado)

    args = parser.parse_args()
    roots = resolve_docs_roots()
    print(f"DOCS roots: {', '.join(str(r) for r, _ in roots)}", file=sys.stderr)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
