"""La memoria del sistema (R-24): donde termina cada ficha en lugar de borrarse.

docs/95-memoria/<sección>/<AAAA>/<AAAA-MM>/<archivo>.md   la ficha tal cual, con un bloque memoria_* en su frontmatter
docs/95-memoria/catalogo.jsonl                            un apunte por hecho: guardada · recuperada · purgada (solo se añade)
docs/95-memoria/registro-accesos.jsonl                    quién vio, buscó, recuperó o purgó qué y cuándo

Solo se añade: una memoria no se edita. El agente no la lee (reglas deny, archivos de exclusión, herramientas que la
ignoran, puerta y CI); el humano la consulta con `memoria.py`. Este módulo no comprueba quién llama: eso lo hace la CLI.
"""

from __future__ import annotations

import getpass
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

_AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(_AQUI.parent / "decisiones"))

from common import rebuild_content, split_frontmatter_parts, update_frontmatter_raw  # noqa: E402
from depurar import enlaces_entrantes  # noqa: E402

CARPETA = "95-memoria"
CATALOGO, ACCESOS = "catalogo.jsonl", "registro-accesos.jsonl"
FIJOS = {"INDICE.md", CATALOGO, ACCESOS}
SECCIONES = {"05-instrucciones": "instrucciones", "20-decisiones": "decisiones", "40-auditorias": "auditorias",
             "45-mejoras-propuestas": "mejoras", "46-evolucion-documentacion": "evolucion", "35-herramientas/propuestas": "herramientas"}
GUARDABLES = ("03-completadas", "04-archivadas", "05-canceladas", "06-listas-para-eliminar")   # 01 y 02 siguen vivas
FICHA_RE = re.compile(r"^(?P<seccion>" + "|".join(re.escape(s) for s in SECCIONES) + r")/(?P<estado>0[1-6]-[a-z-]+)/(?P<fecha>\d{4}-\d{2}-\d{2})/(?P<nombre>[^/]+\.md)$")
STATUS_RECUPERADA = {"20-decisiones": "obsoleta"}   # el resto de secciones: «archivada» (R-17, 04-archivadas)


class ErrorMemoria(ValueError):
    pass


@dataclass
class Memoria:
    id: str
    titulo: str
    ruta: str          # relativa a docs/
    desde: str         # ruta original, relativa a docs/
    estado_previo: str
    creada: str        # fecha de la carpeta de origen (creación, R-17)
    guardada: str
    motivo: str
    sha256: str


def raiz(docs: Path) -> Path:
    return docs / CARPETA


def _sha(f: Path) -> str:
    return hashlib.sha256(f.read_bytes()).hexdigest()


def _quien() -> str:
    try:
        return getpass.getuser()
    except Exception:  # noqa: BLE001 - sin usuario del sistema (contenedores): se anota igual
        return "desconocido"


def _apuntar(docs: Path, archivo: str, datos: dict) -> None:
    f = raiz(docs) / archivo
    f.parent.mkdir(parents=True, exist_ok=True)
    with f.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps({"fecha": datetime.now().isoformat(timespec="seconds"), **datos}, ensure_ascii=False) + "\n")


def registrar_acceso(docs: Path, accion: str, ident: str = "", detalle: str = "") -> None:
    _apuntar(docs, ACCESOS, {"accion": accion, "id": ident, "detalle": detalle, "usuario": _quien()})


def eventos(docs: Path) -> list[dict]:
    f = raiz(docs) / CATALOGO
    salida = []
    for linea in f.read_text(encoding="utf-8").splitlines() if f.is_file() else []:
        try:
            salida.append(json.loads(linea))
        except ValueError:
            continue
    return salida


def vigentes(docs: Path) -> dict[str, Memoria]:
    """id → memoria que está hoy en la carpeta (guardada y ni recuperada ni purgada después)."""
    estado: dict[str, Memoria] = {}
    for e in eventos(docs):
        if e.get("op") == "guardada":
            estado[e["id"]] = Memoria(**{k: e.get(k, "") for k in Memoria.__dataclass_fields__})
        elif e.get("op") in ("recuperada", "purgada"):
            estado.pop(e.get("id", ""), None)
    return estado


def _titulo(cuerpo: str, defecto: str) -> str:
    return next((l[2:].strip() for l in cuerpo.splitlines() if l.startswith("# ")), defecto)


def _git_rm(docs: Path, f: Path) -> None:
    if subprocess.run(["git", "rm", "-q", "-f", "--", str(f)], cwd=docs, capture_output=True).returncode != 0 and f.exists():
        f.unlink()
    if f.parent.is_dir() and not any(f.parent.iterdir()):
        f.parent.rmdir()


def comprobar_guardable(docs: Path, rel: str) -> re.Match[str]:
    m = FICHA_RE.match(rel)
    if not m:
        raise ErrorMemoria(f"{rel}: solo se guardan fichas de colas (<sección>/<estado>/AAAA-MM-DD/archivo.md)")
    if m["estado"] not in GUARDABLES:
        raise ErrorMemoria(f"{rel}: está viva ({m['estado']}); solo se guardan fichas completadas, archivadas, canceladas o listas para memoria")
    if not (docs / rel).is_file():
        raise ErrorMemoria(f"{rel}: no existe")
    vivos = [e for e in enlaces_entrantes(docs, {rel})[rel] if not e.startswith(("90-archivo/", CARPETA + "/"))]
    if vivos:
        raise ErrorMemoria(f"{rel}: la enlazan {', '.join(vivos)} (quita o cambia esos enlaces por «memoria:ID» antes)")
    return m


