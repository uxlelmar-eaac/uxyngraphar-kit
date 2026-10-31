"""Ajustes locales (R-25): aplicar en un proyecto una mejora EVO aprobada sin tocar el núcleo del pack.

Un ajuste es una ficha `97-ajustes-locales/AJ-AAAAMMDD-slug.md` (contenido del proyecto, clase C: ninguna
actualización lo toca). Dice qué archivo del núcleo complementa y guarda la huella que ese archivo tenía al crearlo.
Si una versión nueva del pack cambia el archivo, el ajuste queda «por revisar»; si el CHANGELOG del pack cita la EVO,
la mejora ya llegó al pack y el ajuste puede retirarse.
"""

from __future__ import annotations

import hashlib
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "decisiones"))

from common_frontmatter import rebuild_content, split_frontmatter_parts, update_frontmatter_raw  # noqa: E402

CARPETA = "97-ajustes-locales"
ESTADOS = ("activo", "retirado")
ESTADOS_EVO_APLICABLES = ("approved", "done")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,60}$")
ID_RE = re.compile(r"^AJ-\d{8}-[a-z0-9-]+$")
LISTA_INI, LISTA_FIN = "<!-- ajustes:inicio -->", "<!-- ajustes:fin -->"
LONGITUD_HUELLA = 12
PROHIBIDOS = ("95-memoria/", f"{CARPETA}/", "46-evolucion-documentacion/0")   # un ajuste no complementa la memoria, otro ajuste ni una ficha


class ErrorAjuste(Exception):
    pass


@dataclass
class Ajuste:
    ruta: Path
    id: str
    status: str
    evo: str
    aplica_a: list[str]
    huellas: dict[str, str]
    titulo: str = ""
    problemas: list[str] = field(default_factory=list)


def huella(archivo: Path) -> str:
    if not archivo.is_file():
        return "ausente"
    return hashlib.sha256(archivo.read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:LONGITUD_HUELLA]


def _lista(valor: object) -> list[str]:
    if isinstance(valor, list):
        return [str(v) for v in valor if str(v).strip()]
    return [str(valor)] if valor else []


def leer(md: Path) -> Ajuste:
    _raw, fm, cuerpo = split_frontmatter_parts(md.read_text(encoding="utf-8", errors="replace"))
    huellas = {}
    for h in _lista(fm.get("huellas")):
        ruta, _, valor = h.rpartition("@")
        if ruta:
            huellas[ruta] = valor
    m = re.search(r"^# (.+)$", cuerpo, re.M)
    return Ajuste(md, str(fm.get("id") or md.stem), str(fm.get("status") or ""), str(fm.get("evo") or ""),
                  _lista(fm.get("aplica_a")), huellas, m.group(1).strip() if m else md.stem)


def todos(docs: Path) -> list[Ajuste]:
    raiz = docs / CARPETA
    return [leer(md) for md in sorted(raiz.glob("AJ-*.md"))] if raiz.is_dir() else []


def activos_para(docs: Path, rel: str) -> list[Ajuste]:
    """Ajustes activos que complementan el archivo `rel` (relativo a docs/)."""
    rel = rel.strip().strip("`").removeprefix("docs/").partition("#")[0]
    return [a for a in todos(docs) if a.status == "activo" and rel in a.aplica_a]


def _buscar_evo(docs: Path, evo_id: str) -> Path | None:
    for md in sorted((docs / "46-evolucion-documentacion").glob(f"0[1-6]-*/*/{evo_id}.md")):
        return md
    return None


def _validar_destinos(docs: Path, destinos: list[str]) -> list[str]:
    limpios = []
    for d in destinos:
        rel = d.strip().strip("`").removeprefix("docs/").replace("\\", "/")
        if not rel or rel.startswith(("/", "..")) or ".." in rel.split("/"):
            raise ErrorAjuste(f"ruta no válida: «{d}» (relativa a docs/, sin «..»)")
        if rel.startswith(PROHIBIDOS):
            raise ErrorAjuste(f"«{rel}»: un ajuste solo complementa archivos del pack (reglas, guías, plantillas, protocolos)")
        if not (docs / rel).is_file():
            raise ErrorAjuste(f"no existe {rel} en docs/")
        limpios.append(rel)
    if not limpios:
        raise ErrorAjuste("indica al menos un archivo con --a")
    return sorted(set(limpios))


