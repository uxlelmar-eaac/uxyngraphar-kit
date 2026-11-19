"""«Mis sistemas»: organizar y gestionar los sistemas que escribe la persona (el catálogo local).

Organizar: carpetas (anidadas) y orden manual. Es solo una vista: se guarda en `.organizacion.json` dentro de la
carpeta del catálogo y no mueve ni cambia las carpetas de los sistemas, así que la CLI, el Taller y una versión
anterior del kit los siguen encontrando igual. Lo que falta en ese archivo se ve en la raíz y lo que ya no existe
se olvida solo.

Gestionar: eliminar (a la papelera de `<carpeta de uxyngraphar>/papelera/`, recuperable), restaurar, vaciar,
duplicar y cambiar el nombre. Nada de esto toca el servidor: un borrador web o una versión publicada siguen allí.
"""

from __future__ import annotations

import json
import os
import re
import secrets
import shutil
import tempfile
import time
from pathlib import Path

import casa
import catalogo
import entrada
import nomenclatura

base = catalogo.base
ARCHIVO = ".organizacion.json"
PAPELERA = "papelera"
META = "papelera.json"
MAX_NOMBRE = 40
TEXTOS = {".md", ".json", ".py", ".txt", ".yml", ".yaml", ".toml", ".csv"}
ENTRADA_VALIDA = re.compile(r"^\d{8}-\d{6}-[a-z]+(?:-[a-z]+)*(?:-\d+)?$")


# Organización ------------------------------------------------------------------------------------------------------

def _archivo(raiz: Path | None) -> Path:
    return catalogo.catalogo(raiz) / ARCHIVO


def _vacia() -> dict:
    return {"formato": 1, "carpetas": [], "sistemas": {}, "orden": []}


def _escribir(raiz: Path | None, org: dict) -> None:
    ruta = _archivo(raiz)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".organizacion-", suffix=".tmp", dir=ruta.parent)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(org, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, ruta)


def _limpia(datos, ids: list[str]) -> dict:
    """Organización sin carpetas repetidas ni ciclos y sin sistemas que ya no están en el catálogo."""
    org = _vacia()
    if not isinstance(datos, dict):
        datos = {}
    vistos: set[str] = set()
    crudas = [c for c in datos.get("carpetas") or [] if isinstance(c, dict)]
    for c in crudas:
        cid, nombre = c.get("id"), " ".join(str(c.get("nombre") or "").split())[:MAX_NOMBRE]
        if isinstance(cid, str) and cid not in vistos and nombre:
            vistos.add(cid)
            org["carpetas"].append({"id": cid, "nombre": nombre, "padre": c.get("padre") if isinstance(c.get("padre"), str) else None})
    padres = {c["id"]: c["padre"] for c in org["carpetas"]}
    for c in org["carpetas"]:
        if c["padre"] not in padres:
            c["padre"] = None
            continue
        # un ciclo (a dentro de b dentro de a) se rompe subiendo la carpeta a la raíz
        actual, recorridas = c["padre"], {c["id"]}
        while actual is not None:
            if actual in recorridas:
                c["padre"] = None
                break
            recorridas.add(actual)
            actual = padres.get(actual)
        padres[c["id"]] = c["padre"]
    existentes = set(ids)
    for pid, s in (datos.get("sistemas") or {}).items():
        if pid in existentes and isinstance(s, dict) and s.get("carpeta") in vistos:
            org["sistemas"][pid] = {"carpeta": s["carpeta"]}
    org["orden"] = [p for p in dict.fromkeys(datos.get("orden") or []) if isinstance(p, str) and p in existentes]
    return org


def _ids(raiz: Path | None) -> list[str]:
    return list(catalogo._sistemas(raiz))  # noqa: SLF001


def leer(raiz: Path | None = None) -> dict:
    """La organización guardada y limpia (si había entradas viejas, se guarda ya sin ellas)."""
    ruta = _archivo(raiz)
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        datos = {}
    org = _limpia(datos, _ids(raiz))
    if ruta.is_file() and datos != org:
        _escribir(raiz, org)
    return org


def _guardar(raiz: Path | None, org: dict) -> dict:
    org = _limpia(org, _ids(raiz))
    _escribir(raiz, org)
    return org


