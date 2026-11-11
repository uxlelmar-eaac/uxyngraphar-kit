"""La carpeta de uxyngraphar en este equipo (`~/.uxyngraphar` o `UXYNGRAPHAR_HOME`) y sus archivos JSON.

Los datos de la casa (`proyectos.json`, `flujos/`…) llevan un número de formato en `casa.json`. Cada versión declara el
formato que entiende (FORMATO_CASA) y, al activarse, el instalador le pide adaptarlos (`uxyngraphar _casa migrar`) después
de respaldarlos: hacia delante aplica MIGRACIONES; hacia atrás restaura el respaldo más reciente de su formato.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

DISTRIBUCION = Path(__file__).resolve().parent / "distribucion"
if str(DISTRIBUCION) not in sys.path:
    sys.path.insert(0, str(DISTRIBUCION))

import arranque as ar  # noqa: E402

ARCHIVO_FORMATO = "casa.json"
FORMATO_CASA = 2


def carpeta() -> Path:
    return Path(ar.carpeta_home())


def leer_json(nombre: str, defecto):
    try:
        return json.loads((carpeta() / nombre).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return defecto


def privada() -> Path:
    """La carpeta de uxyngraphar, solo para su dueño (0700 en Linux y macOS; en Windows vale la ACL del perfil)."""
    c = carpeta()
    c.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        os.chmod(c, 0o700)
    return c


def escribir_json(nombre: str, datos, privado: bool = False) -> Path:
    """Escritura atómica. `privado`: secretos como el token del panel (archivo 0600 en una carpeta 0700)."""
    if privado:
        privada()
    ruta = carpeta() / nombre
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tmp = ruta.with_name(ruta.name + ".tmp")
    if privado and os.name != "nt":
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        os.chmod(tmp, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps(datos, ensure_ascii=False, indent=2) + "\n")
    else:
        tmp.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, ruta)
    return ruta


def formato() -> int:
    """Formato de los datos de la casa (0: sin casa.json, como en el legado)."""
    datos = leer_json(ARCHIVO_FORMATO, {})
    valor = datos.get("formato", 0) if isinstance(datos, dict) else 0
    return valor if isinstance(valor, int) and valor >= 0 else 0


def _a_1() -> None:
    """Formato 1: proyectos.json es {"proyectos": [rutas]} (el legado ya lo escribía así; se normaliza si no)."""
    datos = leer_json("proyectos.json", None)
    if datos is None:
        return
    rutas = datos.get("proyectos", []) if isinstance(datos, dict) else datos if isinstance(datos, list) else []
    escribir_json("proyectos.json", {"proyectos": [r for r in rutas if isinstance(r, str)]})


def _a_2() -> None:
    """Formato 2 (herramienta 2.x): los flujos guardados llaman «sistemas» a lo que la 1.x llamaba «paquetes»."""
    flujos = carpeta() / "flujos"
    for ruta in sorted(flujos.glob("*.json")) if flujos.is_dir() else []:
        datos = leer_json(f"flujos/{ruta.name}", None)
        if isinstance(datos, dict) and "paquetes" in datos and "sistemas" not in datos:
            datos["sistemas"] = datos.pop("paquetes")
            escribir_json(f"flujos/{ruta.name}", datos)


MIGRACIONES = {1: _a_1, 2: _a_2}   # formato de destino -> paso desde el anterior


def _respaldo_compatible() -> str:
    """El respaldo más reciente de la casa cuyos datos están en FORMATO_CASA (o anterior)."""
    raiz = carpeta() / "respaldos"
    for d in sorted(raiz.glob("casa-*"), reverse=True) if raiz.is_dir() else []:
        try:
            f = json.loads((d / ARCHIVO_FORMATO).read_text(encoding="utf-8")).get("formato", 0)
        except (OSError, ValueError, AttributeError):
            f = 0
        if (d / ".completo").is_file() and isinstance(f, int) and f <= FORMATO_CASA:
            return str(d)
    return ""


def migrar() -> tuple[int, str]:
    """Deja los datos de la casa en FORMATO_CASA. (0, mensaje) si quedaron listos; (3, motivo) si son de una versión
    más nueva y no hay respaldo compatible."""
    actual = formato()
    if actual > FORMATO_CASA:
        respaldo = _respaldo_compatible()
        if not respaldo:
            return ar.DATOS_INCOMPATIBLES, (f"los datos de {carpeta()} tienen formato {actual} y esta versión entiende hasta el "
                                            f"{FORMATO_CASA}; no hay respaldo compatible en respaldos/")
        ar.restaurar_casa(str(carpeta()), respaldo)
        actual = formato()
        if actual > FORMATO_CASA:
            return ar.DATOS_INCOMPATIBLES, f"el respaldo {respaldo} no es compatible"
        mensaje = f"datos restaurados desde {respaldo} (formato {actual})"
    else:
        mensaje = f"datos en formato {actual}"
    for destino in range(actual + 1, FORMATO_CASA + 1):
        MIGRACIONES[destino]()
        mensaje = f"datos migrados al formato {destino}"
    escribir_json(ARCHIVO_FORMATO, {"formato": FORMATO_CASA})
    return 0, mensaje
