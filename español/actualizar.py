#!/usr/bin/env python3
"""Actualiza uxyngraphar en proyectos que ya lo tienen (en cualquier sistema: python3 actualizar.py; en Windows también py -3 actualizar.py).

  python3 actualizar.py                 abre una pantalla en tu navegador (revisas qué cambiaría y confirmas)
  python3 actualizar.py RUTA [RUTA…]    abre la pantalla con esas carpetas ya cargadas
  python3 actualizar.py RUTA --consola  lo mismo en texto, sin navegador
  python3 actualizar.py RUTA --si       aplica sin preguntar (texto; para scripts)
  --colaborar si|no                     responde a «¿Te gustaría colaborar en la mejora de uxyngraphar?» (se pregunta una vez por proyecto)

Qué hace: detecta los packs instalados (también en monorepos), muestra qué cambiaría, hace copia de seguridad, actualiza SOLO el núcleo
(tu contenido —fichas, instrucciones, rutas, espejo— nunca se toca) y añade las protecciones nuevas (CI, reglas de agentes, .gitignore…).
Un salto de versión mayor se rechaza: requiere una instrucción aprobada (10-guias/actualizar-nucleo.md). Requiere Python 3.10+ y git.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "instalador"))

import api  # noqa: E402
import flujo  # noqa: E402

MARCA = {"ok": "✓", "aviso": "!", "error": "✗"}


def _pregunta(texto: str, auto: bool) -> bool:
    if auto:
        return True
    return input(f"{texto} [s/N] ").strip().lower() in ("s", "si", "sí", "y", "yes")


RESPUESTA: dict = {}   # una sola pregunta por ejecución, aunque haya varios packs


def _colaborar(auto: bool) -> dict:
    if "colaborar" not in RESPUESTA and not auto:
        import consola
        RESPUESTA["colaborar"] = consola.preguntar_colaborar(api.feedback.texto_colaboracion())
    return RESPUESTA


def actualizar_carpeta(ruta: str, auto: bool) -> int:
    info = api.inspeccionar(ruta)
    if not info["ok"]:
        print(f"✗ {info['error']}")
        return 2
    if not info["instalados"]:
        print(f"«{info['nombre']}» no tiene uxyngraphar instalado. Para instalarlo usa python3 instalar.py.")
        return 1
    codigo = 0
    for inst in info["instalados"]:
        repo, docs = Path(info["ruta"]), inst["docs"]
        pack = api.PACKS.get(inst["pack"])
        if pack is None:
            print(f"✗ {docs}: el lock indica un pack desconocido ({inst['pack']!r}).")
            codigo = 2
            continue
        p = flujo.plan_actualizacion(pack, repo, docs)
        print(f"\n● {info['nombre']} · {docs} · pack {inst['pack']} · instalado {p['actual']} → disponible {p['nueva']}")
        if p.get("degradacion"):
            print(f"  ✗ Este pack ({p['nueva']}) es más antiguo que lo instalado ({p['actual']}). No se aplica nada: usa una versión igual o más reciente de uxyngraphar.")
            codigo = 2
            continue
        if p["mayor"]:
            print("  ✗ Salto de versión mayor: requiere una instrucción aprobada. Sigue 10-guias/actualizar-nucleo.md (actualizar-pack.py --migracion-aprobada).")
            codigo = 2
            continue
        if p["al_dia"]:
            print("  El núcleo ya está al día; solo se revisarán las protecciones (CI, reglas de agentes, .gitignore…).")
        else:
            print(f"  {p['nuevos']} archivos nuevos · {p['reemplazar']} reemplazados · {len(p['conflictos'])} en conflicto (quedarán como .uxyngraphar-nuevo).")
            print("  Tu contenido no se toca. Se hace copia de seguridad en .uxyngraphar-respaldo/.")
        if not _pregunta("  ¿Aplicar?", auto):
            print("  Sin cambios.")
            continue
        r = flujo.actualizar_completo(pack, repo, docs)
        for paso in r.pasos:
            print(f"  {MARCA.get(paso.estado, '·')} {paso.texto}" + (f"\n      {paso.detalle}" if paso.detalle else ""))
        if r.ok:
            s = _colaborar(auto) if api.colaboracion_pendiente(repo, docs) else {}
            for texto, estado in api.aplicar_colaboracion(repo, docs, s, "actualizador"):
                print(f"  {MARCA.get(estado, '·')} {texto}")
        d = flujo.diagnostico(repo, docs)
        pend = [x for x in d.pasos if x.estado != "ok"]
        print(f"  Diagnóstico: {len(d.pasos) - len(pend)} ok · {len(pend)} pendiente(s)")
        for x in pend:
            print(f"    {MARCA.get(x.estado, '·')} {x.texto}" + (f"\n        → {x.detalle}" if x.detalle else ""))
        codigo = max(codigo, 0 if r.ok else 2)
    return codigo


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rutas", nargs="*")
    ap.add_argument("--si", action="store_true", help="aplicar sin preguntar (modo texto)")
    ap.add_argument("--consola", action="store_true", help="usar texto en lugar de la pantalla del navegador")
    ap.add_argument("--colaborar", choices=("si", "no"), default=None, help="respuesta a la pregunta de colaboración (con --si y sin esta opción cuenta como No; en CI o con un agente queda pendiente)")
    a = ap.parse_args(argv)
    if a.colaborar:
        RESPUESTA["colaborar"] = a.colaborar
    if not (a.consola or a.si or a.colaborar):
        try:
            import servidor
            return servidor.servir(modo="actualizar", rutas=a.rutas)
        except OSError as exc:
            print(f"No pude abrir la pantalla ({exc}); sigo en modo texto.\n")
    rutas = a.rutas or [input("Carpeta del proyecto a actualizar: ").strip()]
    return max(actualizar_carpeta(r, a.si) for r in rutas)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nCancelado. Si una actualización estaba a mitad, se deshizo: el proyecto quedó como estaba.", file=sys.stderr)
        raise SystemExit(130)
