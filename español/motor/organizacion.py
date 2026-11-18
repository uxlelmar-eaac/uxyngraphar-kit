"""Organización de «Mis proyectos» en el panel: carpetas, etiquetas y el orden que la persona elige arrastrando.

Solo ordena la lista del panel; no toca las carpetas de los proyectos ni sus sistemas. Es distinto de los grupos
(`grupos.py`): un grupo junta repos para actualizarlos y verificarlos a la vez; una carpeta o una etiqueta solo sirven
para encontrarlos. Se guarda en `organizacion.json` de la carpeta de uxyngraphar, aparte de `proyectos.json`, así que
una versión anterior del kit sigue leyendo su lista sin perder nada."""

from __future__ import annotations

import secrets

import casa
import proyectos

ARCHIVO = "organizacion.json"
COLORES = ("oro", "naranja", "verde", "rojo", "arena", "gris")
MAX_NOMBRE = 40


def _vacia() -> dict:
    return {"formato": 1, "carpetas": [], "etiquetas": [], "proyectos": {}, "orden": []}


def _texto(valor, que: str) -> str:
    nombre = " ".join(str(valor or "").split())
    if not nombre:
        raise ValueError(f"falta el nombre de la {que}")
    if len(nombre) > MAX_NOMBRE:
        raise ValueError(f"el nombre de la {que} es demasiado largo (máximo {MAX_NOMBRE} caracteres)")
    return nombre


def _color(valor, defecto: str = "oro") -> str:
    color = str(valor or defecto)
    if color not in COLORES:
        raise ValueError(f"color desconocido «{color}»: {', '.join(COLORES)}")
    return color


def leer() -> dict:
    """La organización guardada, limpia: sin carpetas ni etiquetas repetidas y sin referencias a lo que ya no existe."""
    datos = casa.leer_json(ARCHIVO, {})
    if not isinstance(datos, dict):
        datos = {}
    org = _vacia()
    vistos: set[str] = set()
    for c in datos.get("carpetas") or []:
        if isinstance(c, dict) and isinstance(c.get("id"), str) and c["id"] not in vistos and str(c.get("nombre") or "").strip():
            vistos.add(c["id"])
            org["carpetas"].append({"id": c["id"], "nombre": str(c["nombre"]).strip()[:MAX_NOMBRE],
                                    "color": c.get("color") if c.get("color") in COLORES else "oro"})
    nombres: set[str] = set()
    for e in datos.get("etiquetas") or []:
        nombre = str(e.get("nombre") or "").strip() if isinstance(e, dict) else ""
        if nombre and nombre.lower() not in nombres:
            nombres.add(nombre.lower())
            org["etiquetas"].append({"nombre": nombre[:MAX_NOMBRE], "color": e.get("color") if e.get("color") in COLORES else "gris"})
    etiquetas = {e["nombre"] for e in org["etiquetas"]}
    for ruta, p in (datos.get("proyectos") or {}).items():
        if not isinstance(p, dict):
            continue
        carpeta = p.get("carpeta") if p.get("carpeta") in vistos else None
        suyas = [t for t in dict.fromkeys(p.get("etiquetas") or []) if t in etiquetas]
        if carpeta or suyas:
            org["proyectos"][str(ruta)] = {"carpeta": carpeta, "etiquetas": suyas}
    org["orden"] = [str(r) for r in dict.fromkeys(datos.get("orden") or []) if isinstance(r, str)]
    return org


def _guardar(org: dict) -> dict:
    registrados = set(proyectos.listar())
    org["proyectos"] = {r: p for r, p in org["proyectos"].items() if r in registrados and (p.get("carpeta") or p.get("etiquetas"))}
    org["orden"] = [r for r in org["orden"] if r in registrados]
    casa.escribir_json(ARCHIVO, org)
    return org


def _ruta(ruta) -> str:
    """La ruta tal como está en «Mis proyectos» (la organización usa esa misma escritura como clave)."""
    registrados = proyectos.listar()
    texto = str(ruta or "")
    if texto in registrados:
        return texto
    for r in registrados:
        if texto and proyectos.misma_carpeta(r, texto):
            return r
    raise ValueError(f"{texto or 'esa carpeta'} no está en «Mis proyectos»")


def _proyecto(org: dict, ruta: str) -> dict:
    return org["proyectos"].setdefault(ruta, {"carpeta": None, "etiquetas": []})


def _buscar_carpeta(org: dict, cid) -> dict:
    for c in org["carpetas"]:
        if c["id"] == cid:
            return c
    raise FileNotFoundError("esa carpeta ya no existe; recarga la página")


def _buscar_etiqueta(org: dict, nombre) -> dict:
    for e in org["etiquetas"]:
        if e["nombre"].lower() == str(nombre or "").strip().lower():
            return e
    raise FileNotFoundError(f"no existe la etiqueta «{nombre}»")


# Carpetas ----------------------------------------------------------------------------------------------------------

def crear_carpeta(nombre, color=None) -> dict:
    org = leer()
    nombre = _texto(nombre, "carpeta")
    if any(c["nombre"].lower() == nombre.lower() for c in org["carpetas"]):
        raise FileExistsError(f"ya tienes una carpeta «{nombre}»")
    org["carpetas"].append({"id": "c-" + secrets.token_hex(4), "nombre": nombre, "color": _color(color)})
    return _guardar(org)


def cambiar_carpeta(cid, nombre=None, color=None) -> dict:
    org = leer()
    carpeta = _buscar_carpeta(org, cid)
    if nombre is not None:
        nombre = _texto(nombre, "carpeta")
        if any(c["nombre"].lower() == nombre.lower() and c["id"] != cid for c in org["carpetas"]):
            raise FileExistsError(f"ya tienes una carpeta «{nombre}»")
        carpeta["nombre"] = nombre
    if color is not None:
        carpeta["color"] = _color(color)
    return _guardar(org)


