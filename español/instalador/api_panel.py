"""Lógica del panel de configuración (sin interfaz): proyectos de este equipo, configuración de cada uno y plantilla.

Lee y escribe docs/uxyngraphar.config.json con el lector de la versión del pack que tiene cada proyecto. Antes de
escribir enseña qué cambia, comprueba que nadie tocó el archivo mientras tanto y deja una copia en .uxyngraphar-respaldo/
(se restaura con «respaldos.py restaurar»). La respuesta a «colaborar» pasa por el feedback.py del propio proyecto.
"""

from __future__ import annotations

import copy
import difflib
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import api
import sistema

# Lo que el panel deja cambiar en un proyecto. Fuera quedan `version` (formato), `pila` (informativo),
# `idioma.artefactos` (núcleo) y los campos de consentimiento de `feedback` (solo «colaborar» Sí/No los escribe).
EDITABLES = {
    "rol": None, "limite_lineas": None, "niveles": None, "exenciones_lineas": None, "secretos_permitir": None,
    "respaldos": None, "memoria": None, "reglas_proyecto": None, "codigo": ("raices", "extensiones", "excluir"),
    "idioma": ("conversacion", "commits", "ramas", "glosario", "excluir", "legacy", "locales"), "feedback": ("ocultar",),
}


def _huella(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]


def _plano(datos: dict, prefijo: str = "") -> dict:
    salida = {}
    for k, v in datos.items():
        if isinstance(v, dict):
            salida.update(_plano(v, f"{prefijo}{k}."))
        else:
            salida[f"{prefijo}{k}"] = v
    return salida


def _legibles(antes: dict, despues: dict) -> list[str]:
    a, d = _plano(antes), _plano(despues)
    return [f"{k}: {json.dumps(a.get(k), ensure_ascii=False)} → {json.dumps(d.get(k), ensure_ascii=False)}"
            for k in sorted(set(a) | set(d)) if a.get(k) != d.get(k)]


def persona_presente() -> str:
    """"" si hay una persona delante; si no, por qué el panel no puede cambiar nada (CI o agente)."""
    variable = api.feedback.sin_persona()
    return f"El panel solo lo usa una persona: detecté {variable} (CI o un agente). Ábrelo tú desde tu terminal." if variable else ""


# ---------- proyectos de este equipo ----------

def _estado_version(v: str, propia: str) -> str:
    if v == propia:
        return "al día"
    return "actualizable" if sistema.tupla(v) < sistema.tupla(propia) else "más nuevo que tu herramienta"


def resumen() -> dict:
    propia, salida = sistema.version_herramienta(), []
    for ruta in sistema.leer_proyectos():
        if not Path(ruta).is_dir():
            salida.append({"ruta": ruta, "nombre": Path(ruta).name, "existe": False, "packs": []})
            continue
        info = api.inspeccionar(ruta)
        packs = [{**x, "estado": _estado_version(x["version"], propia)} for x in info.get("instalados", [])]
        salida.append({"ruta": ruta, "nombre": Path(ruta).name, "existe": True, "packs": packs})
    return {"ok": True, "version": propia, "carpeta": str(sistema.home()), "proyectos": salida, "plantilla": sistema.leer_plantilla(),
            "sin_persona": persona_presente(), "colaboracion": api.info_colaboracion()}


def ultima() -> dict:
    v, propia = sistema.ultima_publicada(espera=4), sistema.version_herramienta()
    return {"ok": True, "ultima": v, "propia": propia, "hay_nueva": bool(v) and sistema.tupla(v) > sistema.tupla(propia)}


def agregar(ruta: str) -> dict:
    info = api.inspeccionar(ruta)
    if not info["ok"]:
        return {"ok": False, "error": info["error"]}
    if not info["instalados"]:
        return {"ok": False, "error": f"«{info['nombre']}» no tiene uxyngraphar. Instálalo primero (uxyngraphar instalar)."}
    sistema.guardar_proyectos(sistema.leer_proyectos() + [info["ruta"]])
    return {"ok": True, "ruta": info["ruta"]}


