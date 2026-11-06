#!/usr/bin/env python3
"""Comprueba que este paquete no fue modificado (INTEGRIDAD.json). Código 0 = íntegro; 1 = alterado.

Si falla, el agente se detiene y avisa a la persona: el paquete se repara reinstalándolo desde el panel.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
sys.path.insert(0, str(Path(__file__).resolve().parent))

import uxyn_base as base  # noqa: E402


def main() -> int:
    paquete = base.carpeta_paquete(Path(__file__).resolve().parent)
    errores = base.validar_manifiesto(base.leer_manifiesto(paquete))
    informe = base.comprobar_integridad(paquete)
    if errores or not base.integro(informe):
        print(f"PAQUETE ALTERADO: {paquete.name}. Detente y avisa a la persona; no lo repares tú.", file=sys.stderr)
        for clave in ("errores", "alterados", "faltantes", "añadidos"):
            for rel in informe[clave]:
                print(f"  {clave}: {rel}", file=sys.stderr)
        for e in errores:
            print(f"  manifiesto: {e}", file=sys.stderr)
        return 1
    m = base.leer_manifiesto(paquete)
    print(f"ok: {m['id']} {m['version']} íntegro ({len(base.archivos_del_paquete(paquete))} archivos)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