def borrar_carpeta(cid) -> dict:
    """Borra la carpeta; sus proyectos pasan a «Sin carpeta» (siguen en la lista)."""
    org = leer()
    _buscar_carpeta(org, cid)
    org["carpetas"] = [c for c in org["carpetas"] if c["id"] != cid]
    for p in org["proyectos"].values():
        if p.get("carpeta") == cid:
            p["carpeta"] = None
    return _guardar(org)


def ordenar_carpetas(ids: list) -> dict:
    org = leer()
    posicion = {cid: i for i, cid in enumerate(ids)}
    org["carpetas"].sort(key=lambda c: posicion.get(c["id"], len(posicion)))
    return _guardar(org)


# Proyectos: mover y ordenar -----------------------------------------------------------------------------------------

def mover(rutas: list, carpeta=None, antes=None) -> dict:
    """Mete los proyectos en `carpeta` (None: «Sin carpeta») y, si se da `antes`, los coloca justo delante de ese
    proyecto en el orden manual; si no, al final de la carpeta."""
    org = leer()
    if carpeta:
        _buscar_carpeta(org, carpeta)
    limpias = list(dict.fromkeys(_ruta(r) for r in rutas))
    if not limpias:
        raise ValueError("no hay proyectos que mover")
    for r in limpias:
        _proyecto(org, r)["carpeta"] = carpeta or None
    registrados = proyectos.listar()
    orden = org["orden"] + [r for r in registrados if r not in org["orden"]]   # los que nunca se movieron, en su orden
    orden = [r for r in orden if r not in limpias]
    destino = _ruta(antes) if antes else None
    if destino and destino in orden:
        i = orden.index(destino)
    else:   # detrás del último de esa carpeta
        de_la_carpeta = [i for i, r in enumerate(orden) if (org["proyectos"].get(r) or {}).get("carpeta") == (carpeta or None)]
        i = de_la_carpeta[-1] + 1 if de_la_carpeta else len(orden)
    org["orden"] = orden[:i] + limpias + orden[i:]
    return _guardar(org)


# Etiquetas ---------------------------------------------------------------------------------------------------------

def crear_etiqueta(nombre, color=None) -> dict:
    org = leer()
    nombre = _texto(nombre, "etiqueta")
    if any(e["nombre"].lower() == nombre.lower() for e in org["etiquetas"]):
        raise FileExistsError(f"ya tienes una etiqueta «{nombre}»")
    org["etiquetas"].append({"nombre": nombre, "color": _color(color, COLORES[len(org["etiquetas"]) % len(COLORES)])})
    return _guardar(org)


def cambiar_etiqueta(nombre, nuevo=None, color=None) -> dict:
    org = leer()
    etiqueta = _buscar_etiqueta(org, nombre)
    if nuevo is not None:
        nuevo = _texto(nuevo, "etiqueta")
        if any(e["nombre"].lower() == nuevo.lower() and e is not etiqueta for e in org["etiquetas"]):
            raise FileExistsError(f"ya tienes una etiqueta «{nuevo}»")
        viejo, etiqueta["nombre"] = etiqueta["nombre"], nuevo
        for p in org["proyectos"].values():
            p["etiquetas"] = [nuevo if t == viejo else t for t in p.get("etiquetas", [])]
    if color is not None:
        etiqueta["color"] = _color(color)
    return _guardar(org)


def borrar_etiqueta(nombre) -> dict:
    org = leer()
    viejo = _buscar_etiqueta(org, nombre)["nombre"]
    org["etiquetas"] = [e for e in org["etiquetas"] if e["nombre"] != viejo]
    for p in org["proyectos"].values():
        p["etiquetas"] = [t for t in p.get("etiquetas", []) if t != viejo]
    return _guardar(org)


def etiquetar(rutas: list, nombre, poner: bool = True) -> dict:
    """Pone (o quita) una etiqueta a varios proyectos. Si la etiqueta no existe y se pone, se crea."""
    org = leer()
    try:
        nombre = _buscar_etiqueta(org, nombre)["nombre"]
    except FileNotFoundError:
        if not poner:
            raise
        org = crear_etiqueta(nombre)
        nombre = org["etiquetas"][-1]["nombre"]
    for r in dict.fromkeys(_ruta(r) for r in rutas):
        p = _proyecto(org, r)
        p["etiquetas"] = [t for t in p["etiquetas"] if t != nombre] + ([nombre] if poner else [])
    return _guardar(org)


def poner_etiquetas(ruta, nombres: list) -> dict:
    """Deja en el proyecto exactamente estas etiquetas (las que no existan se crean)."""
    org = leer()
    existentes = {e["nombre"].lower(): e["nombre"] for e in org["etiquetas"]}
    for n in nombres:
        if str(n).strip().lower() not in existentes:
            org = crear_etiqueta(n)
            existentes = {e["nombre"].lower(): e["nombre"] for e in org["etiquetas"]}
    _proyecto(org, _ruta(ruta))["etiquetas"] = list(dict.fromkeys(existentes[str(n).strip().lower()] for n in nombres))
    return _guardar(org)


def olvidar(ruta: str) -> None:
    """Al quitar un proyecto de la lista, su carpeta y etiquetas se olvidan con él."""
    org = leer()
    org["proyectos"] = {r: p for r, p in org["proyectos"].items() if not proyectos.misma_carpeta(r, ruta)}
    org["orden"] = [r for r in org["orden"] if not proyectos.misma_carpeta(r, ruta)]
    casa.escribir_json(ARCHIVO, org)
