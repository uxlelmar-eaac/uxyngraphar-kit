#!/usr/bin/env python3
"""Andamiaje de instrucciones y fichas desde las plantillas del pack (EVO cli-andamiaje).

Uso:  python3 docs/scripts/decisiones/plantillas.py new instruccion --slug login-2fa --acto crear --areas auth
      python3 docs/scripts/decisiones/plantillas.py new mejora|evo|auditoria|propuesta|adr --slug <kebab> [opciones]

Copia la plantilla a `<sección>/<estado>/YYYY-MM-DD/`, rellena id (auto-incrementado donde aplica) y
campos del frontmatter, y pre-valida los enums contra `00-nucleo/frontmatter/`. Nunca sobrescribe.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import rebuild_content, resolve_docs_roots, split_frontmatter_parts, update_frontmatter_raw  # noqa: E402
from common_constantes import ENUMS_FICHA  # noqa: E402

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# alias CLI → (sección, estado inicial, plantilla por defecto, prefijo de id, tipo de enums)
TIPOS = {
    "instruccion": ("05-instrucciones", "01-pendientes", "_PLANTILLA.md", "", "instruccion"),
    "mejora": ("45-mejoras-propuestas", "01-pendientes", "_PLANTILLA-propuesta.md", "MEJ-", "mejora"),
    "evo": ("46-evolucion-documentacion", "01-pendientes", "_PLANTILLA-proceso.md", "EVO-", "evolucion"),
    "auditoria": ("40-auditorias", "02-en-progreso", "_PLANTILLA.md", "AUD-", "auditoria"),
    "propuesta": ("35-herramientas/propuestas", "01-pendientes", "../_PLANTILLA-propuesta.md", "", "herramienta"),
    "adr": ("20-decisiones", "01-pendientes", "_PLANTILLA-ADR.md", "ADR-", "adr"),
}


class ErrorAndamiaje(ValueError):
    """Argumento inválido o plantilla/destino inconsistente."""


def _siguiente(docs: Path, seccion: str, patron: re.Pattern[str]) -> int:
    """Siguiente correlativo NNN según los ids ya presentes (nombre de archivo o `id:` del frontmatter)."""
    usados: list[int] = []
    for md in (docs / seccion).rglob("*.md"):
        m = patron.match(md.stem)
        if not m:
            cabecera = md.read_text(encoding="utf-8", errors="replace")[:1500]
            m = re.search(r"^id:\s*[\"']?" + patron.pattern.lstrip("^"), cabecera, re.M)
        if m:
            usados.append(int(m.group(1)))
    return max(usados, default=0) + 1


LINK_RE = re.compile(r"\]\(([^)\s#]+)(#[^)\s]*)?\)")


def _reubicar_enlaces(cuerpo: str, origen: Path, destino: Path) -> str:
    """Reescribe los enlaces relativos: la ficha vive 2 niveles más abajo que su plantilla (<estado>/<fecha>/)."""

    def cambiar(m: re.Match[str]) -> str:
        objetivo = m.group(1)
        if re.match(r"^([a-z]+:|/)", objetivo):
            return m.group(0)
        absoluto = (origen.parent / objetivo).resolve()
        if not absoluto.exists():
            return m.group(0)
        nuevo = os.path.relpath(absoluto, destino.parent.resolve()).replace(os.sep, "/")
        return f"]({nuevo}{m.group(2) or ''})"

    return LINK_RE.sub(cambiar, cuerpo)


def _lista(valor: str) -> str:
    return "[" + ", ".join(v.strip() for v in valor.split(",") if v.strip()) + "]"


def _validar_enums(enums_tipo: str, campos: dict[str, str]) -> None:
    for clave, valor in campos.items():
        validos = ENUMS_FICHA.get(enums_tipo, {}).get(clave)
        if validos is not None and valor not in validos:
            raise ErrorAndamiaje(f"{clave} «{valor}» no válido; use uno de: {', '.join(sorted(validos))}")


def crear(docs: Path, tipo: str, slug: str, hoy: date | None = None, plantilla: str = "", campos: dict[str, str] | None = None,
          areas: str = "", dry_run: bool = False) -> Path:
    """Crea la ficha y devuelve su ruta. `campos`: enums y textos a fijar en el frontmatter."""
    if tipo not in TIPOS:
        raise ErrorAndamiaje(f"tipo desconocido «{tipo}»; use: {', '.join(TIPOS)}")
    if not SLUG_RE.match(slug):
        raise ErrorAndamiaje(f"slug «{slug}» no es kebab-case (minúsculas, dígitos y guiones)")
    seccion, estado, plantilla_def, prefijo, enums_tipo = TIPOS[tipo]
    campos = dict(campos or {})
    _validar_enums(enums_tipo, campos)
    hoy = hoy or datetime.now(timezone.utc).date()
    iso, compacto = hoy.isoformat(), hoy.strftime("%Y%m%d")
    if plantilla:
        nombre_pl = f"_PLANTILLA-{plantilla}.md"
    elif tipo == "evo" and campos.get("tipo") == "cobertura":
        nombre_pl = "_PLANTILLA-cobertura.md"
    else:
        nombre_pl = plantilla_def
    origen = (docs / seccion / nombre_pl).resolve()
    if not origen.is_file():
        raise ErrorAndamiaje(f"no existe la plantilla {origen}")

    numero = ""
    if tipo == "instruccion":
        patron = re.compile("^" + compacto + r"-(\d{3})")
        numero = f"{_siguiente(docs, seccion, patron):03d}"
        # El id vive en el frontmatter (YYYYMMDD-NNN-slug); el archivo se nombra por slug (R-17).
        ident, nombre = f"{compacto}-{numero}-{slug}", slug
    elif tipo == "adr":
        patron = re.compile(r"^ADR-(\d{3})")
        numero = f"{_siguiente(docs, seccion, patron):03d}"
        ident, nombre = f"ADR-{numero}", f"ADR-{numero}-{slug}"
    elif prefijo:
        ident = nombre = f"{prefijo}{compacto}-{slug}"
    else:
        ident = nombre = slug
    destino = docs / seccion / estado / iso / f"{nombre}.md"
    if destino.exists():
        raise ErrorAndamiaje(f"ya existe {destino}; no se sobrescribe")

    raw, fm, cuerpo = split_frontmatter_parts(origen.read_text(encoding="utf-8"))
    if raw is None:
        raise ErrorAndamiaje(f"la plantilla {origen.name} no tiene frontmatter")
    cambios = {"id": ident}
    for clave in ("proposed_at", "fecha"):
        if clave in fm:
            cambios[clave] = iso
    if "created" in fm:
        cambios["created"] = f"{iso}T00:00:00Z"
    if areas:
        cambios["areas"] = _lista(areas)
    for clave, valor in campos.items():
        cambios[clave] = f'"{valor}"' if clave == "motivo" else valor
    cuerpo = cuerpo.replace("YYYY-MM-DD", iso).replace("YYYYMMDD", compacto)
    if numero:
        cuerpo = cuerpo.replace("NNN", numero)
    cuerpo = _reubicar_enlaces(cuerpo, origen, destino)
    texto = rebuild_content(update_frontmatter_raw(raw, cambios), cuerpo)
    if not dry_run:
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8")
        if tipo == "instruccion":
            _marcar_costo(docs, ident)
    return destino


def _marcar_costo(docs: Path, ident: str) -> None:
    """Abre la fase «Creación de la instrucción» del costo en tokens (10-guias/costo-tokens.md). Nunca falla."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tokens"))
        import costo
        costo.marcar(docs, ident, "instruccion", solo_si_falta=True)
    except Exception:  # noqa: BLE001 - medir el costo nunca debe impedir crear la ficha
        pass


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Andamiaje de fichas desde las plantillas del pack")
    sub = ap.add_subparsers(dest="cmd", required=True)
    nuevo = sub.add_parser("new", help="Crear una ficha nueva")
    nuevo.add_argument("tipo", choices=list(TIPOS))
    nuevo.add_argument("--slug", required=True, help="kebab-case")
    nuevo.add_argument("--areas", default="", help="ids de 25-areas separados por coma")
    nuevo.add_argument("--plantilla", default="", help="variante: p. ej. solo-documentacion, generar-espejo-integral")
    nuevo.add_argument("--fecha", default="", help="YYYY-MM-DD (default: hoy UTC)")
    nuevo.add_argument("--dry-run", action="store_true")
    nuevo.add_argument("--docs", default="", help="raíz del pack (default: autodetectada / DOCS_DIR)")
    for campo in ("acto", "tipo-ficha", "severidad", "prioridad", "impacto", "related-instruction", "motivo"):
        nuevo.add_argument(f"--{campo}", default="")
    a = ap.parse_args(argv)
    mapa = {"acto": a.acto, "tipo": a.tipo_ficha, "severidad": a.severidad, "prioridad": a.prioridad,
            "impacto": a.impacto, "related_instruction": a.related_instruction, "motivo": a.motivo}
    try:
        hoy = date.fromisoformat(a.fecha) if a.fecha else None
        ruta = crear(Path(a.docs).resolve() if a.docs else resolve_docs_roots()[0][0], a.tipo, a.slug, hoy, a.plantilla, {k: v for k, v in mapa.items() if v}, a.areas, a.dry_run)
    except (ErrorAndamiaje, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(("[dry-run] " if a.dry_run else "Creada: ") + str(ruta))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
