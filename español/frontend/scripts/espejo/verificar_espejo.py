"""Detección de deriva del espejo 50 vs código (EVO deriva-espejo; opt-in, WARN por defecto).

Compara el diff de un PR (o del commit en curso) con lo que declaran las instrucciones tocadas:
`anclas_codigo` y `espejo_actualizar`. No juzga contenido: solo comprueba que lo declarado se movió.
"""

from __future__ import annotations

import fnmatch
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

_DECISIONES = Path(__file__).resolve().parent.parent / "decisiones"
if str(_DECISIONES) not in sys.path:
    sys.path.insert(0, str(_DECISIONES))

import alcance  # noqa: E402  (R-21)
from common_frontmatter import parse_simple_yaml  # noqa: E402
from common_constantes import FRONTMATTER_RE  # noqa: E402

# Archivos que no son «código del producto»: no exigen instrucción ni espejo.
IGNORAR_POR_DEFECTO = (
    "README*", "LICENSE*", "CHANGELOG*", ".gitignore", ".gitattributes", ".editorconfig", ".github/*", ".claude/*",
    "*.lock", "package-lock.json", "*.md",
)
ESTADOS_INSTRUCCION = ("02-en-progreso", "03-completadas")


@dataclass
class Instruccion:
    id: str
    rel: str
    status: str
    anclas: list[str]
    espejo: list[str]
    maximo: int = alcance.ESTANDAR                       # tope de archivos de código (R-21)
    bloqueos: list[str] = field(default_factory=list)    # R-21 incumplida


@dataclass
class Hallazgo:
    regla: str
    mensaje: str


def _ruta_ancla(ancla: str) -> str:
    """`src/a.ts:40-80` → `src/a.ts` (también acepta rutas de Windows con `C:`)."""
    base, _, rango = ancla.rpartition(":")
    return base if base and rango.replace("-", "").isdigit() else ancla


def _bajo_docs(ruta: str, docs: str) -> str:
    ruta = ruta.strip().replace("\\", "/")
    return ruta if ruta.startswith(docs + "/") else f"{docs}/{ruta.removeprefix('docs/')}"


def es_codigo(ruta: str, docs: str, ignorar: tuple[str, ...] = IGNORAR_POR_DEFECTO) -> bool:
    if ruta.startswith(docs + "/"):
        return False
    return not any(fnmatch.fnmatch(ruta, p) or fnmatch.fnmatch(Path(ruta).name, p) for p in ignorar)


def leer_instruccion(repo: Path, rel: str) -> Instruccion | None:
    archivo = repo / rel
    if not archivo.is_file():
        return None
    m = FRONTMATTER_RE.match(archivo.read_text(encoding="utf-8"))
    if not m:
        return None
    fm = parse_simple_yaml(m.group(1))

    def lista(clave: str) -> list[str]:
        v = fm.get(clave)
        return [str(x) for x in v] if isinstance(v, list) else ([str(v)] if v else [])

    return Instruccion(str(fm.get("id", Path(rel).stem)), rel, str(fm.get("status", "")), lista("anclas_codigo"), lista("espejo_actualizar"),
                       alcance.leer(fm).maximo, alcance.bloqueos(fm))


def analizar(cambiados: list[str], instrucciones: list[Instruccion], docs: str, ignorar: tuple[str, ...] = IGNORAR_POR_DEFECTO) -> list[Hallazgo]:
    codigo = sorted(r for r in cambiados if es_codigo(r, docs, ignorar))
    if not codigo:
        return []
    h: list[Hallazgo] = []
    if not instrucciones:
        h.append(Hallazgo("R-03", f"Código tocado ({len(codigo)} archivo(s), p. ej. {codigo[0]}) sin una instrucción en {ESTADOS_INSTRUCCION[0]}/ o {ESTADOS_INSTRUCCION[1]}/ dentro del cambio."))
        return h
    declarados = {_ruta_ancla(a).replace("\\", "/") for i in instrucciones for a in i.anclas}
    fuera = [c for c in codigo if not any(c == d or c.startswith(d.rstrip("/") + "/") for d in declarados)]
    if fuera:
        h.append(Hallazgo("anclas", f"Código fuera de las anclas_codigo declaradas: {', '.join(fuera[:5])}{'…' if len(fuera) > 5 else ''}"))
    for i in instrucciones:
        h += [Hallazgo("R-21", f"{i.id}: {b}") for b in i.bloqueos]
    tope = sum(i.maximo for i in instrucciones)
    if len(codigo) > tope:
        h.append(Hallazgo("R-21", f"{len(codigo)} archivos de código en el cambio > {tope} que permiten sus instrucciones: "
                                  "fracciona en entregas más pequeñas o pide ampliación aprobada (1.5–2×)."))
    cambiados_set = set(cambiados)
    for i in instrucciones:
        if i.anclas and not i.espejo:
            h.append(Hallazgo("espejo", f"{i.id}: declara anclas_codigo pero no espejo_actualizar."))
        for e in i.espejo:
            destino = _bajo_docs(e, docs)
            if destino not in cambiados_set:
                h.append(Hallazgo("espejo", f"{i.id}: el espejo declarado no cambió en este diff: {destino}"))
    return h


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", "-c", "core.quotePath=false", *args], cwd=repo, capture_output=True)   # rutas con acentos sin escapar


def raiz_repo(cwd: Path) -> Path | None:
    r = _git(cwd, "rev-parse", "--show-toplevel")
    return Path(r.stdout.decode().strip()) if r.returncode == 0 else None


def cambiados_git(repo: Path, base: str, staged: bool) -> list[str] | None:
    """Rutas cambiadas (relativas a la raíz del repo) o None si no se puede resolver la base."""
    intentos = [("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z")] if staged else [
        ("diff", f"{base}...HEAD", "--name-only", "--diff-filter=ACMR", "-z"),
        ("diff", base, "--name-only", "--diff-filter=ACMR", "-z"),
    ]
    for args in intentos:
        r = _git(repo, *args)
        if r.returncode == 0:
            return [p for p in r.stdout.decode("utf-8").split("\0") if p]
    return None


def instrucciones_del_cambio(repo: Path, cambiados: list[str], docs: str) -> list[Instruccion]:
    salida: list[Instruccion] = []
    for rel in cambiados:
        partes = rel.split("/")
        if rel.startswith(f"{docs}/05-instrucciones/") and any(e in partes for e in ESTADOS_INSTRUCCION) and rel.endswith(".md") \
                and not partes[-1].startswith("_") and partes[-1] != "README.md":
            ins = leer_instruccion(repo, rel)
            if ins:
                salida.append(ins)
    return salida
