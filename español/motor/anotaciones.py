"""Anotaciones de la revisión de archivos: notas y resaltados sobre fragmentos de un sistema del catálogo local.

Son de la persona, no del sistema: se guardan en `.anotaciones.json` del catálogo (como `.organizacion.json`), nunca
dentro del sistema, así que no cambian su validación, su zip ni lo que se instala. uxyn las lee cuando la persona le
pide «usa mis notas y resaltados». Igual que la web (servidor: /me/creador/borradores/<slug>/anotaciones).

Cada anotación: {id, archivo, tipo («nota» | «resaltado»), cita, inicio, fin, nota, estado («abierta» | «resuelta»),
creada}. `inicio`/`fin` son posiciones en el texto del archivo al anotarlo; si el archivo cambia, la cita sirve para
volver a encontrarla.
"""

from __future__ import annotations

import json
import os
import secrets
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import catalogo

ARCHIVO = ".anotaciones.json"
TIPOS = ("nota", "resaltado")
ESTADOS = ("abierta", "resuelta")
MAX_CITA = 4000
MAX_NOTA = 2000
MAX_POR_SISTEMA = 500


def _archivo(raiz: Path | None = None) -> Path:
    return catalogo.catalogo(raiz) / ARCHIVO


def _leer_todo(raiz: Path | None = None) -> dict:
    try:
        datos = json.loads(_archivo(raiz).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return datos.get("sistemas", {}) if isinstance(datos, dict) and isinstance(datos.get("sistemas"), dict) else {}


def _escribir_todo(sistemas: dict, raiz: Path | None = None) -> None:
    ruta = _archivo(raiz)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".anotaciones-", suffix=".tmp", dir=ruta.parent)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump({"formato": 1, "sistemas": sistemas}, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, ruta)


def _existe(pid: str, raiz: Path | None) -> None:
    if not pid or "/" in pid or pid.startswith(".") or not (catalogo.catalogo(raiz) / pid).is_dir():
        raise ValueError(f"no existe el sistema «{pid}» en el catálogo")


def listar(pid: str, raiz: Path | None = None) -> list[dict]:
    """Anotaciones de un sistema, en el orden en que se hicieron."""
    _existe(pid, raiz)
    return [a for a in _leer_todo(raiz).get(pid, []) if isinstance(a, dict)]


def crear(pid: str, archivo: str, tipo: str, cita: str, inicio: int, fin: int, nota: str = "",
          raiz: Path | None = None) -> dict:
    _existe(pid, raiz)
    if tipo not in TIPOS:
        raise ValueError(f"tipo: uno de {', '.join(TIPOS)}")
    cita = str(cita or "")
    if not cita.strip():
        raise ValueError("cita: selecciona un fragmento del archivo")
    if len(cita) > MAX_CITA:
        raise ValueError(f"cita: como mucho {MAX_CITA} caracteres")
    nota = str(nota or "").strip()
    if tipo == "nota" and not nota:
        raise ValueError("nota: escribe qué quieres que cambie")
    if len(nota) > MAX_NOTA:
        raise ValueError(f"nota: como mucho {MAX_NOTA} caracteres")
    catalogo.leer_archivo(pid, archivo, raiz)  # el archivo existe y la ruta es segura
    if not (isinstance(inicio, int) and isinstance(fin, int) and 0 <= inicio < fin):
        raise ValueError("inicio y fin: posiciones del fragmento en el archivo")
    todo = _leer_todo(raiz)
    lista = todo.setdefault(pid, [])
    if len(lista) >= MAX_POR_SISTEMA:
        raise ValueError(f"como mucho {MAX_POR_SISTEMA} anotaciones por sistema: resuelve o borra alguna")
    a = {"id": secrets.token_hex(6), "archivo": archivo, "tipo": tipo, "cita": cita, "inicio": inicio, "fin": fin,
         "nota": nota, "estado": "abierta", "creada": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    lista.append(a)
    _escribir_todo(todo, raiz)
    return a


def cambiar(pid: str, aid: str, *, estado: str | None = None, nota: str | None = None,
            raiz: Path | None = None) -> dict:
    _existe(pid, raiz)
    todo = _leer_todo(raiz)
    for a in todo.get(pid, []):
        if a.get("id") == aid:
            if estado is not None:
                if estado not in ESTADOS:
                    raise ValueError(f"estado: uno de {', '.join(ESTADOS)}")
                a["estado"] = estado
            if nota is not None:
                if len(nota) > MAX_NOTA:
                    raise ValueError(f"nota: como mucho {MAX_NOTA} caracteres")
                a["nota"] = nota.strip()
            _escribir_todo(todo, raiz)
            return a
    raise ValueError("esa anotación ya no existe")


def borrar(pid: str, aid: str, raiz: Path | None = None) -> dict:
    _existe(pid, raiz)
    todo = _leer_todo(raiz)
    antes = todo.get(pid, [])
    todo[pid] = [a for a in antes if a.get("id") != aid]
    if len(todo[pid]) == len(antes):
        raise ValueError("esa anotación ya no existe")
    _escribir_todo(todo, raiz)
    return {"borrada": aid}


def pedido_para_uxyn(anotaciones: list[dict]) -> str:
    """El mensaje que recibe uxyn con las notas y los resaltados abiertos (el mismo texto que arma la web)."""
    abiertas = [a for a in anotaciones if a.get("estado", "abierta") == "abierta"]
    if not abiertas:
        return ""
    lineas = []
    for a in abiertas:
        cita = " ".join(str(a.get("cita") or "").split())
        cita = cita if len(cita) <= 300 else cita[:297] + "…"
        if a.get("tipo") == "nota":
            lineas.append(f"- {a.get('archivo')}: «{cita}» → nota: {a.get('nota')}")
        else:
            lineas.append(f"- {a.get('archivo')}: «{cita}» (resaltado: revisa y mejora este fragmento)")
    return ("Revisa mis notas y resaltados de este sistema y úsalos como guía para mejorarlo. Para cada uno, cambia "
            "lo que pide la nota o mejora el fragmento resaltado, y añade lo que haga falta en otros archivos para que "
            "el sistema sea coherente. Déjalo todo en «Por revisar».\n\n" + "\n".join(lineas))
