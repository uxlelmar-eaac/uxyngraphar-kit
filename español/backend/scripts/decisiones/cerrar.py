"""Cierre asistido de una instrucción: status done, ficha a 03-completadas, enlaces reescritos y recordatorios."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import alcance
from common import estado_dest_rel, rebuild_content, resolve_docs_roots, split_frontmatter_parts, update_frontmatter_raw, utc_now_iso
from depurar_aplicar import reescribir_enlaces

ABIERTAS = ("02-en-progreso",)


class ErrorCierre(ValueError):
    pass


def _buscar(docs: Path, ref: str) -> Path:
    from metricas import fichas
    hallazgos = [f for f in fichas(docs) if f["tipo"] == "instruccion" and (ref in (f["id"], Path(f["path"]).stem) or f["id"].endswith("-" + ref))]
    if not hallazgos:
        raise ErrorCierre(f"no se encontró la instrucción «{ref}»")
    if len(hallazgos) > 1:
        raise ErrorCierre(f"«{ref}» es ambiguo: {', '.join(f['id'] for f in hallazgos)}")
    f = hallazgos[0]
    if f["estado"] not in ABIERTAS:
        raise ErrorCierre(f"{f['id']} está en {f['estado']}; solo se cierran las de 02-en-progreso (¿falta aprobarla?)")
    return docs / f["path"]


def _lista(fm: dict, clave: str) -> list[str]:
    v = fm.get(clave)
    return [str(x) for x in v] if isinstance(v, list) else []


def cerrar(docs: Path, ref: str, dry_run: bool = False) -> list[str]:
    origen = _buscar(docs, ref)
    raw, fm, cuerpo = split_frontmatter_parts(origen.read_text(encoding="utf-8"))
    if raw is None:
        raise ErrorCierre("la ficha no tiene frontmatter")
    rel = origen.relative_to(docs).as_posix()
    destino_rel = estado_dest_rel(rel, fm, "03-completadas")
    bloqueos = alcance.bloqueos(fm)
    if bloqueos:   # R-21: no se da por buena una entrega que excedió el alcance sin fraccionar ni aprobación
        raise ErrorCierre("R-21 — " + "; ".join(bloqueos) + ". Corrige la ficha (o registra la aprobación humana) antes de cerrar.")
    salida: list[str] = []
    faltan = [e for e in _lista(fm, "espejo_actualizar") if not (docs / e.strip().strip("`").removeprefix("docs/")).exists()]
    if faltan:
        salida.append(f"AVISO: espejo_actualizar sin escribir ({len(faltan)}): {', '.join(faltan[:4])}")
    if _lista(fm, "anclas_codigo") and not _lista(fm, "espejo_actualizar"):
        salida.append("AVISO: tiene anclas_codigo pero no espejo_actualizar")
    if len(_lista(fm, "mejoras_propuestas")) > 3:
        salida.append("AVISO: más de 3 mejoras_propuestas (máximo 3)")
    if len(_lista(fm, "evolucion_documentacion")) > 2:
        salida.append("AVISO: más de 2 evolucion_documentacion (máximo 2)")
    if not _lista(fm, "vinculos_salida"):
        salida.append("AVISO: vinculos_salida vacío (se exige con STRICT_VINCULOS)")
    if dry_run:
        return salida + [f"[dry-run] {fm.get('id')}: {rel} → {destino_rel} (status: done)"]
    destino = docs / destino_rel
    if destino.exists():
        raise ErrorCierre(f"ya existe {destino_rel}")
    origen.write_text(rebuild_content(update_frontmatter_raw(raw, {"status": "done", "executed_at": utc_now_iso()}), cuerpo), encoding="utf-8", newline="\n")
    salida += _costo(docs, origen, str(fm.get("id") or origen.stem))
    destino.parent.mkdir(parents=True, exist_ok=True)
    origen.replace(destino)
    reescribir_enlaces(docs, {rel: destino_rel})
    salida += _indice_reglas(docs, _lista(fm, "anclas_codigo"))
    return salida + [f"{fm.get('id')}: cerrada → {destino_rel}", "Recuerda: deuda fuera de alcance → 45 (≤3); gap del sistema documental → 46 (≤2)."]


def _indice_reglas(docs: Path, anclas: list[str]) -> list[str]:
    """Si la instrucción tocó reglas del proyecto (96-reglas-proyecto/), regenera su INDICE.md."""
    if not any("96-reglas-proyecto/" in a for a in anclas):
        return []
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "reglas"))
        import reglas_proyecto
        return ["96-reglas-proyecto/INDICE.md regenerado"] if reglas_proyecto.regenerar_indice(docs) else []
    except Exception as exc:  # noqa: BLE001 - nunca impide cerrar
        return [f"AVISO: no se pudo regenerar 96-reglas-proyecto/INDICE.md ({exc})"]


def _costo(docs: Path, ficha: Path, ident: str) -> list[str]:
    """Cierra la medición del costo en tokens y escribe la tabla en la ficha (10-guias/costo-tokens.md). Nunca impide cerrar."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tokens"))
        import costo
        raiz = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=docs, capture_output=True, text=True).stdout.strip()
        costo.terminar(docs, ident)
        m = costo.medir(Path(raiz) if raiz else docs.parent, docs, ident, ficha)
        costo.escribir(ficha, m)
        return [f"Costo en tokens: {sum(costo.total(v) for v in m['fases'].values()):,} ({m['fuente']}); tabla en «Costo en tokens».".replace(",", " ")]
    except Exception as exc:  # noqa: BLE001
        return [f"AVISO: no se pudo medir el costo en tokens ({exc}); usa costo-tokens.py medir {ident}"]


def cmd_cerrar(args: argparse.Namespace) -> int:
    docs = Path(args.docs).resolve() if args.docs else resolve_docs_roots()[0][0]
    try:
        lineas = cerrar(docs, args.ref, args.dry_run)
    except ErrorCierre as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print("\n".join(lineas))
    return 0
