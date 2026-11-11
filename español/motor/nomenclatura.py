"""Nomenclatura de los sistemas del kit uxyngraphar (norma: NOMENCLATURA.md; vocabulario: nomenclatura.json).

Rige solo lo que pertenece al kit: ids, títulos, familia, prefijos y status de fichas, frases de activación, scripts y
nombres de archivos de los sistemas del catálogo. No se aplica a los proyectos donde se instalan.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

NORMA = json.loads((Path(__file__).resolve().parent / "nomenclatura.json").read_text(encoding="utf-8"))
ID = re.compile(r"^[a-z]+(?:-[a-z]+){1,4}$")
MAX_ID = 40
MAX_DESCRIPCION = 300
PREFIJO = re.compile(r"^[A-Z]{3}$")
SCRIPT = re.compile(r"^(?:verificar-[a-z]+(?:-[a-z]+)*|[a-z]+(?:_[a-z]+)*)\.py$")
DOCUMENTO = re.compile(r"^(?:[a-z0-9]+(?:-[a-z0-9]+)*|[A-Z0-9]+(?:-[A-Z0-9]+)*)\.md$")
FRASE = re.compile(r"^[a-z0-9]+(?:[ -][a-z0-9]+)*$")
README_FRASES = re.compile(r"«(?:usa el sistema de gobernanza|usa el sistema|sigue el protocolo) ([^»]+)»")


def sin_tildes(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def _palabras(frase: str) -> list[str]:
    return frase.replace("-", " ").split()


def _contenida(corta: str, larga: str) -> bool:
    a, b = _palabras(corta), _palabras(larga)
    return any(b[i:i + len(a)] == a for i in range(len(b) - len(a) + 1))


def problemas_id(pid: str) -> list[str]:
    errores = []
    if not ID.match(pid) or len(pid) > MAX_ID:
        return [f"id «{pid}»: de 2 a 5 palabras en minúsculas ASCII sin dígitos, unidas por guiones, máximo {MAX_ID} caracteres"]
    palabras = pid.split("-")
    if palabras[0] in NORMA["verbos"] or palabras[0].startswith("uxyn"):
        errores.append(f"id «{pid}»: empieza por el objeto gobernado, no por un verbo ni por el nombre del kit")
    if palabras[0] in NORMA["palabras_funcion"] or palabras[-1] in NORMA["palabras_funcion"]:
        errores.append(f"id «{pid}»: no empieza ni termina con un enlace")
    for p in palabras:
        if p in NORMA["abreviaturas"]:
            errores.append(f"id «{pid}»: sin abreviaturas («{p}»)")
        elif p in NORMA["palabras_funcion"] and p not in NORMA["enlaces"]:
            errores.append(f"id «{pid}»: enlace «{p}» no permitido (usa {', '.join(NORMA['enlaces'])})")
    return errores


def problemas_titulo(pid: str, titulo: str) -> list[str]:
    if "(" in titulo or ":" in titulo:
        return [f"título «{titulo}»: sin paréntesis ni subtítulos (el matiz va en la descripción)"]
    if sin_tildes(titulo).lower().split() != pid.split("-"):
        return [f"título «{titulo}»: deben ser las palabras del id, en orden, con tildes (p. ej. «{pid.replace('-', ' ').capitalize()}»)"]
    if titulo[:1] != titulo[:1].upper():
        return [f"título «{titulo}»: con mayúscula inicial"]
    return []


def _status(pid: str, d: dict) -> list[str]:
    """Status que usa un tipo de ficha: los de «estados» (con carpeta) y los de «status_validos» (sin carpeta)."""
    return list(dict.fromkeys([*d.get("estados", {}), *(d.get("status_validos") or [])]))


def problemas_sistema(carpeta: Path, m: dict) -> tuple[list[str], list[str]]:
    """(errores, heredados) de un sistema aislado; los heredados son status declarados como pendientes de migrar."""
    pid = m.get("id", "")
    errores = problemas_id(pid) + problemas_titulo(pid, str(m.get("titulo", "")))
    if m.get("familia") not in NORMA["familias"]:
        errores.append(f"familia «{m.get('familia')}»: una de {', '.join(NORMA['familias'])}")
    if len(str(m.get("descripcion", ""))) > MAX_DESCRIPCION:
        errores.append(f"descripción: máximo {MAX_DESCRIPCION} caracteres")
    heredados = []
    validos = set(NORMA["status"]["canonicos"]) | set(NORMA["status"]["complementarios"]) | set(NORMA["status"]["dominio"].get(pid, []))
    declarados = set(NORMA["status"]["heredados"].get(pid, []))
    for tipo, d in m.get("fichas", {}).items():
        if not PREFIJO.match(d.get("prefijo", "")):
            errores.append(f"fichas.{tipo}.prefijo «{d.get('prefijo')}»: exactamente 3 letras mayúsculas")
        elif d["prefijo"] in NORMA["prefijos_reservados"]:
            errores.append(f"fichas.{tipo}.prefijo «{d['prefijo']}»: reservado")
        if d.get("carpeta") in NORMA.get("carpetas_reservadas", []):
            errores.append(f"fichas.{tipo}.carpeta «{d['carpeta']}»: reservada")
        if d.get("plantilla") != f"plantillas/{tipo}.md":
            errores.append(f"fichas.{tipo}.plantilla: debe ser plantillas/{tipo}.md")
        for variante, ruta in d.get("variantes", {}).items():
            if ruta != f"plantillas/{tipo}-{variante}.md":
                errores.append(f"fichas.{tipo}.variantes.{variante}: debe ser plantillas/{tipo}-{variante}.md")
        for s in _status(pid, d):
            if s in validos:
                continue
            if s in declarados:
                heredados.append(f"fichas.{tipo}: status «{s}» heredado (pendiente de pasar al vocabulario)")
            else:
                errores.append(f"fichas.{tipo}: status «{s}» fuera del vocabulario de NOMENCLATURA.md")
    usados = {s for d in m.get("fichas", {}).values() for s in _status(pid, d)}
    for s in sorted(declarados - usados):
        errores.append(f"nomenclatura.json declara el status heredado «{s}», que {pid} ya no usa: quítalo")
    activacion = [str(f) for f in m.get("activacion", [])]
    if activacion[:1] != [pid]:
        errores.append("activacion: la primera frase es el id")
    if pid.replace("-", " ") not in activacion:
        errores.append(f"activacion: falta «{pid.replace('-', ' ')}» (el id con espacios)")
    for frase in activacion:
        if not FRASE.match(frase):
            errores.append(f"activacion «{frase}»: minúsculas ASCII sin tildes ni signos")
        elif len(_palabras(frase)) == 1 and frase not in NORMA["frases_de_una_palabra"]:
            errores.append(f"activacion «{frase}»: al menos dos palabras (o un término de «frases_de_una_palabra»)")
    entrada = Path(carpeta) / "README.md"
    if entrada.is_file():
        texto = entrada.read_text(encoding="utf-8")
        if texto.split("\n", 1)[0] != f"# {m.get('titulo')}":
            errores.append("README.md: la primera línea es «# <título>»")
        for frase in README_FRASES.findall(texto.split("\n## ", 1)[0]):
            if frase not in activacion:
                errores.append(f"README.md cita «{frase}», que no está en activacion")
    scripts = Path(carpeta) / "scripts"
    for s in sorted(scripts.glob("*.py")) if scripts.is_dir() else []:
        if not SCRIPT.match(s.name):
            errores.append(f"scripts/{s.name}: <tema>.py, <tema>_<aspecto>.py o verificar-<tema>.py")
        elif re.split(r"[_.-]", s.name)[0] in NORMA["verbos"] and not s.name.startswith("verificar-"):
            errores.append(f"scripts/{s.name}: el nombre es el tema (sustantivo), no un verbo")
    for sub in ("docs", "plantillas"):
        for f in sorted((Path(carpeta) / sub).rglob("*")) if (Path(carpeta) / sub).is_dir() else []:
            if f.is_file() and not DOCUMENTO.match(f.name):
                errores.append(f"{sub}/{f.relative_to(Path(carpeta) / sub).as_posix()}: kebab-case.md o MAYUSCULAS.md")
            elif f.is_file() and f.name in NORMA.get("archivos_nucleo", []):
                errores.append(f"{sub}/{f.relative_to(Path(carpeta) / sub).as_posix()}: nombre reservado de un archivo del núcleo")
    return errores, heredados


def revisar_catalogo(sistemas: dict[str, tuple[Path, dict]]) -> dict[str, tuple[list[str], list[str]]]:
    """{id: (errores, heredados)} con las reglas de cada sistema y las que cruzan el catálogo."""
    salida = {pid: problemas_sistema(c, m) for pid, (c, m) in sistemas.items()}
    prefijos: dict[str, str] = {}
    frases: dict[str, str] = {}
    for pid, (_, m) in sorted(sistemas.items()):
        for tipo, d in m.get("fichas", {}).items():
            p = d.get("prefijo")
            if p in prefijos and prefijos[p] != f"{pid}.{tipo}":
                salida[pid][0].append(f"fichas.{tipo}.prefijo «{p}»: ya lo usa {prefijos[p]}")
            prefijos.setdefault(p, f"{pid}.{tipo}")
        for otro in sistemas:
            if otro != pid and otro.startswith(pid + "-"):
                salida[pid][0].append(f"id «{pid}»: es prefijo de «{otro}»")
        for frase in m.get("activacion", []):
            if frase in frases and frases[frase] != pid:
                salida[pid][0].append(f"activacion «{frase}»: repetida en {frases[frase]}")
            frases.setdefault(frase, pid)
    for pid, (_, m) in sistemas.items():
        for otro, (_, mo) in sistemas.items():
            if otro == pid:
                continue
            for corta in m.get("activacion", []):
                for larga in mo.get("activacion", []):
                    if corta != larga and _contenida(corta, larga):
                        salida[pid][0].append(f"activacion «{corta}»: está dentro de «{larga}» ({otro})")
    return salida


def singular(palabra: str) -> str:
    if re.search(r"[nrldz]es$", palabra):
        return palabra[:-2]
    return palabra[:-1] if palabra.endswith("s") else palabra


def proponer_prefijo(pid: str, usados: set[str]) -> str:
    palabras = [p for p in pid.split("-") if p not in NORMA["palabras_funcion"]]
    letras = sin_tildes(palabras[0]).upper()
    candidatos = [letras[:3], "".join(p[0] for p in palabras[:3]).upper()]
    candidatos += [letras[0] + a + b for i, a in enumerate(letras[1:]) for b in letras[i + 2:]]
    for c in candidatos:
        if PREFIJO.match(c) and c not in usados and c not in NORMA["prefijos_reservados"]:
            return c
    raise ValueError(f"no encuentro un prefijo libre para «{pid}»: elígelo a mano")
