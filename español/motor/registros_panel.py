"""Cola en memoria de eventos del panel (API) para el visor de Logs del UI."""

from __future__ import annotations

import threading
import time
from collections import deque

_MAX = 400
_OMITIR = {"/api/latido", "/api/agente/progreso", "/api/registros"}
_cola: deque[dict] = deque(maxlen=_MAX)
_lock = threading.Lock()
_seq = 0


def anotar(*, metodo: str, ruta: str, codigo: int, ms: float, detalle: str = "") -> None:
    base = (ruta or "").split("?", 1)[0]
    if base in _OMITIR:
        return
    global _seq
    with _lock:
        _seq += 1
        _cola.appendleft({
            "id": _seq,
            "t": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "nivel": "error" if codigo >= 400 else "info",
            "origen": "panel",
            "titulo": f"{metodo} {base} → {codigo}",
            "detalle": (detalle or "")[:500] or None,
            "ruta": base,
            "ms": round(ms),
            "ok": codigo < 400,
        })


def listar(desde: int = 0) -> list[dict]:
    with _lock:
        items = list(_cola)
    if desde:
        items = [e for e in items if int(e.get("id") or 0) > desde]
    return items
