"""Flujos guardados: plantillas reutilizables de «qué sistemas y cómo trabaja el agente» (`flujos/<id>.json` en la carpeta
de uxyngraphar, fuera de `versiones/`, así que sobreviven a las actualizaciones). Aplicar uno a un proyecto instala los
sistemas que falten y escribe su FLUJO.json."""

from __future__ import annotations

import re
import time
import unicodedata
from pathlib import Path

import casa
import fuentes
import especificacion as esp
import generar
import repo

CARPETA = "flujos"
FORMATO = 1


def _carpeta() -> Path:
    return casa.carpeta() / CARPETA


def _slug(nombre: str) -> str:
    plano = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", plano).strip("-")[:60] or "flujo"


def _ruta(fid: str) -> Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", str(fid or "")):
        raise ValueError(f"flujo guardado no válido: «{fid}»")
    return _carpeta() / f"{fid}.json"


def _id_libre(nombre: str, propio: str | None = None) -> str:
    base_id, n = _slug(nombre), 1
    fid = base_id
    while _ruta(fid).exists() and fid != propio:
        n += 1
        fid = f"{base_id}-{n}"
    return fid


def validar(datos: dict) -> list[str]:
    errores = []
    if not isinstance(datos, dict):
        return ["el flujo guardado debe ser un objeto JSON"]
    if not str(datos.get("nombre") or "").strip():
        errores.append("ponle un nombre al flujo")
    sistemas = datos.get("sistemas")
    if not isinstance(sistemas, list) or not all(isinstance(p, str) for p in sistemas):
        return errores + ["sistemas: lista de ids"]
    faltan = sorted(set(sistemas) - set(fuentes.versiones()))
    if faltan:
        errores.append("sistemas que no están en el catálogo: " + ", ".join(faltan))
    errores += [e.replace("sistema no instalado", "sistema que no está en el flujo") for e in
                esp.validar_flujo(datos.get("flujo"), set(sistemas))]
    return errores


def _limpio(datos: dict) -> dict:
    flujo = {**esp.FLUJO_INICIAL, **(datos.get("flujo") or {})}
    return {"formato": FORMATO, "nombre": str(datos.get("nombre", "")).strip(), "descripcion": str(datos.get("descripcion") or "").strip(),
            "sistemas": list(dict.fromkeys(datos.get("sistemas") or [])), "flujo": flujo,
            "actualizado": time.strftime("%Y-%m-%d %H:%M")}


def listar() -> list[dict]:
    carpeta = _carpeta()
    salida = []
    for ruta in sorted(carpeta.glob("*.json")) if carpeta.is_dir() else []:
        try:
            salida.append({"id": ruta.stem, **casa.leer_json(f"{CARPETA}/{ruta.name}", {})})
        except TypeError:
            continue
    return sorted(salida, key=lambda f: (str(f.get("nombre", "")).lower(), f["id"]))


def leer(fid: str) -> dict:
    ruta = _ruta(fid)
    if not ruta.is_file():
        raise FileNotFoundError(f"no existe el flujo guardado «{fid}»")
    return {"id": fid, **casa.leer_json(f"{CARPETA}/{ruta.name}", {})}


def guardar(datos: dict) -> str:
    """Crea o (con «id») reemplaza un flujo guardado. Devuelve su id."""
    limpio = _limpio(datos)
    errores = validar(limpio)
    if errores:
        raise ValueError("; ".join(errores))
    propio = datos.get("id") or None
    if propio:
        _ruta(propio)
    fid = propio or _id_libre(limpio["nombre"])
    casa.escribir_json(f"{CARPETA}/{fid}.json", limpio)
    return fid


def desde_proyecto(raiz: Path, nombre: str, descripcion: str = "") -> str:
    """Guarda como plantilla los sistemas instalados y el FLUJO.json de un proyecto."""
    sistemas = [m["id"] for m in generar.instalados(raiz)]
    flujo = generar.leer_flujo(raiz) if generar.ruta_flujo(raiz).is_file() else dict(esp.FLUJO_INICIAL)   # sin escribir en el proyecto
    return guardar({"nombre": nombre, "descripcion": descripcion, "sistemas": sistemas, "flujo": flujo})


def aplicar(fid: str, raices: list[str]) -> list[dict]:
    """Instala lo que falte y escribe FLUJO.json en cada proyecto. Un fallo en uno no detiene a los demás."""
    datos = leer(fid)
    resultados = []
    for r in raices:
        fila = {"ruta": r, "instalados": [], "error": ""}
        try:
            raiz = Path(r).resolve()
            if not raiz.is_dir():
                raise FileNotFoundError("la carpeta del proyecto no existe")
            faltan = [p for p in datos["sistemas"] if not repo.carpeta_instalada(raiz, p).exists()]
            if faltan:
                fila["instalados"] = repo.instalar(raiz, faltan)
            else:
                generar.regenerar(raiz)
            errores = generar.guardar_flujo(raiz, {**esp.FLUJO_INICIAL, **datos["flujo"]})
            if errores:
                raise ValueError("; ".join(errores))
        except (ValueError, FileNotFoundError, FileExistsError) as e:
            fila["error"] = str(e)
        except Exception as e:  # noqa: BLE001 - un proyecto que falla no detiene a los demás
            fila["error"] = f"{type(e).__name__}: {e}"
        resultados.append(fila)
    return resultados


def duplicar(fid: str) -> str:
    datos = leer(fid)
    datos.pop("id")
    datos["nombre"] = f"{datos.get('nombre', fid)} (copia)"
    return guardar(datos)


def borrar(fid: str) -> None:
    ruta = _ruta(fid)
    if not ruta.is_file():
        raise FileNotFoundError(f"no existe el flujo guardado «{fid}»")
    ruta.unlink()


def exportar(fid: str) -> dict:
    datos = leer(fid)
    datos.pop("id")
    return datos


def importar(datos: dict) -> str:
    if not isinstance(datos, dict):
        raise ValueError("el archivo no es un flujo guardado")
    datos = {k: v for k, v in datos.items() if k != "id"}
    return guardar(datos)