def crear(docs: Path, evo_id: str, destinos: list[str], regla: str, slug: str = "", por: str = "", hoy: date | None = None) -> Path:
    """Crea el ajuste a partir de una EVO aprobada. Marca la EVO con `ajuste_local`. No toca el núcleo."""
    hoy = hoy or date.today()
    evo = _buscar_evo(docs, evo_id)
    if evo is None:
        raise ErrorAjuste(f"no encuentro la ficha {evo_id} en 46-evolucion-documentacion/")
    raw, fm, _c = split_frontmatter_parts(evo.read_text(encoding="utf-8"))
    if str(fm.get("status")) not in ESTADOS_EVO_APLICABLES:
        raise ErrorAjuste(f"{evo_id} está «{fm.get('status')}»: solo se aplica en local una EVO aprobada por una persona (approved)")
    if not regla.strip() or "<escribe" in regla:
        raise ErrorAjuste("falta el texto de la regla local (--texto ARCHIVO o «-» para leerlo de la entrada)")
    rels = _validar_destinos(docs, destinos)
    slug = slug or evo_id.split("-", 2)[-1]
    if not SLUG_RE.match(slug):
        raise ErrorAjuste(f"slug no válido: «{slug}» (minúsculas, números y guiones)")
    ident = f"AJ-{hoy:%Y%m%d}-{slug}"
    destino = docs / CARPETA / f"{ident}.md"
    if destino.exists():
        raise ErrorAjuste(f"ya existe {destino.name}")
    lineas = ["---", f"id: {ident}", "status: activo", f"evo: {evo_id}", "aplica_a:", *[f"  - {r}" for r in rels],
              "huellas:", *[f"  - {r}@{huella(docs / r)}" for r in rels], f"creado: {hoy.isoformat()}",
              f"aprobado_por: {por or 'humano'}", "---", "",
              f"# {ident} — {evo_id}", "",
              "> Ajuste local (R-25). Complementa el núcleo **solo en este proyecto**; el núcleo no se edita. "
              "Si contradice al archivo que complementa, **manda este ajuste**.", "",
              "## Regla local", "", regla.strip(), "",
              "## Complementa a", "", *[f"- `docs/{r}`" for r in rels], "",
              "## Origen", "", f"Ficha `{evo.relative_to(docs).as_posix()}` (aprobada). Retirar: `python3 docs/scripts/ajustes.py retirar {ident}`.", ""]
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(lineas), encoding="utf-8", newline="\n")
    _, _f, cuerpo = split_frontmatter_parts(evo.read_text(encoding="utf-8"))
    evo.write_text(rebuild_content(update_frontmatter_raw(raw or "", {"ajuste_local": ident}), cuerpo), encoding="utf-8", newline="\n")
    escribir_lista(docs)
    return destino


def retirar(docs: Path, ident: str, motivo: str = "", hoy: date | None = None) -> Path:
    hoy = hoy or date.today()
    md = docs / CARPETA / f"{ident}.md"
    if not ID_RE.match(ident) or not md.is_file():
        raise ErrorAjuste(f"no existe el ajuste {ident}")
    raw, _fm, cuerpo = split_frontmatter_parts(md.read_text(encoding="utf-8"))
    cambios = {"status": "retirado", "retirado": hoy.isoformat()}
    if motivo:
        cambios["motivo_retiro"] = '"' + motivo.replace('"', "'") + '"'
    md.write_text(rebuild_content(update_frontmatter_raw(raw or "", cambios), cuerpo), encoding="utf-8", newline="\n")
    escribir_lista(docs)
    return md


def revisar(docs: Path, changelog: Path | None = None) -> list[Ajuste]:
    """Cada ajuste con sus problemas: destino borrado, núcleo cambiado desde que se creó, o la EVO ya llegó al pack."""
    texto_changelog = (changelog or docs / "CHANGELOG.md")
    texto = texto_changelog.read_text(encoding="utf-8", errors="replace") if texto_changelog.is_file() else ""
    salida = []
    for a in todos(docs):
        if a.status not in ESTADOS:
            a.problemas.append(f"status «{a.status}» no válido (activo o retirado)")
        if a.status != "activo":
            salida.append(a)
            continue
        if not a.aplica_a:
            a.problemas.append("no dice qué archivo complementa (aplica_a)")
        for rel in a.aplica_a:
            actual = huella(docs / rel)
            if actual == "ausente":
                a.problemas.append(f"{rel} ya no existe en el pack")
            elif a.huellas.get(rel) and a.huellas[rel] != actual:
                a.problemas.append(f"{rel} cambió con una actualización del pack: revisa si el ajuste sigue haciendo falta")
        if a.evo and a.evo in texto:
            a.problemas.append(f"el CHANGELOG del pack ya cita {a.evo}: la mejora llegó al pack; probablemente puedes retirarlo")
        salida.append(a)
    return salida


def confirmar_revision(docs: Path, ident: str) -> Path:
    """Tras revisar un ajuste «por revisar», guarda las huellas actuales (el ajuste sigue valiendo con el núcleo nuevo)."""
    md = docs / CARPETA / f"{ident}.md"
    if not ID_RE.match(ident) or not md.is_file():
        raise ErrorAjuste(f"no existe el ajuste {ident}")
    a = leer(md)
    texto = md.read_text(encoding="utf-8")
    bloque = re.compile(r"^huellas:\n(?:  - .*\n)*", re.M)
    nuevo = "huellas:\n" + "".join(f"  - {r}@{huella(docs / r)}\n" for r in a.aplica_a)
    md.write_text(bloque.sub(lambda _m: nuevo, texto, count=1), encoding="utf-8", newline="\n")
    return md


def tabla(ajustes: list[Ajuste]) -> str:
    activos = [a for a in ajustes if a.status == "activo"]
    if not activos:
        return "_Ningún ajuste activo._"
    filas = ["| ajuste | complementa a | origen |", "|--------|---------------|--------|"]
    filas += [f"| [{a.id}]({a.ruta.name}) | {', '.join(f'`{r}`' for r in a.aplica_a)} | {a.evo or '—'} |" for a in activos]
    return "\n".join(filas)


def escribir_lista(docs: Path) -> Path | None:
    """Rehace la lista de ajustes activos en INDICE.md, entre sus marcadores (fuera de la zona del pack)."""
    indice = docs / CARPETA / "INDICE.md"
    if not indice.is_file():
        return None
    texto = indice.read_text(encoding="utf-8")
    bloque = f"{LISTA_INI}\n{tabla(todos(docs))}\n{LISTA_FIN}"
    if LISTA_INI in texto and LISTA_FIN in texto:
        antes, resto = texto.split(LISTA_INI, 1)
        nuevo = antes + bloque + resto.split(LISTA_FIN, 1)[1]
    else:
        nuevo = texto.rstrip("\n") + "\n\n## Ajustes activos\n\n" + bloque + "\n"
    if nuevo != texto:
        indice.write_text(nuevo, encoding="utf-8", newline="\n")
    return indice
