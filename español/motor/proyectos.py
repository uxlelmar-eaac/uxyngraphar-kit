"""Proyectos registrados en este equipo (`proyectos.json` en la carpeta de uxyngraphar),
explorador de carpetas para elegirlos desde el panel y resumen de cada uno."""

from __future__ import annotations

import os
from pathlib import Path

import casa
import fuentes
import especificacion as esp
import generar
import repo

ARCHIVO = "proyectos.json"
IGNORAR = {"node_modules", "vendor", "dist", "build", "target", "venv", ".venv", "__pycache__"}
MAX_BUSQUEDA = 200

base = esp.base


def listar() -> list[str]:
    datos = casa.leer_json(ARCHIVO, {})
    rutas = datos.get("proyectos", []) if isinstance(datos, dict) else []
    return [str(r) for r in rutas if isinstance(r, str)]


def _guardar(rutas: list[str]) -> None:
    casa.escribir_json(ARCHIVO, {"proyectos": sorted(dict.fromkeys(rutas), key=lambda r: Path(r).name.lower())})


def _normalizar(ruta: str) -> str:
    destino = Path(str(ruta or "")).expanduser()
    if not str(ruta or "").strip() or not destino.is_dir():
        raise ValueError(f"no existe la carpeta «{ruta}»")
    return str(destino.resolve())


def agregar(rutas: list[str]) -> list[str]:
    nuevas = [_normalizar(r) for r in rutas]
    _guardar(listar() + nuevas)
    return nuevas


def misma_carpeta(a: str, b: str) -> bool:
    """Dos rutas a la misma carpeta, escritas o no igual (enlaces como /var → /private/var, nombres cortos de Windows,
    mayúsculas en Windows)."""
    def canonica(r: str) -> str:
        return os.path.normcase(str(Path(r).expanduser().resolve()))
    return canonica(a) == canonica(b)


def registrado(ruta: str, registrados: list[str] | None = None) -> bool:
    return any(misma_carpeta(r, ruta) for r in (listar() if registrados is None else registrados))


def quitar(ruta: str) -> None:
    """Lo saca de la lista del panel; no toca la carpeta del proyecto."""
    _guardar([r for r in listar() if not misma_carpeta(r, ruta)])


def _es_repo(carpeta: Path) -> bool:
    return (carpeta / ".git").exists()


def _tiene_uxyngraphar(carpeta: Path) -> bool:
    return (carpeta / base.CARPETA_RAIZ).is_dir()


def carpetas(ruta: str | None = None) -> dict:
    """Subcarpetas visibles de `ruta` (por defecto, la carpeta personal) para el explorador del panel."""
    actual = Path(ruta).expanduser() if ruta else Path.home()
    if not actual.is_dir():
        raise ValueError(f"no existe la carpeta «{ruta}»")
    actual = actual.resolve()
    hijas = []
    try:
        entradas = sorted(os.scandir(actual), key=lambda e: e.name.lower())
    except PermissionError:
        entradas = []
    for e in entradas:
        if e.name.startswith(".") or not e.is_dir(follow_symlinks=False):
            continue
        c = Path(e.path)
        try:
            hijas.append({"nombre": e.name, "ruta": str(c), "repo": _es_repo(c), "uxyngraphar": _tiene_uxyngraphar(c)})
        except PermissionError:
            continue
    padre = str(actual.parent) if actual.parent != actual else None
    return {"ruta": str(actual), "padre": padre, "inicio": str(Path.home()), "repo": _es_repo(actual), "carpetas": hijas}


def buscar(ruta: str, profundidad: int = 4) -> list[dict]:
    """Repos git bajo `ruta` (sin entrar en carpetas ocultas ni de dependencias; no baja dentro de un repo)."""
    raiz = Path(_normalizar(ruta))
    registrados = listar()
    hallados: list[dict] = []

    def recorrer(carpeta: Path, nivel: int) -> None:
        if len(hallados) >= MAX_BUSQUEDA:
            return
        if _es_repo(carpeta):
            hallados.append({"ruta": str(carpeta), "nombre": carpeta.name, "registrado": registrado(str(carpeta), registrados),
                             "uxyngraphar": _tiene_uxyngraphar(carpeta)})
            return
        if nivel >= profundidad:
            return
        try:
            hijas = sorted(e.path for e in os.scandir(carpeta) if e.is_dir(follow_symlinks=False)
                           and not e.name.startswith(".") and e.name not in IGNORAR)
        except PermissionError:
            return
        for h in hijas:
            recorrer(Path(h), nivel + 1)

    recorrer(raiz, 0)
    return hallados


def resumen(ruta: str, versiones: dict[str, str] | None = None) -> dict:
    """Lo que el panel muestra de un proyecto sin abrirlo: sistemas, actualizaciones, integridad y flujo."""
    carpeta = Path(ruta)
    datos = {"ruta": ruta, "nombre": carpeta.name, "grupo": carpeta.parent.name, "existe": carpeta.is_dir(),
             "sistemas": [], "actualizables": 0, "alterados": 0, "modo": None}
    if not datos["existe"]:
        return datos
    filas = repo.estado(carpeta, versiones=versiones)
    datos["sistemas"] = [f["id"] for f in filas]
    datos["actualizables"] = sum(1 for f in filas if f["actualizable"])
    datos["alterados"] = sum(1 for f in filas if not f["integro"])
    if generar.ruta_flujo(carpeta).is_file():
        try:
            datos["modo"] = generar.leer_flujo(carpeta).get("modo")
        except ValueError:
            datos["modo"] = None
    return datos


def resumenes() -> list[dict]:
    """Un resumen por proyecto registrado; si uno no se puede leer (permisos, manifiesto roto…) sale con su «error» y
    los demás se muestran igual."""
    versiones = fuentes.versiones()
    salida = []
    for r in listar():
        try:
            salida.append(resumen(r, versiones))
        except Exception as e:  # noqa: BLE001 - un proyecto ilegible no deja la lista del panel en blanco
            salida.append({"ruta": r, "nombre": Path(r).name, "grupo": Path(r).parent.name, "existe": Path(r).is_dir(),
                           "sistemas": [], "actualizables": 0, "alterados": 0, "modo": None,
                           "error": f"{type(e).__name__}: {e}"})
    return salida
