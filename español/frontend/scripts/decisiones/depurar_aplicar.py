"""Aplicación de un plan de depuración aprobado por un humano. Mover es reversible; lo que antes se borraba va a la memoria (R-24)."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any

from archivado import aplicar as aplicar_mov, candidatos
from depurar import LINK_RE
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "memoria"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "nucleo"))
import almacen  # noqa: E402
from terminal import hay_terminal  # noqa: E402


def reescribir_enlaces(docs: Path, mapa: dict[str, str]) -> int:
    """Actualiza en todo `docs` los enlaces relativos que apuntaban a rutas movidas (`mapa` antiguo→nuevo, relativas a docs)."""
    absolutos = {(docs / o).resolve(): docs / n for o, n in mapa.items()}
    cambios = 0
    for md in docs.rglob("*.md"):
        if md.relative_to(docs).parts[0] == almacen.CARPETA:   # una memoria no se edita (R-24)
            continue
        texto = md.read_text(encoding="utf-8", errors="replace")

        def cambiar(m: re.Match[str]) -> str:
            nonlocal cambios
            if re.match(r"^([a-z]+:|/)", m.group(1)):
                return m.group(0)
            nuevo = absolutos.get((md.parent / m.group(1)).resolve())
            if nuevo is None:
                return m.group(0)
            cambios += 1
            return m.group(0).replace(m.group(1), os.path.relpath(nuevo, md.parent).replace(os.sep, "/"), 1)

        nuevo_texto = LINK_RE.sub(cambiar, texto)
        if nuevo_texto != texto:
            md.write_text(nuevo_texto, encoding="utf-8", newline="\n")
    return cambios


def _es_humano() -> bool:
    return hay_terminal() or "1" in (os.environ.get("UXYNGRAPHAR_HUMANO"), os.environ.get("uxyngraphar_HUMANO"))  # minúsculas: alias antiguo


def _a_memoria(docs: Path, item: dict[str, Any], dry_run: bool) -> str:
    """Guarda la ficha en la memoria del sistema (R-24). Nada se borra: la acción «eliminar» de un plan es sinónimo de «memoria»."""
    motivo = str(item.get("motivo", "")).strip()
    if not motivo:
        return f"RECHAZADO {item['id']}: falta `motivo` en el plan"
    try:
        if dry_run:
            almacen.comprobar_guardable(docs, item["path"])
            return f"[dry-run] guardaría en memoria {item['path']}"
        m = almacen.guardar(docs, item["path"], motivo)
    except almacen.ErrorMemoria as exc:
        return f"RECHAZADO {item['id']}: {exc}"
    return f"A MEMORIA {item['id']}: {item['path']} → {m.ruta}"


def aplicar_plan(docs: Path, plan: list[dict[str, Any]], dry_run: bool = True) -> list[str]:
    """Ejecuta los ítems aprobados del plan. Nada se borra: lo que sale de las colas termina en la memoria (R-24)."""
    salida: list[str] = []
    aprobados = [i for i in plan if i.get("aprobado") is True]
    if not aprobados:
        return ["Plan sin ítems aprobados (`aprobado: true`): nada que hacer."]
    for accion in ("archivar", "limpiar"):
        paths = {i["path"] for i in aprobados if i["accion"] == accion}
        if not paths:
            continue
        cands = [c for c in candidatos(accion, [(docs, docs.name)], -1) if c.path in paths]
        salida += aplicar_mov(cands, dry_run=dry_run)
        if not dry_run:
            reescribir_enlaces(docs, {c.path: c.destino for c in cands if (docs / c.destino).exists()})
        salida += [f"OMITIDO {p}: no es candidata de {accion} (¿cambió de estado?)" for p in sorted(paths - {c.path for c in cands})]
    for item in (i for i in aprobados if i["accion"] in ("memoria", "eliminar")):
        if not dry_run and not _es_humano():
            salida.append(f"RECHAZADO {item['id']}: guardar en memoria exige una persona en la terminal (o UXYNGRAPHAR_HUMANO=1)")
        else:
            salida.append(_a_memoria(docs, item, dry_run))
    return salida
