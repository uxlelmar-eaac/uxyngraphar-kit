"""`uxyngraphar diagnostico`: un informe del equipo y de los proyectos registrados para entender qué pasa o pegarlo en una
incidencia (M-17). Con `anonimizar`, la carpeta personal pasa a `~` y cada proyecto se nombra solo por su carpeta.
`avisos()` resume lo que pide atención en la portada del panel (M-28)."""

from __future__ import annotations

import json
import os
import platform
import shutil
import sys
from pathlib import Path

import casa
import fuentes
import especificacion as esp
import generar
import herramienta
import protecciones
import proyectos
import repo
import transaccion
import vocabulario

base = esp.base


def _proyecto(ruta: str, versiones: dict[str, str]) -> dict:
    raiz = Path(ruta)
    fila: dict = {"ruta": ruta, "nombre": raiz.name, "existe": raiz.is_dir()}
    if not fila["existe"]:
        return fila
    fila["tipo"] = "actual" if (raiz / base.CARPETA_RAIZ).is_dir() else "sin_uxyngraphar"
    if fila["tipo"] != "actual":
        return fila
    filas = repo.estado(raiz, versiones=versiones)
    fila["sistemas"] = len(filas)
    fila["alterados"] = [f["id"] for f in filas if not f["integro"]]
    fila["actualizables"] = [f["id"] for f in filas if f["actualizable"]]
    fila["interrumpida"] = bool(transaccion.interrumpida(raiz))
    fila["ocupado"] = bool(transaccion.ocupado(raiz))
    flujo = generar.ruta_flujo(raiz)
    if flujo.is_file():
        try:
            errores = esp.validar_flujo(generar.leer_flujo(raiz), {m["id"] for m in generar.instalados(raiz)})
        except ValueError as e:
            errores = [f"no es JSON válido: {e}"]
        fila["flujo"] = errores or "válido"
    else:
        fila["flujo"] = "no existe"
    fila["archivos_agente"] = {n: (raiz / n).is_file() and generar.INICIO in (raiz / n).read_text(encoding="utf-8", errors="replace")
                               for n in generar.ARCHIVOS_AGENTE}
    try:
        cfg = protecciones.leer_ajustes_claude(raiz / protecciones.CLAUDE) if (raiz / protecciones.CLAUDE).is_file() else {}
        deny = set(cfg.get("permissions", {}).get("deny", []))
        faltan = [r for r in protecciones.reglas_deny(generar.instalados(raiz)) if r not in deny]
        fila["protecciones"] = "al día" if not faltan else f"faltan {len(faltan)} reglas (uxyngraphar reparar --proyectos)"
    except ValueError as e:
        fila["protecciones"] = str(e)
    fila["vocabulario_pendiente"] = vocabulario.pendientes(raiz)
    import memorias_repo
    fila["memorias_propuestas"] = memorias_repo.propuestas(raiz)
    return fila


def informe(red: bool = True) -> dict:
    home = casa.carpeta()
    activa = herramienta.ar.version_activa(str(home))
    datos: dict = {
        "uxyngraphar": {"version": herramienta.version(), "instalada": herramienta.instalada(), "activa": activa,
                        "guardadas": herramienta.ar.versiones_guardadas(str(home)), "carpeta": str(home)},
        "sistema": {"python": sys.version.split()[0], "ejecutable": sys.executable, "so": platform.platform()},
        "comando": {"lanzador": herramienta.lanzador(), "en_path": bool(shutil.which("uxyngraphar")),
                    "path_bin": herramienta.ar.en_path(herramienta.ar.carpeta_bin(str(home)))},
    }
    if red:
        datos["uxyngraphar"]["ultima"] = herramienta.ultima()
    import panel
    estado_panel = casa.leer_json(panel.ESTADO, None)
    datos["panel"] = ("abierto" if panel.panel_abierto() else "panel.json huérfano (uxyngraphar reparar)") if estado_panel else "cerrado"
    versiones = fuentes.versiones()
    datos["proyectos"] = []
    for ruta in proyectos.listar():
        try:
            datos["proyectos"].append(_proyecto(ruta, versiones))
        except Exception as e:  # noqa: BLE001 - un proyecto ilegible no impide el informe de los demás
            datos["proyectos"].append({"ruta": ruta, "nombre": Path(ruta).name, "error": f"{type(e).__name__}: {e}"})
    return datos


