"""Lógica del asistente de actualización (sin interfaz): revisar, comparar y aplicar. La usa la pantalla web (servidor.py)."""

from __future__ import annotations

import difflib
import subprocess
from pathlib import Path

import api
from api import PACKS, cfgmod, flujo

act, cl, lock = flujo.act, flujo.cl, flujo.lock

GRUPOS = {
    "añadir": ("Archivos nuevos", "uxyngraphar trae estos archivos y tu proyecto todavía no los tiene. Se copian."),
    "reemplazar": ("Se actualizan", "Cambiaron en uxyngraphar y tú no los habías tocado. Se reemplazan (con copia de seguridad)."),
    "zona": ("Índices y README al día", "Solo se actualiza la parte que mantiene uxyngraphar (entre marcadores); tus filas y notas se conservan (con copia de seguridad)."),
    "restaurar": ("Se restauran", "Se devuelven a la versión de uxyngraphar (con copia de seguridad)."),
    "conflicto": ("Necesitan tu decisión", "Los editaste tú y también cambiaron en uxyngraphar. No se tocan: la versión nueva queda al lado como «.uxyngraphar-nuevo»."),
    "modificado-local": ("Núcleo editado en tu proyecto", "El núcleo no debería editarse (regla R-20). Aquí no se sobrescribe; revisa si fue a propósito."),
    "plantilla-cambiada": ("Plantillas con novedades", "Son tuyas (las rellenaste). uxyngraphar trae una versión nueva; nada se pisa, mira las novedades si te interesan."),
    "retirado": ("Ya no existen en uxyngraphar", "No se borran. Puedes quitarlos tú cuando quieras."),
}
CON_DIFERENCIAS = ("zona", "conflicto", "modificado-local", "plantilla-cambiada")
LIMITE_BYTES, LIMITE_LINEAS = 300_000, 400


def _git_cambios(repo: Path, docs: str) -> int:
    """Archivos de docs/ con cambios sin commit (para avisar: con git limpio es fácil deshacer)."""
    try:
        r = subprocess.run(["git", "status", "--porcelain", "--", docs], cwd=repo, capture_output=True, text=True)
    except OSError:
        return 0
    return len([x for x in r.stdout.splitlines() if x.strip()]) if r.returncode == 0 else 0


def _pack_de(repo: Path, docs: str) -> Path | None:
    return PACKS.get((lock.leer(repo, docs) or {}).get("pack", ""))


def _titulo(rol: str, repo: Path, docs: str) -> str:
    return f"{rol.capitalize()} en {repo.name}" + (f"/{docs.rpartition('/')[0]}" if "/" in docs else "")


def _ficha(pid: str, pack: Path, repo: Path, docs: str, rol: str) -> dict:
    base = {"id": pid, "repo": str(repo), "docs": docs, "pack": rol, "titulo": _titulo(rol, repo, docs)}
    try:
        p = act.planificar(pack, repo, docs)
        diag = flujo.diagnostico(repo, docs)
    except Exception as exc:  # noqa: BLE001 - se muestra en la tarjeta en lugar de romper la pantalla
        return {**base, "estado": "error", "error": str(exc), "grupos": [], "pendientes": []}
    degradacion = not p.sin_lock and lock.es_degradacion(p.adoptada, p.nueva)
    mayor = lock.mayor(p.nueva) != lock.mayor(p.adoptada) and not p.sin_lock
    hay_cambios = bool(p.de("añadir", "reemplazar", "zona", "restaurar", "conflicto")) or p.nueva != p.adoptada
    grupos = [{"tipo": t, "titulo": ti, "explica": ex, "archivos": [a.rel for a in p.de(t)], "diferencias": t in CON_DIFERENCIAS}
              for t, (ti, ex) in GRUPOS.items() if p.de(t)]
    return {**base, "estado": "degradacion" if degradacion else "mayor" if mayor else "actualizar" if hay_cambios else "al_dia", "actual": p.adoptada, "nueva": p.nueva,
            "git_sucio": _git_cambios(repo, docs), "grupos": grupos, "colaboracion_pendiente": api.colaboracion_pendiente(repo, docs),
            "pendientes": [x.__dict__ for x in diag.pasos if x.estado != "ok"], "verificaciones_ok": sum(1 for x in diag.pasos if x.estado == "ok")}


def revisar(rutas: list[str]) -> dict:
    """Por cada carpeta: qué packs tiene instalados y qué cambiaría en cada uno (sin escribir nada)."""
    vistos: set[str] = set()
    proyectos = []
    for ruta in rutas:
        info = api.inspeccionar(ruta)
        if not info["ok"]:
            proyectos.append({"ruta": ruta, "nombre": ruta, "ok": False, "error": info["error"], "packs": []})
            continue
        base, packs = Path(info["ruta"]), []
        for inst in info["instalados"]:
            pack = PACKS.get(inst["pack"])
            repo, docs = cfgmod.normalizar(base, inst["docs"])
            pid = f"{repo}|{docs}"
            if pid in vistos:
                continue
            vistos.add(pid)
            if pack is None:
                packs.append({"id": pid, "repo": str(repo), "docs": docs, "pack": inst["pack"], "titulo": _titulo(inst["pack"], repo, docs),
                              "estado": "error", "error": f"El lock indica un pack desconocido ({inst['pack']!r}).", "grupos": [], "pendientes": []})
            else:
                packs.append(_ficha(pid, pack, repo, docs, inst["pack"]))
        proyectos.append({"ruta": info["ruta"], "nombre": info["nombre"], "ok": True, "instalado": bool(info["instalados"]), "packs": packs})
    return {"ok": True, "proyectos": proyectos}


