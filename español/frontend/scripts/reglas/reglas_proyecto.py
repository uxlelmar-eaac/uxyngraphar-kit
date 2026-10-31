"""Reglas del proyecto (`96-reglas-proyecto/`): reglas que el equipo pone a su propio código, fuera del núcleo.

No son reglas del núcleo (R-xx): el núcleo solo indica dónde están y cómo se aplican. Cada regla es una ficha
`96-reglas-proyecto/RP-NNN.md` (contenido del proyecto, clase C). El agente lee por defecto solo `INDICE.md`;
`contexto.py` le añade las reglas que tocan las anclas de su instrucción, y `controlar.py` evalúa sin IA las que
traen `comprobacion_prohibido` / `comprobacion_obligatorio`. Guía: 96-reglas-proyecto/_PROTOCOLO.md.
"""

from __future__ import annotations

import fnmatch
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "decisiones"))

from common_frontmatter import split_frontmatter_parts  # noqa: E402

CARPETA = "96-reglas-proyecto"
ESTADOS = ("activa", "retirada")
NIVELES = ("bloqueante", "aviso")
ID_RE = re.compile(r"^RP-\d{3}$")
EXCEPCION_RE = re.compile(r"^\s*(RP-\d{3})\s*:\s*(\S.*)$")
LISTA_INI, LISTA_FIN = "<!-- reglas:inicio -->", "<!-- reglas:fin -->"
# Valores de `reglas_proyecto` en uxyngraphar.config.json.
MODOS_EXCEPCION = ("en_instruccion", "ficha_aparte", "prohibidas")
MODOS_CAMBIO = ("instruccion_aprobada", "solo_humano")
ESTADOS_INSTRUCCION_APROBADA = ("approved", "executing", "done")
ESTADOS_FICHA_EXCEPCION = ("aprobada", "pendiente", "rechazada")


@dataclass
class Regla:
    ruta: Path
    id: str
    titulo: str
    status: str
    nivel: str
    aplica_a: list[str]
    resumen: str
    prohibido: str = ""
    obligatorio: str = ""
    cuerpo: str = ""
    problemas: list[str] = field(default_factory=list)

    @property
    def activa(self) -> bool:
        return self.status == "activa" and not self.problemas


def _texto(v: object) -> str:
    return "" if v is None else str(v).strip()


def _lista(v: object) -> list[str]:
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    return [_texto(v)] if _texto(v) else []


def leer(md: Path) -> Regla:
    raw, fm, cuerpo = split_frontmatter_parts(md.read_text(encoding="utf-8", errors="replace"))
    r = Regla(md, _texto(fm.get("id")), _texto(fm.get("titulo")), _texto(fm.get("status")), _texto(fm.get("nivel")),
              _lista(fm.get("aplica_a")), _texto(fm.get("resumen")), _texto(fm.get("comprobacion_prohibido")),
              _texto(fm.get("comprobacion_obligatorio")), cuerpo.strip())
    if raw is None:
        r.problemas.append("sin frontmatter")
    if not ID_RE.match(r.id):
        r.problemas.append(f"id «{r.id}»: use RP-NNN")
    elif md.stem != r.id:
        r.problemas.append(f"el archivo debe llamarse {r.id}.md")
    if r.status not in ESTADOS:
        r.problemas.append(f"status «{r.status}»: {' | '.join(ESTADOS)}")
    if r.nivel not in NIVELES:
        r.problemas.append(f"nivel «{r.nivel}»: {' | '.join(NIVELES)}")
    if not r.aplica_a:
        r.problemas.append("aplica_a vacío: lista de globs de código (p. ej. src/**/*.ts)")
    if not r.titulo or not r.resumen:
        r.problemas.append("faltan titulo o resumen (una línea)")
    for nombre, patron in (("comprobacion_prohibido", r.prohibido), ("comprobacion_obligatorio", r.obligatorio)):
        if patron:
            try:
                re.compile(patron)
            except re.error as exc:
                r.problemas.append(f"{nombre}: regex inválida ({exc})")
    return r


def todas(docs: Path) -> list[Regla]:
    carpeta = docs / CARPETA
    return [leer(md) for md in sorted(carpeta.glob("RP-*.md"))] if carpeta.is_dir() else []


def activas(docs: Path) -> list[Regla]:
    return [r for r in todas(docs) if r.activa]


def coincide(ruta: str, globs: list[str]) -> bool:
    """`src/**/*.ts` también cubre `src/a.ts` (el `**` puede ser vacío)."""
    ruta = ruta.replace("\\", "/")
    return any(fnmatch.fnmatch(ruta, g) or fnmatch.fnmatch(ruta, g.replace("/**/", "/")) for g in globs)


