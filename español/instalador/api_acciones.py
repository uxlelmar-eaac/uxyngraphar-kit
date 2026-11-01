"""Acciones del panel sobre un proyecto: salud y arreglos, pendientes por decidir, copias de seguridad, memoria,
colaboración, ganchos de git, protecciones, reglas del equipo y orden de las fichas.

Cada acción usa los scripts de la versión del pack que tiene el proyecto (<carpeta del pack>/scripts/), igual que si la
persona los ejecutara en su terminal. Nada cambia sin una vista previa antes; lo que escribe exige una persona delante
(api_panel.persona_presente) y, si toca archivos, deja copia en .uxyngraphar-respaldo/ (se restaura desde el propio panel).
"""

from __future__ import annotations

import difflib
import getpass
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import api_panel as panel

MARCA_JSON = "@@uxyngraphar-json@@"
SIN_SCRIPT = "Este proyecto tiene una versión del pack sin {}: actualízalo desde «Mis proyectos»."
VIEJO = "Esta versión del pack no permite hacerlo desde el panel: actualiza el proyecto desde «Mis proyectos»."
# Código que se ejecuta con los scripts del proyecto: argv = carpeta scripts, repo, carpeta del pack, datos JSON.
PREAMBULO = ("import sys, json\nfrom pathlib import Path\nS = Path(sys.argv[1])\n"
             "sys.path[:0] = [str(S / d) for d in ('nucleo', 'control', 'decisiones', 'ganchos')] + [str(S)]\n"
             "REPO, DOCS, ARGS = Path(sys.argv[2]), sys.argv[3], json.loads(sys.argv[4])\n"
             f"def fin(x):\n    print('\\n{MARCA_JSON}' + json.dumps(x, ensure_ascii=False, default=str))\n    sys.exit(0)\n")
# Lo que puede tocar «Arreglar» (doctor --fix): se copia antes y se informa de lo que cambió de verdad.
TOCA_ARREGLAR = (".gitignore", ".gitattributes", ".claude/settings.json", ".cursorignore", ".geminiignore", ".aiexclude",
                 ".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS")
QUE_ARREGLA = ["Termina o deshace una actualización que quedó a medias (con su propia copia de seguridad).",
               "Añade a .gitignore y .gitattributes las líneas de uxyngraphar que falten.",
               "Regenera las reglas que impiden a los agentes tocar el núcleo (.claude/settings.json, .cursorignore, .geminiignore, .aiexclude).",
               "Regenera el bloque de uxyngraphar en CODEOWNERS (si ya existe) y quita del lock una ruta local.",
               "Pone al día las frases de activación en ESTADO.md.",
               "Crea el workflow de CI si ninguno ejecuta uxyngraphar e instala el gancho pre-commit (uno ajeno no se toca).",
               "Nunca toca el núcleo del pack ni tu contenido."]
GANCHOS = ("pre-commit", "commit-msg", "pre-push")
PROPIETARIO_RE = re.compile(r"^(@[A-Za-z0-9_.-]+(/[A-Za-z0-9_.-]+)?|[^@\s]+@[^@\s]+\.[^@\s]+)$")


# ---------- ejecutar los scripts del proyecto ----------

def _ubicar(ruta: str, docs: str) -> tuple[Path, str, Path]:
    repo = Path(ruta or ".").expanduser().resolve()
    docs = (docs or "").replace("\\", "/").strip("/")
    return repo, docs, repo / docs / "scripts"


