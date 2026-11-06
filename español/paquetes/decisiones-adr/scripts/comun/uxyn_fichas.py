"""Fichas de un paquete: crear desde plantilla, listar, cambiar de estado y validar.

Parte del propio paquete (`scripts/comun/`). Los tipos de ficha se declaran en «fichas» del manifiesto.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import uxyn_base as base

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NO_FICHAS = {"INDICE.md", "README.md", "ajustes.json"}


@dataclass
class Ficha:
    tipo: str
    ruta: Path
    id: str
    status: str | None
    titulo: str


def tipos(paquete: Path) -> dict:
    return base.leer_manifiesto(paquete).get("fichas", {})


def definicion(paquete: Path, tipo: str) -> dict:
    t = tipos(paquete)
    if tipo not in t:
        raise ValueError(f"tipo de ficha desconocido «{tipo}»; tipos: {', '.join(t) or '(ninguno)'}")
    return t[tipo]


def _titulo(cuerpo: str, defecto: str) -> str:
    for linea in cuerpo.splitlines():
        if linea.startswith("# "):
            return linea[2:].strip()
    return defecto


def crear(paquete: Path, tipo: str, slug: str, titulo: str = "", subcarpeta: str = "", hoy: date | None = None,
          por_humano: bool = False) -> Path:
    """Crea una ficha nueva con el status inicial del tipo y devuelve su ruta."""
    if not SLUG.match(slug):
        raise ValueError("slug: kebab-case ASCII (a-z, 0-9, guiones)")
    d = definicion(paquete, tipo)
    if d["inicial"] in d.get("solo_humano", []) and not por_humano:
        raise PermissionError(f"las fichas «{tipo}» nacen «{d['inicial']}»: solo las crea una persona (--humano)")
    hoy = hoy or date.today()
    fid = f"{d['prefijo']}-{hoy.strftime('%Y%m%d')}-{slug}"
    raiz = base.carpeta_trabajo(paquete) / d["carpeta"]
    if "estados" in d:
        destino = raiz / d["estados"][d["inicial"]] / f"{fid}.md"
    else:
        if subcarpeta and (".." in Path(subcarpeta).parts or Path(subcarpeta).is_absolute()):
            raise ValueError("subcarpeta: ruta relativa dentro de la carpeta del tipo")
        destino = raiz / subcarpeta / f"{fid}.md"
    if destino.exists() or any(f.id == fid for f in listar(paquete, tipo)):
        raise FileExistsError(f"ya existe la ficha {fid}")
    plantilla = (Path(paquete) / d["plantilla"]).read_text(encoding="utf-8")
    texto = (plantilla.replace("{{id}}", fid).replace("{{fecha}}", hoy.isoformat())
             .replace("{{titulo}}", titulo or slug.replace("-", " ")).replace("{{status}}", d["inicial"]))
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8")
    return destino


def listar(paquete: Path, tipo: str | None = None) -> list[Ficha]:
    salida = []
    trabajo = base.carpeta_trabajo(paquete, crear=False)
    for nombre, d in tipos(paquete).items():
        if tipo and nombre != tipo:
            continue
        raiz = trabajo / d["carpeta"]
        if not raiz.is_dir():
            continue
        for p in sorted(raiz.rglob("*.md")):
            if p.name in NO_FICHAS or p.name.startswith("_"):
                continue
            fm, cuerpo = base.leer_frontmatter(p.read_text(encoding="utf-8"))
            salida.append(Ficha(nombre, p, str(fm.get("id") or p.stem), fm.get("status"), _titulo(cuerpo, p.stem)))
    return salida


def buscar(paquete: Path, fid: str) -> Ficha:
    hallazgos = [f for f in listar(paquete) if f.id == fid or f.ruta.stem == fid]
    if not hallazgos:
        raise FileNotFoundError(f"no encuentro la ficha «{fid}»")
    if len(hallazgos) > 1:
        raise ValueError(f"id ambiguo «{fid}»: {', '.join(str(f.ruta) for f in hallazgos)}")
    return hallazgos[0]


def cambiar_estado(paquete: Path, fid: str, nuevo: str, por_humano: bool = False) -> Path:
    """Pone `status: nuevo` y, en tipos con estados, mueve la ficha a la carpeta de ese estado."""
    f = buscar(paquete, fid)
    d = definicion(paquete, f.tipo)
    if nuevo in d.get("solo_humano", []) and not por_humano:
        raise PermissionError(f"«{nuevo}» solo lo asigna una persona (usa --humano si eres tú)")
    validos = d.get("estados") or {s: None for s in d["status_validos"]}
    if nuevo not in validos:
        raise ValueError(f"status inválido «{nuevo}»; válidos: {', '.join(validos)}")
    texto = base.escribir_campo(f.ruta.read_text(encoding="utf-8"), "status", nuevo)
    destino = f.ruta
    if "estados" in d:
        destino = base.carpeta_trabajo(paquete) / d["carpeta"] / d["estados"][nuevo] / f.ruta.name
        if destino != f.ruta and destino.exists():
            raise FileExistsError(f"ya hay un archivo {destino.name} en {d['estados'][nuevo]}/")
        destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8")
    if destino != f.ruta:
        f.ruta.unlink()
    return destino


def validar(paquete: Path) -> tuple[list[str], list[str]]:
    """(errores, avisos) de todas las fichas del trabajo."""
    errores, avisos = [], []
    trabajo = base.carpeta_trabajo(paquete, crear=False)
    vistos: dict[str, Path] = {}
    for f in listar(paquete):
        d = definicion(paquete, f.tipo)
        rel = f.ruta.relative_to(trabajo).as_posix()
        if f.status is None:
            avisos.append(f"{rel}: sin frontmatter «status»")
            continue
        if f.id in vistos:
            errores.append(f"{rel}: id repetido (también en {vistos[f.id].relative_to(trabajo).as_posix()})")
        vistos[f.id] = f.ruta
        if "estados" in d:
            carpeta_estado = f.ruta.relative_to(trabajo / d["carpeta"]).parts[0]
            if f.status not in d["estados"]:
                errores.append(f"{rel}: status «{f.status}» no válido; válidos: {', '.join(d['estados'])}")
            elif d["estados"][f.status] != carpeta_estado:
                errores.append(f"{rel}: status «{f.status}» debe vivir en {d['estados'][f.status]}/")
        elif f.status not in d["status_validos"]:
            avisos.append(f"{rel}: status «{f.status}» fuera de {', '.join(d['status_validos'])}")
    return errores, avisos