def vista(raiz: Path | None = None) -> dict:
    """Carpetas, orden y sistemas (con su carpeta y si validan) para la sección «Mis sistemas»."""
    org = leer(raiz)
    posicion = {pid: i for i, pid in enumerate(org["orden"])}
    sistemas = []
    for m in catalogo.listar(raiz):
        sistemas.append({"id": m["id"], "titulo": m.get("titulo") or m["id"], "descripcion": m.get("descripcion", ""),
                         "familia": m.get("familia", ""), "version": m.get("version", ""),
                         "errores": m.get("errores", []), "avisos": m.get("avisos", []),
                         "carpeta": (org["sistemas"].get(m["id"]) or {}).get("carpeta")})
    sistemas.sort(key=lambda s: (posicion.get(s["id"], len(posicion)), s["titulo"].lower()))
    return {"carpetas": org["carpetas"], "orden": [s["id"] for s in sistemas], "sistemas": sistemas,
            "catalogo": str(catalogo.catalogo(raiz)), "papelera": len(papelera())}


def _carpeta(org: dict, cid) -> dict:
    for c in org["carpetas"]:
        if c["id"] == cid:
            return c
    raise FileNotFoundError("esa carpeta ya no existe; recarga la página")


def _nombre(valor) -> str:
    nombre = " ".join(str(valor or "").split())
    if not nombre:
        raise ValueError("falta el nombre de la carpeta")
    if len(nombre) > MAX_NOMBRE:
        raise ValueError(f"el nombre de la carpeta es demasiado largo (máximo {MAX_NOMBRE} caracteres)")
    return nombre


def _hermana_repetida(org: dict, nombre: str, padre, salvo=None) -> None:
    if any(c["nombre"].lower() == nombre.lower() and c["padre"] == padre and c["id"] != salvo for c in org["carpetas"]):
        raise FileExistsError(f"ya hay una carpeta «{nombre}» ahí")


def _descendientes(org: dict, cid: str) -> set[str]:
    salida, pendientes = set(), [cid]
    while pendientes:
        actual = pendientes.pop()
        for c in org["carpetas"]:
            if c["padre"] == actual and c["id"] not in salida:
                salida.add(c["id"])
                pendientes.append(c["id"])
    return salida


def crear_carpeta(nombre, padre=None, raiz: Path | None = None) -> dict:
    org = leer(raiz)
    nombre = _nombre(nombre)
    if padre:
        _carpeta(org, padre)
    _hermana_repetida(org, nombre, padre or None)
    org["carpetas"].append({"id": "c-" + secrets.token_hex(4), "nombre": nombre, "padre": padre or None})
    return _guardar(raiz, org)


def renombrar_carpeta(cid, nombre, raiz: Path | None = None) -> dict:
    org = leer(raiz)
    c = _carpeta(org, cid)
    nombre = _nombre(nombre)
    _hermana_repetida(org, nombre, c["padre"], salvo=cid)
    c["nombre"] = nombre
    return _guardar(raiz, org)


def mover_carpeta(cid, padre=None, antes=None, raiz: Path | None = None) -> dict:
    """Mete la carpeta dentro de `padre` (None: la raíz) y, con `antes`, la coloca delante de esa carpeta hermana."""
    org = leer(raiz)
    c = _carpeta(org, cid)
    if padre:
        _carpeta(org, padre)
        if padre == cid or padre in _descendientes(org, cid):
            raise ValueError("una carpeta no puede ir dentro de sí misma")
    _hermana_repetida(org, c["nombre"], padre or None, salvo=cid)
    c["padre"] = padre or None
    resto = [x for x in org["carpetas"] if x["id"] != cid]
    i = next((n for n, x in enumerate(resto) if x["id"] == antes), len(resto)) if antes else len(resto)
    org["carpetas"] = resto[:i] + [c] + resto[i:]
    return _guardar(raiz, org)


def contenido_carpeta(cid, raiz: Path | None = None) -> dict:
    """Subcarpetas y sistemas que hay dentro (a cualquier profundidad)."""
    org = leer(raiz)
    _carpeta(org, cid)
    todas = {cid} | _descendientes(org, cid)
    return {"carpetas": len(todas) - 1, "sistemas": sorted(p for p, s in org["sistemas"].items() if s["carpeta"] in todas)}


