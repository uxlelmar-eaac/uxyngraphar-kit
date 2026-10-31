"""Utilidades comunes del validador de documentación (solo stdlib).

Comparte el parser de frontmatter con el tooling `decisiones` (misma semántica YAML).
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator, Mapping

_DECISIONES = Path(__file__).resolve().parent.parent / "decisiones"
if str(_DECISIONES) not in sys.path:
    sys.path.insert(0, str(_DECISIONES))

from common_constantes import FRONTMATTER_RE  # noqa: E402
from common_frontmatter import parse_simple_yaml  # noqa: E402

IGNORAR_DIRS = {".git", ".decisiones", "__pycache__", "node_modules", "95-memoria"}   # memoria: R-24, no se lee
FECHA_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass
class Opciones:
    """Interruptores `STRICT_*`: con 1 el aviso correspondiente pasa a error."""

    decisiones: bool = False
    vinculos: bool = False
    presupuesto: bool = False
    cliente: bool = False
    estados: bool = False
    ids: bool = False
    max_dias_decisiones: int = 30


def opciones_desde_entorno(env: Mapping[str, str] | None = None) -> Opciones:
    env = os.environ if env is None else env
    todo = env.get("STRICT_ALL", "0") == "1"

    def flag(nombre: str) -> bool:
        return todo or env.get(nombre, "0") == "1"

    try:
        dias = int(env.get("DECISIONES_MAX_DAYS", "30") or 30)
    except ValueError:
        dias = 30
    return Opciones(
        decisiones=flag("STRICT_DECISIONES"),
        vinculos=flag("STRICT_VINCULOS"),
        presupuesto=flag("STRICT_PRESUPUESTO"),
        cliente=flag("STRICT_CLIENTE_STANDALONE"),
        estados=flag("STRICT_ESTADOS"),
        ids=flag("STRICT_IDS"),
        max_dias_decisiones=dias,
    )


@dataclass
class Reporte:
    """Acumula avisos y errores; imprime en stderr como el validador .sh original."""

    imprimir: bool = True
    errores: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)

    def warn(self, mensaje: str) -> None:
        self.avisos.append(mensaje)
        if self.imprimir:
            print(f"WARN: {mensaje}", file=sys.stderr)

    def fail(self, mensaje: str) -> None:
        self.errores.append(mensaje)
        if self.imprimir:
            print(f"ERROR: {mensaje}", file=sys.stderr)

    def segun(self, estricto: bool, mensaje: str) -> None:
        (self.fail if estricto else self.warn)(mensaje)


@dataclass
class Pack:
    docs: Path  # raíz de la documentación (carpeta con 00-nucleo/, 05-instrucciones/, …)
    cwd: Path  # raíz del repo desde donde se ejecuta (busca AGENTES.md)
    tipo: str = "servidor"  # «servidor» o «cliente», según AGENTES.md


def resolver_docs(entorno: Mapping[str, str], cwd: Path) -> Path:
    elegido = entorno.get("DOCS_DIR")
    if elegido:
        return (cwd / elegido).resolve()
    if (cwd / "INDICE.md").is_file() and not (cwd / "docs" / "INDICE.md").is_file():
        return cwd.resolve()
    return (cwd / "docs").resolve()


def detectar_tipo(docs: Path, cwd: Path) -> str:
    """«cliente» si el título de AGENTES.md lo dice; «servidor» en cualquier otro caso."""
    for base in (docs, docs.parent, cwd):
        for nombre in ("AGENTES.md", "AGENTS.md"):
            f = base / nombre
            if f.is_file():
                primera = f.read_text(encoding="utf-8").splitlines()[:1]
                if primera and "cliente" in primera[0].lower():
                    return "cliente"
                if primera and "servidor" in primera[0].lower():
                    return "servidor"
    return "servidor"


def iter_md(docs: Path) -> Iterator[Path]:
    for p in sorted(docs.rglob("*.md")):
        if not (set(p.relative_to(docs).parts) & IGNORAR_DIRS):
            yield p


def leer_ficha(path: Path) -> tuple[dict[str, Any] | None, str]:
    """(frontmatter | None si no hay, cuerpo)."""
    texto = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(texto)
    if not m:
        return None, texto
    return parse_simple_yaml(m.group(1)), texto[m.end():]


def lista(fm: Mapping[str, Any], clave: str) -> list[str]:
    valor = fm.get(clave)
    if valor is None or valor == "":
        return []
    if isinstance(valor, list):
        return [str(v) for v in valor if str(v).strip()]
    return [str(valor)]


def sin_codigo(texto: str) -> str:
    """Quita bloques de código y código en línea (los ejemplos no cuentan como enlaces)."""
    texto = re.sub(r"^(```|~~~).*?^\1[^\n]*$", "", texto, flags=re.S | re.M)
    return re.sub(r"`[^`\n]*`", "", texto)
