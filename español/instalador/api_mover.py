"""Mover la carpeta del pack de un proyecto (docs/ → uxyngraphar/): lo usan «uxyngraphar mover-carpeta» y el panel.

Siempre lo pide una persona (nunca un agente ni el CI) y nunca ocurre al actualizar. La lógica vive en el núcleo del pack
(scripts/nucleo/mover.py) de esta herramienta; el proyecto debe tener ya las herramientas 1.1.0 o posteriores.
"""

from __future__ import annotations

from pathlib import Path

import api
import mover  # noqa: E402  (scripts/nucleo del pack, en sys.path gracias a api)


def candidatos(ruta: str) -> list[dict]:
    """Los packs del proyecto que podrían moverse a la carpeta nueva (los que siguen en «docs»)."""
    info = api.inspeccionar(ruta)
    if not info.get("ok"):
        return []
    return [{"ruta": info["ruta"], "docs": x["docs"], "hacia": mover.destino_de(x["docs"], api.carpeta_pack.CARPETA)}
            for x in info["instalados"] if x["docs"].rpartition("/")[2] != api.carpeta_pack.CARPETA]


def _sin_persona() -> str:
    variable = api.feedback.sin_persona()
    return f"Mover la carpeta lo decide una persona: detecté {variable} (CI o un agente)." if variable else ""


def ver(ruta: str, docs: str, nombre: str = "") -> dict:
    """Qué cambiaría. No escribe nada."""
    try:
        repo, docs = api.cfgmod.normalizar(Path(ruta).expanduser(), docs)
        plan = mover.planificar(repo, docs, nombre or api.carpeta_pack.CARPETA)
    except (mover.ErrorMover, OSError) as exc:
        return {"ok": False, "error": str(exc)}
    return {"ok": True, **plan.a_dict(), "texto": mover.formatear(plan)}


def aplicar(ruta: str, docs: str, nombre: str = "") -> dict:
    motivo = _sin_persona()
    if motivo:
        return {"ok": False, "error": motivo}
    try:
        repo, docs = api.cfgmod.normalizar(Path(ruta).expanduser(), docs)
        plan = mover.planificar(repo, docs, nombre or api.carpeta_pack.CARPETA)
        carpeta = mover.aplicar(plan)
    except (mover.ErrorMover, OSError) as exc:
        return {"ok": False, "error": f"No se movió nada: {exc}"}
    siguiente = (f"Revisa con git status y haz commit (git ya ve {plan.desde}/ → {plan.hacia}/ como un renombrado)." if plan.git
                 else f"La carpeta ahora es {plan.hacia}/.")
    return {"ok": True, **plan.a_dict(), "respaldo": f"actualizacion/{carpeta.name}", "siguiente": siguiente}
