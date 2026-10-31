#!/usr/bin/env python3
"""Validación ligera de documentación del pack (solo stdlib; Windows, Linux y macOS).

Uso (desde la raíz del repo):  python3 docs/scripts/validar-documentacion.py [ruta-docs]
Salida: 0 = OK (puede haber WARN) · 1 = errores.
Variables: DOCS_DIR, DECISIONES_MAX_DAYS y los interruptores STRICT_* (ver 10-guias/ci-validacion-documentacion.md).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "validacion"))

import validar_enlaces  # noqa: E402
import validar_estructura  # noqa: E402
import validar_fichas  # noqa: E402
import validar_pack  # noqa: E402
import validar_vinculos  # noqa: E402
from validar_comun import Pack, Reporte, detectar_tipo, opciones_desde_entorno, resolver_docs  # noqa: E402


def validar(pack: Pack, rep: Reporte, op) -> None:
    validar_estructura.validar(pack, rep, op)
    validar_enlaces.validar(pack, rep)
    validar_pack.validar_decisiones_antiguas(pack, rep, op)
    fichas = validar_fichas.validar(pack, rep, op)
    validar_vinculos.validar(fichas, rep, op)
    validar_pack.validar_cliente_autocontenido(pack, rep, op)


def main(argv: list[str] | None = None) -> int:
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            try:
                flujo.reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, OSError):
                pass
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] in (["-h"], ["--help"]):
        print(__doc__)
        return 0
    entorno = dict(os.environ)
    if argv:
        entorno["DOCS_DIR"] = argv[0]
    cwd = Path.cwd()
    docs = resolver_docs(entorno, cwd)
    pack = Pack(docs=docs, cwd=cwd, tipo=detectar_tipo(docs, cwd))
    op = opciones_desde_entorno(entorno)
    rep = Reporte()
    print(f"Validando documentación {'cliente ' if pack.tipo == 'cliente' else ''}en: {docs}")
    if not docs.is_dir():
        rep.fail(f"No existe la carpeta de documentación: {docs}")
    else:
        validar(pack, rep, op)
    if rep.errores:
        print("FALLÓ: corregir ERROR arriba.")
        return 1
    print("OK: validación completada (revisar WARN si hay).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
