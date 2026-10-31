#!/usr/bin/env python3
"""Ajustes locales (R-25): aplicar en este proyecto una mejora EVO aprobada sin editar el núcleo del pack.

El ajuste vive en docs/97-ajustes-locales/ (contenido del proyecto: ninguna actualización lo toca) y el agente lo sigue
cuando trabaja con el archivo del núcleo que complementa. Lo crea y lo retira una persona.

Uso:  python3 docs/scripts/ajustes.py crear --evo EVO-ID --a 10-guias/guia.md [--a …] --texto regla.md [--slug s] [--por NOMBRE]
      python3 docs/scripts/ajustes.py listar
      python3 docs/scripts/ajustes.py verificar           # tras actualizar: qué ajustes hay que revisar
      python3 docs/scripts/ajustes.py revisado AJ-ID      # el ajuste sigue valiendo con el núcleo nuevo
      python3 docs/scripts/ajustes.py retirar AJ-ID [--motivo "…"]
  --texto   archivo con la regla local, o «-» para leerla de la entrada estándar
Salida: 0 · 1 si `verificar` encuentra ajustes por revisar · 2 si la orden no se pudo hacer.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "ajustes"))

import ajustes_locales as almacen  # noqa: E402


def _texto(origen: str) -> str:
    if origen == "-":
        return sys.stdin.read()
    return Path(origen).read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("orden", choices=("crear", "listar", "verificar", "revisado", "retirar"))
    ap.add_argument("ajuste", nargs="?", help="id del ajuste (revisado, retirar)")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--evo", help="ficha EVO aprobada de la que sale el ajuste")
    ap.add_argument("--a", action="append", default=[], dest="destinos", metavar="RUTA", help="archivo del pack (relativo a docs/) que complementa")
    ap.add_argument("--texto", help="archivo con la regla local, o «-»")
    ap.add_argument("--slug", default="")
    ap.add_argument("--por", default=os.environ.get("UXYNGRAPHAR_HUMANO", ""), help="quién lo aprueba (por defecto UXYNGRAPHAR_HUMANO)")
    ap.add_argument("--motivo", default="")
    a = ap.parse_args(argv)
    docs = Path(a.repo).resolve() / a.docs
    try:
        if a.orden == "crear":
            if not a.evo or not a.texto:
                raise almacen.ErrorAjuste("crear necesita --evo y --texto")
            ruta = almacen.crear(docs, a.evo, a.destinos, _texto(a.texto), a.slug, a.por)
            print(f"Ajuste creado: {ruta.relative_to(docs.parent).as_posix()}. El núcleo no cambió; el agente seguirá este ajuste.")
            return 0
        if a.orden in ("retirar", "revisado"):
            if not a.ajuste:
                raise almacen.ErrorAjuste(f"{a.orden} necesita el id del ajuste (AJ-…)")
            if a.orden == "retirar":
                almacen.retirar(docs, a.ajuste, a.motivo)
                print(f"{a.ajuste} retirado: el agente vuelve a seguir solo el núcleo.")
            else:
                almacen.confirmar_revision(docs, a.ajuste)
                print(f"{a.ajuste}: huellas al día; sigue activo.")
            return 0
    except (almacen.ErrorAjuste, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    revisados = almacen.revisar(docs)
    if a.orden == "listar":
        if not revisados:
            print("Sin ajustes locales.")
        for aj in revisados:
            marca = "por revisar" if aj.problemas else aj.status
            print(f"{aj.id:<40} {marca:<12} {', '.join(aj.aplica_a)}  ({aj.evo or 'sin EVO'})")
        return 0
    pendientes = [aj for aj in revisados if aj.problemas]
    for aj in pendientes:
        for p in aj.problemas:
            print(f"REVISAR {aj.id}: {p}")
    if pendientes:
        print("Decide en cada uno: `ajustes.py revisado ID` (sigue valiendo) o `ajustes.py retirar ID` (ya no hace falta).")
        return 1
    print(f"OK: {sum(1 for aj in revisados if aj.status == 'activo')} ajuste(s) activo(s) al día.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
