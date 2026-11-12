"""Cliente del servidor de sistemas de gobernanza (`/v1/sistemas`): índice, búsqueda, descarga y publicación.

Servidor: `UXYNGRAPHAR_SERVIDOR`, si no la clave «servidor» de `casa.json`, si no SERVIDOR_POR_DEFECTO.
`UXYNGRAPHAR_SIN_RED=1` lo apaga (las pruebas y los equipos sin red trabajan solo con el catálogo local).

Caché en la casa (`~/.uxyngraphar/sistemas-de-gobernanza/`):
  indice.json                                   último índice recibido (+ etag y hora), sirve sin red
  biblioteca.json                               tu biblioteca (lo adquirido y lo propio, ADR 0012), sirve sin red
  <editor>/<id>/<version>/<id>/                 sistemas traídos, ya construidos y en solo lectura
Solo la biblioteca estándar (ADR 0001): urllib, json, hashlib.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import artefacto
import casa
import especificacion as esp

base = esp.base

SERVIDOR_POR_DEFECTO = "https://api.uxyngraphar.com/v1"
CARPETA_CACHE = "sistemas-de-gobernanza"
ARCHIVO_INDICE = "indice.json"
ARCHIVO_BIBLIOTECA = "biblioteca.json"
ARCHIVO_SESION = "sesion.json"
VIGENCIA_INDICE = 600          # segundos antes de volver a preguntar por el índice
SEGUNDOS_RED = 15
SEGUNDOS_INDICE = 5            # el índice se consulta al listar proyectos: sin red no debe frenar
PAUSA_TRAS_FALLO = 60          # tras un fallo de red no se vuelve a intentar en este proceso durante este tiempo
_caido_hasta = 0.0
MARCA_COMPLETO = ".completo"
REFERENCIA = re.compile(r"^(?:(?P<editor>[a-z0-9]+(?:-[a-z0-9]+)*)/)?(?P<id>[a-z0-9]+(?:-[a-z0-9]+)*)(?:@(?P<version>\d+\.\d+\.\d+))?$")


class SinServidor(RuntimeError):
    """No hay servidor configurado o no responde (y no hay caché que sirva)."""


class NoEncontrado(LookupError):
    """El servidor no tiene ese sistema o esa versión."""


class DePago(PermissionError):
    """El sistema es de pago y esta cuenta no lo tiene (HTTP 402)."""


def servidor() -> str | None:
    if os.environ.get("UXYNGRAPHAR_SIN_RED"):
        return None
    ajustes = casa.leer_json(casa.ARCHIVO_FORMATO, {})
    url = os.environ.get("UXYNGRAPHAR_SERVIDOR") or (ajustes.get("servidor") if isinstance(ajustes, dict) else None)
    url = (url or SERVIDOR_POR_DEFECTO).rstrip("/")
    if not url.startswith(("https://", "http://127.0.0.1", "http://localhost")):
        raise SinServidor(f"servidor «{url}»: solo https (o http en 127.0.0.1/localhost para pruebas)")
    return url


def cache() -> Path:
    return casa.carpeta() / CARPETA_CACHE


def _pedir(ruta: str, datos: bytes | None = None, cabeceras: dict | None = None, metodo: str | None = None,
           segundos: float = SEGUNDOS_RED):
    global _caido_hasta
    url = servidor()
    if not url:
        raise SinServidor("sin red (UXYNGRAPHAR_SIN_RED)")
    if time.time() < _caido_hasta and datos is None:
        raise SinServidor(f"{url}: no respondió hace poco")
    pedido = urllib.request.Request(url + ruta, data=datos, method=metodo,  # noqa: S310 - servidor https configurado
                                    headers={"User-Agent": f"uxyngraphar/{esp.VERSION_MOTOR}", "Accept": "application/json",
                                             **(cabeceras or {})})
    try:
        return urllib.request.urlopen(pedido, timeout=segundos)  # noqa: S310 - servidor https configurado
    except urllib.error.HTTPError as e:
        if e.code == 304:
            return e
        detalle = ""
        try:
            cuerpo = json.loads(e.read().decode("utf-8"))
            detalle = cuerpo.get("message") or cuerpo.get("error") or ""
            detalle = "; ".join(detalle) if isinstance(detalle, list) else str(detalle)
        except (ValueError, AttributeError, OSError):
            pass
        if e.code == 404:
            raise NoEncontrado(detalle or f"no existe: {ruta}") from None
        if e.code == 402:
            raise DePago(detalle or "es de pago: cómpralo en el Mercado y vuelve a intentarlo") from None
        if e.code == 401:
            raise PermissionError(detalle or "sin sesión o caducada: uxyngraphar iniciar-sesion") from None
        raise SinServidor(f"{url}{ruta}: HTTP {e.code} {detalle}".strip()) from None
    except (urllib.error.URLError, OSError) as e:
        _caido_hasta = time.time() + PAUSA_TRAS_FALLO
        raise SinServidor(f"{url}: no responde ({getattr(e, 'reason', e)})") from None


def _json(ruta: str) -> dict:
    with _pedir(ruta) as r:
        return json.loads(r.read().decode("utf-8"))


# ── índice ────────────────────────────────────────────────────────────────────

def _indice_guardado() -> dict:
    try:
        return json.loads((cache() / ARCHIVO_INDICE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def indice(refrescar: bool = False) -> dict:
    """{"formato": 1, "sistemas": [{editor, id, titulo, descripcion, familia, etiquetas, problemas,
    versiones: [{version, sha256, tamano, motor, retirada}]}]}. Sin red usa el último guardado (o lanza SinServidor)."""
    guardado = _indice_guardado()
    fresco = guardado and time.time() - guardado.get("_recibido", 0) < VIGENCIA_INDICE
    if fresco and not refrescar and guardado.get("_servidor") == servidor():
        return guardado
    try:
        cabeceras = {"If-None-Match": guardado["_etag"]} if guardado.get("_etag") and guardado.get("_servidor") == servidor() else {}
        with _pedir("/sistemas/indice", cabeceras=cabeceras, segundos=SEGUNDOS_INDICE) as r:
            if getattr(r, "code", 200) == 304:
                datos = guardado
            else:
                datos = json.loads(r.read().decode("utf-8"))
                if not isinstance(datos, dict) or not isinstance(datos.get("sistemas"), list):
                    raise SinServidor("el servidor devolvió un índice inválido")
                datos["_etag"] = r.headers.get("ETag", "")
        datos.update(_recibido=time.time(), _servidor=servidor())
        cache().mkdir(parents=True, exist_ok=True)
        (cache() / ARCHIVO_INDICE).write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
        return datos
    except SinServidor:
        if guardado.get("sistemas") is not None:
            return guardado
        raise


def _compatibles(s: dict) -> list[dict]:
    vs = [v for v in s.get("versiones", []) if not v.get("retirada") and esp.motor_compatible(v.get("motor") or ">=0.0")]
    return sorted(vs, key=lambda v: esp.version_tupla(v["version"]), reverse=True)


def versiones_disponibles(refrescar: bool = False) -> dict[str, dict]:
    """Por id: la última versión compatible con este motor ({editor, version, sha256, …}). Si dos editores usan el
    mismo id, gana «uxyngraphar» (los demás se traen con editor/id)."""
    salida: dict[str, dict] = {}
    try:
        publicos = indice(refrescar).get("sistemas", [])
    except SinServidor:
        publicos = []
        if not _sistemas_biblioteca():
            raise
    for s in _con_biblioteca(publicos):
        vs = _compatibles(s)
        if not vs:
            continue
        actual = salida.get(s["id"])
        if actual and actual["editor"] == artefacto.EDITOR_POR_DEFECTO:
            continue
        if actual and s.get("editor") != artefacto.EDITOR_POR_DEFECTO:
            continue
        salida[s["id"]] = {**vs[0], "editor": s.get("editor", artefacto.EDITOR_POR_DEFECTO), "titulo": s.get("titulo", "")}
    return salida


def resolver(ref: str) -> dict:
    """`[editor/]id[@version]` → {editor, id, version, sha256, tamano, motor} según el índice."""
    m = REFERENCIA.match(ref.strip())
    if not m:
        raise ValueError(f"referencia «{ref}»: usa id, editor/id o editor/id@X.Y.Z")
    try:
        publicos = indice().get("sistemas", [])
    except SinServidor:
        publicos = []
        if not _sistemas_biblioteca():
            raise
    candidatos = [s for s in _con_biblioteca(publicos) if s.get("id") == m["id"]
                  and (not m["editor"] or s.get("editor") == m["editor"])]
    if not candidatos:
        raise NoEncontrado(f"el servidor no tiene «{ref}»")
    if len(candidatos) > 1:
        propios = [s for s in candidatos if s.get("editor") == artefacto.EDITOR_POR_DEFECTO]
        if not propios:
            raise ValueError(f"«{m['id']}» existe con varios editores ({', '.join(s['editor'] for s in candidatos)}): usa editor/id")
        candidatos = propios
    (s,) = candidatos
    if m["version"]:
        vs = [v for v in s.get("versiones", []) if v["version"] == m["version"]]
        if not vs:
            raise NoEncontrado(f"«{s['editor']}/{s['id']}» no tiene la versión {m['version']}")
        if not esp.motor_compatible(vs[0].get("motor") or ">=0.0"):
            raise ValueError(f"{s['id']}@{m['version']} requiere motor {vs[0]['motor']} (este es {esp.VERSION_MOTOR})")
    else:
        vs = _compatibles(s)
        if not vs:
            raise NoEncontrado(f"«{s['editor']}/{s['id']}» no tiene versiones para el motor {esp.VERSION_MOTOR}")
    return {"editor": s["editor"], "id": s["id"], **vs[0]}


def buscar(texto: str = "", familia: str = "") -> list[dict]:
    """Busca en el servidor; sin red, en el índice guardado (título, descripción, id, etiquetas y problemas)."""
    try:
        q = urllib.parse.urlencode({k: v for k, v in (("q", texto), ("familia", familia)) if v})
        datos = _json("/sistemas" + (f"?{q}" if q else ""))
        return datos.get("sistemas", datos.get("items", [])) if isinstance(datos, dict) else datos
    except SinServidor as fallo:
        try:
            guardados = indice().get("sistemas", [])
        except SinServidor:
            raise fallo from None
        palabras = [p for p in texto.lower().split() if p]
        salida = []
        for s in guardados:
            pajar = " ".join([s.get("id", ""), s.get("titulo", ""), s.get("descripcion", ""),
                              *s.get("etiquetas", []), *s.get("problemas", [])]).lower()
            if all(p in pajar for p in palabras) and (not familia or s.get("familia") == familia):
                salida.append(s)
        return salida


def ficha(ref: str) -> dict:
    r = resolver(ref)
    try:
        return {**_json(f"/sistemas/{r['editor']}/{r['id']}"), "resuelta": r}
    except SinServidor:
        return {**next(s for s in indice()["sistemas"] if s["id"] == r["id"] and s["editor"] == r["editor"]), "resuelta": r}


# ── traer ─────────────────────────────────────────────────────────────────────

def en_cache(editor: str, pid: str, version: str) -> Path | None:
    c = cache() / editor / pid / version
    return c / pid if (c / MARCA_COMPLETO).is_file() and (c / pid).is_dir() else None


def traer(ref: str) -> Path:
    """Descarga (si no está en la caché) la versión resuelta, comprueba su sha256, la valida y devuelve la carpeta
    construida `<cache>/<editor>/<id>/<version>/<id>/`."""
    r = resolver(ref)
    hecho = en_cache(r["editor"], r["id"], r["version"])
    if hecho and base.integro(base.comprobar_integridad(hecho)):
        return hecho
    destino = cache() / r["editor"] / r["id"] / r["version"]
    if destino.exists():
        import repo
        repo.borrar_arbol(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destino.parent, prefix=".descargando-") as tmp:
        zip_ = Path(tmp) / artefacto.nombre(r["id"], r["version"])
        with _pedir(f"/sistemas/{r['editor']}/{r['id']}/versiones/{r['version']}/descarga",
                    cabeceras={"Accept": "application/zip", **_autorizacion()}) as resp, open(zip_, "wb") as f:
            shutil.copyfileobj(resp, f)
        huella = artefacto.sha256_de(zip_)
        if r.get("sha256") and huella != r["sha256"]:
            raise artefacto.ArtefactoInvalido(f"{r['id']}@{r['version']}: sha256 distinto al del índice ({huella} ≠ {r['sha256']})")
        pid, m = artefacto.leer(zip_)
        if pid != r["id"] or m.get("version") != r["version"]:
            raise artefacto.ArtefactoInvalido(f"el artefacto trae {pid}@{m.get('version')} y se pidió {r['id']}@{r['version']}")
        carpeta = artefacto.desempaquetar(zip_, Path(tmp) / "x")
        final = Path(tmp) / "final"
        final.mkdir()
        carpeta.rename(final / pid)
        (final / MARCA_COMPLETO).write_text(json.dumps({"sha256": huella, "editor": r["editor"]}) + "\n", encoding="utf-8")
        final.rename(destino)
    import repo
    repo.solo_lectura(destino / r["id"])
    return destino / r["id"]


# ── biblioteca (lo adquirido y lo propio) ─────────────────────────────────────

def _biblioteca_guardada() -> dict:
    try:
        datos = json.loads((cache() / ARCHIVO_BIBLIOTECA).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(datos, dict) or not isinstance(datos.get("sistemas"), list):
        return {}
    try:
        actual = servidor()
    except SinServidor:
        actual = None
    # La biblioteca de otro servidor no vale para este.
    return datos if not actual or datos.get("_servidor") in (None, actual) else {}


def _sistemas_biblioteca() -> list[dict]:
    """Lo de la biblioteca guardada con forma de índice ({editor, id, titulo, versiones: [...]}), sin usar la red."""
    salida = []
    for b in _biblioteca_guardada().get("sistemas", []):
        if not isinstance(b, dict) or not REFERENCIA.match(f"{b.get('editor')}/{b.get('id')}"):
            continue
        versiones = [{"version": b["version"], "sha256": b.get("sha256") or "", "tamano": b.get("tamano") or 0,
                      "motor": b.get("motor") or ">=0.0", "retirada": False}] if b.get("version") else []
        salida.append({"editor": b["editor"], "id": b["id"], "titulo": b.get("titulo", ""), "versiones": versiones,
                       "origen": b.get("origen"), "de_pago": bool(b.get("de_pago")), "privado": bool(b.get("privado"))})
    return salida


def _con_biblioteca(publicos: list[dict]) -> list[dict]:
    """El índice público más lo de la biblioteca que no aparece en él (lo de pago y lo privado)."""
    vistos = {(s.get("editor"), s.get("id")) for s in publicos}
    return [*publicos, *(s for s in _sistemas_biblioteca() if (s["editor"], s["id"]) not in vistos)]


def biblioteca(refrescar: bool = True) -> dict:
    """Pide `/me/biblioteca` con la sesión (304 si no cambió). Sin red devuelve la guardada; sin sesión, lanza
    PermissionError. {"sistemas": [{editor, id, titulo, version, sha256, tamano, motor, origen, de_pago, privado}]}"""
    guardada = _biblioteca_guardada()
    if not refrescar and guardada:
        return guardada
    if not token():
        raise PermissionError("sin sesión: uxyngraphar iniciar-sesion")
    cabeceras = {**_autorizacion()}
    if guardada.get("_etag") and guardada.get("_servidor") == servidor():
        cabeceras["If-None-Match"] = guardada["_etag"]
    try:
        with _pedir("/me/biblioteca", cabeceras=cabeceras) as r:
            if getattr(r, "code", 200) == 304:
                datos = guardada
            else:
                datos = json.loads(r.read().decode("utf-8"))
                if not isinstance(datos, dict) or not isinstance(datos.get("sistemas"), list):
                    raise SinServidor("el servidor devolvió una biblioteca inválida")
                datos["_etag"] = r.headers.get("ETag", "")
    except SinServidor:
        if guardada:
            return guardada
        raise
    datos.update(_recibido=time.time(), _servidor=servidor(), _usuario=sesion().get("usuario"))
    cache().mkdir(parents=True, exist_ok=True)
    (cache() / ARCHIVO_BIBLIOTECA).write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
    return datos


def olvidar_biblioteca() -> bool:
    ruta = cache() / ARCHIVO_BIBLIOTECA
    if ruta.is_file():
        ruta.unlink()
        return True
    return False


def sincronizar(avisar=None) -> dict:
    """Trae a la caché todo lo de la biblioteca (comprobando cada sha256). Nunca toca los repos: las
    actualizaciones se aplican por repo cuando la persona decide. {"total", "descargados", "al_dia", "omitidos", "fallidos"}"""
    datos = biblioteca(refrescar=True)
    salida = {"total": 0, "descargados": [], "al_dia": [], "omitidos": [], "fallidos": []}
    for b in datos.get("sistemas", []):
        if not isinstance(b, dict):
            continue
        ref = f"{b.get('editor')}/{b.get('id')}"
        salida["total"] += 1
        if not b.get("version") or not b.get("sha256"):
            salida["omitidos"].append({"ref": ref, "motivo": "sin versión publicada"})
            continue
        if not esp.motor_compatible(b.get("motor") or ">=0.0"):
            salida["omitidos"].append({"ref": ref, "motivo": f"requiere motor {b['motor']}"})
            continue
        if en_cache(b["editor"], b["id"], b["version"]):
            salida["al_dia"].append(ref)
            continue
        try:
            traer(f"{ref}@{b['version']}")
            salida["descargados"].append(f"{ref}@{b['version']}")
            if avisar:
                avisar(f"{ref}@{b['version']}")
        except (SinServidor, NoEncontrado, PermissionError, artefacto.ArtefactoInvalido, OSError, ValueError) as e:
            salida["fallidos"].append({"ref": ref, "error": str(e)})
    return salida


def limpiar_cache() -> int:
    """Borra los sistemas traídos y el índice guardado; devuelve cuántas versiones había."""
    c = cache()
    if not c.is_dir():
        return 0
    n = len(list(c.glob(f"*/*/*/{MARCA_COMPLETO}")))
    import repo
    repo.borrar_arbol(c)
    return n


# ── sesión y publicación ──────────────────────────────────────────────────────
#
# `sesion.json` (privado) guarda UNA credencial para el servidor en el que se creó (ADR 0011):
#   {"tipo": "sesion", "token": "uxk_…", "servidor", "usuario", "equipo"}   iniciar-sesion (flujo de dispositivo)
#   {"tipo": "publicacion", "token": "uxp_…", "servidor"}                     sesion guardar <token> (CI, automatizaciones)
# El token solo viaja al servidor que lo emitió; `UXYNGRAPHAR_TOKEN` tiene prioridad (CI).

PREFIJO_SESION = "uxk_"
SEGUNDOS_POR_DEFECTO_CODIGO = 600


class SesionRechazada(PermissionError):
    """La persona rechazó el código o caducó antes de aprobarlo."""


def sesion() -> dict:
    datos = casa.leer_json(ARCHIVO_SESION, {})
    if not isinstance(datos, dict) or not datos.get("token"):
        return {}
    datos.setdefault("tipo", "sesion" if str(datos["token"]).startswith(PREFIJO_SESION) else "publicacion")
    return datos


def token() -> str | None:
    if os.environ.get("UXYNGRAPHAR_TOKEN"):
        return os.environ["UXYNGRAPHAR_TOKEN"]
    datos = sesion()
    if not datos:
        return None
    try:
        actual = servidor()
    except SinServidor:
        actual = None
    # Una credencial guardada para otro servidor no se envía a este.
    if datos.get("servidor") and actual and datos["servidor"] != actual:
        return None
    return datos.get("token")


def _autorizacion() -> dict:
    clave = token()
    return {"Authorization": f"Bearer {clave}"} if clave else {}


def guardar_token(valor: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9._~+/=-]{16,512}", valor or ""):
        raise ValueError("token de publicación con formato inválido")
    tipo = "sesion" if valor.startswith(PREFIJO_SESION) else "publicacion"
    return casa.escribir_json(ARCHIVO_SESION, {"tipo": tipo, "token": valor, "servidor": servidor()}, privado=True)


def borrar_token() -> bool:
    ruta = casa.carpeta() / ARCHIVO_SESION
    if ruta.is_file():
        ruta.unlink()
        return True
    return False


def _pedir_json(ruta: str, cuerpo: dict | None = None, metodo: str = "POST", con_sesion: bool = False,
                segundos: float = SEGUNDOS_RED) -> tuple[int, dict]:
    """Como `_pedir`, pero devuelve (código HTTP, JSON) también en 4xx: el flujo de dispositivo usa 428/403/410."""
    cabeceras = {"Content-Type": "application/json", **(_autorizacion() if con_sesion else {})}
    datos = json.dumps(cuerpo or {}).encode() if metodo in ("POST", "PUT", "PATCH") else None
    url = servidor()
    if not url:
        raise SinServidor("sin red (UXYNGRAPHAR_SIN_RED)")
    pedido = urllib.request.Request(url + ruta, data=datos, method=metodo,  # noqa: S310 - servidor https configurado
                                    headers={"User-Agent": f"uxyngraphar/{esp.VERSION_MOTOR}", "Accept": "application/json", **cabeceras})
    try:
        with urllib.request.urlopen(pedido, timeout=segundos) as r:  # noqa: S310 - servidor https configurado
            texto = r.read().decode("utf-8")
            return r.status, (json.loads(texto) if texto.strip() else {})
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8") or "{}")
        except (ValueError, OSError):
            return e.code, {}
    except (urllib.error.URLError, OSError) as e:
        raise SinServidor(f"{url}: no responde ({getattr(e, 'reason', e)})") from None


def _mensaje(cuerpo: dict, por_defecto: str) -> str:
    m = cuerpo.get("message") or cuerpo.get("error") or por_defecto
    return "; ".join(m) if isinstance(m, list) else str(m)


def nombre_equipo() -> str:
    import platform
    import socket
    nombre = socket.gethostname().split(".")[0] or "equipo"
    return f"{nombre} ({platform.system() or 'sistema'})"[:80]


def pedir_codigo(equipo: str | None = None) -> dict:
    """Paso 1 del inicio de sesión: {codigo_dispositivo, codigo_usuario, url, url_completa, intervalo, caduca_en}."""
    codigo, cuerpo = _pedir_json("/dispositivo/codigo", {"equipo": equipo or nombre_equipo()})
    if codigo != 201 and codigo != 200:
        raise SinServidor(_mensaje(cuerpo, f"no se pudo iniciar sesión (HTTP {codigo})"))
    if not cuerpo.get("codigo_dispositivo") or not cuerpo.get("codigo_usuario"):
        raise SinServidor("el servidor devolvió una respuesta inesperada")
    return cuerpo


def consultar_codigo(codigo_dispositivo: str) -> dict:
    """Paso 2 (una consulta): {"estado": pendiente|lento|denegado|caducado|aprobado, …}. Si se aprobó, guarda la sesión."""
    codigo, cuerpo = _pedir_json("/dispositivo/token", {"codigo_dispositivo": codigo_dispositivo})
    estado = cuerpo.get("estado") or {428: "pendiente", 429: "lento", 403: "denegado", 410: "caducado"}.get(codigo, "")
    if codigo == 200 and cuerpo.get("token"):
        casa.escribir_json(ARCHIVO_SESION, {"tipo": "sesion", "token": cuerpo["token"], "servidor": servidor(),
                                            "usuario": cuerpo.get("usuario"), "equipo": nombre_equipo()}, privado=True)
        return {"estado": "aprobado", "usuario": cuerpo.get("usuario")}
    if not estado:
        raise SinServidor(_mensaje(cuerpo, f"respuesta inesperada del servidor (HTTP {codigo})"))
    return {"estado": estado}


def iniciar_sesion(equipo: str | None = None, avisar=None, esperar=time.sleep) -> dict:
    """Flujo de dispositivo completo: pide el código, llama a `avisar(datos)` para mostrarlo y espera la aprobación.
    Devuelve {"usuario"}; lanza SesionRechazada si se rechaza o caduca."""
    datos = pedir_codigo(equipo)
    if avisar:
        avisar(datos)
    intervalo = max(1, int(datos.get("intervalo") or 5))
    limite = time.time() + int(datos.get("caduca_en") or SEGUNDOS_POR_DEFECTO_CODIGO)
    while time.time() < limite:
        esperar(intervalo)
        r = consultar_codigo(datos["codigo_dispositivo"])
        if r["estado"] == "aprobado":
            return r
        if r["estado"] == "lento":
            intervalo += 5
        elif r["estado"] == "denegado":
            raise SesionRechazada("se rechazó la conexión de este equipo")
        elif r["estado"] == "caducado":
            break
    raise SesionRechazada("el código caducó sin aprobarse; vuelve a ejecutar «uxyngraphar iniciar-sesion»")


def quien_soy() -> dict:
    """{"usuario", "nombre", "email", "equipo", "conectado"} de la sesión del kit (lanza PermissionError si no vale)."""
    if not token():
        raise PermissionError("sin sesión: uxyngraphar iniciar-sesion")
    codigo, cuerpo = _pedir_json("/dispositivo/sesion", metodo="GET", con_sesion=True)
    if codigo == 401:
        raise PermissionError("la sesión caducó o se revocó: uxyngraphar iniciar-sesion")
    if codigo != 200:
        raise SinServidor(_mensaje(cuerpo, f"HTTP {codigo}"))
    return cuerpo


def cerrar_sesion() -> dict:
    """Revoca la sesión en el servidor (si hay red y es una sesión del kit) y borra la local."""
    datos = sesion()
    revocada = False
    if datos.get("tipo") == "sesion" and token():
        try:
            codigo, _ = _pedir_json("/dispositivo/sesion", metodo="DELETE", con_sesion=True)
            revocada = codigo in (200, 204)
        except SinServidor:
            revocada = False
    olvidar_biblioteca()
    return {"revocada": revocada, "borrada": borrar_token()}


def publicar(zip_: Path, token_: str | None = None) -> dict:
    """Sube un artefacto (POST /sistemas/publicar, cuerpo application/zip). Devuelve la versión creada."""
    clave = token_ or token()
    if not clave:
        raise PermissionError("sin sesión: uxyngraphar iniciar-sesion (en CI: UXYNGRAPHAR_TOKEN con un token de automatización)")
    artefacto.leer(Path(zip_))
    datos = Path(zip_).read_bytes()
    with _pedir("/sistemas/publicar", datos=datos, metodo="POST",
                cabeceras={"Content-Type": "application/zip", "Authorization": f"Bearer {clave}",
                           "X-Uxyn-Sha256": artefacto.sha256_de(Path(zip_))}) as r:
        return json.loads(r.read().decode("utf-8"))
