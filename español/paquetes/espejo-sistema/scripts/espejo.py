#!/usr/bin/env python3
"""Espejo del sistema.

  python3 uxyngraphar/espejo-sistema/scripts/espejo.py mapa [--faltantes]
  python3 uxyngraphar/espejo-sistema/scripts/espejo.py ver <ruta-del-codigo>
  python3 uxyngraphar/espejo-sistema/scripts/espejo.py nuevo <ruta-del-codigo>
  python3 uxyngraphar/espejo-sistema/scripts/espejo.py huerfanos
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
sys.path.insert(0, str(Path(__file__).resolve().parent))

import espejo_mapa as mapa  # noqa: E402
import uxyn_base as base  # noqa: E402

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)


def relativo(raiz: Path, ruta: str) -> str:
    p = (raiz / ruta).resolve() if not Path(ruta).is_absolute() else Path(ruta).resolve()
    if raiz.resolve() not in p.parents:
        raise ValueError(f"{ruta} está fuera de la app")
    return p.relative_to(raiz.resolve()).as_posix()


def nuevo(rel: str) -> Path:
    raiz = base.raiz_app(PAQUETE)
    origen = raiz / rel
    if not origen.exists():
        raise FileNotFoundError(f"no existe {rel}")
    destino = mapa.ruta_espejo(PAQUETE, rel, origen.is_dir())
    if destino.exists():
        raise FileExistsError(f"ya existe el espejo {destino}")
    plantilla = (PAQUETE / "plantillas" / ("carpeta.md" if origen.is_dir() else "archivo.md")).read_text(encoding="utf-8")
    lineas = 0 if origen.is_dir() else len(origen.read_text(encoding="utf-8", errors="replace").splitlines())
    texto = (plantilla.replace("{{nombre}}", origen.name).replace("{{ruta}}", rel)
             .replace("{{lineas}}", str(lineas)).replace("{{fecha}}", date.today().isoformat()))
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8")
    return destino


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("mapa").add_argument("--faltantes", action="store_true")
    sub.add_parser("ver").add_argument("ruta")
    sub.add_parser("nuevo").add_argument("ruta")
    sub.add_parser("huerfanos")
    a = ap.parse_args(argv)
    raiz = base.raiz_app(PAQUETE)
    ajustes = base.leer_ajustes(PAQUETE)
    try:
        if a.cmd == "mapa":
            archivos, carpetas = mapa.codigo(PAQUETE, ajustes)
            elementos = [(c, True) for c in carpetas] + [(f, False) for f in archivos]
            con = 0
            for rel, es_carpeta in sorted(elementos):
                tiene = mapa.ruta_espejo(PAQUETE, rel, es_carpeta).is_file()
                con += tiene
                if not (a.faltantes and tiene):
                    print(f"{'✓' if tiene else '·'} {rel}{'/' if es_carpeta else ''}")
            print(f"cobertura: {con}/{len(elementos)}")
        elif a.cmd == "ver":
            rel = relativo(raiz, a.ruta)
            ruta = mapa.ruta_espejo(PAQUETE, rel, (raiz / rel).is_dir())
            print(ruta.read_text(encoding="utf-8") if ruta.is_file() else f"sin espejo: {rel} (créalo con «espejo.py nuevo {rel}»)")
        elif a.cmd == "nuevo":
            print(nuevo(relativo(raiz, a.ruta)))
        else:
            for h in mapa.huerfanos(PAQUETE, ajustes):
                print(h)
    except (ValueError, FileNotFoundError, FileExistsError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
