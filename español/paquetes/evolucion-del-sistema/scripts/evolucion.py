#!/usr/bin/env python3
"""Evolución del sistema: matriz de cobertura y exportación de EVO para llevarlas al catálogo.

  python3 uxyngraphar/paquetes/evolucion-del-sistema/scripts/evolucion.py matriz                crea la matriz si falta y la muestra
  python3 uxyngraphar/paquetes/evolucion-del-sistema/scripts/evolucion.py exportar --humano [--todas]
      informe Markdown con las EVO aprobadas (o todas las no cerradas) en trabajo/…/exportaciones/, sin rutas absolutas
      ni datos del proyecto fuera de las fichas; marca «exportada». Nada sale del equipo: la persona decide a quién lo envía.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import date
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import uxyn_base as base  # noqa: E402
import uxyn_fichas as fichas  # noqa: E402

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)
MATRIZ = "MATRIZ-COBERTURA.md"


def matriz() -> Path:
    destino = base.carpeta_trabajo(PAQUETE) / MATRIZ
    if not destino.exists():
        shutil.copy2(PAQUETE / "plantillas" / MATRIZ, destino)
        destino.chmod(0o644)
    return destino


def _anonimo(texto: str) -> str:
    """Quita rutas absolutas de la máquina (la ficha puede citar rutas del repo, no del disco)."""
    raiz = str(base.raiz_app(PAQUETE))
    return texto.replace(raiz + "/", "").replace(str(Path.home()), "~")


def exportar(todas: bool, hoy: date | None = None) -> Path:
    base.exigir_humano("exportar EVO")
    hoy = hoy or date.today()
    elegidas = [f for f in fichas.listar(PAQUETE, "evo") if f.status == "approved" or (todas and f.status == "pending")]
    if not elegidas:
        raise ValueError("no hay EVO que exportar (aprobadas, o pendientes con --todas)")
    partes = [f"# Propuestas EVO para el catálogo uxyngraphar ({hoy.isoformat()})", ""]
    for f in elegidas:
        partes += [f"---\n\n<!-- {f.id} · {f.status} -->", _anonimo(f.ruta.read_text(encoding="utf-8")), ""]
        f.ruta.write_text(base.escribir_campo(f.ruta.read_text(encoding="utf-8"), "exportada", hoy.isoformat()), encoding="utf-8")
    destino = base.carpeta_trabajo(PAQUETE) / "exportaciones" / f"EXPORTACION-{hoy.isoformat()}.md"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(partes), encoding="utf-8")
    return destino


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("matriz")
    ex = sub.add_parser("exportar")
    ex.add_argument("--humano", action="store_true")
    ex.add_argument("--todas", action="store_true", help="incluye también las pendientes")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "matriz":
            print(matriz().read_text(encoding="utf-8"))
        else:
            if not a.humano:
                raise PermissionError("exportar es una acción de la persona (--humano)")
            print(exportar(a.todas))
    except (ValueError, FileNotFoundError, PermissionError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
