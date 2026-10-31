"""Paquete de contexto de una instrucción: todo lo que el agente necesita leer, en un solo bloque y con presupuesto."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "decisiones"))

import alcance  # noqa: E402  (R-21)

sys.path.insert(0, str(AQUI.parent / "ajustes"))
import ajustes_locales as ajustes  # noqa: E402  (R-25)

sys.path.insert(0, str(AQUI.parent / "reglas"))
import reglas_proyecto  # noqa: E402  (96-reglas-proyecto)
from common_frontmatter import split_frontmatter  # noqa: E402
from estimar import extraer_seccion, limpiar, tokens  # noqa: E402

LIMITE_ARCHIVO_SIN_RANGO = 200
RANGO_RE = re.compile(r"^(.*?):(\d+)(?:-(\d+))?$")


@dataclass
class Parte:
    titulo: str
    texto: str
    nota: str = ""

    @property
    def tokens(self) -> int:
        return tokens(self.texto)


@dataclass
class Paquete:
    partes: list[Parte] = field(default_factory=list)
    omitidas: list[Parte] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    bloqueos: list[str] = field(default_factory=list)   # R-21: impiden ejecutar

    @property
    def total(self) -> int:
        return sum(p.tokens for p in self.partes)

    def render(self) -> str:
        sal = [f"BLOQUEADO (R-21): {b}" for b in self.bloqueos]
        if self.bloqueos:
            sal.append("No edites código: corrige la instrucción (fracciona o pide la ampliación) y espera aprobación. "
                       "Guía: docs/00-nucleo/ampliacion-alcance.md\n")
        sal += [f"=== {p.titulo}{' — ' + p.nota if p.nota else ''} ===\n{p.texto.rstrip()}\n" for p in self.partes]
        if self.omitidas:
            sal.append("=== OMITIDO por presupuesto (pídelo explícitamente si lo necesitas) ===\n" + "\n".join(f"- {p.titulo} (~{p.tokens} tokens)" for p in self.omitidas))
        sal += [f"AVISO: {a}" for a in self.avisos]
        sal.append(f"[~{self.total} tokens]")
        return "\n".join(sal)


def localizar_instruccion(docs: Path, ref: str) -> Path | None:
    """`ref`: ruta a la ficha, o id/slug (se busca en 05-instrucciones, ignorando plantillas y archivadas)."""
    directa = Path(ref)
    if directa.is_file():
        return directa.resolve()
    for md in sorted((docs / "05-instrucciones").rglob("*.md")):
        if md.name.startswith("_") or md.name == "README.md" or "/04-" in md.as_posix() or "/06-" in md.as_posix():
            continue
        fm, _, _ = split_frontmatter(md.read_text(encoding="utf-8"))
        if ref in (str(fm.get("id", "")), md.stem) or str(fm.get("id", "")).endswith("-" + ref):
            return md
    return None


def _compactar_frontmatter(fm: dict) -> str:
    return "\n".join(f"{k}: {v}" for k, v in fm.items() if v not in ("", None, [], {}, "null"))


def _ficha(md: Path) -> Parte:
    texto = md.read_text(encoding="utf-8")
    fm, cuerpo, _ = split_frontmatter(texto)
    cuerpo = limpiar(cuerpo)
    corte = re.search(r"^## (Decisión a tomar|Resultado|Anexo)\b", cuerpo, re.M)
    if corte:
        cuerpo = cuerpo[: corte.start()]
    return Parte(f"INSTRUCCIÓN {fm.get('id', md.stem)}", _compactar_frontmatter(fm) + "\n---\n" + cuerpo.strip() + "\n")


def _lista(fm: dict, clave: str) -> list[str]:
    v = fm.get(clave)
    return [str(x) for x in v] if isinstance(v, list) else ([str(v)] if v else [])


def _documento(docs: Path, entrada: str, avisos: list[str]) -> Parte:
    ruta, _, ancla = entrada.partition("#")
    rel = ruta.strip().strip("`").removeprefix("docs/")
    if rel.startswith("95-memoria/") or rel.startswith("memoria:"):   # R-24: la memoria no llega al agente
        avisos.append(f"{entrada}: está en la memoria del sistema; el agente no la lee. Si hace falta, pídesela al humano (R-24)")
        return Parte(entrada, "(memoria del sistema: no disponible para el agente)")
    f = docs / rel
    if not f.is_file():
        avisos.append(f"no existe el documento citado: {entrada}")
        return Parte(entrada, "(no existe)")
    texto = limpiar(f.read_text(encoding="utf-8"))
    if ancla:
        sec = extraer_seccion(texto, ancla)
        if sec is None:
            avisos.append(f"sección «{ancla}» no encontrada en {rel}; se incluye el documento completo")
        else:
            return Parte(f"{rel}#{ancla}", sec, "fragmento")
    return Parte(rel, texto)


def _codigo(repo: Path, ancla: str, avisos: list[str]) -> Parte:
    m = RANGO_RE.match(ancla.strip().strip("`"))
    ruta, a, b = (m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))) if m else (ancla.strip().strip("`"), 0, 0)
    f = repo / ruta
    if not f.is_file():
        avisos.append(f"el ancla de código no existe: {ancla}")
        return Parte(ancla, "(no existe)")
    lineas = f.read_text(encoding="utf-8", errors="replace").splitlines()
    nota = ""
    if a:
        ini, fin = max(a, 1), min(b, len(lineas))
    else:
        ini, fin = 1, min(len(lineas), LIMITE_ARCHIVO_SIN_RANGO)
        if len(lineas) > fin:
            nota = f"solo las primeras {fin} de {len(lineas)} líneas; declara un rango en el ancla"
            avisos.append(f"{ruta}: ancla sin rango en un archivo de {len(lineas)} líneas")
    cuerpo = "\n".join(f"{n:>5}  {lineas[n - 1]}" for n in range(ini, fin + 1))
    return Parte(f"{ruta}:{ini}-{fin}", cuerpo, nota)


def _ajustes_de(docs: Path, entrada: str) -> list[Parte]:
    """R-25: el ajuste local activo de un archivo del núcleo viaja justo detrás de él (y manda sobre él)."""
    partes = []
    for aj in ajustes.activos_para(docs, entrada):
        _fm, cuerpo, _raw = split_frontmatter(aj.ruta.read_text(encoding="utf-8"))
        partes.append(Parte(f"{ajustes.CARPETA}/{aj.ruta.name}", limpiar(cuerpo), f"ajuste local: manda sobre {', '.join(aj.aplica_a)}"))
    return partes


def construir(docs: Path, instruccion: Path, max_tokens: int = 12000, repo: Path | None = None) -> Paquete:
    repo = repo or docs.parent
    fm, _, _ = split_frontmatter(instruccion.read_text(encoding="utf-8"))
    paq = Paquete()
    candidatas = [_ficha(instruccion)]
    reglas = reglas_proyecto.para_anclas(docs, _lista(fm, "anclas_codigo"))
    if reglas:   # solo las que tocan las anclas; cuerpo solo de las bloqueantes (ahorro de tokens)
        candidatas.append(Parte(f"REGLAS DEL PROYECTO ({len(reglas)})", reglas_proyecto.render_contexto(reglas), "96-reglas-proyecto"))
    for e in _lista(fm, "lectura_minima"):
        candidatas.append(_documento(docs, e, paq.avisos))
        candidatas += _ajustes_de(docs, e)
    candidatas += [_documento(docs, e, paq.avisos) for e in _lista(fm, "espejo_leer")]
    candidatas += [_codigo(repo, a, paq.avisos) for a in _lista(fm, "anclas_codigo")]
    try:
        max_docs, max_cod = int(fm.get("presupuesto_max_docs", 8)), int(fm.get("presupuesto_max_archivos_codigo", 5))
    except (TypeError, ValueError):
        max_docs, max_cod = 8, 5
    n_docs = len(_lista(fm, "lectura_minima")) + len(_lista(fm, "espejo_leer"))
    if n_docs > max_docs:
        paq.avisos.append(f"{n_docs} documentos > presupuesto_max_docs={max_docs}")
    if len(_lista(fm, "anclas_codigo")) > max_cod and max_cod <= alcance.ESTANDAR:
        paq.avisos.append(f"{len(_lista(fm, 'anclas_codigo'))} anclas de código > presupuesto_max_archivos_codigo={max_cod}")
    paq.bloqueos = alcance.bloqueos(fm)
    usados = 0
    for parte in candidatas:
        if usados + parte.tokens <= max_tokens or not paq.partes:
            paq.partes.append(parte)
            usados += parte.tokens
        else:
            paq.omitidas.append(parte)
    return paq