def _entorno(humano: bool) -> dict:
    """Sin DOCS_DIR(S) de la persona (cada script usa su propio pack); UXYNGRAPHAR_HUMANO solo si escribe una persona."""
    env = {k: v for k, v in os.environ.items() if k not in ("DOCS_DIR", "DOCS_DIRS", "UXYNGRAPHAR_HUMANO")}
    env.update(PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    if humano:
        env["UXYNGRAPHAR_HUMANO"] = "1"
    return env


def _proceso(orden: list[str], repo: Path, humano: bool, timeout: int) -> subprocess.CompletedProcess | str:
    try:
        return subprocess.run(orden, cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              stdin=subprocess.DEVNULL, env=_entorno(humano), timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return str(exc)


def correr(ruta: str, docs: str, script: str, args: list[str], humano: bool = False, timeout: int = 300) -> dict:
    """Ejecuta <pack>/scripts/<script> del proyecto. `ok` es el código 0; cada acción interpreta el resto."""
    repo, docs, scripts = _ubicar(ruta, docs)
    if not (scripts / script).is_file():
        return {"ok": False, "error": SIN_SCRIPT.format(script)}
    r = _proceso([sys.executable, str(scripts / script), *args], repo, humano, timeout)
    if isinstance(r, str):
        return {"ok": False, "error": f"No se pudo ejecutar {script}: {r}"}
    salida = (r.stdout.strip() + ("\n" + r.stderr.strip() if r.stderr.strip() else "")).strip()
    return {"ok": r.returncode == 0, "codigo": r.returncode, "salida": salida, "stdout": r.stdout, "stderr": r.stderr}


def fragmento(ruta: str, docs: str, codigo: str, datos: dict | None = None, humano: bool = False, timeout: int = 120) -> dict:
    """Ejecuta `codigo` con los módulos del pack del proyecto; el código termina con fin({...})."""
    repo, docs, scripts = _ubicar(ruta, docs)
    if not scripts.is_dir():
        return {"ok": False, "error": f"No encuentro {docs}/scripts en {repo}."}
    r = _proceso([sys.executable, "-c", PREAMBULO + codigo, str(scripts), str(repo), docs, json.dumps(datos or {})], repo, humano, timeout)
    if isinstance(r, str):
        return {"ok": False, "error": f"No se pudo ejecutar: {r}"}
    if MARCA_JSON not in r.stdout:
        return {"ok": False, "error": VIEJO, "detalle": (r.stderr or r.stdout).strip()[-1500:]}
    return json.loads(r.stdout.rsplit(MARCA_JSON, 1)[1])


def _sin_persona() -> dict | None:
    motivo = panel.persona_presente()
    return {"ok": False, "error": motivo} if motivo else None


# ---------- copias de seguridad de lo que cambia el panel ----------

def _huella(archivo: Path) -> str | None:
    return hashlib.sha256(archivo.read_bytes()).hexdigest() if archivo.is_file() else None


def respaldar(repo: Path, rels: list[str], motivo: str) -> Path:
    """Copia los archivos que existen en .uxyngraphar-respaldo/<fecha>/ con el manifiesto que entiende respaldos.py."""
    base, n = datetime.now().strftime("%Y%m%d-%H%M%S"), 1
    carpeta = repo / ".uxyngraphar-respaldo" / base
    while carpeta.exists():
        carpeta, n = repo / ".uxyngraphar-respaldo" / f"{base}-{n}", n + 1
    existentes = sorted({r for r in rels if (repo / r).is_file()})
    for rel in existentes:
        (carpeta / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo / rel, carpeta / rel)
    _manifiesto(carpeta, existentes, [], motivo)
    return carpeta


def _manifiesto(carpeta: Path, archivos: list[str], añadidos: list[str], motivo: str) -> None:
    carpeta.mkdir(parents=True, exist_ok=True)
    datos = {"origen": "actualizacion", "fecha": datetime.now().isoformat(timespec="seconds"), "archivos": sorted(set(archivos)),
             "añadidos": sorted(set(añadidos)), "motivo": motivo}
    (carpeta / "_respaldo.json").write_text(json.dumps(datos, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def cerrar_respaldo(carpeta: Path, antes: dict, despues: dict, motivo: str) -> tuple[str, list[str]]:
    """Deja en la copia solo lo que cambió (y anota lo creado, que se retira al restaurar). Sin cambios, la borra."""
    cambiados = sorted(r for r in set(antes) | set(despues) if antes.get(r) != despues.get(r))
    if not cambiados:
        shutil.rmtree(carpeta, ignore_errors=True)
        return "", []
    for rel in [r for r in antes if antes[r] and r not in cambiados]:
        (carpeta / rel).unlink(missing_ok=True)
    _manifiesto(carpeta, [r for r in cambiados if antes.get(r)], [r for r in cambiados if not antes.get(r)], motivo)
    return f"actualizacion/{carpeta.name}", cambiados


# ---------- salud: doctor y «Arreglar» ----------

def _candidatos(repo: Path, docs: str) -> list[str]:
    flujos = repo / ".github" / "workflows"
    extra = [p.relative_to(repo).as_posix() for p in flujos.iterdir() if p.is_file()] if flujos.is_dir() else []
    return sorted({*TOCA_ARREGLAR, f"{docs}/.uxyngraphar.lock", f"{docs}/ESTADO.md", *extra})


def _chequeos(r: dict) -> dict:
    try:
        lista = json.loads(r.get("stdout") or "")
    except ValueError:
        return {"ok": False, "error": r.get("error") or "El doctor no respondió como se esperaba.", "salida": r.get("salida", "")}
    orden = {"ERROR": 0, "WARN": 1, "INFO": 2, "OK": 3}
    lista.sort(key=lambda c: orden.get(c.get("nivel"), 9))
    cuenta = {n: sum(1 for c in lista if c.get("nivel") == n) for n in orden}
    return {"ok": True, "chequeos": lista, "cuenta": cuenta}


def doctor(ruta: str, docs: str) -> dict:
    """Chequeo completo (solo lee) y qué haría «Arreglar», con los archivos que podría tocar."""
    repo, docs, _ = _ubicar(ruta, docs)
    r = _chequeos(correr(str(repo), docs, "doctor.py", ["--json", "--repo", str(repo), "--docs", docs]))
    if r["ok"]:
        r.update(que_arregla=QUE_ARREGLA, archivos=[x for x in _candidatos(repo, docs) if (repo / x).is_file()])
    return r


def arreglar(ruta: str, docs: str) -> dict:
    """doctor --fix con copia previa de lo que puede tocar; devuelve qué cambió de verdad y el diagnóstico nuevo."""
    if (no := _sin_persona()):
        return no
    repo, docs, scripts = _ubicar(ruta, docs)
    if not (scripts / "doctor.py").is_file():
        return {"ok": False, "error": SIN_SCRIPT.format("doctor.py")}
    antes = {rel: _huella(repo / rel) for rel in _candidatos(repo, docs)}
    carpeta = respaldar(repo, list(antes), "Arreglar (doctor --fix) desde el panel")
    r = correr(str(repo), docs, "doctor.py", ["--fix", "--json", "--repo", str(repo), "--docs", docs], humano=True)
    despues = {rel: _huella(repo / rel) for rel in _candidatos(repo, docs)}
    respaldo, cambiados = cerrar_respaldo(carpeta, antes, despues, "Arreglar (doctor --fix) desde el panel")
    hechas = [l[5:] for l in (r.get("stderr") or "").splitlines() if l.startswith("fix: ")]
    return {**_chequeos(r), "hechas": hechas, "cambiados": cambiados, "respaldo": respaldo}


# ---------- pendientes por decidir (instrucciones, mejoras, EVO, propuestas, ADR, auditorías) ----------

_DECIDIR = """
import scanner, session, applier
from session_acciones import error_de_accion, opciones_de_item
raiz = (REPO / DOCS).resolve()
items = scanner.scan_all([(raiz, Path(DOCS).name)])
if ARGS.get("listar"):
    fin({"ok": True, "items": [i.to_dict() for i in items]})
items = [i for i in items if i.id == ARGS["id"]]
if not items:
    fin({"ok": False, "error": "Ya no está pendiente (¿lo decidió otra persona?). Recarga la lista."})
item = items[0].to_dict()
error = error_de_accion(str(item.get("tipo") or ""), ARGS["accion"], opciones_de_item(item))
if error:
    fin({"ok": False, "error": error})
if ARGS.get("aplicar"):
    session.register_decision(ARGS["id"], ARGS["accion"], item, registered_by=ARGS["por"])
    sesion = session.load_active_session()
    mias = [d for d in sesion["decisions"] if d.get("id") == ARGS["id"] and d.get("docs_root") == item.get("docs_root") and not d.get("applied")]
    res = applier.apply_session({"session_id": sesion["session_id"], "decisions": mias}, dry_run=False, permitidas=[raiz])
    session.save_active_session(sesion)
    final = mias[0].get("path") if mias else item["path"]
else:
    entrada = {"id": ARGS["id"], "group_id": ARGS["id"], "action": ARGS["accion"], "applied": False, "path": item["path"],
               "docs_root": item["docs_root"], "pack_label": item.get("pack_label"), "tipo": item.get("tipo"),
               "title": item.get("title"), "opciones": opciones_de_item(item)}
    res = applier.apply_session({"session_id": "vista-previa", "decisions": [entrada]}, dry_run=True, permitidas=[raiz])
    final = item["path"]
fin({"ok": bool(res) and all(x.get("ok") for x in res), "resultados": res, "item": item, "ruta_final": final,
     "error": "; ".join(str(x.get("error")) for x in res if x.get("error"))})
"""


def pendientes(ruta: str, docs: str) -> dict:
    return fragmento(ruta, docs, _DECIDIR, {"listar": True})


def ficha(ruta: str, docs: str, rel: str) -> dict:
    """Texto de una ficha del pack (para leerla antes de decidir). Nunca fuera del pack ni de la memoria."""
    repo, docs, _ = _ubicar(ruta, docs)
    base = (repo / docs).resolve()
    archivo = (base / rel).resolve()
    if not archivo.is_relative_to(base) or archivo.suffix != ".md" or "95-memoria" in archivo.relative_to(base).parts or not archivo.is_file():
        return {"ok": False, "error": "Esa ficha no está en la carpeta del pack."}
    return {"ok": True, "ruta": f"{docs}/{archivo.relative_to(base).as_posix()}", "texto": archivo.read_text(encoding="utf-8", errors="replace")[:200_000]}


def decision_previa(ruta: str, docs: str, ident: str, accion: str) -> dict:
    return fragmento(ruta, docs, _DECIDIR, {"id": ident, "accion": accion})


def _archivos_pack(repo: Path, docs: str) -> dict:
    base = repo / docs
    return {p.relative_to(repo).as_posix(): _huella(p) for p in base.rglob("*") if p.is_file() and ".decisiones" not in p.parts}


def decidir(ruta: str, docs: str, ident: str, accion: str) -> dict:
    """Registra y aplica una decisión (como decisiones.py register + apply), con copia de la ficha antes."""
    if (no := _sin_persona()):
        return no
    previa = decision_previa(ruta, docs, ident, accion)
    if not previa.get("ok"):
        return previa
    repo, docs, _ = _ubicar(ruta, docs)
    origen = f"{docs}/{previa['item']['path']}"
    antes = _archivos_pack(repo, docs)
    carpeta = respaldar(repo, [origen], f"decisión «{accion}» sobre {ident} desde el panel")
    por = f"{os.environ.get('DECISIONES_USER') or getpass.getuser()} (panel)"
    r = fragmento(str(repo), docs, _DECIDIR, {"id": ident, "accion": accion, "aplicar": True, "por": por}, humano=True)
    despues = _archivos_pack(repo, docs)
    nuevos = {k: v for k, v in despues.items() if k not in antes}   # la ficha movida o un borrador creado: se retiran al restaurar
    respaldo, cambiados = cerrar_respaldo(carpeta, {origen: antes.get(origen)}, {origen: despues.get(origen), **nuevos},
                                          f"decisión «{accion}» sobre {ident} desde el panel")
    otros = sorted(k for k in antes if k != origen and antes[k] != despues.get(k))   # otros cambios (van en git)
    return {**r, "respaldo": respaldo, "cambiados": cambiados + otros}


# ---------- copias de seguridad (respaldos.py) ----------

_RESPALDOS = """
import respaldos as rs
if ARGS.get("plan"):
    r = rs.buscar(REPO, DOCS, ARGS["id"])
    if r is None:
        fin({"ok": False, "error": "Esa copia ya no existe."})
    fin({"ok": True, "id": r.id, **rs.plan_restaurar(r, ARGS.get("archivos") or None)})
cad = {r.id for r in rs.caducados(REPO, DOCS)}
fin({"ok": True, "politica": rs.politica(REPO, DOCS), "copias": [{"id": r.id, "origen": r.origen, "fecha": r.fecha.strftime("%Y-%m-%d %H:%M"),
     "dias": r.dias, "archivos": r.archivos, "anadidos": r.añadidos, "carpeta": str(r.carpeta), "base": str(r.base),
     "motivo": r.info.get("motivo", ""), "version_antes": r.info.get("version_antes", ""), "version_despues": r.info.get("version_despues", ""),
     "caducada": r.id in cad} for r in rs.listar(REPO, DOCS)]})
"""


def respaldos(ruta: str, docs: str) -> dict:
    return fragmento(ruta, docs, _RESPALDOS)


def respaldo_plan(ruta: str, docs: str, ident: str, archivos: list[str] | None = None) -> dict:
    return fragmento(ruta, docs, _RESPALDOS, {"plan": True, "id": ident, "archivos": archivos or []})


def respaldo_diferencia(ruta: str, docs: str, ident: str, rel: str) -> dict:
    """Cómo cambiaría un archivo al restaurarlo: lo de ahora frente a lo guardado en la copia."""
    lista = respaldos(ruta, docs)
    copia = next((c for c in lista.get("copias", []) if c["id"] == ident), None)
    if not copia or rel not in copia["archivos"]:
        return {"ok": False, "error": "Ese archivo no está en la copia."}
    guardado, actual = Path(copia["carpeta"]) / rel, Path(copia["base"]) / rel
    leer = (lambda p: p.read_text(encoding="utf-8", errors="replace").splitlines() if p.is_file() else [])
    diff = list(difflib.unified_diff(leer(actual), leer(guardado), "ahora", "tras restaurar", lineterm="", n=2))
    return {"ok": True, "diff": diff[:2000], "existe": actual.is_file()}


def restaurar(ruta: str, docs: str, ident: str, archivos: list[str] | None = None) -> dict:
    if (no := _sin_persona()):
        return no
    repo, docs, _ = _ubicar(ruta, docs)
    extra = [x for a in (archivos or []) for x in ("--archivo", a)]
    return correr(str(repo), docs, "respaldos.py", ["restaurar", ident, *extra, "--repo", str(repo), "--docs", docs, "--aplicar"], humano=True)


def limpiar_respaldos(ruta: str, docs: str, aplicar: bool) -> dict:
    if aplicar and (no := _sin_persona()):
        return no
    repo, docs, _ = _ubicar(ruta, docs)
    r = correr(str(repo), docs, "respaldos.py", ["limpiar", "--repo", str(repo), "--docs", docs, *(["--aplicar"] if aplicar else [])], humano=aplicar)
    return {**r, "ok": r.get("codigo") in (0, 1), "nada": r.get("codigo") == 1}


# ---------- memoria del sistema (memoria.py; solo personas: R-24) ----------

def memoria(ruta: str, docs: str, orden: str, ident: str = "", texto: str = "", motivo: str = "", confirmar: str = "") -> dict:
    if (no := _sin_persona()):
        return no
    repo, docs, _ = _ubicar(ruta, docs)
    pre = ["--repo", str(repo), "--docs", docs]
    args = {"buscar": ["buscar", texto], "ver": ["ver", ident], "recuperar": ["recuperar", ident],
            "purgar": ["purgar", ident, "--confirmar", confirmar, "--motivo", motivo]}.get(orden)
    if args is None or (orden != "buscar" and not ident) or (orden == "purgar" and not motivo.strip()):
        return {"ok": False, "error": "Faltan datos: el id de la memoria (y el motivo para purgar)."}
    r = correr(str(repo), docs, "memoria.py", [*pre, *args], humano=True)
    return {**r, "ok": r.get("codigo") in (0, 1) if orden == "buscar" else r.get("ok", False)}


# ---------- colaboración (feedback.py) ----------

def feedback(ruta: str, docs: str, orden: str) -> dict:
    if orden not in ("estado", "previsualizar", "enviar"):
        return {"ok": False, "error": "Orden desconocida."}
    if orden == "enviar" and (no := _sin_persona()):
        return no
    repo, docs, _ = _ubicar(ruta, docs)
    r = correr(str(repo), docs, "feedback.py", [orden, "--repo", str(repo), "--docs", docs], humano=orden == "enviar", timeout=120)
    return {**r, "ok": r.get("codigo") in (0, 1), "nada": r.get("codigo") == 1}


# ---------- ganchos de git y protecciones ----------

_PROTECCION = """
import instalar_ganchos as g, proteccion
try:
    d = g.dir_ganchos(REPO)
    ganchos = {n: {"existe": (d / n).is_file(), "nuestro": g.es_nuestro(d / n), "docs": g.docs_del_gancho(d / n)} for n in ARGS["nombres"]}
except RuntimeError:
    d, ganchos = None, {}
if ARGS.get("propietario"):
    proteccion.codeowners(REPO, DOCS, ARGS["propietario"])
fin({"ok": True, "git": d is not None, "carpeta": str(d or ""), "ganchos": ganchos, "propietario": proteccion.propietario_actual(REPO, DOCS)})
"""


def protecciones(ruta: str, docs: str) -> dict:
    return fragmento(ruta, docs, _PROTECCION, {"nombres": list(GANCHOS)})


def ganchos(ruta: str, docs: str, quitar: bool = False, pre_push: bool = False) -> dict:
    if (no := _sin_persona()):
        return no
    repo, docs, _ = _ubicar(ruta, docs)
    args = ["--quitar"] if quitar else ["--docs", docs, *(["--pre-push"] if pre_push else [])]
    return correr(str(repo), docs, "instalar-ganchos.py", args, humano=True)


def propietario(ruta: str, docs: str, quien: str, aplicar: bool) -> dict:
    """Quién aprueba los cambios al núcleo (bloque de uxyngraphar en CODEOWNERS)."""
    quien = (quien or "").strip()
    if not PROPIETARIO_RE.match(quien):
        return {"ok": False, "error": "Escribe un usuario o equipo de GitHub con @ (p. ej. @juanperez o @mi-org/equipo) o un correo."}
    repo, docs, _ = _ubicar(ruta, docs)
    if not aplicar:
        actual = protecciones(str(repo), docs)
        return {"ok": actual.get("ok", False), "error": actual.get("error", ""), "antes": actual.get("propietario", ""), "despues": quien,
                "archivos": [r for r in ("CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS") if (repo / r).is_file()] or [".github/CODEOWNERS (nuevo)"]}
    if (no := _sin_persona()):
        return no
    rels = ["CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS"]
    antes = {r: _huella(repo / r) for r in rels}
    carpeta = respaldar(repo, rels, "propietario del núcleo (CODEOWNERS) desde el panel")
    r = fragmento(str(repo), docs, _PROTECCION, {"nombres": list(GANCHOS), "propietario": quien}, humano=True)
    respaldo, cambiados = cerrar_respaldo(carpeta, antes, {x: _huella(repo / x) for x in rels}, "propietario del núcleo (CODEOWNERS)")
    return {**r, "respaldo": respaldo, "cambiados": cambiados}


# ---------- reglas del equipo y orden de las fichas ----------

def reglas(ruta: str, docs: str) -> dict:
    repo, docs, _ = _ubicar(ruta, docs)
    listar = correr(str(repo), docs, "reglas.py", ["listar", "--repo", str(repo), "--docs", docs])
    validar = correr(str(repo), docs, "reglas.py", ["validar", "--repo", str(repo), "--docs", docs])
    if listar.get("error"):
        return listar
    return {"ok": True, "lista": listar.get("salida", ""), "validar": validar.get("salida", ""), "valido": validar.get("ok", False)}


def ordenar(ruta: str, docs: str, orden: str, dias: int, aplicar: bool) -> dict:
    """Archivar completadas antiguas (03→04) o apartar canceladas (05→06). Nunca borra: solo mueve fichas."""
    if orden not in ("archivar", "limpiar") or not isinstance(dias, int) or dias < 1:
        return {"ok": False, "error": "Indica archivar o limpiar y un número de días mayor que 0."}
    if aplicar and (no := _sin_persona()):
        return no
    repo, docs, _ = _ubicar(ruta, docs)
    return correr(str(repo), docs, "decisiones/decisiones.py", [orden, "--dias", str(dias), *(["--apply"] if aplicar else [])], humano=aplicar)