def borrar_carpeta(cid, confirmar: bool = False, raiz: Path | None = None) -> dict:
    """Borra la carpeta y sus subcarpetas; sus sistemas pasan a la raíz. Si tiene algo dentro, pide `confirmar`.
    No borra ningún sistema."""
    dentro = contenido_carpeta(cid, raiz)
    if (dentro["sistemas"] or dentro["carpetas"]) and not confirmar:
        raise ValueError(f"la carpeta tiene {len(dentro['sistemas'])} sistema(s) y {dentro['carpetas']} subcarpeta(s): "
                         "confírmalo (los sistemas pasan a la raíz; no se borra ninguno)")
    org = leer(raiz)
    todas = {cid} | _descendientes(org, cid)
    org["carpetas"] = [c for c in org["carpetas"] if c["id"] not in todas]
    for pid in [p for p, s in org["sistemas"].items() if s["carpeta"] in todas]:
        del org["sistemas"][pid]
    return _guardar(raiz, org)


def mover(ids: list, carpeta=None, antes=None, raiz: Path | None = None) -> dict:
    """Mete los sistemas en `carpeta` (None: la raíz) y, con `antes`, los coloca delante de ese sistema; si no, al final
    de la carpeta."""
    org = leer(raiz)
    existentes = _ids(raiz)
    if carpeta:
        _carpeta(org, carpeta)
    limpios = list(dict.fromkeys(str(i) for i in ids))
    if not limpios:
        raise ValueError("no hay sistemas que mover")
    for pid in limpios:
        if pid not in existentes:
            raise FileNotFoundError(f"el catálogo no tiene el sistema «{pid}»")
        if carpeta:
            org["sistemas"][pid] = {"carpeta": carpeta}
        else:
            org["sistemas"].pop(pid, None)
    orden = org["orden"] + sorted(p for p in existentes if p not in org["orden"])
    orden = [p for p in orden if p not in limpios]
    if antes and antes in orden:
        i = orden.index(antes)
    else:
        dela = [n for n, p in enumerate(orden) if (org["sistemas"].get(p) or {}).get("carpeta") == (carpeta or None)]
        i = dela[-1] + 1 if dela else len(orden)
    org["orden"] = orden[:i] + limpios + orden[i:]
    return _guardar(raiz, org)


def arbol(raiz: Path | None = None) -> list[str]:
    """Líneas de texto con las carpetas y sus sistemas (para la CLI)."""
    v = vista(raiz)
    lineas: list[str] = []

    def pintar(padre, nivel: int) -> None:
        for c in [c for c in v["carpetas"] if c["padre"] == padre]:
            lineas.append(f"{'  ' * nivel}{c['nombre']}/")
            pintar(c["id"], nivel + 1)
        for s in [s for s in v["sistemas"] if s["carpeta"] == padre]:
            estado = "valida" if not s["errores"] else f"{len(s['errores'])} error(es)"
            lineas.append(f"{'  ' * nivel}- {s['id']}  {s['version']}  {s['titulo']}  ({estado})")

    pintar(None, 0)
    return lineas


# Papelera ----------------------------------------------------------------------------------------------------------

def carpeta_papelera() -> Path:
    return casa.carpeta() / PAPELERA


def instalado_en(pid: str) -> list[str]:
    """Proyectos registrados en el panel que tienen instalado este sistema."""
    import proyectos
    try:
        return [p.get("nombre") or p.get("ruta", "") for p in proyectos.resumenes()
                if p.get("existe") and pid in (p.get("sistemas") or [])]
    except Exception:  # noqa: BLE001 - un proyecto ilegible no impide eliminar
        return []


def avisos_eliminar(pid: str, raiz: Path | None = None) -> dict:
    """Lo que conviene saber antes de eliminar: dónde está instalado. Los borradores web y lo publicado los añade la web
    (con la sesión); en ningún caso se tocan."""
    catalogo.carpeta(pid, raiz)
    return {"id": pid, "proyectos": instalado_en(pid)}