def registrar_instalados(resultado: dict) -> dict:
    """Instalado desde el panel: los proyectos que quedaron bien pasan a «Mis proyectos»."""
    nuevas = [d["repo"] for d in resultado.get("destinos", []) if d.get("ok") and d.get("repo")]
    if nuevas:
        sistema.guardar_proyectos(sistema.leer_proyectos() + nuevas)
    return resultado


def quitar(ruta: str) -> dict:
    sistema.guardar_proyectos([p for p in sistema.leer_proyectos() if p != ruta])
    return {"ok": True}


def salud(ruta: str, docs: str) -> dict:
    sys.path.insert(0, str(sistema.ES / "backend" / "scripts"))
    import flota
    f = flota.revisar(Path(ruta), docs, "")
    if f.get("error"):
        return {"ok": False, "error": f["error"]}
    return {"ok": True, "errores": f["errores"], "avisos": f["avisos"], "motivos": f["motivos"][:12]}


# ---------- bienvenida tras el instalador de una línea ----------

def bienvenida() -> dict | None:
    """Lo que hizo el instalador (cada línea de la consola) y lo que queda por decidir, como el PATH."""
    try:
        datos = json.loads((sistema.home() / "ultima-instalacion.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    bin_dir = sistema.ar.carpeta_bin(str(sistema.home()))
    datos["path_pendiente"] = bool(datos.get("path_pendiente")) and not sistema.ar.en_path(bin_dir)
    datos["bin"] = bin_dir
    return datos


def decidir_path(agregar: bool) -> dict:
    """Respuesta a «¿Añadir el comando uxyngraphar al PATH?» de la bienvenida."""
    motivo = persona_presente()
    if motivo:
        return {"ok": False, "error": motivo}
    home = sistema.home()
    archivo = home / "ultima-instalacion.json"
    try:
        datos = json.loads(archivo.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        datos = {}
    texto = ""
    if agregar:
        registro = sistema.ar.leer_registro(str(home))
        texto = sistema.ar.asegurar_path(str(home), registro) or "El comando ya estaba en tu PATH."
        sistema.ar.escribir_atomico(str(home / "instalacion.json"), json.dumps(registro, indent=2, ensure_ascii=True) + "\n")
    else:
        texto = f"No toqué el PATH. Usa el comando con su ruta completa: {datos.get('lanzador', '')}"
    datos.update(path_pendiente=False, path_decision="si" if agregar else "no")
    sistema.ar.escribir_atomico(str(archivo), json.dumps(datos, indent=2, ensure_ascii=True) + "\n")
    return {"ok": True, "texto": texto}


# ---------- configuración de un proyecto ----------

def _leer(ruta: str, docs: str) -> tuple[Path, object, Path, str, dict | None]:
    repo = Path(ruta).expanduser().resolve()
    cfgmod = sistema.modulo_config(repo, docs)
    archivo = repo / docs / cfgmod.NOMBRE
    texto = archivo.read_text(encoding="utf-8") if archivo.is_file() else ""
    try:
        crudo = json.loads(texto) if texto.strip() else {}
    except ValueError:
        crudo = None
    return repo, cfgmod, archivo, texto, crudo if isinstance(crudo, dict) or crudo is None else None


def ver(ruta: str, docs: str) -> dict:
    repo, cfgmod, archivo, texto, crudo = _leer(ruta, docs)
    if not (repo / docs).is_dir():
        return {"ok": False, "error": f"No encuentro {docs}/ en {repo}"}
    efectiva, problemas = cfgmod.cargar(repo, docs)
    fb = efectiva.get("feedback") or {}
    return {"ok": True, "ruta": str(repo), "docs": docs, "archivo": str(archivo), "existe": archivo.is_file(), "huella": _huella(texto),
            "ilegible": crudo is None, "efectiva": efectiva, "problemas": problemas, "defecto": cfgmod.por_defecto(efectiva.get("rol", "servidor")),
            "opciones": {"niveles": list(cfgmod.NIVELES), "controles": list(cfgmod.CONTROLES),
                         "excepciones": list(getattr(cfgmod, "MODOS_EXCEPCION", ())), "cambios_reglas": list(getattr(cfgmod, "MODOS_CAMBIO_REGLAS", ()))},
            "colaborar": {"activo": bool(fb.get("activo")), "respondido": fb.get("respondido", ""), "respondido_en": fb.get("respondido_en", ""),
                          "url": fb.get("url", ""), "disponible": (repo / docs / "scripts" / "feedback.py").is_file()},
            "guia": f"{docs}/10-guias/configuracion-uxyngraphar.md"}


def _propuesta(ruta: str, docs: str, cambios: dict) -> dict:
    repo, cfgmod, archivo, texto, crudo = _leer(ruta, docs)
    if crudo is None:
        return {"ok": False, "error": f"{cfgmod.NOMBRE} no es JSON válido: corrígelo a mano antes de cambiarlo desde el panel.", "huella": _huella(texto)}
    antes, _ = cfgmod.cargar(repo, docs)
    nuevo = cfgmod._fusionar(copy.deepcopy(crudo), sistema.filtrar(cambios or {}, EDITABLES))
    despues = cfgmod._fusionar(cfgmod.por_defecto(), copy.deepcopy(nuevo))
    texto_nuevo = json.dumps(nuevo, ensure_ascii=False, indent=2) + "\n"
    diff = list(difflib.unified_diff(texto.splitlines(), texto_nuevo.splitlines(), "ahora", "después", lineterm="", n=1))
    return {"ok": True, "repo": repo, "archivo": archivo, "texto_nuevo": texto_nuevo, "huella": _huella(texto),
            "problemas": cfgmod.validar(despues), "cambios": _legibles(antes, despues), "diff": diff, "despues": despues}


def previsualizar(ruta: str, docs: str, cambios: dict) -> dict:
    p = _propuesta(ruta, docs, cambios)
    return {k: v for k, v in p.items() if k in ("ok", "error", "huella", "problemas", "cambios", "diff")}


def _respaldar(repo: Path, archivo: Path) -> str:
    """Copia el archivo actual en .uxyngraphar-respaldo/<fecha>/ con el manifiesto que entiende respaldos.py."""
    if not archivo.is_file():
        return ""
    base, n = datetime.now().strftime("%Y%m%d-%H%M%S"), 1
    carpeta = repo / ".uxyngraphar-respaldo" / base
    while carpeta.exists():
        carpeta, n = repo / ".uxyngraphar-respaldo" / f"{base}-{n}", n + 1
    rel = archivo.relative_to(repo).as_posix()
    (carpeta / rel).parent.mkdir(parents=True, exist_ok=True)
    (carpeta / rel).write_bytes(archivo.read_bytes())
    manifiesto = {"origen": "actualizacion", "fecha": datetime.now().isoformat(timespec="seconds"), "archivos": [rel], "añadidos": [],
                  "motivo": "cambio de configuración desde el panel"}
    (carpeta / "_respaldo.json").write_text(json.dumps(manifiesto, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return f"actualizacion/{carpeta.name}"


def _proteger_reglas(repo: Path, docs: str) -> None:
    """Con `cambios_reglas: solo_humano`, añade las reglas deny del agente (con la versión del pack del proyecto)."""
    scripts = repo / docs / "scripts"
    codigo = ("import sys; sys.path[:0] = [sys.argv[1] + '/nucleo', sys.argv[1] + '/control']; import proteccion; "
              "from pathlib import Path; proteccion.reglas_agente(Path(sys.argv[2]), sys.argv[3])")
    subprocess.run([sys.executable, "-c", codigo, str(scripts), str(repo), docs], capture_output=True, timeout=60)


def guardar(ruta: str, docs: str, cambios: dict, huella: str, respaldar: bool = True) -> dict:
    motivo = persona_presente()
    if motivo:
        return {"ok": False, "error": motivo}
    p = _propuesta(ruta, docs, cambios)
    if not p["ok"]:
        return p
    if p["huella"] != huella:
        return {"ok": False, "error": "El archivo cambió desde que lo abriste (¿lo editó otra persona o un editor?). Vuelve a cargarlo."}
    if p["problemas"]:
        return {"ok": False, "error": "Hay valores inválidos; corrígelos antes de guardar.", "problemas": p["problemas"]}
    if not p["cambios"]:
        return {"ok": True, "sin_cambios": True}
    respaldo = _respaldar(p["repo"], p["archivo"]) if respaldar else ""
    p["archivo"].parent.mkdir(parents=True, exist_ok=True)
    tmp = p["archivo"].with_name(p["archivo"].name + ".tmp")
    tmp.write_text(p["texto_nuevo"], encoding="utf-8", newline="\n")
    tmp.replace(p["archivo"])
    if (p["despues"].get("reglas_proyecto") or {}).get("cambios_reglas") == "solo_humano":
        _proteger_reglas(p["repo"], docs)
    return {"ok": True, "respaldo": respaldo, "cambios": p["cambios"], "archivo": str(p["archivo"])}


def colaborar(ruta: str, docs: str, si: bool, borrar_remoto: bool = False) -> dict:
    """Sí/No a «colaborar» con el feedback.py del proyecto (registra consentimiento y fecha, o lo revoca)."""
    motivo = persona_presente()
    if motivo:
        return {"ok": False, "error": motivo}
    repo = Path(ruta).expanduser().resolve()
    script = repo / docs / "scripts" / "feedback.py"
    if not script.is_file():
        return {"ok": False, "error": "Este proyecto tiene una versión del pack sin envío de sugerencias: actualízalo primero."}
    orden = ["activar", "--acepto"] if si else ["revocar", *(["--borrar-remoto"] if borrar_remoto else [])]
    r = subprocess.run([sys.executable, str(script), *orden, "--repo", str(repo), "--docs", docs], capture_output=True, text=True, timeout=60)
    return {"ok": r.returncode == 0, "salida": (r.stdout + r.stderr).strip()}


# ---------- plantilla de este equipo ----------

def ver_plantilla() -> dict:
    cfgmod = sistema.modulo_config()
    return {"ok": True, "plantilla": sistema.leer_plantilla(), "defecto": cfgmod.por_defecto(), "archivo": str(sistema.home() / sistema.ARCHIVO_PLANTILLA),
            "opciones": {"niveles": list(cfgmod.NIVELES), "controles": list(cfgmod.CONTROLES),
                         "excepciones": list(cfgmod.MODOS_EXCEPCION), "cambios_reglas": list(cfgmod.MODOS_CAMBIO_REGLAS)}}


def guardar_plantilla(plantilla: dict) -> dict:
    motivo = persona_presente()
    return {"ok": False, "error": motivo} if motivo else sistema.guardar_plantilla(plantilla or {})


def plantilla_en(destinos: list[dict], aplicar: bool) -> dict:
    """Simula (o aplica) la plantilla en varios proyectos. Cada destino: {ruta, docs, huella?}."""
    plantilla, salida = sistema.leer_plantilla(), []
    if not plantilla:
        return {"ok": False, "error": "Aún no guardaste ninguna plantilla."}
    for d in destinos:
        if aplicar:
            r = guardar(d.get("ruta", ""), d.get("docs", "docs"), plantilla, d.get("huella", ""))
        else:
            r = previsualizar(d.get("ruta", ""), d.get("docs", "docs"), plantilla)
        salida.append({"ruta": d.get("ruta", ""), "docs": d.get("docs", "docs"), **r})
    return {"ok": all(x.get("ok") for x in salida), "destinos": salida}


def plantilla_al_instalar(repo: Path, docs: str) -> tuple[str, str] | None:
    """Tras instalar un proyecto nuevo: aplica la plantilla de este equipo (si hay). Devuelve (texto, estado) para el informe."""
    plantilla = sistema.leer_plantilla()
    if not plantilla:
        return None
    try:
        r = guardar(str(repo), docs, plantilla, _propuesta(str(repo), docs, {})["huella"], respaldar=False)
    except Exception as exc:  # noqa: BLE001 - la plantilla nunca rompe una instalación
        return (f"No se pudo aplicar tu plantilla de configuración: {exc}", "aviso")
    if not r.get("ok"):
        return (f"No se aplicó tu plantilla de configuración: {r.get('error')}", "aviso")
    return (f"Tu plantilla de configuración se aplicó a {docs}/uxyngraphar.config.json" if not r.get("sin_cambios")
            else "Tu plantilla de configuración ya coincidía con la de este proyecto", "ok")