def diferencia(repo: str, docs: str, rel: str) -> dict:
    """Diferencias línea a línea entre tu archivo y el de uxyngraphar. Solo para archivos que el plan marca como distintos."""
    try:
        r, d = cfgmod.normalizar(Path(repo), docs)
        pack = _pack_de(r, d)
        if pack is None:
            return {"ok": False, "error": "Este proyecto no tiene uxyngraphar instalado."}
        plan = act.planificar(pack, r, d)
        permitido = {a.rel for a in plan.de(*CON_DIFERENCIAS)}
        if rel not in permitido:
            return {"ok": False, "error": "Ese archivo no tiene diferencias que mostrar."}
        local, nuevo = r / cl.destino(rel, d), pack / rel
        if max(local.stat().st_size, nuevo.stat().st_size) > LIMITE_BYTES:
            return {"ok": False, "error": "El archivo es demasiado grande para compararlo aquí; ábrelo en tu editor."}
        a = local.read_text(encoding="utf-8", errors="replace").splitlines()
        if rel in {x.rel for x in plan.de("zona")}:   # se muestra el resultado real: tu archivo con la parte del pack al día
            b = (act._fusion(local, nuevo) or local.read_text(encoding="utf-8", errors="replace")).splitlines()
        else:
            b = nuevo.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"No pude comparar: {exc}"}
    marcas = {"@": "h", "+": "a", "-": "q", " ": "c"}
    lineas = [{"t": marcas.get(x[0], "c"), "x": x} for x in difflib.unified_diff(a, b, "Tu versión", "Versión nueva", lineterm="", n=2)
              if not x.startswith(("---", "+++"))]
    return {"ok": True, "lineas": lineas[:LIMITE_LINEAS], "truncado": len(lineas) > LIMITE_LINEAS, "igual": not lineas}


def info_colaboracion() -> dict:
    return api.info_colaboracion()


def aplicar(seleccion: list[dict], colaborar: str = "") -> dict:
    """Actualiza lo elegido. El pack se toma siempre del lock del proyecto, nunca de lo que envía la pantalla.

    `colaborar` («si»/«no») responde una vez a la pregunta de colaboración en los packs que aún no la tienen."""
    destinos, todo_ok = [], True
    for item in seleccion:
        repo = Path(str(item.get("repo", "")))
        if not repo.is_dir():
            destinos.append({"titulo": str(repo), "ok": False, "pasos": [{"texto": "La carpeta ya no existe", "estado": "error", "detalle": str(repo)}], "diagnostico": []})
            todo_ok = False
            continue
        repo, docs = cfgmod.normalizar(repo, str(item.get("docs", "docs")))
        pack = _pack_de(repo, docs)
        rol = (lock.leer(repo, docs) or {}).get("pack", "")
        titulo = _titulo(rol, repo, docs)
        if pack is None:
            destinos.append({"titulo": titulo, "ok": False, "pasos": [{"texto": "Este proyecto no tiene uxyngraphar instalado", "estado": "error", "detalle": ""}], "diagnostico": []})
            todo_ok = False
            continue
        r = flujo.actualizar_completo(pack, repo, docs, str(item.get("migracion") or "").strip())
        if r.ok:
            for texto, estado in api.aplicar_colaboracion(repo, docs, {"colaborar": colaborar}, "actualizador"):
                r.add(texto, estado)
        diag = flujo.diagnostico(repo, docs) if r.ok else flujo.Resultado()
        todo_ok = todo_ok and r.ok
        destinos.append({"titulo": titulo, "repo": str(repo), "docs": docs, "ok": r.ok, "pasos": [p.__dict__ for p in r.pasos],
                         "respaldo": next((p.detalle for p in r.pasos if p.texto.startswith("Copia de seguridad")), ""),
                         "conflictos": sum(1 for p in r.pasos if ".uxyngraphar-nuevo" in p.detalle),
                         "diagnostico": [p.__dict__ for p in diag.pasos if p.estado != "ok"], "diagnostico_ok": sum(1 for p in diag.pasos if p.estado == "ok")})
    return {"ok": todo_ok, "destinos": destinos, "siguientes": siguientes_pasos(destinos)}


def siguientes_pasos(destinos: list[dict]) -> list[str]:
    pasos = []
    if any(d.get("conflictos") for d in destinos):
        pasos.append("Busca los archivos «.uxyngraphar-nuevo» (están junto a los tuyos), compara, quédate con lo que quieras y borra la copia «.uxyngraphar-nuevo».")
    if any(d.get("ok") for d in destinos):
        pasos.append("Haz commit de lo actualizado (docs/, AGENTES.md, .claude/, .github/) para dejar el proyecto en un punto limpio.")
        pasos.append("Si algo no te convence, la copia de seguridad está en «.uxyngraphar-respaldo/» dentro del repositorio.")
    return pasos