def eliminar(ids: list, raiz: Path | None = None) -> list[dict]:
    """Mueve los sistemas a la papelera (recuperables con `restaurar`). No toca proyectos ni el servidor."""
    org = leer(raiz)
    limpios = list(dict.fromkeys(str(i) for i in ids))
    if not limpios:
        raise ValueError("no hay sistemas que eliminar")
    origenes = [(pid, catalogo.carpeta(pid, raiz)) for pid in limpios]   # todos existen antes de mover ninguno
    nombres = {c["id"]: c["nombre"] for c in org["carpetas"]}
    hechos = []
    for pid, origen in origenes:
        m = base.leer_manifiesto(origen)
        sello = time.strftime("%Y%m%d-%H%M%S")
        nombre, n = f"{sello}-{pid}", 1
        while (carpeta_papelera() / nombre).exists():
            n += 1
            nombre = f"{sello}-{pid}-{n}"
        destino = carpeta_papelera() / nombre
        destino.mkdir(parents=True)
        carpeta = (org["sistemas"].get(pid) or {}).get("carpeta")
        vecinos = [p for p in org["orden"] if (org["sistemas"].get(p) or {}).get("carpeta") == carpeta]
        siguiente = vecinos[vecinos.index(pid) + 1] if pid in vecinos and vecinos.index(pid) + 1 < len(vecinos) else None
        meta = {"formato": 1, "id": pid, "titulo": m.get("titulo", pid), "version": m.get("version", ""),
                "familia": m.get("familia", ""), "eliminado": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "catalogo": str(catalogo.catalogo(raiz)), "carpeta": carpeta, "nombre_carpeta": nombres.get(carpeta), "siguiente": siguiente}
        try:
            shutil.move(str(origen), str(destino / pid))
        except BaseException:
            shutil.rmtree(destino, ignore_errors=True)
            raise
        (destino / META).write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        hechos.append({"entrada": nombre, "id": pid, "titulo": meta["titulo"]})
    _guardar(raiz, org)
    return hechos


def _entrada(nombre) -> Path:
    nombre = str(nombre or "")
    if not ENTRADA_VALIDA.match(nombre):
        raise ValueError(f"no hay nada en la papelera con el nombre «{nombre}»")
    ruta = carpeta_papelera() / nombre
    if not (ruta / META).is_file():
        raise FileNotFoundError(f"no hay nada en la papelera con el nombre «{nombre}»")
    return ruta


def papelera(raiz: Path | None = None) -> list[dict]:
    """Lo que hay en la papelera, lo más reciente primero (con «choca» si ya hay un sistema con ese id)."""
    c = carpeta_papelera()
    existentes = set(_ids(raiz)) if catalogo.catalogo(raiz).is_dir() else set()
    salida = []
    for d in sorted(c.iterdir(), reverse=True) if c.is_dir() else []:
        try:
            meta = json.loads((d / META).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(meta, dict) and (d / str(meta.get("id"))).is_dir():
            salida.append({**meta, "entrada": d.name, "choca": meta.get("id") in existentes})
    return salida


def resolver_entrada(valor: str, raiz: Path | None = None) -> str:
    """El nombre de la entrada de la papelera: el dado o, si es un id, su entrada más reciente."""
    if ENTRADA_VALIDA.match(str(valor or "")) and (carpeta_papelera() / str(valor) / META).is_file():
        return str(valor)
    for e in papelera(raiz):
        if e["id"] == valor:
            return e["entrada"]
    raise FileNotFoundError(f"no hay nada en la papelera con el nombre o id «{valor}» (uxyngraphar papelera)")


def restaurar(nombre, raiz: Path | None = None) -> dict:
    """Devuelve el sistema al catálogo (y a su carpeta si aún existe)."""
    d = _entrada(nombre)
    meta = json.loads((d / META).read_text(encoding="utf-8"))
    pid = str(meta["id"])
    destino = catalogo.catalogo(raiz) / pid
    if destino.exists():
        raise FileExistsError(f"ya hay un sistema «{pid}» en el catálogo: cámbiale el nombre o elimínalo antes de restaurar este")
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(d / pid), str(destino))
    shutil.rmtree(d, ignore_errors=True)
    org = leer(raiz)
    carpeta = meta.get("carpeta") if any(c["id"] == meta.get("carpeta") for c in org["carpetas"]) else None
    siguiente = meta.get("siguiente")
    if siguiente not in org["orden"] or (org["sistemas"].get(siguiente) or {}).get("carpeta") != carpeta:
        siguiente = None
    if carpeta or siguiente:
        mover([pid], carpeta, antes=siguiente, raiz=raiz)   # vuelve a su carpeta y a su sitio
    return {"id": pid, "titulo": meta.get("titulo", pid), "carpeta": meta.get("nombre_carpeta") if carpeta else None}


