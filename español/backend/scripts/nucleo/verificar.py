"""Integridad del núcleo instalado: detecta ediciones, borrados y extensiones no autorizadas (R-14)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import clasificacion as cl
import lock


@dataclass
class Hallazgo:
    codigo: str   # NUCLEO-MODIFICADO · NUCLEO-ELIMINADO · NUCLEO-EXTENDIDO · FUERA-DE-TAXONOMIA · SIN-LOCK · LOCK-ALTERADO · DIVERGE-DEL-PACK
    ruta: str
    mensaje: str


AYUDA = "El núcleo no se edita en el proyecto. Mejora → ficha EVO en 46; el humano la implementa en uxyngraphar; llega con actualizar-pack.py. Restaurar → actualizar-pack.py --restaurar-nucleo (humano)."


def verificar(repo: Path, docs: str = "docs") -> list[Hallazgo]:
    docs = docs.strip("/")
    datos = lock.leer(repo, docs)
    if datos is None:
        return [Hallazgo("SIN-LOCK", f"{docs}/{lock.LOCK_NOMBRE}", "no hay línea base; instala con instalar-pack.py o crea el lock con actualizar-pack.py")]
    base: dict[str, dict[str, str]] = datos.get("archivos", {})
    h: list[Hallazgo] = []
    if not lock.sello_valido(datos):
        h.append(Hallazgo("LOCK-ALTERADO", f"{docs}/{lock.LOCK_NOMBRE}", "el lock fue editado a mano; contrástalo con el pack (--contra) y restaura con actualizar-pack.py"))
    for rel, info in sorted(base.items()):
        if info["clase"] != "N":
            continue
        f = repo / cl.destino(rel, docs)
        if not f.is_file():
            h.append(Hallazgo("NUCLEO-ELIMINADO", cl.destino(rel, docs), "archivo del núcleo borrado"))
        elif lock.sha(f) != info["sha256"]:
            h.append(Hallazgo("NUCLEO-MODIFICADO", cl.destino(rel, docs), "el contenido difiere de la línea base"))
    raiz_docs = repo / docs
    for p in sorted(raiz_docs.rglob("*")) if raiz_docs.is_dir() else []:
        if not p.is_file():
            continue
        rel = p.relative_to(raiz_docs).as_posix()
        if rel in base:
            continue
        clase = cl.clasificar(rel)
        if clase == "N":
            h.append(Hallazgo("NUCLEO-EXTENDIDO", f"{docs}/{rel}", "archivo nuevo en una zona reservada al núcleo"))
        elif clase is None:
            h.append(Hallazgo("FUERA-DE-TAXONOMIA", f"{docs}/{rel}", "ruta que no pertenece a la taxonomía del pack"))
    return h


def contra_pack(repo: Path, docs: str, pack: Path) -> list[Hallazgo]:
    """Verificación independiente del lock: compara cada archivo N del proyecto con el pack fuente."""
    docs = docs.strip("/")
    h: list[Hallazgo] = []
    for rel, info in lock.inventario(pack, (lock.leer(repo, docs) or {}).get("perfil", "completo")).items():
        if info["clase"] != "N":
            continue
        f = repo / cl.destino(rel, docs)
        if not f.is_file():
            h.append(Hallazgo("NUCLEO-ELIMINADO", cl.destino(rel, docs), "falta respecto al pack"))
        elif lock.sha(f) != info["sha256"]:
            h.append(Hallazgo("DIVERGE-DEL-PACK", cl.destino(rel, docs), f"difiere del pack {lock.version_de(pack)}"))
    return h
