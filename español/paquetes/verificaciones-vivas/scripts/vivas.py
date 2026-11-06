#!/usr/bin/env python3
"""Verificaciones vivas: contrastan la documentación con el código. Solo bajo pedido.

  python3 uxyngraphar/paquetes/verificaciones-vivas/scripts/vivas.py [REVISION…] [--ejecutar] [--informe]

REVISION: rutas, paginas, anclas, decisiones, manuales, vinculos, humo (sin REVISION: todas menos humo).
  --ejecutar  ejecuta los comandos de humo de los ajustes
  --informe   guarda el resultado como auditoría (auditorias-tecnicas) o como INFORME-*.md
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

sys.dont_write_bytecode = True   # el paquete es inmutable: ni cachés dentro
AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI / "comun")]

import uxyn_base as base  # noqa: E402
import uxyn_fichas as fichas  # noqa: E402
import vivas_datos as datos  # noqa: E402

AUDITORIAS = "auditorias-tecnicas"


def correr(revisiones: list[str], ejecutar: bool) -> dict[str, list[datos.Hallazgo]]:
    a = datos.ajustes()
    return {r: datos.humo(a, ejecutar) if r == "humo" else datos.REVISIONES[r](a) for r in revisiones}


def _tabla(resultado: dict[str, list[datos.Hallazgo]]) -> tuple[str, int, str]:
    filas, n, peor = [], 0, "info"
    for revision, hallazgos in resultado.items():
        for h in hallazgos:
            if h.severidad == "info":
                continue
            n += 1
            peor = min(peor, h.severidad, key=datos.SEVERIDADES.index)
            filas.append(f"| {n} | {h.severidad} | {revision}: {h.hallazgo.replace('|', '/')} | `{h.evidencia}` |")
    return "\n".join(filas), n, peor


def informe(resultado: dict[str, list[datos.Hallazgo]], hoy: date | None = None) -> Path:
    hoy = hoy or date.today()
    filas, n, peor = _tabla(resultado)
    nombres = "-".join(resultado)
    metodo = f"`vivas.py {' '.join(resultado)}` (verificaciones-vivas), {hoy.isoformat()}."
    notas = "\n".join(f"- {r}: {h.hallazgo}" for r, hs in resultado.items() for h in hs if h.severidad == "info") or "…"
    aud = datos.instalado(AUDITORIAS)
    if aud:
        slug, k = f"vivas-{nombres}"[:60].strip("-"), 2
        while any(f.id == f"AUD-{hoy:%Y%m%d}-{slug}" for f in fichas.listar(aud, "auditoria")):
            slug, k = f"vivas-{nombres}"[:56].strip("-") + f"-{k}", k + 1
        ruta = fichas.crear(aud, "auditoria", slug, f"Verificaciones vivas: {', '.join(resultado)}", hoy=hoy)
        texto = ruta.read_text(encoding="utf-8")
        texto = base.escribir_campo(texto, "findings_count", str(n))
        texto = base.escribir_campo(texto, "severidad", peor if n else "info")
        texto = texto.replace("|---|-----------|----------|-----------|\n", "|---|-----------|----------|-----------|\n" + (filas + "\n" if filas else ""), 1)
        texto = texto.replace("Qué se revisó y cómo (comandos, archivos, mediciones), para que otra persona pueda repetirlo.", metodo, 1)
        texto = texto.replace("## Notas\n…", f"## Notas\n{notas}", 1)
        ruta.write_text(texto, encoding="utf-8")
        return ruta
    ruta = base.carpeta_trabajo(datos.PAQUETE) / f"INFORME-{hoy:%Y%m%d}-{nombres}.md"
    ruta.write_text(f"# Verificaciones vivas: {', '.join(resultado)}\n\n## Método\n{metodo}\n\n## Hallazgos\n"
                    "| # | Severidad | Hallazgo | Evidencia |\n|---|-----------|----------|-----------|\n"
                    + (filas + "\n" if filas else "") + f"\n## Notas\n{notas}\n", encoding="utf-8")
    return ruta


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("revisiones", nargs="*")
    ap.add_argument("--ejecutar", action="store_true")
    ap.add_argument("--informe", action="store_true")
    a = ap.parse_args(argv)
    desconocidas = [r for r in a.revisiones if r not in (*datos.REVISIONES, "humo")]
    if desconocidas:
        ap.error(f"revisión desconocida: {', '.join(desconocidas)} (válidas: {', '.join([*datos.REVISIONES, 'humo'])})")
    revisiones = a.revisiones or [*datos.REVISIONES, *(["humo"] if a.ejecutar else [])]
    resultado = correr(revisiones, a.ejecutar)
    for revision, hallazgos in resultado.items():
        for h in hallazgos:
            print(f"[{revision}] {h.severidad}: {h.hallazgo} — {h.evidencia}")
    _, n, _ = _tabla(resultado)
    print(f"verificaciones-vivas: {n} hallazgos")
    if a.informe:
        print(f"informe: {informe(resultado).relative_to(datos.raiz()).as_posix()}")
    return 1 if n else 0


if __name__ == "__main__":
    raise SystemExit(main())
