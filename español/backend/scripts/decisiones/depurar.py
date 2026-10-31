"""Diagnóstico de depuración del contenido del proyecto (solo lectura): qué archivar, limpiar, revisar o guardar en la memoria (R-24)."""

from __future__ import annotations

import os
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "nucleo"))

import clasificacion as cl  # noqa: E402
from archivado import candidatos  # noqa: E402
from metricas import fichas  # noqa: E402

LINK_RE = re.compile(r"\]\(([^)\s#]+)(?:#[^)\s]*)?\)")
ANCLA_RE = re.compile(r"^\s*-\s*[`\"']?([^\s`\"':]+(?::\d+(?:-\d+)?)?)", re.M)


def enlaces_entrantes(docs: Path, objetivos: set[str]) -> dict[str, list[str]]:
    """Para cada ruta (relativa a docs) de `objetivos`, qué archivos .md la enlazan."""
    res: dict[str, list[str]] = {o: [] for o in objetivos}
    absolutos = {(docs / o).resolve(): o for o in objetivos}
    for md in docs.rglob("*.md"):
        if md.relative_to(docs).parts[0] == "95-memoria":   # R-24: la memoria no se lee ni cuenta como enlace vivo
            continue
        for m in LINK_RE.finditer(md.read_text(encoding="utf-8", errors="replace")):
            if re.match(r"^([a-z]+:|/)", m.group(1)):
                continue
            alvo = (md.parent / m.group(1)).resolve()
            if alvo in absolutos and md.resolve() != alvo:
                res[absolutos[alvo]].append(md.relative_to(docs).as_posix())
    return {k: sorted(set(v)) for k, v in res.items()}


def anclas_huerfanas(docs: Path) -> list[dict[str, str]]:
    """Instrucciones en curso o cerradas cuyas `anclas_codigo` ya no existen en el repo."""
    repo = docs.parent
    salida: list[dict[str, str]] = []
    for f in fichas(docs):
        if f["tipo"] != "instruccion" or f["estado"] not in ("02-en-progreso", "03-completadas"):
            continue
        anclas = f["fm"].get("anclas_codigo") or []
        for a in anclas if isinstance(anclas, list) else []:
            ruta = re.sub(r":\d+(-\d+)?$", "", str(a)).strip()
            if not ruta or "<" in ruta or ruta.startswith(("ruta/", "http")) or (repo / ruta).exists():
                continue
            salida.append({"id": f["id"], "path": f["path"], "ancla": str(a)})
    return salida


def espejo_huerfano(docs: Path) -> list[str]:
    """Archivos del espejo cuyo código fuente ya no existe (solo si la raíz de código existe en el repo)."""
    repo, base = docs.parent, docs / "50-sistema-integral"
    salida: list[str] = []
    if not base.is_dir():
        return salida
    for md in sorted(base.rglob("*.md")):
        rel = md.relative_to(docs).as_posix()
        partes = md.relative_to(base).parts
        if cl.clasificar(rel) != "C" or len(partes) < 2 or not (repo / partes[0]).exists():
            continue
        if md.name == "README.md":
            existe = (repo.joinpath(*partes[:-1])).is_dir()
        else:
            carpeta = repo.joinpath(*partes[:-1])
            existe = carpeta.is_dir() and any(carpeta.glob(md.stem + ".*"))
        if not existe:
            salida.append(rel)
    return salida


