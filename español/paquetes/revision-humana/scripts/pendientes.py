"""Fichas que esperan una decisión de una persona en los paquetes instalados; compartido por revision.py y su verificación."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import uxyn_base as base
import uxyn_fichas as fichas

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)


@dataclass
class Pendiente:
    paquete: str
    carpeta: Path
    tipo: str
    id: str
    status: str
    titulo: str
    dias: int
    opciones: list[str]
    comandos: dict


def raiz() -> Path:
    return base.raiz_app(PAQUETE)


def _dias(ruta: Path, hoy: date) -> int:
    fm, _ = base.leer_frontmatter(ruta.read_text(encoding="utf-8"))
    for clave in ("actualizado", "fecha"):
        try:
            return (hoy - date.fromisoformat(str(fm.get(clave))[:10])).days
        except ValueError:
            continue
    return (hoy - datetime.fromtimestamp(ruta.stat().st_mtime).date()).days


def instalados() -> list[Path]:
    carpeta = raiz() / base.CARPETA_PAQUETES
    return sorted(c for c in carpeta.iterdir() if (c / base.MANIFIESTO).is_file() and not c.name.startswith(".")) \
        if carpeta.is_dir() else []


def recoger(hoy: date | None = None) -> list[Pendiente]:
    hoy = hoy or date.today()
    salida = []
    for carpeta in instalados():
        m = base.leer_manifiesto(carpeta)
        for tipo, d in m.get("fichas", {}).items():
            esperan = base.status_que_esperan(d)
            if not esperan:
                continue
            for f in fichas.listar(carpeta, tipo):
                if f.status in esperan:
                    salida.append(Pendiente(m["id"], carpeta, tipo, f.id, f.status, f.titulo.replace("|", "/"),
                                            _dias(f.ruta, hoy), list(d.get("solo_humano", [])), dict(d.get("comandos", {}))))
    return sorted(salida, key=lambda p: (-p.dias, p.paquete, p.id))


def comando(p: Pendiente, decision: str) -> list[str]:
    """Argumentos (relativos a la carpeta del paquete) para poner `decision` en la ficha `p`."""
    plantilla = p.comandos.get(decision) or f"scripts/comun/fichas.py estado {{id}} {decision} --humano"
    return plantilla.replace("{id}", p.id).split()
