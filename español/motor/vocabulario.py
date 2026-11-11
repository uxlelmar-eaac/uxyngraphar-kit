"""`uxyngraphar nomenclatura migrar`: pasa las fichas de un proyecto del vocabulario heredado (status en inglés y
sinónimos) al de NOMENCLATURA.md, según `vocabulario.json`.

Por defecto solo simula. Al aplicar: toma el candado del proyecto, respalda las carpetas de trabajo afectadas (fuera del
repo, junto a los respaldos de sus transacciones), reescribe el `status:` del frontmatter, mueve cada ficha a la carpeta
de su estado nuevo cuando su tipo tiene `estados` y, si algo falla, restaura el respaldo. Nunca toca `uxyngraphar/sistemas-de-gobernanza/`.
"""

from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

import especificacion as esp
import generar
import transaccion
import uxyn_fichas as fichas  # scripts/comun/ de sistemas-de-gobernanza/_base: lo pone en sys.path especificacion

base = esp.base
TABLA = Path(__file__).resolve().parent / "vocabulario.json"


def migraciones() -> dict[str, dict[str, str]]:
    """{sistema: {status heredado: status nuevo}}."""
    return json.loads(TABLA.read_text(encoding="utf-8"))["migraciones"]


def plan(raiz_app: Path, extra: dict[str, dict[str, str]] | None = None) -> list[dict]:
    """Un cambio por ficha con status heredado: {sistema, ficha, antes, despues, origen, destino} (rutas relativas a la
    raíz de la app). `extra` añade equivalencias."""
    raiz_app = Path(raiz_app).resolve()
    tabla = migraciones()
    for pid, eq in (extra or {}).items():
        tabla[pid] = {**tabla.get(pid, {}), **eq}
    cambios = []
    for m in generar.instalados(raiz_app):
        if m["id"] not in tabla:
            continue
        eq = tabla[m["id"]]
        sistema = raiz_app / base.CARPETA_SISTEMAS_DE_GOBERNANZA / m["id"]
        for f in fichas.listar(sistema):
            if f.status not in eq:
                continue
            nuevo = eq[f.status]
            d = m.get("fichas", {}).get(f.tipo, {})
            destino = f.ruta
            if d.get("estados") and nuevo in d["estados"]:
                carpeta = (base.carpeta_trabajo(sistema, crear=False) / d.get("carpeta", ".")).resolve()
                if f.ruta.resolve().parent.parent == carpeta:   # está en una carpeta de estado (puede que ya no exista)
                    destino = carpeta / d["estados"][nuevo] / f.ruta.name
            cambios.append({"sistema": m["id"], "ficha": f.id, "antes": f.status, "despues": nuevo,
                            "origen": f.ruta.relative_to(raiz_app).as_posix(), "destino": destino.relative_to(raiz_app).as_posix()})
    return cambios


def pendientes(raiz_app: Path) -> int:
    """Cuántas fichas del proyecto siguen con un status heredado (0 si nada que migrar)."""
    try:
        return len(plan(raiz_app))
    except (OSError, ValueError):
        return 0


def _aplicar_cambio(raiz_app: Path, c: dict) -> None:
    origen, destino = raiz_app / c["origen"], raiz_app / c["destino"]
    texto = base.escribir_campo(origen.read_text(encoding="utf-8"), "status", c["despues"])
    if destino != origen:
        if destino.exists():
            raise FileExistsError(f"{c['destino']} ya existe: renombra una de las dos fichas y vuelve a migrar")
        destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8")
    if destino != origen:
        origen.unlink()


def aplicar(raiz_app: Path, extra: dict[str, dict[str, str]] | None = None) -> dict:
    """Aplica el plan con respaldo y vuelta atrás. Devuelve {cambios, respaldo}."""
    raiz_app = Path(raiz_app).resolve()
    with transaccion.candado(raiz_app, "nomenclatura migrar"):
        cambios = plan(raiz_app, extra)
        if not cambios:
            return {"cambios": [], "respaldo": ""}
        respaldo = transaccion.carpeta_respaldos(raiz_app) / f"vocabulario-{time.strftime('%Y%m%d-%H%M%S')}"
        trabajo = raiz_app / base.CARPETA_TRABAJO
        afectados = sorted({c["sistema"] for c in cambios})
        for pid in afectados:
            shutil.copytree(trabajo / pid, respaldo / pid)
        try:
            for c in cambios:
                _aplicar_cambio(raiz_app, c)
        except BaseException:
            for pid in afectados:
                transaccion.borrar(trabajo / pid)
                shutil.copytree(respaldo / pid, trabajo / pid)
            raise
        (respaldo / "cambios.json").write_text(json.dumps(cambios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {"cambios": cambios, "respaldo": str(respaldo)}
