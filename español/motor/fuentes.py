"""De dónde salen los sistemas que se instalan: el catálogo local (si lo hay) y el servidor.

El instalador llega vacío: `sistemas-de-gobernanza/` solo trae `_base`. Los sistemas se buscan y se traen del servidor
(`remoto`). Quien escribe sistemas tiene además un catálogo local con fuentes (`UXYNGRAPHAR_CATALOGO`, la clave
«catalogo_local» de `casa.json`, o el propio `sistemas-de-gobernanza/` del kit cuando trae sistemas, como en el repo de
desarrollo). Si un id está en los dos, se usa la versión más alta; a igual versión, la local.

Con un `cat` explícito (las pruebas, `--catalogo`) solo se usa esa carpeta.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import casa
import catalogo
import especificacion as esp
import remoto

base = esp.base


def carpeta_local(cat: Path | None = None) -> Path | None:
    if cat:
        return Path(cat)
    ajustes = casa.leer_json(casa.ARCHIVO_FORMATO, {})
    elegida = os.environ.get("UXYNGRAPHAR_CATALOGO") or (ajustes.get("catalogo_local") if isinstance(ajustes, dict) else None)
    c = Path(elegida).expanduser() if elegida else esp.CATALOGO
    return c if c.is_dir() else None


def locales(cat: Path | None = None) -> dict[str, str]:
    c = carpeta_local(cat)
    return catalogo.versiones(c) if c else {}


def remotas() -> dict[str, dict]:
    try:
        return remoto.versiones_disponibles()
    except (remoto.SinServidor, ValueError):
        return {}


def ids_conocidos() -> list[str]:
    """Ids del catálogo local y del último índice guardado, sin usar la red (autocompletado)."""
    guardados = remoto._indice_guardado().get("sistemas", [])  # noqa: SLF001 - lectura de la caché propia
    return sorted(set(locales()) | {s.get("id") for s in guardados if isinstance(s, dict) and s.get("id")})


def _elegir(pid: str, local: str | None, remota: dict | None) -> str | None:
    if local and (not remota or esp.version_tupla(local) >= esp.version_tupla(remota["version"])):
        return "local"
    return "servidor" if remota else None


def versiones(cat: Path | None = None) -> dict[str, str]:
    """Versión disponible de cada sistema (la que se instalaría)."""
    loc = locales(cat)
    if cat:
        return loc
    rem = remotas()
    salida = {}
    for pid in sorted(set(loc) | set(rem)):
        salida[pid] = loc[pid] if _elegir(pid, loc.get(pid), rem.get(pid)) == "local" else rem[pid]["version"]
    return salida


def origenes(cat: Path | None = None) -> dict[str, str]:
    """Por id: «local» o «servidor» (de dónde saldría al instalar)."""
    loc = locales(cat)
    rem = {} if cat else remotas()
    return {pid: _elegir(pid, loc.get(pid), rem.get(pid)) for pid in sorted(set(loc) | set(rem))}


def construir(pid: str, destino: Path, cat: Path | None = None) -> Path:
    """Deja el sistema construido en `destino/<id>/`: desde el catálogo local o traído del servidor."""
    c = carpeta_local(cat)
    loc = catalogo.versiones(c).get(pid) if c else None
    rem = None if cat else remotas().get(pid)
    if _elegir(pid, loc, rem) == "local":
        return catalogo.construir(pid, destino, c)
    if not rem:
        donde = "el catálogo" if cat else "el catálogo local ni el servidor"
        raise FileNotFoundError(f"«{pid}» no está en {donde} (búscalo con: uxyngraphar buscar)")
    traido = remoto.traer(f"{rem['editor']}/{pid}@{rem['version']}")
    salida = Path(destino) / pid
    if salida.exists():
        shutil.rmtree(salida)
    shutil.copytree(traido, salida, copy_function=shutil.copy)
    for p in salida.rglob("*"):
        if p.is_file():
            p.chmod(0o644 | (0o100 if p.suffix == ".py" else 0))
    return salida
