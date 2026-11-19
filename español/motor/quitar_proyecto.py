"""Quitar un proyecto del panel: «solo desvincular» (sale de la lista y de sus grupos) o «quitar todo» (además retira
todo lo que uxyngraphar puso en él). Nunca se borra código de la persona ni nada que uxyngraphar no creó: los archivos
ajenos que haya dentro de la carpeta de sistemas se dejan donde estaban y los archivos de sistemas que la persona
modificó se copian antes a `respaldos/quitados/` de la carpeta de uxyngraphar."""
from __future__ import annotations

import contextlib
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import casa
import especificacion as esp
import generar
import grupos
import proyectos
import protecciones
import repo

base = esp.base


def _rel(raiz: Path, ruta: Path) -> str:
    return ruta.relative_to(raiz).as_posix()


def _grupos_de(ruta: str) -> tuple[list[str], list[str]]:
    """(grupos en los que está, grupos que se quedarían con menos de dos proyectos y desaparecen)."""
    dentro, desaparecen = [], []
    for nombre, miembros in grupos.listar().items():
        if any(proyectos.misma_carpeta(m, ruta) for m in miembros):
            dentro.append(nombre)
            if len([m for m in miembros if not proyectos.misma_carpeta(m, ruta)]) < 2:
                desaparecen.append(nombre)
    return dentro, desaparecen


def plan(ruta: str) -> dict:
    """Todo lo que haría «quitar todo», sin tocar nada: sistemas, archivos que se borran o se editan, archivos que se
    respaldan (modificados por la persona), archivos ajenos que se conservan y lo que no se toca nunca."""
    raiz = Path(str(ruta)).expanduser()
    existe = raiz.is_dir()
    raiz = raiz.resolve() if existe else raiz.absolute()
    dentro, desaparecen = _grupos_de(str(raiz))
    salida: dict = {"ruta": str(raiz), "nombre": raiz.name, "existe": existe, "registrado": proyectos.registrado(str(raiz)),
                    "grupos": dentro, "grupos_que_desaparecen": desaparecen, "con_uxyngraphar": False, "sistemas": [],
                    "borrar": [], "editar": [], "respaldar": [], "ajenos": [], "conservar": []}
    if not existe:
        return salida
    salida["con_uxyngraphar"] = (raiz / base.CARPETA_RAIZ).is_dir()
    carpeta = raiz / base.CARPETA_SISTEMAS_DE_GOBERNANZA
    ids: set[str] = set()
    if carpeta.is_dir():
        try:
            estado = repo.estado(raiz)
        except Exception:  # noqa: BLE001 - un proyecto a medio instalar se quita igual
            estado = []
        for s in estado if isinstance(estado, list) else []:
            sid = str(s.get("id", ""))
            informe = s.get("informe") or {}
            ids.add(sid)
            alterados = sorted({*informe.get("alterados", []), *informe.get("añadidos", [])})
            salida["sistemas"].append({"id": sid, "version": s.get("version", ""), "integro": bool(s.get("integro", True)),
                                       "modificados": alterados})
            salida["borrar"].append(f"{base.CARPETA_SISTEMAS_DE_GOBERNANZA}/{sid}/")
            salida["respaldar"] += [f"{base.CARPETA_SISTEMAS_DE_GOBERNANZA}/{sid}/{a}" for a in alterados
                                    if (carpeta / sid / a).is_file()]
        for hijo in sorted(carpeta.iterdir()):
            if hijo.name not in ids and not hijo.name.startswith("."):   # «.x.anterior»: restos de uxyngraphar
                salida["ajenos"].append(_rel(raiz, hijo) + ("/" if hijo.is_dir() else ""))
    for r in (raiz / base.CARPETA_RAIZ / esp.INDICE, generar.ruta_flujo(raiz)):
        if r.is_file():
            salida["borrar"].append(_rel(raiz, r))
    for nombre in (*generar.ARCHIVOS_AGENTE, *generar.OPCIONALES):
        r = raiz / nombre
        if r.is_file() and not r.is_symlink() and generar.INICIO in r.read_text(encoding="utf-8", errors="replace"):
            solo_bloque = not generar.quitar_bloque(r.read_text(encoding="utf-8", errors="replace")).strip()
            (salida["borrar"] if solo_bloque else salida["editar"]).append(
                nombre if solo_bloque else f"{nombre} (solo el bloque de uxyngraphar)")
    for nombre in (protecciones.CLAUDE, *protecciones.EXCLUSIONES):
        if (raiz / nombre).is_file():
            salida["editar"].append(f"{nombre} (solo las reglas de uxyngraphar; si no queda nada más, se borra)")
    import conexiones
    import integracion
    try:
        hay = integracion.estado(raiz)
    except Exception:  # noqa: BLE001 - sin git no hay gancho
        hay = {}
    if hay.get("workflow"):
        salida["borrar"].append(integracion.WORKFLOW)
    if hay.get("precommit"):
        salida["editar"].append("gancho pre-commit de git (solo el de uxyngraphar)")
    try:
        conectados = conexiones.restos(raiz)
    except Exception:  # noqa: BLE001 - una configuración ilegible no impide ver el resto del plan
        conectados = []
    ya = " ".join(salida["borrar"] + salida["editar"])
    salida["editar"] += [f"conexión de agente: {c}" for c in conectados
                         if not (c.startswith("bloque de uxyngraphar en ") and c.rsplit(" ", 1)[-1] in ya)]
    trabajo = raiz / base.CARPETA_TRABAJO
    if trabajo.is_dir():
        if any(x.is_file() for x in trabajo.rglob("*")):
            salida["conservar"].append(f"{base.CARPETA_TRABAJO}/ (tu trabajo con los sistemas)")
        else:
            salida["borrar"].append(f"{base.CARPETA_TRABAJO}/ (solo carpetas vacías)")
    salida["conservar"].append("tu código y cualquier archivo que uxyngraphar no creó")
    return salida