def diagnosticar(docs: Path, hoy: date | None = None, dias_archivar: int = 90, dias_limpiar: int = 180, dias_eliminar: int = 30,
                 dias_memoria: int = 180) -> dict[str, Any]:
    """`dias_eliminar`: días en 06 antes de proponer la memoria; `dias_memoria`: días en 04-archivadas (R-24; config «memoria»)."""
    hoy = hoy or datetime.now(timezone.utc).date()
    raices = [(docs, docs.name)]
    arch, limp = candidatos("archivar", raices, dias_archivar, hoy), candidatos("limpiar", raices, dias_limpiar, hoy)
    edad = lambda f: (hoy - date.fromisoformat(f["fecha"])).days  # noqa: E731
    a_memoria = [f for f in fichas(docs) if (f["estado"] == "06-listas-para-eliminar" and edad(f) > dias_eliminar)
                 or (f["estado"] == "04-archivadas" and edad(f) > dias_memoria)]
    # Una EVO es una propuesta al pack fuente: no sale de las colas mientras no se haya exportado (scripts/exportar-evo.py --marcar).
    evo_sin_exportar = [f["path"] for f in a_memoria if f["path"].startswith("46-") and not f["fm"].get("exportada_al_pack")]
    vencidas = [{"id": f["id"], "path": f["path"], "dias": edad(f), "estado": f["estado"]} for f in a_memoria if f["path"] not in evo_sin_exportar]
    mover = [{"accion": a, "id": c.id, "path": c.path, "destino": c.destino, "dias": c.dias} for a, cs in (("archivar", arch), ("limpiar", limp)) for c in cs]
    tocados = {m["path"] for m in mover} | {v["path"] for v in vencidas}
    return {"docs": str(docs), "fecha": hoy.isoformat(), "umbrales": {"archivar": dias_archivar, "limpiar": dias_limpiar, "eliminar": dias_eliminar, "memoria": dias_memoria},
            "mover": mover, "vencidas": vencidas, "evo_sin_exportar": evo_sin_exportar, "anclas_huerfanas": anclas_huerfanas(docs), "espejo_huerfano": espejo_huerfano(docs),
            "enlaces_entrantes": {k: v for k, v in enlaces_entrantes(docs, tocados).items() if v}}


def plan_desde(d: dict[str, Any]) -> list[dict[str, Any]]:
    """Plan editable: cada acción propuesta con `aprobado: false`. Lo vencido va a la memoria con un motivo ya escrito (editable)."""
    items = [{"accion": m["accion"], "id": m["id"], "path": m["path"], "aprobado": False} for m in d["mover"]]
    items += [{"accion": "memoria", "id": v["id"], "path": v["path"], "aprobado": False,
               "motivo": f"{v.get('estado', '06-listas-para-eliminar')} durante {v['dias']} días"} for v in d["vencidas"]]
    return items


def informe_md(d: dict[str, Any]) -> str:
    u = d["umbrales"]
    l = [f"# Informe de depuración — {d['fecha']}", "", f"Raíz: `{d['docs']}` · umbrales: archivar >{u['archivar']} d, limpiar >{u['limpiar']} d, "
         f"a memoria >{u['eliminar']} d en 06 o >{u.get('memoria', 180)} d en 04 (por carpeta de fecha).", ""]
    secciones = [
        ("Candidatas a mover (archivar / limpiar)", [f"- {m['accion']}: `{m['path']}` ({m['dias']} d) → `{m['destino']}`" for m in d["mover"]]),
        ("A la memoria del sistema (decisión humana; nada se borra)", [f"- `{v['path']}` ({v['dias']} d)" for v in d["vencidas"]]),
        ("EVO retenidas: exportarlas antes de guardarlas en memoria (exportar-evo.py --estados para-eliminar --marcar)", [f"- `{x}`" for x in d.get("evo_sin_exportar", [])]),
        ("Instrucciones con anclas de código inexistentes (revisar: ¿código borrado o ancla errónea?)", [f"- `{a['path']}` → `{a['ancla']}`" for a in d["anclas_huerfanas"]]),
        ("Espejo sin código fuente (candidato a retirar con instrucción mejorar-docs)", [f"- `{p}`" for p in d["espejo_huerfano"]]),
        ("Enlaces entrantes que se reescribirán al mover (o impiden guardar en memoria)", [f"- `{k}` ← {', '.join(f'`{x}`' for x in v)}" for k, v in d["enlaces_entrantes"].items()]),
    ]
    for titulo, lineas in secciones:
        l += [f"## {titulo} ({len(lineas)})", ""] + (lineas or ["- Nada."]) + [""]
    return "\n".join(l)
