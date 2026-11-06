"""Paquetes en un repo: instalar, actualizar, quitar y verificar. Nunca toca el trabajo de `uxyngraphar/trabajo/<id>/`
salvo que se pida quitarlo explícitamente."""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

import catalogo
import especificacion as esp
import generar

base = esp.base


class InstalacionAntigua(RuntimeError):
    """El repo tiene una instalación 1.x: primero hay que migrarla."""


def _forzar_escritura(funcion, ruta, _exc):
    os.chmod(ruta, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
    funcion(ruta)


def borrar_arbol(ruta: Path) -> None:
    if Path(ruta).exists():
        if sys.version_info >= (3, 12):
            shutil.rmtree(ruta, onexc=_forzar_escritura)
        else:
            shutil.rmtree(ruta, onerror=_forzar_escritura)


def solo_lectura(carpeta: Path) -> None:
    for p in Path(carpeta).rglob("*"):
        if p.is_file():
            p.chmod(stat.S_IREAD | (stat.S_IXUSR if p.suffix == ".py" else 0) | stat.S_IRGRP | stat.S_IROTH)


def instalacion_1x(raiz_app: Path) -> Path | None:
    """Carpeta de un pack 1.x en la raíz de la app (`uxyngraphar/` o `docs/` con lock o numeración 00–97)."""
    for nombre in (base.CARPETA_RAIZ, "docs"):
        c = Path(raiz_app) / nombre
        if (c / ".uxyngraphar.lock").is_file() or ((c / "00-nucleo").is_dir() and (c / "05-instrucciones").is_dir()):
            return c
    return None


def _exigir_2x(raiz_app: Path) -> None:
    antigua = instalacion_1x(raiz_app)
    if antigua:
        raise InstalacionAntigua(f"{antigua} es una instalación 1.x; migra primero con: uxyngraphar migrar --repo {raiz_app}")


def carpeta_instalada(raiz_app: Path, pid: str) -> Path:
    return Path(raiz_app) / base.CARPETA_PAQUETES / pid


def _colocar(raiz_app: Path, pid: str, cat: Path | None) -> Path:
    """Construye desde el catálogo y reemplaza `uxyngraphar/paquetes/<id>/` de forma atómica (con vuelta atrás)."""
    paquetes = Path(raiz_app) / base.CARPETA_PAQUETES
    paquetes.mkdir(parents=True, exist_ok=True)
    destino = paquetes / pid
    with tempfile.TemporaryDirectory(dir=paquetes, prefix=".construyendo-") as tmp:
        nuevo = catalogo.construir(pid, Path(tmp), cat)
        anterior = paquetes / f".{pid}.anterior"
        borrar_arbol(anterior)
        if destino.exists():
            destino.rename(anterior)
        try:
            nuevo.rename(destino)
        except OSError:
            if anterior.exists():
                anterior.rename(destino)
            raise
        borrar_arbol(anterior)
    solo_lectura(destino)
    return destino


def instalar(raiz_app: Path, ids: list[str], cat: Path | None = None, paquete_base: str | None = None) -> list[str]:
    """Instala `ids`. Con `paquete_base`, FLUJO.json pasa a `trabajar_con` ese paquete (se aplica en cada pedido)."""
    raiz_app = Path(raiz_app).resolve()
    _exigir_2x(raiz_app)
    if paquete_base and paquete_base not in ids and not carpeta_instalada(raiz_app, paquete_base).exists():
        raise ValueError(f"--base {paquete_base}: instálalo en la misma orden o antes")
    hechos = []
    for pid in ids:
        if carpeta_instalada(raiz_app, pid).exists():
            raise FileExistsError(f"«{pid}» ya está instalado; usa actualizar")
        _colocar(raiz_app, pid, cat)
        base.carpeta_trabajo(carpeta_instalada(raiz_app, pid))
        hechos.append(pid)
    generar.regenerar(raiz_app)
    if paquete_base:
        errores = generar.guardar_flujo(raiz_app, {**generar.leer_flujo(raiz_app), "modo": "trabajar_con", "trabajar_con": paquete_base})
        if errores:
            raise ValueError("FLUJO.json no cambió: " + "; ".join(errores))
    return hechos


def estado(raiz_app: Path, cat: Path | None = None) -> list[dict]:
    """Por paquete instalado: versión, versión del catálogo, integridad y si hay actualización."""
    disponibles = {m["id"]: m["version"] for m in catalogo.listar(cat)}
    salida = []
    for m in generar.instalados(raiz_app):
        informe = base.comprobar_integridad(carpeta_instalada(raiz_app, m["id"]))
        en_catalogo = disponibles.get(m["id"])
        actualizable = bool(en_catalogo) and m.get("version") != "?" and esp.version_tupla(en_catalogo) > esp.version_tupla(m["version"])
        salida.append({"id": m["id"], "titulo": m.get("titulo", ""), "version": m.get("version"), "catalogo": en_catalogo,
                       "integro": base.integro(informe), "informe": informe, "actualizable": actualizable})
    return salida


def actualizar(raiz_app: Path, ids: list[str] | None = None, cat: Path | None = None, forzar: bool = False) -> list[str]:
    """Actualiza (o repara si está alterado) los paquetes indicados; sin ids, todos los instalados."""
    raiz_app = Path(raiz_app).resolve()
    _exigir_2x(raiz_app)
    hechos = []
    for e in estado(raiz_app, cat):
        if ids and e["id"] not in ids:
            continue
        if not e["catalogo"]:
            continue
        retroceso = esp.version_tupla(e["catalogo"]) < esp.version_tupla(e["version"]) if e["version"] != "?" else False
        if retroceso and not forzar:
            raise ValueError(f"«{e['id']}»: el catálogo ({e['catalogo']}) es más antiguo que lo instalado ({e['version']}); usa --forzar")
        if e["actualizable"] or not e["integro"] or forzar:
            _colocar(raiz_app, e["id"], cat)
            hechos.append(e["id"])
    for pid in ids or []:
        if not carpeta_instalada(raiz_app, pid).exists():
            raise FileNotFoundError(f"«{pid}» no está instalado")
    generar.regenerar(raiz_app)
    return hechos


def quitar(raiz_app: Path, pid: str, con_trabajo: bool = False) -> None:
    raiz_app = Path(raiz_app).resolve()
    carpeta = carpeta_instalada(raiz_app, pid)
    if not (carpeta / base.MANIFIESTO).is_file():
        raise FileNotFoundError(f"«{pid}» no está instalado")
    borrar_arbol(carpeta)
    if con_trabajo:
        borrar_arbol(raiz_app / base.CARPETA_TRABAJO / pid)
    ruta_flujo = generar.ruta_flujo(raiz_app)
    if ruta_flujo.is_file():
        flujo = generar.leer_flujo(raiz_app)
        flujo["leer_por_defecto"] = [x for x in flujo.get("leer_por_defecto", []) if x != pid]
        flujo["secuencia"] = [x for x in flujo.get("secuencia", []) if x != pid]
        if flujo.get("trabajar_con") == pid:
            flujo["trabajar_con"] = None
        if esp.validar_flujo(flujo):
            flujo["modo"] = "manual"
        generar.guardar_flujo(raiz_app, flujo)
    generar.regenerar(raiz_app)


def verificar(raiz_app: Path) -> list[dict]:
    """Ejecuta, por paquete instalado, sus `verificaciones` (cada una en su propio proceso)."""
    resultados = []
    for m in generar.instalados(raiz_app):
        carpeta = carpeta_instalada(raiz_app, m["id"])
        for v in m.get("verificaciones", []):
            r = subprocess.run([sys.executable, "-B", "-X", "utf8", str(carpeta / v)], cwd=raiz_app, capture_output=True, text=True)
            resultados.append({"paquete": m["id"], "verificacion": v, "codigo": r.returncode, "salida": (r.stdout + r.stderr).strip()})
    return resultados