def guardar(docs: Path, rel: str, motivo: str, hoy: date | None = None) -> Memoria:
    """Mueve una ficha a la memoria. Primero escribe la copia y su apunte; solo después quita el original."""
    if not motivo.strip():
        raise ErrorMemoria("guardar en memoria exige un motivo")
    m = comprobar_guardable(docs, rel)
    hoy = hoy or date.today()
    origen = docs / rel
    raw, fm, cuerpo = split_frontmatter_parts(origen.read_text(encoding="utf-8"))
    ident = str(fm.get("id") or origen.stem)
    if ident in vigentes(docs):
        raise ErrorMemoria(f"ya hay una memoria con id {ident}")
    marca = {"memoria_desde": rel, "memoria_estado_previo": m["estado"], "memoria_guardada": hoy.isoformat(), "memoria_motivo": json.dumps(motivo.strip(), ensure_ascii=False)}
    texto = rebuild_content(update_frontmatter_raw(raw if raw is not None else f"id: {ident}\n", marca), cuerpo)
    carpeta = raiz(docs) / SECCIONES[m["seccion"]] / f"{hoy:%Y}" / f"{hoy:%Y-%m}"
    destino, n = carpeta / m["nombre"], 2
    while destino.exists():
        destino, n = carpeta / f"{Path(m['nombre']).stem}-{n}.md", n + 1
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8", newline="\n")
    mem = Memoria(ident, _titulo(cuerpo, origen.stem), destino.relative_to(docs).as_posix(), rel, m["estado"], m["fecha"], hoy.isoformat(), motivo.strip(), _sha(destino))
    _apuntar(docs, CATALOGO, {"op": "guardada", **mem.__dict__})
    _git_rm(docs, origen)
    return mem


def buscar(docs: Path, texto: str = "", seccion: str = "") -> list[Memoria]:
    """Busca solo en el catálogo (id, título, motivo, ruta de origen): no abre ninguna ficha."""
    t = texto.lower()
    salida = [m for m in vigentes(docs).values()
              if (not t or t in f"{m.id} {m.titulo} {m.motivo} {m.desde}".lower()) and (not seccion or m.ruta.startswith(f"{CARPETA}/{seccion}/"))]
    return sorted(salida, key=lambda m: (m.guardada, m.id), reverse=True)


def _una(docs: Path, ident: str) -> Memoria:
    mem = vigentes(docs).get(ident)
    if mem is None:
        raise ErrorMemoria(f"no hay ninguna memoria con id {ident} (búscala con: memoria.py buscar TEXTO)")
    return mem


def leer(docs: Path, ident: str) -> str:
    return (docs / _una(docs, ident).ruta).read_text(encoding="utf-8")


def recuperar(docs: Path, ident: str) -> str:
    """Devuelve la ficha a <sección>/04-archivadas/<fecha de creación>/ sin el bloque memoria_*. Devuelve la ruta nueva."""
    mem = _una(docs, ident)
    m = FICHA_RE.match(mem.desde)
    if not m:
        raise ErrorMemoria(f"{ident}: ruta de origen no reconocida ({mem.desde})")
    destino = docs / m["seccion"] / "04-archivadas" / m["fecha"] / m["nombre"]
    if destino.exists():
        raise ErrorMemoria(f"ya existe {destino.relative_to(docs).as_posix()}")
    raw, _fm, cuerpo = split_frontmatter_parts((docs / mem.ruta).read_text(encoding="utf-8"))
    lineas = [l for l in (raw or "").splitlines() if not l.startswith("memoria_")]
    raw = update_frontmatter_raw("\n".join(lineas) + "\n", {"status": STATUS_RECUPERADA.get(m["seccion"], "archivada")})
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(rebuild_content(raw, cuerpo), encoding="utf-8", newline="\n")
    _apuntar(docs, CATALOGO, {"op": "recuperada", "id": ident, "a": destino.relative_to(docs).as_posix(), "usuario": _quien()})
    _git_rm(docs, docs / mem.ruta)
    return destino.relative_to(docs).as_posix()


def purgar(docs: Path, ident: str, motivo: str) -> None:
    """Borrado definitivo (dato sensible). El catálogo guarda solo el id, la fecha y el motivo, nunca el contenido."""
    if not motivo.strip():
        raise ErrorMemoria("purgar exige un motivo")
    mem = _una(docs, ident)
    _apuntar(docs, CATALOGO, {"op": "purgada", "id": ident, "motivo": motivo.strip(), "usuario": _quien()})
    _git_rm(docs, docs / mem.ruta)


def verificar(docs: Path) -> list[str]:
    """Problemas de integridad: memorias tocadas o borradas a mano, o archivos que entraron sin pasar por el catálogo."""
    base = raiz(docs)
    if not base.is_dir():
        return []
    problemas, esperados = [], {}
    for m in vigentes(docs).values():
        esperados[m.ruta] = m
        f = docs / m.ruta
        if not f.is_file():
            problemas.append(f"falta {m.ruta} ({m.id}): se borró sin «memoria.py purgar»")
        elif _sha(f) != m.sha256:
            problemas.append(f"{m.ruta} ({m.id}) cambió: una memoria no se edita")
    for f in sorted(base.rglob("*")):
        rel = f.relative_to(docs).as_posix()
        if f.is_file() and f.name not in FIJOS and rel not in esperados:
            problemas.append(f"{rel} no está en el catálogo: entró sin «memoria.py guardar»")
    return problemas
