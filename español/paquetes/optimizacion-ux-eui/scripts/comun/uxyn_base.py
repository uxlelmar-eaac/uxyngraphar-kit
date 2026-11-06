"""Base de un paquete de gobernanza uxyngraphar 2.0: rutas, frontmatter, manifiesto e integridad.

Parte del propio paquete (`scripts/comun/`); los paquetes nuevos lo reciben de `paquetes/!base/`. Solo librería estándar.
El paquete vive en `<raiz-app>/uxyngraphar/paquetes/<id>/` y escribe su trabajo en `<raiz-app>/uxyngraphar/trabajo/<id>/`.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

MANIFIESTO = "paquete.json"
INTEGRIDAD = "INTEGRIDAD.json"
ENTRADA = "README.md"
CARPETA_RAIZ = "uxyngraphar"
CARPETA_PAQUETES = "uxyngraphar/paquetes"
CARPETA_TRABAJO = "uxyngraphar/trabajo"
FORMATO_MANIFIESTO = 1
FORMATO_INTEGRIDAD = 1

ID_VALIDO = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
REQUISITO_MOTOR = re.compile(r"^>=\d+\.\d+(?:\.\d+)?$")
CARPETA_ESTADO = re.compile(r"^[a-z]+(?:-[a-z]+)*$")
CARPETA_FICHAS = re.compile(r"^(?:\.|[a-z0-9]+(?:-[a-z0-9]+)*)$")
IGNORAR = re.compile(r"(?:^|/)__pycache__(?:/|$)|\.pyc$|(?:^|/)\.DS_Store$")


# ---------- rutas ----------

def carpeta_paquete(desde: str | Path) -> Path:
    """Carpeta del paquete: la primera, subiendo desde `desde`, que contiene el manifiesto."""
    p = Path(desde).resolve()
    for c in [p, *p.parents]:
        if (c / MANIFIESTO).is_file():
            return c
    raise FileNotFoundError(f"no encuentro {MANIFIESTO} subiendo desde {p}")


def raiz_app(paquete: Path) -> Path:
    """Raíz de la app: `<raiz-app>/uxyngraphar/paquetes/<id>/` → `<raiz-app>`."""
    return paquete.resolve().parents[2]


def carpeta_trabajo(paquete: Path, crear: bool = True) -> Path:
    """`<raiz-app>/uxyngraphar/trabajo/<id>/` (se crea si falta)."""
    destino = raiz_app(paquete) / CARPETA_TRABAJO / leer_manifiesto(paquete)["id"]
    if crear:
        destino.mkdir(parents=True, exist_ok=True)
    return destino


def leer_manifiesto(paquete: Path) -> dict:
    return json.loads((Path(paquete) / MANIFIESTO).read_text(encoding="utf-8"))


def leer_ajustes(paquete: Path) -> dict:
    """Ajustes efectivos: valores por defecto del manifiesto + `uxyngraphar/trabajo/<id>/ajustes.json` del proyecto."""
    efectivos = dict(leer_manifiesto(paquete).get("ajustes", {}))
    archivo = carpeta_trabajo(paquete, crear=False) / "ajustes.json"
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
    for linea in partes[0].splitlines()[1:]:
        linea = linea.split(" #", 1)[0].rstrip()
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
            errores.append(f"{donde}.carpeta: «.» solo vale si el paquete tiene un único tipo de ficha")
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
    return errores


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
        errores.append("motor: requisito «>=X.Y»")
    if not _lista_de_textos(m.get("activacion")):
        errores.append("activacion: lista no vacía de frases")
    elif m.get("id") not in m["activacion"]:
        errores.append("activacion: debe incluir el id del paquete")
    if m.get("entrada") != ENTRADA:
        errores.append(f"entrada: debe ser «{ENTRADA}»")
    verif = m.get("verificaciones")
    if not isinstance(verif, list) or not all(isinstance(v, str) and v.startswith("scripts/") and v.endswith(".py") for v in verif):
        errores.append("verificaciones: lista de «scripts/*.py»")
    if "fichas" in m:
        errores += _validar_fichas(m["fichas"])
    if "ajustes" in m and not isinstance(m["ajustes"], dict):
        errores.append("ajustes: objeto con valores por defecto")
    return errores


# ---------- integridad ----------

def sha256(ruta: Path) -> str:
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def archivos_del_paquete(paquete: Path) -> list[str]:
    """Rutas relativas (con «/») de todo lo que forma el paquete, sin INTEGRIDAD.json ni cachés."""
    base = Path(paquete)
    salida = []
    for p in sorted(base.rglob("*")):
        rel = p.relative_to(base).as_posix()
        if p.is_file() and rel != INTEGRIDAD and not IGNORAR.search(rel):
            salida.append(rel)
    return salida


def calcular_integridad(paquete: Path) -> dict:
    m = leer_manifiesto(paquete)
    return {"formato": FORMATO_INTEGRIDAD, "algoritmo": "sha256", "paquete": m["id"], "version": m["version"],
            "archivos": {rel: sha256(Path(paquete) / rel) for rel in archivos_del_paquete(paquete)}}


def comprobar_integridad(paquete: Path) -> dict:
    """{"alterados": [...], "faltantes": [...], "añadidos": [...], "errores": [...]}; todo vacío = íntegro."""
    paquete = Path(paquete)
    informe = {"alterados": [], "faltantes": [], "añadidos": [], "errores": []}
    try:
        registro = json.loads((paquete / INTEGRIDAD).read_text(encoding="utf-8"))
        esperados = registro["archivos"]
        m = leer_manifiesto(paquete)
    except (OSError, ValueError, KeyError) as e:
        informe["errores"].append(f"no puedo leer {INTEGRIDAD} o el manifiesto: {e}")
        return informe
    if registro.get("paquete") != m.get("id") or registro.get("version") != m.get("version"):
        informe["errores"].append("INTEGRIDAD.json no corresponde al id/versión del manifiesto")
    presentes = set(archivos_del_paquete(paquete))
    for rel, h in esperados.items():
        if rel not in presentes:
            informe["faltantes"].append(rel)
        elif sha256(paquete / rel) != h:
            informe["alterados"].append(rel)
    informe["añadidos"] = sorted(presentes - set(esperados))
    return informe


def integro(informe: dict) -> bool:
    return not any(informe.values())
