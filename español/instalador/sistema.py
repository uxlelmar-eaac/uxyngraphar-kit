"""Lo que es de este equipo y no de un proyecto: carpeta de la herramienta, proyectos registrados, última versión y plantilla.

Lo usan el comando «uxyngraphar» y el panel del navegador. La plantilla (plantilla-config.json en la carpeta de la herramienta)
guarda los valores que la persona prefiere para sus proyectos: se aplican al instalar uno nuevo y, si ella lo pide, a los
existentes. Nunca manda sobre el archivo de un proyecto: cada proyecto sigue decidiendo con su docs/uxyngraphar.config.json.
"""

from __future__ import annotations

import importlib.util
import json
import os
import tempfile
from pathlib import Path

import arranque as ar

ES = Path(__file__).resolve().parent.parent   # versiones/X.Y.Z/ (instalada) o español/ (copia del repositorio)
ARCHIVO_PLANTILLA = "plantilla-config.json"
# Lo que una plantilla puede fijar: preferencias de trabajo que valen para cualquier proyecto. Lo propio de cada
# repositorio (rol, pila, carpetas de código, exenciones) y el consentimiento de «colaborar» nunca van en la plantilla.
CLAVES_PLANTILLA = {
    "niveles": None, "limite_lineas": None, "respaldos": None, "memoria": None, "reglas_proyecto": None,
    "idioma": ("conversacion", "commits", "ramas"), "feedback": ("ocultar",),
}


def home() -> Path:
    return Path(ar.carpeta_home())


def version_herramienta() -> str:
    texto = (ES / "backend" / "VERSION.md").read_text(encoding="utf-8")
    return next((l.split(":", 1)[1].strip() for l in texto.splitlines() if l.startswith("version:")), "desconocida")


def tupla(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split(".")) if ar.VERSION_RE.match(v or "") else (0,)


def ultima_publicada(espera: int = 5) -> str:
    """Última versión publicada en GitHub, o "" si no hay red (nunca falla)."""
    with tempfile.TemporaryDirectory() as t:
        destino = os.path.join(t, "SHA256SUMS")
        try:
            ar.descargar(ar.url_ultima("SHA256SUMS"), destino, intentos=1, espera=espera)
            return ar.version_de_sumas(ar.leer_sumas(destino))
        except (ar.ErrorInstalacion, OSError):
            return ""


# ---------- proyectos registrados (proyectos.json) ----------

def leer_proyectos() -> list[str]:
    try:
        return list(json.loads((home() / "proyectos.json").read_text(encoding="utf-8")).get("proyectos", []))
    except (OSError, ValueError):
        return []


def guardar_proyectos(lista: list[str]) -> None:
    home().mkdir(parents=True, exist_ok=True)
    ar.escribir_atomico(str(home() / "proyectos.json"), json.dumps({"proyectos": sorted(set(lista))}, indent=2, ensure_ascii=False) + "\n")


# ---------- lector de configuración del propio proyecto ----------

def modulo_config(repo: Path | None = None, docs: str = "docs"):
    """El lector de configuración de la versión del pack que tiene el proyecto; si falta, el de la herramienta."""
    propio = repo / docs / "scripts" / "control" / "uxyngraphar_config.py" if repo else None
    ruta = propio if propio and propio.is_file() else ES / "backend" / "scripts" / "control" / "uxyngraphar_config.py"
    spec = importlib.util.spec_from_file_location(f"uxyngraphar_config_{abs(hash(str(ruta)))}", ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


# ---------- plantilla de este equipo ----------

def filtrar(datos: dict, permitidas: dict) -> dict:
    """Solo las claves permitidas (None = la sección entera; tupla = esas subclaves). Lo demás se descarta en silencio."""
    salida: dict = {}
    for clave, sub in permitidas.items():
        if clave in datos and sub is None:
            salida[clave] = datos[clave]
        elif clave in datos and isinstance(datos[clave], dict):
            dentro = {k: datos[clave][k] for k in sub if k in datos[clave]}
            if dentro:
                salida[clave] = dentro
    return salida


def filtrar_plantilla(datos: dict) -> dict:
    return filtrar(datos, CLAVES_PLANTILLA)


def leer_plantilla() -> dict:
    try:
        datos = json.loads((home() / ARCHIVO_PLANTILLA).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return filtrar_plantilla(datos) if isinstance(datos, dict) else {}


def problemas_plantilla(plantilla: dict) -> list[str]:
    cfgmod = modulo_config()
    return cfgmod.validar(cfgmod._fusionar(cfgmod.por_defecto(), json.loads(json.dumps(plantilla))))


def guardar_plantilla(plantilla: dict) -> dict:
    plantilla = filtrar_plantilla(plantilla)
    problemas = problemas_plantilla(plantilla)
    if problemas:
        return {"ok": False, "problemas": problemas}
    home().mkdir(parents=True, exist_ok=True)
    archivo = home() / ARCHIVO_PLANTILLA
    if plantilla:
        ar.escribir_atomico(str(archivo), json.dumps(plantilla, indent=2, ensure_ascii=False) + "\n")
    elif archivo.is_file():
        archivo.unlink()
    return {"ok": True, "problemas": [], "archivo": str(archivo), "plantilla": plantilla}
