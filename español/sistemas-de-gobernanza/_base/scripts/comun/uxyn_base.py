"""Base de un sistema de gobernanza uxyngraphar (protocolo de sistemas v1): rutas, frontmatter, manifiesto e integridad.

Parte del propio sistema (`scripts/comun/`); los sistemas nuevos lo reciben de `sistemas-de-gobernanza/_base/`. Solo librería estándar.
El sistema vive en `<raiz-app>/uxyngraphar/sistemas-de-gobernanza/<id>/` y escribe su trabajo en `<raiz-app>/uxyngraphar/trabajo/<id>/`.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

MANIFIESTO = "sistema.json"
INTEGRIDAD = "INTEGRIDAD.json"
ENTRADA = "README.md"
DESCRIPCION = "SISTEMA.md"
MEMORIAS = "MEMORIAS.md"
LIMITES = "LIMITES.md"
PERMISOS = "PERMISOS.md"
NUCLEO = (MANIFIESTO, ENTRADA, DESCRIPCION, MEMORIAS, LIMITES, PERMISOS)
SCRIPTS = "scripts"
CARPETA_RAIZ = "uxyngraphar"
CARPETA_SISTEMAS_DE_GOBERNANZA = "uxyngraphar/sistemas-de-gobernanza"
CARPETA_TRABAJO = "uxyngraphar/trabajo"
# Memorias del proyecto: `uxyngraphar/trabajo/<id>/memorias/MEM-…md`; ninguna ficha usa esa carpeta ni ese prefijo.
CARPETA_MEMORIAS = "memorias"
PREFIJO_MEMORIA = "MEM"
FORMATO_MANIFIESTO = 1
FORMATO_INTEGRIDAD = 1

# Piezas estándar (opcionales): nombre en «piezas» → ruta reservada dentro del sistema.
PIEZAS = {
    "proceso": "proceso",
    "skills": "skills",
    "componentes": "COMPONENTES.md",
    "herramientas": "HERRAMIENTAS.md",
    "andamiaje": "andamiaje",
    "plantillas": "plantillas",
    "referencia": "referencia",
    "ejemplos": "ejemplos",
    "pruebas": "pruebas",
    "cambios": "CHANGELOG.md",
}
RESERVADOS = {*NUCLEO, INTEGRIDAD, SCRIPTS, *PIEZAS.values()}

ID_VALIDO = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
REQUISITO_MOTOR = re.compile(r"^>=\d+\.\d+(?:\.\d+)?(?:,<\d+(?:\.\d+){0,2})?$")   # «>=1.0» o «>=1.0,<2»
CARPETA_ESTADO = re.compile(r"^[a-z]+(?:-[a-z]+)*$")
CARPETA_FICHAS = re.compile(r"^(?:\.|[a-z0-9]+(?:-[a-z0-9]+)*)$")
IGNORAR = re.compile(r"(?:^|/)__pycache__(?:/|$)|\.pyc$|(?:^|/)\.DS_Store$")
VARIABLE_HUMANO = "UXYNGRAPHAR_HUMANO"


# ---------- salida ----------

def _salida_utf8() -> None:
    """Los scripts escriben en UTF-8 aunque la salida vaya a un tubo o archivo (en Windows sería la página de códigos
    local, que no tiene «→» y rompe el script o lo que lee su salida). La consola interactiva ya es UTF-8."""
    for flujo in (sys.stdout, sys.stderr):
        if flujo is not None and hasattr(flujo, "reconfigure") and (flujo.encoding or "").lower().replace("-", "") != "utf8":
            flujo.reconfigure(encoding="utf-8", errors="replace")


_salida_utf8()


# ---------- quién ejecuta ----------

def terminal_interactiva() -> bool:
    flujo = sys.stdin
    try:
        if flujo is None or not flujo.isatty():
            return False
        if os.name != "nt":
            return True
        # En Windows, NUL (la entrada vacía con que se lanza a un agente) también dice ser terminal: solo cuenta una consola.
        import ctypes
        import msvcrt
        modo = ctypes.c_uint32()
        return bool(ctypes.windll.kernel32.GetConsoleMode(msvcrt.get_osfhandle(flujo.fileno()), ctypes.byref(modo)))
    except (OSError, ValueError, AttributeError):
        return False


def es_humano() -> bool:
    """Una persona: `UXYNGRAPHAR_HUMANO=1` o terminal interactiva fuera de CI. Los agentes ejecutan sin terminal."""
    if os.environ.get(VARIABLE_HUMANO) == "1":
        return True
    if os.environ.get("CI", "").lower() in ("1", "true", "yes"):
        return False
    return terminal_interactiva()


def exigir_humano(accion: str) -> None:
    if not es_humano():
        raise PermissionError(f"{accion}: solo una persona (terminal interactiva o {VARIABLE_HUMANO}=1). "
                              "Si eres un agente, pide a la persona que lo ejecute")


# ---------- rutas ----------

def carpeta_sistema(desde: str | Path) -> Path:
    """Carpeta del sistema: la primera, subiendo desde `desde`, que contiene el manifiesto."""
    p = Path(desde).resolve()
    for c in [p, *p.parents]:
        if (c / MANIFIESTO).is_file():
            return c
    raise FileNotFoundError(f"no encuentro {MANIFIESTO} subiendo desde {p}")


def raiz_app(sistema: Path) -> Path:
    """Raíz de la app: `<raiz-app>/uxyngraphar/sistemas-de-gobernanza/<id>/` → `<raiz-app>`."""
    return sistema.resolve().parents[2]


def carpeta_trabajo(sistema: Path, crear: bool = True) -> Path:
    """`<raiz-app>/uxyngraphar/trabajo/<id>/` (se crea si falta)."""
    destino = raiz_app(sistema) / CARPETA_TRABAJO / leer_manifiesto(sistema)["id"]
    if crear:
        destino.mkdir(parents=True, exist_ok=True)
    return destino


def leer_manifiesto(sistema: Path) -> dict:
    return json.loads((Path(sistema) / MANIFIESTO).read_text(encoding="utf-8"))


def leer_ajustes(sistema: Path) -> dict:
    """Ajustes efectivos: valores por defecto del manifiesto + `uxyngraphar/trabajo/<id>/ajustes.json` del proyecto."""
    efectivos = dict(leer_manifiesto(sistema).get("ajustes", {}))
    archivo = carpeta_trabajo(sistema, crear=False) / "ajustes.json"
    if archivo.is_file():
        efectivos.update(json.loads(archivo.read_text(encoding="utf-8")))
    return efectivos


# ---------- frontmatter ----------

def _valor(texto: str):
    t = texto.strip()
    if t in ("", "null", "~"):
        return None
    if t in ("true", "false"):
        return t == "true"
    if t.startswith("[") and t.endswith("]"):
        dentro = t[1:-1].strip()
        return [] if not dentro else [str(_valor(x)) for x in dentro.split(",")]
    if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'":
        return t[1:-1]
    return t


def leer_frontmatter(texto: str) -> tuple[dict, str]:
    """Frontmatter YAML plano (clave: valor, listas en línea). Devuelve ({}, texto) si no hay."""
    if not texto.startswith("---"):
        return {}, texto
    partes = texto.split("\n---", 1)
    if len(partes) < 2:
        return {}, texto
    datos: dict = {}
    clave_lista = None
    for cruda in partes[0].splitlines()[1:]:
        linea = cruda.split(" #", 1)[0].rstrip()
        elemento = linea.strip()
        if clave_lista and elemento.startswith("- "):
            if not isinstance(datos.get(clave_lista), list):
                datos[clave_lista] = []
            datos[clave_lista].append(str(_valor(elemento[2:])))
            continue
        clave_lista = None
        if ":" in linea and not linea.startswith((" ", "\t", "-")):
            clave, _, resto = linea.partition(":")
            datos[clave.strip()] = _valor(resto)
            if not resto.strip():
                clave_lista = clave.strip()
    cuerpo = partes[1].split("\n", 1)[1] if "\n" in partes[1] else ""
    return datos, cuerpo


def escribir_campo(texto: str, clave: str, valor: str) -> str:
    """Reemplaza (o añade) `clave: valor` dentro del frontmatter."""
    patron = re.compile(rf"^{re.escape(clave)}:.*$", re.M)
    cabecera, sep, resto = texto.partition("\n---")
    if patron.search(cabecera):
        cabecera = patron.sub(f"{clave}: {valor}", cabecera, count=1)
    else:
        cabecera = f"{cabecera}\n{clave}: {valor}"
    return cabecera + sep + resto


# ---------- manifiesto ----------

def _lista_de_textos(valor) -> bool:
    return isinstance(valor, list) and all(isinstance(x, str) and x.strip() for x in valor)


def _validar_fichas(fichas) -> list[str]:
    if not isinstance(fichas, dict):
        return ["«fichas» debe ser un objeto {tipo: definición}"]
    errores = []
    for tipo, d in fichas.items():
        donde = f"fichas.{tipo}"
        if not ID_VALIDO.match(tipo) or not isinstance(d, dict):
            errores.append(f"{donde}: nombre inválido o definición no es un objeto")
            continue
        for campo in ("carpeta", "prefijo", "plantilla", "inicial"):
            if not isinstance(d.get(campo), str) or not d[campo].strip():
                errores.append(f"{donde}.{campo}: obligatorio (texto)")
        if isinstance(d.get("carpeta"), str) and not CARPETA_FICHAS.match(d["carpeta"]):
            errores.append(f"{donde}.carpeta: «.» (raíz del trabajo) o un nombre kebab-case")
        elif d.get("carpeta") == "." and len(fichas) > 1:
            errores.append(f"{donde}.carpeta: «.» solo vale si el sistema tiene un único tipo de ficha")
        elif d.get("carpeta") == CARPETA_MEMORIAS:
            errores.append(f"{donde}.carpeta: «{CARPETA_MEMORIAS}» está reservada para las memorias del proyecto")
        if d.get("prefijo") == PREFIJO_MEMORIA:
            errores.append(f"{donde}.prefijo: «{PREFIJO_MEMORIA}» está reservado para las memorias del proyecto")
        estados, validos = d.get("estados"), d.get("status_validos")
        if (estados is None) == (validos is None):
            errores.append(f"{donde}: define «estados» (con carpetas) o «status_validos» (plana), no ambos")
        elif estados is not None:
            if not isinstance(estados, dict) or not estados or not all(isinstance(v, str) and CARPETA_ESTADO.match(v) for v in estados.values()):
                errores.append(f"{donde}.estados: objeto {{status: «carpeta-kebab»}} no vacío")
            elif d.get("inicial") not in estados:
                errores.append(f"{donde}.inicial: debe ser una clave de «estados»")
        elif not _lista_de_textos(validos) or d.get("inicial") not in validos:
            errores.append(f"{donde}.status_validos: lista de textos que incluya «inicial»")
        if "solo_humano" in d and not _lista_de_textos(d["solo_humano"]) and d["solo_humano"] != []:
            errores.append(f"{donde}.solo_humano: lista de status")
        todos = set(estados or {}) | set(validos or [])
        if "espera_humano" in d and (not _lista_de_textos(d["espera_humano"]) or not set(d["espera_humano"]) <= todos):
            errores.append(f"{donde}.espera_humano: lista de status del tipo (los que esperan una decisión de una persona)")
        comandos = d.get("comandos", {})
        if not isinstance(comandos, dict) or not all(
                k in todos and isinstance(v, str) and v.startswith("scripts/") and "{id}" in v for k, v in comandos.items()):
            errores.append(f"{donde}.comandos: {{status: «scripts/… {{id}} …»}} para decidir ese status")
        variantes = d.get("variantes", {})
        if not isinstance(variantes, dict) or not all(
                ID_VALIDO.match(k) and isinstance(v, str) and v.startswith("plantillas/") for k, v in variantes.items()):
            errores.append(f"{donde}.variantes: {{nombre-kebab: «plantillas/….md»}}")
    return errores


def status_que_esperan(d: dict) -> list[str]:
    """Status de un tipo de ficha que esperan una decisión de una persona («espera_humano» o, si no, el inicial)."""
    if "espera_humano" in d:
        return list(d["espera_humano"])
    return [d["inicial"]] if d.get("solo_humano") and d["inicial"] not in d["solo_humano"] else []


def validar_manifiesto(m) -> list[str]:
    """Errores del manifiesto (lista vacía = válido). Contrato en ESPECIFICACION.md del kit."""
    if not isinstance(m, dict):
        return ["el manifiesto debe ser un objeto JSON"]
    errores = []
    if m.get("manifiesto_formato") != FORMATO_MANIFIESTO:
        errores.append(f"manifiesto_formato: debe ser {FORMATO_MANIFIESTO}")
    if not isinstance(m.get("id"), str) or not ID_VALIDO.match(m["id"]):
        errores.append("id: kebab-case ASCII (a-z, 0-9, guiones)")
    if not isinstance(m.get("version"), str) or not SEMVER.match(m["version"]):
        errores.append("version: semver X.Y.Z")
    for campo in ("titulo", "descripcion"):
        if not isinstance(m.get(campo), str) or not m[campo].strip():
            errores.append(f"{campo}: obligatorio (texto)")
    if not isinstance(m.get("motor"), str) or not REQUISITO_MOTOR.match(m["motor"]):
        errores.append("motor: requisito «>=X.Y» o, con techo, «>=X.Y,<Z»")
    if not _lista_de_textos(m.get("activacion")):
        errores.append("activacion: lista no vacía de frases")
    elif m.get("id") not in m["activacion"]:
        errores.append("activacion: debe incluir el id del sistema")
    if m.get("entrada") != ENTRADA:
        errores.append(f"entrada: debe ser «{ENTRADA}»")
    verif = m.get("verificaciones")
    if not isinstance(verif, list) or not all(isinstance(v, str) and v.startswith("scripts/") and v.endswith(".py") for v in verif):
        errores.append("verificaciones: lista de «scripts/*.py»")
    if "fichas" in m:
        errores += _validar_fichas(m["fichas"])
    if "ajustes" in m and not isinstance(m["ajustes"], dict):
        errores.append("ajustes: objeto con valores por defecto")
    for campo, nuevo in (("protegidos", "protegidas"), ("fuera_de_ia", "fuera_de_ia")):
        if campo in m:
            errores.append(f"{campo}: no va suelto; muévelo a «permisos.rutas.{nuevo}»")
    errores += validar_permisos(m.get("permisos"))
    activar = m.get("al_activar_sistema")
    if activar is not None and not (isinstance(activar, str) and activar.startswith("scripts/") and "{id}" in activar):
        errores.append("al_activar_sistema: «scripts/… {id}» (se ejecuta al activar cualquier sistema)")
    errores += _validar_distribucion(m)
    errores += _validar_alcance(m.get("alcance"))
    errores += _validar_piezas(m)
    return errores


IDIOMA = re.compile(r"^[a-z]{2}$")
LICENCIA = re.compile(r"^(?:[A-Za-z0-9.+-]+(?: (?:OR|AND|WITH) [A-Za-z0-9.+-]+)*|propietaria)$")


def _validar_distribucion(m: dict) -> list[str]:
    """Campos opcionales del protocolo para servir el sistema desde el servidor de sistemas de gobernanza."""
    errores = []
    if "editor" in m and not (isinstance(m["editor"], str) and ID_VALIDO.match(m["editor"])):
        errores.append("editor: kebab-case ASCII (el espacio de nombres del autor; por defecto «uxyngraphar»)")
    if "idioma" in m and not (isinstance(m["idioma"], str) and IDIOMA.match(m["idioma"])):
        errores.append("idioma: código de dos letras (p. ej. «es»)")
    if "licencia" in m and not (isinstance(m["licencia"], str) and LICENCIA.match(m["licencia"])):
        errores.append("licencia: identificador SPDX (p. ej. «CC-BY-4.0») o «propietaria»")
    if "etiquetas" in m and not (isinstance(m["etiquetas"], list) and len(m["etiquetas"]) <= 12
                                 and all(isinstance(e, str) and ID_VALIDO.match(e) for e in m["etiquetas"])):
        errores.append("etiquetas: hasta 12, en kebab-case")
    if "repositorio" in m and not (isinstance(m["repositorio"], str) and m["repositorio"].startswith("https://")):
        errores.append("repositorio: URL https de la fuente")
    return errores


def _texto(valor) -> bool:
    return isinstance(valor, str) and bool(valor.strip())


def _relativa(ruta) -> bool:
    return _texto(ruta) and not ruta.startswith("/") and ".." not in ruta.split("/") and "\\" not in ruta


def _validar_alcance(alcance) -> list[str]:
    """«alcance»: los problemas concretos que resuelve el sistema y lo que deja fuera (y a quién lo deriva)."""
    if not isinstance(alcance, dict):
        return ["alcance: obligatorio, objeto con «problemas» y «fuera_de_alcance»"]
    errores = []
    problemas = alcance.get("problemas")
    if not isinstance(problemas, list) or not problemas:
        errores.append("alcance.problemas: al menos un problema {id, descripcion}")
    else:
        vistos = set()
        for i, p in enumerate(problemas):
            if not isinstance(p, dict) or not isinstance(p.get("id"), str) or not ID_VALIDO.match(p["id"]) or not _texto(p.get("descripcion")):
                errores.append(f"alcance.problemas[{i}]: {{id: kebab-case, descripcion: texto}}")
            elif p["id"] in vistos:
                errores.append(f"alcance.problemas: id repetido «{p['id']}»")
            else:
                vistos.add(p["id"])
    fuera = alcance.get("fuera_de_alcance")
    if not isinstance(fuera, list) or not fuera:
        errores.append("alcance.fuera_de_alcance: al menos una entrada {tema, derivar_a}")
    else:
        for i, f in enumerate(fuera):
            derivar = f.get("derivar_a") if isinstance(f, dict) else None
            if not isinstance(f, dict) or not _texto(f.get("tema")) or not (derivar is None or (isinstance(derivar, str) and ID_VALIDO.match(derivar))):
                errores.append(f"alcance.fuera_de_alcance[{i}]: {{tema: texto, derivar_a: id de sistema o null}}")
    return errores


CLAVES_RUTAS = ("protegidas", "fuera_de_ia")
CLAVES_ACCIONES = ("agente", "solo_persona")


def rutas_permiso(m: dict, clave: str) -> list[str]:
    """`permisos.rutas.<clave>` del manifiesto («protegidas» o «fuera_de_ia»), o [] si no las declara."""
    permisos = m.get("permisos") if isinstance(m.get("permisos"), dict) else {}
    rutas = permisos.get("rutas") if isinstance(permisos.get("rutas"), dict) else {}
    return list(rutas.get(clave) or [])


def acciones_permiso(m: dict, clave: str) -> list[str]:
    """`permisos.acciones.<clave>` del manifiesto («agente» o «solo_persona»), normalizadas, o []."""
    permisos = m.get("permisos") if isinstance(m.get("permisos"), dict) else {}
    acciones = permisos.get("acciones") if isinstance(permisos.get("acciones"), dict) else {}
    return [" ".join(a.split()) for a in acciones.get(clave) or []]


def script_de_accion(accion: str) -> str:
    """«scripts/x.py subcomando …» → «scripts/x.py»."""
    partes = accion.split(maxsplit=1)
    return partes[0] if partes else ""


def validar_permisos(permisos) -> list[str]:
    """«permisos»: rutas del trabajo que el agente no escribe o no lee, y acciones que hace solo o que decide una persona."""
    forma = ("permisos: obligatorio, objeto {rutas: {protegidas, fuera_de_ia}, acciones: {agente, solo_persona}}")
    if not isinstance(permisos, dict) or set(permisos) - {"rutas", "acciones"}:
        return [forma]
    errores = []
    rutas, acciones = permisos.get("rutas", {}), permisos.get("acciones", {})
    if not isinstance(rutas, dict) or set(rutas) - set(CLAVES_RUTAS):
        errores.append(f"permisos.rutas: objeto con {', '.join(CLAVES_RUTAS)}")
    else:
        for clave in CLAVES_RUTAS:
            valor = rutas.get(clave, [])
            if not isinstance(valor, list) or not all(_relativa(r) for r in valor):
                errores.append(f"permisos.rutas.{clave}: lista de rutas (globs) relativas a uxyngraphar/trabajo/<id>/")
    if not isinstance(acciones, dict) or set(acciones) - set(CLAVES_ACCIONES):
        errores.append(f"permisos.acciones: objeto con {', '.join(CLAVES_ACCIONES)}")
        return errores
    vistas: dict[str, str] = {}
    for clave in CLAVES_ACCIONES:
        valor = acciones.get(clave, [])
        if not isinstance(valor, list) or not all(
                _texto(a) and script_de_accion(a).startswith("scripts/") and script_de_accion(a).endswith(".py")
                and _relativa(script_de_accion(a)) for a in valor):
            errores.append(f"permisos.acciones.{clave}: lista de «scripts/….py [subcomando]»")
            continue
        for a in valor:
            normal = " ".join(a.split())
            if normal in vistas:
                errores.append(f"permisos.acciones: «{normal}» está en «{vistas[normal]}» y en «{clave}»"
                               if vistas[normal] != clave else f"permisos.acciones.{clave}: «{normal}» repetida")
            vistas[normal] = clave
    return errores


def ids_problemas(m: dict) -> set[str]:
    alcance = m.get("alcance") if isinstance(m.get("alcance"), dict) else {}
    return {p["id"] for p in alcance.get("problemas") or [] if isinstance(p, dict) and isinstance(p.get("id"), str)}


def _validar_piezas(m: dict) -> list[str]:
    """«piezas» (estándar, opcionales) y «extensiones» (libres, declaradas), y los campos que dependen de ellas."""
    errores = []
    piezas = m.get("piezas")
    if not isinstance(piezas, list) or not all(isinstance(p, str) for p in piezas):
        return ["piezas: lista de piezas estándar (puede estar vacía): " + ", ".join(PIEZAS)]
    for p in piezas:
        if p == "limites":
            errores.append(f"piezas: «limites» no es una pieza; {LIMITES} es parte del núcleo (quítala de «piezas»)")
        elif p not in PIEZAS:
            errores.append(f"piezas: «{p}» no es una pieza estándar ({', '.join(PIEZAS)}); lo propio va en «extensiones»")
    if len(set(piezas)) != len(piezas):
        errores.append("piezas: repetidas")
    proceso = m.get("proceso")
    if "proceso" in piezas:
        if not isinstance(proceso, list) or not proceso or not all(isinstance(f, str) and ID_VALIDO.match(f) for f in proceso):
            errores.append("proceso: lista ordenada de fases (kebab-case), una por archivo proceso/<fase>.md")
        elif len(set(proceso)) != len(proceso):
            errores.append("proceso: fases repetidas")
    elif proceso is not None:
        errores.append("proceso: solo con la pieza «proceso» en «piezas»")
    andamiaje = m.get("andamiaje")
    if "andamiaje" in piezas:
        if not isinstance(andamiaje, dict) or not andamiaje:
            errores.append("andamiaje: objeto {variante: {descripcion, destino}} no vacío")
        else:
            for nombre, d in andamiaje.items():
                if not ID_VALIDO.match(nombre) or not isinstance(d, dict) or not _texto(d.get("descripcion")) or not _relativa(d.get("destino")):
                    errores.append(f"andamiaje.{nombre}: {{descripcion: texto, destino: ruta relativa a la raíz de la app}}")
    elif andamiaje is not None:
        errores.append("andamiaje: solo con la pieza «andamiaje» en «piezas»")
    if m.get("fichas") and "plantillas" not in piezas:
        errores.append("fichas: necesitan la pieza «plantillas» en «piezas»")
    extensiones = m.get("extensiones", {})
    if not isinstance(extensiones, dict):
        errores.append("extensiones: objeto {ruta: para qué sirve}")
    else:
        for ruta, para in extensiones.items():
            if not _relativa(ruta) or "/" in ruta.strip("/") or ruta in RESERVADOS or not _texto(para):
                errores.append(f"extensiones.{ruta}: nombre de primer nivel no reservado y una frase de para qué sirve")
    return errores


# ---------- integridad ----------

def sha256(ruta: Path) -> str:
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def archivos_del_sistema(sistema: Path) -> list[str]:
    """Rutas relativas (con «/») de todo lo que forma el sistema, sin INTEGRIDAD.json ni cachés."""
    base = Path(sistema)
    salida = []
    for p in sorted(base.rglob("*")):
        rel = p.relative_to(base).as_posix()
        if p.is_file() and rel != INTEGRIDAD and not IGNORAR.search(rel):
            salida.append(rel)
    return salida


def calcular_integridad(sistema: Path) -> dict:
    m = leer_manifiesto(sistema)
    return {"formato": FORMATO_INTEGRIDAD, "algoritmo": "sha256", "sistema": m["id"], "version": m["version"],
            "archivos": {rel: sha256(Path(sistema) / rel) for rel in archivos_del_sistema(sistema)}}


def comprobar_integridad(sistema: Path) -> dict:
    """{"alterados": [...], "faltantes": [...], "añadidos": [...], "errores": [...]}; todo vacío = íntegro."""
    sistema = Path(sistema)
    informe = {"alterados": [], "faltantes": [], "añadidos": [], "errores": []}
    try:
        registro = json.loads((sistema / INTEGRIDAD).read_text(encoding="utf-8"))
        esperados = registro["archivos"]
        m = leer_manifiesto(sistema)
    except (OSError, ValueError, KeyError) as e:
        informe["errores"].append(f"no puedo leer {INTEGRIDAD} o el manifiesto: {e}")
        return informe
    if registro.get("sistema") != m.get("id") or registro.get("version") != m.get("version"):
        informe["errores"].append("INTEGRIDAD.json no corresponde al id/versión del manifiesto")
    presentes = set(archivos_del_sistema(sistema))
    for rel, h in esperados.items():
        if rel not in presentes:
            informe["faltantes"].append(rel)
        elif sha256(sistema / rel) != h:
            informe["alterados"].append(rel)
    informe["añadidos"] = sorted(presentes - set(esperados))
    return informe


def integro(informe: dict) -> bool:
    return not any(informe.values())


# ---------- huella de FLUJO.json (fuera del repo) ----------

def carpeta_casa() -> Path:
    """La carpeta de datos de uxyngraphar de este equipo (misma regla que el instalador)."""
    propia = os.environ.get("UXYNGRAPHAR_HOME")
    if propia:
        return Path(propia).expanduser().resolve()
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "uxyngraphar"
    return Path.home() / ".uxyngraphar"


def ruta_huella_flujo(raiz: Path) -> Path:
    raiz = Path(raiz).resolve()
    clave = hashlib.sha256(str(raiz).encode("utf-8")).hexdigest()[:12]
    return carpeta_casa() / "huellas" / f"{raiz.name}-{clave}.json"


def flujo_cambiado_fuera(raiz: Path) -> bool:
    """FLUJO.json no coincide con la huella que dejó el motor al escribirlo (si hay huella en este equipo)."""
    huella, flujo = ruta_huella_flujo(raiz), Path(raiz) / CARPETA_RAIZ / "FLUJO.json"
    try:
        esperado = json.loads(huella.read_text(encoding="utf-8")).get("FLUJO.json")
    except (OSError, ValueError, AttributeError):
        return False
    actual = sha256(flujo) if flujo.is_file() else None
    return esperado != actual