def vaciar(nombre=None) -> int:
    """Borra para siempre una entrada de la papelera (o toda si no se da). Devuelve cuántas borró."""
    if nombre:
        shutil.rmtree(_entrada(nombre))
        return 1
    c = carpeta_papelera()
    entradas = [d for d in c.iterdir() if d.is_dir() and ENTRADA_VALIDA.match(d.name)] if c.is_dir() else []
    for d in entradas:
        shutil.rmtree(d)
    return len(entradas)


# Duplicar y cambiar el nombre ----------------------------------------------------------------------------------------

def _reemplazar_textos(c: Path, cambios: list[tuple[str, str]]) -> None:
    for f in sorted(c.rglob("*")):
        rel = f.relative_to(c).as_posix()
        if not f.is_file() or f.suffix.lower() not in TEXTOS or rel.startswith("scripts/comun/") or base.IGNORAR.search(rel):
            continue
        try:
            texto = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        nuevo = texto
        for viejo, otro in cambios:
            if viejo and viejo != otro:
                nuevo = nuevo.replace(viejo, otro)
        if nuevo != texto:
            f.write_text(nuevo, encoding="utf-8")


def _errores_nombres(raiz: Path | None) -> dict[str, list[str]]:
    return {pid: errores for pid, (errores, _) in nomenclatura.revisar_catalogo(catalogo._sistemas(raiz)).items()}  # noqa: SLF001


def _comprobar_nuevo(nuevo_id: str, titulo: str, raiz: Path | None, salvo: str | None = None) -> None:
    errores = nomenclatura.problemas_id(nuevo_id) + nomenclatura.problemas_titulo(nuevo_id, titulo)
    otros = [p for p in _ids(raiz) if p != salvo]
    if nuevo_id in otros or (catalogo.catalogo(raiz) / nuevo_id).exists():
        errores.append(f"ya hay un sistema «{nuevo_id}» en el catálogo")
    errores += [f"id «{nuevo_id}»: choca con «{o}» (uno es prefijo del otro)" for o in otros
                if o != nuevo_id and (o.startswith(nuevo_id + "-") or nuevo_id.startswith(o + "-"))]
    if errores:
        raise ValueError("; ".join(errores))