def ruta_de_ancla(ancla: str) -> str:
    """`src/a.ts:40-80` → `src/a.ts`."""
    base, _, rango = ancla.rpartition(":")
    return base if base and rango.replace("-", "").isdigit() else ancla


def para_anclas(docs: Path, anclas: list[str]) -> list[Regla]:
    """Reglas activas cuyo `aplica_a` toca alguna de las anclas de código de una instrucción."""
    rutas = [ruta_de_ancla(a) for a in anclas]
    return [r for r in activas(docs) if any(coincide(x, r.aplica_a) for x in rutas)]


def render_contexto(reglas: list[Regla]) -> str:
    """Bloque compacto para contexto.py: id, nivel y resumen; el cuerpo solo de las bloqueantes (ahorro de tokens)."""
    lineas = []
    for r in reglas:
        lineas.append(f"- {r.id} [{r.nivel}] {r.resumen}")
        if r.nivel == "bloqueante" and r.cuerpo:
            lineas += [f"  {l}" for l in r.cuerpo.splitlines() if l.strip()]
    lineas.append("Excepción: solo declarada en `excepciones_reglas` de la instrucción («RP-NNN: motivo») y aprobada por una persona.")
    return "\n".join(lineas) + "\n"


def filas_indice(reglas: list[Regla]) -> list[str]:
    return [f"| {r.id} | {r.nivel} | {', '.join(f'`{g}`' for g in r.aplica_a)} | {r.resumen} |" for r in reglas if r.activa]


def indice_esperado(docs: Path, texto: str) -> str:
    """INDICE.md con la tabla entre marcadores regenerada desde las reglas activas (el resto del archivo se conserva)."""
    filas = filas_indice(todas(docs)) or ["| — | — | — | (sin reglas activas) |"]
    bloque = "\n".join([LISTA_INI, "| id | nivel | aplica_a | resumen |", "|----|-------|----------|---------|", *filas, LISTA_FIN])
    if LISTA_INI in texto and LISTA_FIN in texto:
        antes, resto = texto.split(LISTA_INI, 1)
        return antes + bloque + resto.split(LISTA_FIN, 1)[1]
    return texto.rstrip("\n") + "\n\n" + bloque + "\n"


def regenerar_indice(docs: Path) -> bool:
    """Pone al día INDICE.md. True si cambió."""
    f = docs / CARPETA / "INDICE.md"
    actual = f.read_text(encoding="utf-8") if f.is_file() else "# Reglas del proyecto — índice\n"
    nuevo = indice_esperado(docs, actual)
    if nuevo == actual:
        return False
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(nuevo, encoding="utf-8", newline="\n")
    return True


def indice_al_dia(docs: Path) -> bool:
    f = docs / CARPETA / "INDICE.md"
    return not f.is_file() or indice_esperado(docs, f.read_text(encoding="utf-8")) == f.read_text(encoding="utf-8")


def incumplimiento(regla: Regla, texto: str) -> str:
    """Motivo si el texto de un archivo incumple la comprobación de la regla ("" si cumple o no hay comprobación)."""
    if regla.prohibido:
        for n, linea in enumerate(texto.splitlines(), 1):
            if re.search(regla.prohibido, linea):
                return f"línea {n} contiene lo prohibido ({regla.prohibido})"
    if regla.obligatorio and not re.search(regla.obligatorio, texto, re.M):
        return f"falta lo obligatorio ({regla.obligatorio})"
    return ""


def excepciones(fm: dict) -> tuple[dict[str, str], list[str]]:
    """`excepciones_reglas` de una instrucción → ({RP-NNN: motivo}, problemas de formato)."""
    salida, problemas = {}, []
    for item in _lista(fm.get("excepciones_reglas")):
        m = EXCEPCION_RE.match(item)
        if m:
            salida[m.group(1)] = m.group(2)
        else:
            problemas.append(f"excepciones_reglas «{item}»: use «RP-NNN: motivo»")
    return salida, problemas


def fichas_excepcion_aprobadas(docs: Path) -> set[tuple[str, str]]:
    """Modo `ficha_aparte`: pares (regla, instrucción) con ficha `EX-*.md` en status aprobada."""
    salida = set()
    carpeta = docs / CARPETA
    for md in sorted(carpeta.glob("EX-*.md")) if carpeta.is_dir() else []:
        _raw, fm, _c = split_frontmatter_parts(md.read_text(encoding="utf-8", errors="replace"))
        if _texto(fm.get("status")) == "aprobada":
            salida.add((_texto(fm.get("regla")), _texto(fm.get("instruccion"))))
    return salida


def config(cfg: dict) -> tuple[str, str]:
    rp = cfg.get("reglas_proyecto") or {}
    return rp.get("excepciones", "en_instruccion"), rp.get("cambios_reglas", "instruccion_aprobada")
