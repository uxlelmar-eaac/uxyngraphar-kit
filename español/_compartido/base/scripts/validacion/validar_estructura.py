"""Validación de estructura: índices, carpetas, estados (R-17), plantillas y scripts."""

from __future__ import annotations

from validar_comun import FECHA_RE, Opciones, Pack, Reporte, leer_ficha

CARPETAS = (
    "00-nucleo", "05-instrucciones", "10-guias", "15-rutas", "20-decisiones", "25-areas",
    "30-manuales", "35-herramientas", "40-auditorias", "45-mejoras-propuestas",
    "46-evolucion-documentacion", "50-sistema-integral", "90-archivo", "95-memoria",
)
SECCIONES_ESTADO = (
    "05-instrucciones", "20-decisiones", "40-auditorias", "45-mejoras-propuestas",
    "46-evolucion-documentacion", "35-herramientas/propuestas",
)
ESTADOS = (
    "01-pendientes", "02-en-progreso", "03-completadas", "04-archivadas",
    "05-canceladas", "06-listas-para-eliminar",
)
PLANTILLAS_CON_FRONTMATTER = ("05-instrucciones/_PLANTILLA.md", "40-auditorias/_PLANTILLA.md")


def validar_indices(pack: Pack, rep: Reporte) -> None:
    for nombre in ("INDICE.md", "PROTOCOLO.md"):
        if not (pack.docs / nombre).is_file():
            rep.fail(f"Falta {pack.docs / nombre}")
    if not any((base / n).is_file() for base in (pack.cwd, pack.docs, pack.docs.parent) for n in ("AGENTES.md", "AGENTS.md")):
        rep.fail("Falta AGENTES.md (o alias AGENTS.md) en la raíz del repo")
    for d in CARPETAS:
        if not (pack.docs / d).is_dir():
            rep.fail(f"Falta carpeta {pack.docs / d}")
        elif not (pack.docs / d / "INDICE.md").is_file():
            rep.warn(f"Sin INDICE: {pack.docs / d / 'INDICE.md'}")
    if not (pack.docs / "00-nucleo" / "registro-ids-compartidos.md").is_file():
        rep.warn("Falta registro-ids-compartidos.md")


def validar_estados(pack: Pack, rep: Reporte) -> None:
    for sec in SECCIONES_ESTADO:
        base = pack.docs / sec
        if not (base / "01-pendientes").is_dir():
            rep.fail(f"Falta carpeta de estado {base / '01-pendientes'}")
        for est in ESTADOS:
            carpeta = base / est
            if not carpeta.is_dir():
                rep.warn(f"Sin estado {est}: {carpeta}")
                continue
            for hijo in sorted(carpeta.iterdir()):
                if hijo.is_dir() and not FECHA_RE.match(hijo.name):
                    rep.warn(f"Subcarpeta sin formato YYYY-MM-DD: {hijo}")
                elif hijo.is_file() and hijo.suffix == ".md" and hijo.name != "README.md":
                    rep.warn(f"Ficha sin carpeta de fecha (R-17): {hijo}")


def validar_plantillas(pack: Pack, rep: Reporte) -> None:
    for rel in PLANTILLAS_CON_FRONTMATTER:
        f = pack.docs / rel
        if not f.is_file():
            continue
        fm, _ = leer_ficha(f)
        if fm is None or "id" not in fm:
            rep.fail(f"Sin id en frontmatter: {f}")
        elif "status" not in fm:
            rep.fail(f"Sin status en frontmatter: {f}")
    sec = pack.docs / "05-instrucciones"
    if sec.is_dir():
        for f in sorted(sec.glob("_PLANTILLA*.md")):
            if "Contrato IA" not in f.read_text(encoding="utf-8"):
                rep.warn(f"Plantilla sin bloque Contrato IA: {f}")


def validar_scripts(pack: Pack, rep: Reporte) -> None:
    """Un script con CRLF no se ejecuta en Linux/macOS (ver .gitattributes)."""
    carpeta = pack.docs / "scripts"
    if not carpeta.is_dir():
        return
    for f in sorted(list(carpeta.glob("*.sh")) + list(carpeta.glob("*.py"))):
        if b"\r" in f.read_bytes():
            rep.fail(f"Finales de línea CRLF en {f} — convertir a LF (.gitattributes: eol=lf)")


def validar(pack: Pack, rep: Reporte, op: Opciones) -> None:
    validar_indices(pack, rep)
    validar_estados(pack, rep)
    validar_plantillas(pack, rep)
    validar_scripts(pack, rep)
