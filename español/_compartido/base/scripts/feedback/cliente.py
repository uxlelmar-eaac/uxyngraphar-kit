"""Envío voluntario de sugerencias (fichas EVO) a quien mantiene uxyngraphar.

Principios (10-guias/envio-sugerencias.md):
  - Apagado por defecto. Solo lo enciende una persona: respondiendo «Sí» a la pregunta del instalador o del actualizador
    (que antes muestra qué sale y qué no) o con `feedback.py activar`.
  - Con el envío activo, solo se envía cuando una persona usa uxyngraphar (`instalar`, `actualizar`, `feedback.py enviar`).
    Nunca desde CI, ganchos de git ni el agente (`enviar_si_corresponde` lo comprueba).
  - Solo salen las fichas EVO de la carpeta 46, limpias: sin nombre del proyecto, rutas del equipo, correos, enlaces ni
    credenciales. Nada de código, git, usuario ni equipo. Un identificador aleatorio permite pedir el borrado.
  - El receptor oficial es el backend de uxyngraphar (NestJS + Postgres), repo uxyngraphar-backend.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
import uuid
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
for sub in ("decisiones", "control", "nucleo"):
    sys.path.insert(0, str(AQUI.parent / sub))

import secretos  # noqa: E402
import uxyngraphar_config as cfgmod  # noqa: E402
from common_frontmatter import rebuild_content, split_frontmatter_parts, update_frontmatter_raw  # noqa: E402

FORMATO = 1
TERMINOS = "v1"
# Receptor oficial: el backend de uxyngraphar (repo uxyngraphar-backend), base «/v1» de su API.
# Receptor oficial en producción (api.uxyngraphar.com). Único sitio donde se cambia la URL.
URL_FEEDBACK_OFICIAL = "https://api.uxyngraphar.com/v1"
ORIGENES = ("instalador", "actualizador", "manual")
# Variables que delatan un entorno sin persona delante: ahí nunca se envía nada solo.
ENTORNOS_SIN_PERSONA = ("CI", "GITHUB_ACTIONS", "GITLAB_CI", "BUILDKITE", "JENKINS_URL", "CLAUDECODE", "UXYNGRAPHAR_AGENTE")
PREGUNTA = "¿Te gustaría colaborar en la mejora de uxyngraphar?"
QUE_SALE = (
    "Las fichas EVO de docs/46-evolucion-documentacion/: id, estado, tipo, impacto, prioridad, archivos del pack que proponen cambiar y su texto",
    "La versión y el tipo de pack (servidor o cliente)",
    "Un identificador aleatorio de la instalación (sirve para pedir el borrado)",
)
QUE_NO_SALE = (
    "Código, historia de git, ramas ni remotos",
    "El nombre del proyecto ni los nombres que pongas en feedback.ocultar",
    "Rutas de tu equipo, correos y enlaces (se cambian por [ruta], [correo], [enlace])",
    "Líneas que parezcan credenciales, comentarios HTML ni el campo areas",
    "Tu usuario, el nombre del equipo, tus ajustes locales ni métricas de uso",
)
CUANDO_SE_ENVIA = ("Si respondes Sí, al terminar cada «instalar» o «actualizar» que hagas tú se envían las fichas EVO nuevas o cambiadas "
                   "(verás cuántas). Nunca desde CI, ganchos de git ni el agente. Lo apagas cuando quieras con «feedback.py revocar».")
CAMPOS = ("id", "status", "tipo", "impacto", "prioridad", "propuesta_cambio", "proposed_at", "instruction_derivada")
ESTADOS = ("pending", "approved", "done", "rejected", "archivada")
MAX_CUERPO = 8000
ESPERA = 15
MARCA_FECHA, MARCA_HUELLA = "feedback_enviada", "feedback_huella"

_CORREO = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_URL = re.compile(r"\b(?:https?|ftp|ssh|git)://\S+|\bgit@[\w.-]+:\S+")
_RUTA = re.compile(r"(?:[A-Za-z]:\\|\\\\|/(?:home|Users|root|mnt|media|opt|srv|var|tmp|private)/)[^\s`'\")\]]*[^\s`'\")\].,;:]")


class ErrorEnvio(Exception):
    pass


def limpiar(texto: str, proyecto: str = "", ocultar: tuple[str, ...] = ()) -> str:
    """Quita lo que identifica al proyecto o a la persona. Las líneas con algo parecido a una credencial no salen.
    `ocultar`: nombres que tú añades (cliente, producto, empresa) en `feedback.ocultar` de la configuración."""
    texto = re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    lineas = []
    for linea in texto.splitlines():
        if secretos.escanear_texto("sugerencia.md", linea):
            lineas.append("[línea omitida: parecía una credencial]")
            continue
        linea = _URL.sub("[enlace]", linea)
        linea = _CORREO.sub("[correo]", linea)
        linea = _RUTA.sub("[ruta]", linea)
        if proyecto and len(proyecto) >= 3:
            linea = re.sub(re.escape(proyecto), "[proyecto]", linea, flags=re.I)
        for termino in ocultar:
            if len(termino.strip()) >= 2:
                linea = re.sub(re.escape(termino.strip()), "[oculto]", linea, flags=re.I)
        lineas.append(linea)
    salida = re.sub(r"\n{3,}", "\n\n", "\n".join(lineas)).strip()
    return salida if len(salida) <= MAX_CUERPO else salida[:MAX_CUERPO] + "\n[…recortado]"


def _valor(v: object, proyecto: str, ocultar: tuple[str, ...]) -> object:
    if isinstance(v, list):
        return [limpiar(str(x), proyecto, ocultar) for x in v]
    return None if v is None else limpiar(str(v), proyecto, ocultar)


def _huella(datos: dict) -> str:
    return hashlib.sha256(json.dumps(datos, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:12]


def fichas(docs: Path, proyecto: str, estados: tuple[str, ...] = ESTADOS, todas: bool = False, ocultar: tuple[str, ...] = ()) -> list[tuple[Path, dict]]:
    """(ruta, ficha limpia) de cada EVO por enviar: nueva o cambiada desde el último envío (todas=True: también las ya enviadas)."""
    salida = []
    for md in sorted((docs / "46-evolucion-documentacion").glob("0[1-6]-*/*/EVO-*.md")):
        raw, fm, cuerpo = split_frontmatter_parts(md.read_text(encoding="utf-8", errors="replace"))
        if raw is None or str(fm.get("status", "")) not in estados:
            continue
        ficha = {k: _valor(fm.get(k), proyecto, ocultar) for k in CAMPOS if fm.get(k) not in (None, "", [])}
        ficha["cuerpo"] = limpiar(cuerpo, proyecto, ocultar)
        if fm.get("ajuste_local"):
            ficha["aplicada_en_local"] = True
        ficha["huella"] = _huella(ficha)
        if todas or str(fm.get(MARCA_HUELLA, "")) != ficha["huella"]:
            salida.append((md, ficha))
    return salida


def paquete(docs: Path, cfg: dict, proyecto: str, version: str, pack: str, todas: bool = False) -> tuple[list[Path], dict]:
    ocultar = tuple(cfg["feedback"].get("ocultar") or ())
    items = fichas(docs, proyecto, todas=todas, ocultar=ocultar)
    datos = {"formato": FORMATO, "terminos": TERMINOS, "id_instalacion": cfg["feedback"].get("id_instalacion") or "(se crea al activar)",
             "pack": pack, "version": version, "fecha": date.today().isoformat(),
             "fichas": [f for _md, f in items]}
    return [md for md, _f in items], datos


def marcar(rutas: list[Path], datos: dict, fecha: str | None = None) -> int:
    fecha = fecha or date.today().isoformat()
    por_id = {f.get("id"): f["huella"] for f in datos["fichas"]}
    for md in rutas:
        raw, fm, cuerpo = split_frontmatter_parts(md.read_text(encoding="utf-8"))
        h = por_id.get(fm.get("id"))
        if h:
            md.write_text(rebuild_content(update_frontmatter_raw(raw or "", {MARCA_FECHA: fecha, MARCA_HUELLA: h}), cuerpo), encoding="utf-8", newline="\n")
    return len(rutas)


def _peticion(metodo: str, url: str, cuerpo: dict | None, version: str) -> dict:
    if not cfgmod.url_permitida(url):
        raise ErrorEnvio(f"dirección no permitida: {url} (solo https://, o http hacia este equipo)")
    import os
    cabeceras = {"Content-Type": "application/json; charset=utf-8", "User-Agent": f"uxyngraphar-feedback/{version}"}
    token = os.environ.get("UXYNGRAPHAR_FEEDBACK_TOKEN", "")
    if token:
        cabeceras["Authorization"] = f"Bearer {token}"
    datos = json.dumps(cuerpo, ensure_ascii=False).encode("utf-8") if cuerpo is not None else None
    req = urllib.request.Request(url, data=datos, headers=cabeceras, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=ESPERA) as r:   # noqa: S310 - esquema validado arriba
            texto = r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        raise ErrorEnvio(f"el servidor respondió {exc.code}: {exc.read().decode('utf-8', errors='replace')[:200]}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ErrorEnvio(f"no se pudo conectar con {url}: {exc}") from exc
    try:
        return json.loads(texto) if texto.strip() else {}
    except ValueError:
        return {}


def enviar(url: str, datos: dict, version: str) -> dict:
    return _peticion("POST", url.rstrip("/") + "/sugerencias", datos, version)


def borrar_remoto(url: str, id_instalacion: str, version: str) -> dict:
    return _peticion("DELETE", url.rstrip("/") + f"/instalaciones/{id_instalacion}", None, version)


def leer_config_crudo(repo: Path, docs: str) -> dict:
    f = repo / docs / cfgmod.NOMBRE
    if not f.is_file():
        return {}
    try:
        datos = json.loads(f.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise ErrorEnvio(f"{cfgmod.NOMBRE} ilegible ({exc}); corrígelo antes de activar el envío") from exc
    return datos if isinstance(datos, dict) else {}


def guardar_feedback(repo: Path, docs: str, feedback: dict) -> Path:
    """Cambia solo la sección `feedback` del archivo de configuración; el resto queda como estaba."""
    datos = leer_config_crudo(repo, docs)
    datos["feedback"] = feedback
    f = repo / docs / cfgmod.NOMBRE
    f.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return f


def nuevo_id() -> str:
    return str(uuid.uuid4())


def texto_colaboracion(url: str = URL_FEEDBACK_OFICIAL) -> str:
    """La pregunta en lenguaje llano, con qué sale y qué no (consola del instalador y del actualizador)."""
    l = [PREGUNTA, "", f"Si dices que sí, se activa el envío de sugerencias a quien mantiene uxyngraphar ({url}).", "", "Qué sale:"]
    l += [f"  + {x}" for x in QUE_SALE] + ["", "Qué no sale nunca:"] + [f"  - {x}" for x in QUE_NO_SALE]
    l += ["", CUANDO_SE_ENVIA]
    return "\n".join(l)


def info_colaboracion(url: str = URL_FEEDBACK_OFICIAL) -> dict:
    """Lo mismo para la pantalla del navegador."""
    return {"pregunta": PREGUNTA, "url": url, "sale": list(QUE_SALE), "no_sale": list(QUE_NO_SALE), "cuando": CUANDO_SE_ENVIA}


def necesita_respuesta(cfg: dict) -> bool:
    """¿Hay que hacer la pregunta? Solo si nadie respondió aún y el envío no se activó antes a mano."""
    fb = cfg.get("feedback") or {}
    return not fb.get("respondido") and fb.get("activo") is not True


def registrar_respuesta(repo: Path, docs: str, acepta: bool, origen: str, fecha: str | None = None) -> dict:
    """Guarda la respuesta de una persona en la sección `feedback` (con Sí activa el envío con consentimiento y fecha)."""
    if origen not in ORIGENES:
        raise ValueError(f"origen desconocido: {origen}")
    fecha = fecha or date.today().isoformat()
    actual = {**cfgmod.por_defecto()["feedback"], **(leer_config_crudo(repo, docs).get("feedback") or {})}
    if acepta:
        nuevo = {**actual, "activo": True, "url": actual.get("url") or URL_FEEDBACK_OFICIAL,
                 "consentimiento": f"{fecha} ({TERMINOS})", "id_instalacion": actual.get("id_instalacion") or nuevo_id(),
                 "respondido": "si", "respondido_en": fecha, "origen": origen}
    else:
        nuevo = {**actual, "activo": False, "consentimiento": "", "respondido": "no", "respondido_en": fecha, "origen": origen}
    guardar_feedback(repo, docs, nuevo)
    return nuevo


def sin_persona(entorno: dict | None = None) -> str:
    """Nombre de la variable que indica CI o agente (vacío si hay una persona delante)."""
    entorno = os.environ if entorno is None else entorno
    return next((v for v in ENTORNOS_SIN_PERSONA if str(entorno.get(v, "")).strip().lower() not in ("", "0", "false")), "")


def enviar_si_corresponde(repo: Path, docs: str, entorno: dict | None = None) -> str | None:
    """Tras «instalar» o «actualizar» hechos por una persona: con el envío activo, manda las fichas EVO nuevas o cambiadas.

    Devuelve una línea para mostrar (o None si no hay nada que decir). Nunca lanza: un fallo de red solo avisa.
    No hace nada en CI ni cuando lo ejecuta un agente (ENTORNOS_SIN_PERSONA).
    """
    try:
        if sin_persona(entorno):
            return None
        import lock
        cfg, problemas = cfgmod.cargar(repo, docs)
        fb = cfg["feedback"]
        if not fb.get("activo") or any(p.startswith("feedback") for p in problemas):
            return None
        datos_lock = lock.leer(repo, docs) or {}
        version = datos_lock.get("version") or lock.version_de(repo / docs)
        pack = datos_lock.get("pack") or lock.tipo_pack(repo / docs)
        rutas, datos = paquete(repo / docs, cfg, repo.name, version, pack)
        if not datos["fichas"]:
            return "Sugerencias: no hay fichas EVO nuevas o cambiadas que enviar."
        respuesta = enviar(fb["url"], datos, version)
        marcar(rutas, datos)
        guardadas = respuesta.get("guardadas")
        return (f"Sugerencias: enviadas {len(datos['fichas'])} ficha(s) EVO"
                + (f" (el servidor guardó {guardadas} nuevas)" if isinstance(guardadas, int) else "") + ".")
    except ErrorEnvio as exc:
        return f"Sugerencias: no se pudieron enviar ({exc}). Se intentará la próxima vez; también puedes usar «feedback.py enviar»."
    except Exception as exc:  # noqa: BLE001 - nunca rompe una instalación o actualización
        return f"Sugerencias: no se pudieron preparar ({exc})."