def _copiar(origen: Path, nuevo_id: str, titulo: str, raiz: Path | None, conservar_frases: bool) -> dict:
    """Copia el sistema de `origen` en el catálogo como `nuevo_id`: textos, manifiesto, prefijos y bloques al día.
    Si deja errores de nombres nuevos en el catálogo (frases o prefijos repetidos), deshace la copia y lo explica."""
    m = base.leer_manifiesto(origen)
    viejo_id, viejo_titulo = m["id"], m.get("titulo", "")
    antes = _errores_nombres(raiz)
    destino = catalogo.catalogo(raiz) / nuevo_id
    shutil.copytree(origen, destino, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", base.INTEGRIDAD))
    try:
        _reemplazar_textos(destino, [(viejo_titulo, titulo), (viejo_id, nuevo_id),
                                     (viejo_id.replace("-", " "), nuevo_id.replace("-", " "))])
        nm = base.leer_manifiesto(destino)
        cambiadas = [f for f in nm.get("activacion") or [] if f not in (m.get("activacion") or [])]
        conservadas = [f for f in nm.get("activacion") or [] if f in (m.get("activacion") or [])]
        propias = [nuevo_id, nuevo_id.replace("-", " ")]
        extra = cambiadas + (conservadas if conservar_frases else [])
        nm["activacion"] = list(dict.fromkeys(propias + [f for f in extra if f not in propias]))
        quitadas = [f for f in conservadas if f not in nm["activacion"]]
        nm["id"], nm["titulo"] = nuevo_id, titulo
        usados = {d.get("prefijo") for p, (_, mm) in catalogo._sistemas(raiz).items()  # noqa: SLF001
                  if p not in (nuevo_id, viejo_id if conservar_frases else None) for d in mm.get("fichas", {}).values()}
        if not conservar_frases:
            for d in nm.get("fichas", {}).values():
                d["prefijo"] = nomenclatura.proponer_prefijo(nuevo_id, usados)
                usados.add(d["prefijo"])
        catalogo._escribir_manifiesto(destino, nm)  # noqa: SLF001
        entrada.actualizar(destino)
        despues = _errores_nombres(raiz)
        nuevos = [f"{p}: {e}" for p, es in despues.items() for e in es if p != nuevo_id and e not in antes.get(p, [])]
        propios_antes = len(antes.get(viejo_id, []))
        if len(despues.get(nuevo_id, [])) > propios_antes:
            nuevos += [f"{nuevo_id}: {e}" for e in despues[nuevo_id]]
        if nuevos:
            raise ValueError("no se puede con ese nombre: " + "; ".join(nuevos))
    except BaseException:
        shutil.rmtree(destino, ignore_errors=True)
        raise
    return {"id": nuevo_id, "titulo": titulo, "frases_quitadas": quitadas,
            "prefijos": {t: d["prefijo"] for t, d in nm.get("fichas", {}).items()}}


def duplicar(pid: str, nuevo_id: str, titulo: str, raiz: Path | None = None) -> dict:
    """Copia el sistema con otro id y título (prefijos de fichas nuevos; las frases de activación propias que
    chocarían con el original se quitan). La copia queda en la misma carpeta, justo detrás del original."""
    origen = catalogo.carpeta(pid, raiz)
    nuevo_id, titulo = str(nuevo_id).strip(), " ".join(str(titulo).split())
    _comprobar_nuevo(nuevo_id, titulo, raiz)
    r = _copiar(origen, nuevo_id, titulo, raiz, conservar_frases=False)
    org = leer(raiz)
    carpeta = (org["sistemas"].get(pid) or {}).get("carpeta")
    orden = org["orden"] + sorted(p for p in _ids(raiz) if p not in org["orden"])
    siguiente = orden[orden.index(pid) + 1] if pid in orden and orden.index(pid) + 1 < len(orden) else None
    mover([nuevo_id], carpeta, antes=siguiente if siguiente != nuevo_id else None, raiz=raiz)
    return r


def renombrar(pid: str, titulo: str, nuevo_id: str | None = None, raiz: Path | None = None) -> dict:
    """Cambia el título y, si se da otro id, también el id.

    El título tiene que ser las palabras del id (NOMENCLATURA.md), así que con el mismo id solo cambian tildes y
    mayúsculas. Cambiar el id es seguro de esta forma: se crea el sistema con el id nuevo (mismos prefijos y frases) y
    el anterior va a la papelera, recuperable. Los proyectos que lo tienen instalado siguen con el id anterior hasta que
    instales el nuevo, y un borrador web o una versión publicada no cambian de nombre."""
    origen = catalogo.carpeta(pid, raiz)
    titulo = " ".join(str(titulo).split())
    nuevo_id = str(nuevo_id or pid).strip()
    m = base.leer_manifiesto(origen)
    if nuevo_id == pid:
        errores = nomenclatura.problemas_titulo(pid, titulo)
        if errores:
            raise ValueError("; ".join(errores) + ". El título sigue al id: para otro nombre, cambia también el id")
        _reemplazar_textos(origen, [(m.get("titulo", ""), titulo)])
        m = base.leer_manifiesto(origen)
        m["titulo"] = titulo
        catalogo._escribir_manifiesto(origen, m)  # noqa: SLF001
        entrada.actualizar(origen)
        return {"id": pid, "titulo": titulo, "anterior": None}
    _comprobar_nuevo(nuevo_id, titulo, raiz, salvo=pid)
    org = leer(raiz)
    carpeta = (org["sistemas"].get(pid) or {}).get("carpeta")
    siguiente = next((p for p in org["orden"][org["orden"].index(pid) + 1:]), None) if pid in org["orden"] else None
    (hecho,) = eliminar([pid], raiz)
    try:
        r = _copiar(carpeta_papelera() / hecho["entrada"] / pid, nuevo_id, titulo, raiz, conservar_frases=True)
    except BaseException:
        restaurar(hecho["entrada"], raiz)
        raise
    mover([nuevo_id], carpeta, antes=siguiente, raiz=raiz)
    return {**r, "anterior": {"id": pid, "entrada": hecho["entrada"]}}