def desvincular(ruta: str) -> dict:
    """Saca el proyecto de la lista del panel, de sus carpetas del panel y de sus grupos (un grupo que se quedaría
    con menos de dos proyectos se borra). No toca la carpeta del proyecto."""
    import organizacion
    dentro, desaparecen = _grupos_de(ruta)
    todos = grupos.listar()
    for nombre in dentro:
        if nombre in desaparecen:
            todos.pop(nombre, None)
        else:
            todos[nombre] = [m for m in todos[nombre] if not proyectos.misma_carpeta(m, ruta)]
    if dentro:
        grupos._guardar(todos)
    proyectos.quitar(ruta)
    organizacion.olvidar(ruta)
    return {"grupos_actualizados": [g for g in dentro if g not in desaparecen], "grupos_borrados": desaparecen}


def quitar(ruta: str, todo: bool = False) -> dict:
    """«Solo desvincular» (todo=False) o «quitar todo». Si la carpeta ya no existe, solo se desvincula."""
    import desinstalacion
    p = plan(ruta)
    resultado: dict = {"ruta": p["ruta"], "nombre": p["nombre"], "todo": bool(todo), "existe": p["existe"], "hechos": [],
                       "respaldo": "", "respaldados": [], "conservados": [], "restos": []}
    if todo and p["existe"]:
        raiz = Path(p["ruta"])
        if p["respaldar"]:
            destino = casa.carpeta() / "respaldos" / "quitados" / f"{p['nombre']}-{datetime.now():%Y%m%d-%H%M%S}"
            for rel in p["respaldar"]:
                (destino / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(raiz / rel, destino / rel)
            resultado["respaldo"] = str(destino)
            resultado["respaldados"] = list(p["respaldar"])
        # Lo ajeno que haya en la carpeta de sistemas sale antes y vuelve a su sitio después: no se borra nunca.
        aparte = Path(tempfile.mkdtemp(prefix="uxyngraphar-ajenos-", dir=str(casa.carpeta())))
        try:
            for rel in p["ajenos"]:
                shutil.move(str(raiz / rel.rstrip("/")), str(aparte / Path(rel.rstrip("/")).name))
            try:
                r = desinstalacion.retirar_de_proyecto(str(raiz), False)
                resultado["hechos"] += r.get("hechos", [])
                resultado["restos"] = r.get("restos", [])
            finally:
                for rel in p["ajenos"]:
                    origen = aparte / Path(rel.rstrip("/")).name
                    if origen.exists():
                        (raiz / rel.rstrip("/")).parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(origen), str(raiz / rel.rstrip("/")))
                        resultado["conservados"].append(rel)
        finally:
            shutil.rmtree(aparte, ignore_errors=True)
        _podar_vacias(raiz, [x["id"] for x in p["sistemas"]])
    elif todo:
        resultado["hechos"].append("la carpeta ya no existe: solo se quita de la lista")
    resultado.update(desvincular(p["ruta"]))
    resultado["hechos"].append("quitado de la lista del panel" if p["registrado"] else "no estaba en la lista del panel")
    return resultado


def _podar_vacias(raiz: Path, ids: list[str]) -> None:
    """Borra las carpetas vacías que creó uxyngraphar: `uxyngraphar/trabajo/<id>/` de los sistemas retirados (con sus
    subcarpetas vacías), `trabajo/`, `sistemas-de-gobernanza/` y `uxyngraphar/` si se quedan vacías. Solo carpetas
    vacías: un archivo nunca se toca, ni ninguna otra carpeta."""
    trabajo = raiz / base.CARPETA_TRABAJO
    candidatas: list[Path] = []
    for sid in ids:
        d = trabajo / sid
        if d.is_dir() and not d.is_symlink():
            candidatas += sorted((x for x in d.rglob("*") if x.is_dir() and not x.is_symlink()),
                                 key=lambda x: len(x.parts), reverse=True)
            candidatas.append(d)
    candidatas += [trabajo, raiz / base.CARPETA_SISTEMAS_DE_GOBERNANZA, raiz / base.CARPETA_RAIZ]
    for d in candidatas:
        if d.is_dir() and not d.is_symlink():
            with contextlib.suppress(OSError):
                d.rmdir()   # solo si está vacía