def anonimizar(datos: dict) -> dict:
    """Quita la carpeta personal y las rutas completas de los proyectos (se queda el nombre de cada uno)."""
    texto = json.dumps(datos, ensure_ascii=False)
    for p in datos.get("proyectos", []):
        texto = texto.replace(json.dumps(p["ruta"], ensure_ascii=False)[1:-1], f"<proyecto {p['nombre']}>")
    carpeta = datos.get("uxyngraphar", {}).get("carpeta", "")
    if carpeta and not carpeta.startswith(str(Path.home())):
        texto = texto.replace(json.dumps(carpeta, ensure_ascii=False)[1:-1], "<carpeta de uxyngraphar>")
    for casa_usuario in {str(Path.home()), str(Path.home().resolve()), os.path.expanduser("~")}:
        texto = texto.replace(json.dumps(casa_usuario, ensure_ascii=False)[1:-1], "~")
    return json.loads(texto)


def texto(datos: dict) -> str:
    u, s = datos["uxyngraphar"], datos["sistema"]
    lineas = [f"uxyngraphar {u['version']} ({'instalada' if u['instalada'] else 'copia del repositorio'}); activa: {u['activa'] or '—'}; "
              f"guardadas: {', '.join(u['guardadas']) or '—'}",
              f"carpeta: {u['carpeta']}"]
    if "ultima" in u:
        ultima = u["ultima"]
        lineas.append(f"última publicada: {ultima.get('ultima') or '?'}" + (" (hay una nueva)" if ultima.get("hay_nueva") else "")
                      + (f" — sin red: {ultima['error']}" if ultima.get("error") else ""))
    lineas += [f"Python {s['python']} ({s['ejecutable']}) en {s['so']}",
               f"comando: {datos['comando']['lanzador'] or '—'}; en el PATH: {'sí' if datos['comando']['en_path'] else 'no'}",
               f"panel: {datos['panel']}", "", "Proyectos:"]
    for p in datos["proyectos"]:
        if p.get("error") or not p.get("existe"):
            lineas.append(f"  {p['nombre']}: {p.get('error') or 'la carpeta ya no existe'}")
            continue
        if p["tipo"] != "actual":
            lineas.append(f"  {p['nombre']}: sin uxyngraphar")
            continue
        partes = [f"{p['sistemas']} sistemas"]
        partes += [f"alterados: {', '.join(p['alterados'])}"] if p["alterados"] else []
        partes += [f"actualizables: {', '.join(p['actualizables'])}"] if p["actualizables"] else []
        partes += ["cambio interrumpido (reparar)"] if p["interrumpida"] else []
        partes += [f"FLUJO.json: {p['flujo'] if isinstance(p['flujo'], str) else '; '.join(p['flujo'])}"]
        faltan = [n for n, ok in p["archivos_agente"].items() if not ok]
        partes += [f"sin bloque en {', '.join(faltan)}"] if faltan else []
        partes += [f"protecciones: {p['protecciones']}"]
        partes += [f"{p['vocabulario_pendiente']} fichas con status heredados"] if p["vocabulario_pendiente"] else []
        partes += [f"{p['memorias_propuestas']} memorias propuestas por aprobar"] if p.get("memorias_propuestas") else []
        lineas.append(f"  {p['nombre']}: " + "; ".join(partes))
    return "\n".join(lineas) + "\n"


def avisos(red: bool = True) -> list[dict]:
    """Lo que pide atención, para la portada del panel: {tipo, mensaje, accion, ruta}."""
    datos = informe(red)
    salida = []
    ultima = datos["uxyngraphar"].get("ultima") or {}
    if ultima.get("hay_nueva"):
        salida.append({"tipo": "version", "mensaje": f"Hay una versión nueva de uxyngraphar: {ultima['ultima']}.",
                       "accion": "actualizar", "ruta": ""})
    for p in datos["proyectos"]:
        if p.get("tipo") != "actual":
            continue
        if p["interrumpida"]:
            salida.append({"tipo": "interrumpida", "mensaje": f"{p['nombre']}: un cambio quedó a medias.", "accion": "reparar", "ruta": p["ruta"]})
        if p["actualizables"]:
            salida.append({"tipo": "actualizable", "mensaje": f"{p['nombre']}: {len(p['actualizables'])} sistema(s) con versión nueva.",
                           "accion": "abrir", "ruta": p["ruta"]})
        if isinstance(p["flujo"], list):
            salida.append({"tipo": "flujo", "mensaje": f"{p['nombre']}: FLUJO.json no es válido.", "accion": "reparar", "ruta": p["ruta"]})
        if p["vocabulario_pendiente"]:
            salida.append({"tipo": "vocabulario", "mensaje": f"{p['nombre']}: {p['vocabulario_pendiente']} ficha(s) con status antiguos.",
                           "accion": "abrir", "ruta": p["ruta"]})
        if p.get("memorias_propuestas"):
            salida.append({"tipo": "memorias", "mensaje": f"{p['nombre']}: {p['memorias_propuestas']} memoria(s) propuesta(s) por el agente esperan tu decisión.",
                           "accion": "abrir", "ruta": p["ruta"]})
    return salida
