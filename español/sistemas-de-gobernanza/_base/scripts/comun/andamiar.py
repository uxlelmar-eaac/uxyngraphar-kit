#!/usr/bin/env python3
"""Andamiaje del sistema: crea en el proyecto la estructura de `andamiaje/<variante>/`. Nunca sobrescribe.

  python3 scripts/comun/andamiar.py                                 variantes disponibles
  python3 scripts/comun/andamiar.py <variante> --nombre <nombre>    muestra lo que crearía (no toca nada)
  python3 scripts/comun/andamiar.py <variante> --nombre <nombre> --aplicar

En rutas, `__nombre__` se sustituye por el nombre; en el contenido, `{{nombre}}`, `{{Nombre}}` (PascalCase) y
`{{nombreCamel}}` (camelCase, para identificadores). Los archivos de código del andamiaje llevan el sufijo `.plantilla`
(`__nombre__.controller.ts.plantilla`), que se quita al crearlos: así el typecheck y los linters del proyecto no toman por
código las plantillas del sistema instalado.
El destino de cada variante está en «andamiaje» del manifiesto, relativo a la raíz de la app (`{nombre}` admitido).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True   # el sistema es inmutable: ni cachés dentro
sys.path.insert(0, str(Path(__file__).resolve().parent))

import uxyn_base as base  # noqa: E402

NOMBRE_VALIDO = re.compile(r"^[a-z][a-z0-9]*(?:[-_][a-z0-9]+)*$")
SUFIJO = ".plantilla"


def pascal(nombre: str) -> str:
    return "".join(p[:1].upper() + p[1:] for p in re.split(r"[-_]", nombre))


def camel(nombre: str) -> str:
    p = pascal(nombre)
    return p[:1].lower() + p[1:]


def variantes(sistema: Path) -> dict:
    return base.leer_manifiesto(sistema).get("andamiaje") or {}


def plan(sistema: Path, variante: str, nombre: str, raiz: Path) -> list[tuple[Path, str, bool]]:
    """[(destino, contenido, ya_existe)] de lo que crearía la variante, sin escribir nada."""
    definicion = variantes(sistema).get(variante)
    if definicion is None:
        raise ValueError(f"variante «{variante}» inexistente; disponibles: {', '.join(variantes(sistema)) or '(ninguna)'}")
    if not NOMBRE_VALIDO.match(nombre):
        raise ValueError(f"nombre «{nombre}»: minúsculas, dígitos, guiones o guiones bajos; empieza por letra")
    origen = Path(sistema) / base.PIEZAS["andamiaje"] / variante
    destino = (Path(raiz) / definicion["destino"].replace("{nombre}", nombre)).resolve()
    if Path(raiz).resolve() not in (destino, *destino.parents):
        raise ValueError(f"destino fuera de la raíz de la app: {definicion['destino']}")
    salida = []
    for p in sorted(origen.rglob("*")):
        if not p.is_file() or base.IGNORAR.search(p.as_posix()):
            continue
        rel = p.relative_to(origen).as_posix().replace("__nombre__", nombre)
        rel = rel[: -len(SUFIJO)] if rel.endswith(SUFIJO) else rel
        texto = (p.read_text(encoding="utf-8").replace("{{nombreCamel}}", camel(nombre))
                 .replace("{{nombre}}", nombre).replace("{{Nombre}}", pascal(nombre)))
        final = destino / rel
        salida.append((final, texto, final.exists()))
    return salida


def aplicar(sistema: Path, variante: str, nombre: str, raiz: Path) -> tuple[list[Path], list[Path]]:
    """Crea lo que falta; devuelve (creados, omitidos porque ya existían)."""
    creados, omitidos = [], []
    for final, texto, existe in plan(sistema, variante, nombre, raiz):
        if existe:
            omitidos.append(final)
            continue
        final.parent.mkdir(parents=True, exist_ok=True)
        final.write_text(texto, encoding="utf-8")
        creados.append(final)
    return creados, omitidos


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="andamiar.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("variante", nargs="?")
    p.add_argument("--nombre")
    p.add_argument("--aplicar", action="store_true")
    a = p.parse_args(argv)
    sistema = base.carpeta_sistema(Path(__file__).resolve().parent)
    if not a.variante:
        for nombre, d in variantes(sistema).items():
            print(f"{nombre}\t{d['destino']}\t{d['descripcion']}")
        return 0
    if not a.nombre:
        print("error: falta --nombre", file=sys.stderr)
        return 1
    raiz = base.raiz_app(sistema)
    try:
        if not a.aplicar:
            for final, _, existe in plan(sistema, a.variante, a.nombre, raiz):
                print(f"{'existe, se omitiría' if existe else 'crearía'}: {final.relative_to(raiz).as_posix()}")
            print("(simulación: añade --aplicar para crear)")
            return 0
        creados, omitidos = aplicar(sistema, a.variante, a.nombre, raiz)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    for f in creados:
        print(f"creado: {f.relative_to(raiz).as_posix()}")
    for f in omitidos:
        print(f"omitido (ya existe): {f.relative_to(raiz).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
