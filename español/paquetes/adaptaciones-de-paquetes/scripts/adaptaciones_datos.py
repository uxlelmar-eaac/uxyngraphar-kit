"""Datos de los ajustes locales; compartido por adaptaciones.py y verificar-adaptaciones.py."""

from __future__ import annotations

from pathlib import Path

import uxyn_base as base
import uxyn_fichas as fichas

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)
VACIO = (None, "", "null")
REGLAS = "reglas-del-proyecto"


def raiz() -> Path:
    return base.raiz_app(PAQUETE)


def ajustes() -> list[tuple[fichas.Ficha, dict, str]]:
    salida = []
    for f in fichas.listar(PAQUETE, "ajuste"):
        fm, cuerpo = base.leer_frontmatter(f.ruta.read_text(encoding="utf-8"))
        salida.append((f, fm, cuerpo))
    return salida


def activos_de(pid: str) -> list[tuple[fichas.Ficha, dict, str]]:
    return [(f, fm, c) for f, fm, c in ajustes() if f.status == "activo" and fm.get("paquete") == pid]


def objetivo_ajuste(fm: dict) -> Path:
    return raiz() / base.CARPETA_PAQUETES / str(fm.get("paquete")) / str(fm.get("aplica_a") or base.ENTRADA)


def estado_ajuste(fm: dict) -> str:
    """«vigente», «por revisar» (el archivo del paquete cambió) o «sin paquete»."""
    objetivo = objetivo_ajuste(fm)
    if not objetivo.is_file():
        return "sin paquete"
    return "vigente" if fm.get("huella") == base.sha256(objetivo) else "por revisar"


def reglas_activas() -> int:
    """Reglas `activa` en el trabajo de reglas-del-proyecto, solo si ese paquete está instalado (se lee, no se importa)."""
    if not (raiz() / base.CARPETA_PAQUETES / REGLAS).is_dir():
        return 0
    carpeta = raiz() / base.CARPETA_TRABAJO / REGLAS / "reglas"
    total = 0
    for ruta in carpeta.rglob("*.md") if carpeta.is_dir() else []:
        try:
            fm, _ = base.leer_frontmatter(ruta.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, OSError):
            continue
        total += fm.get("status") == "activa"
    return total
