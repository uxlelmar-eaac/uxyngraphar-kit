"""Versión de texto del asistente (para terminales sin navegador o para automatizar con --si)."""

from __future__ import annotations

import argparse
import sys

import api


ICONO = {"ok": "✓", "aviso": "!", "error": "✕"}


def preguntar(texto: str, defecto: str, auto: bool) -> str:
    if auto:
        return defecto
    try:
        r = input(f"{texto}" + (f" [{defecto}]" if defecto else "") + ": ").strip()
    except EOFError:
        return defecto
    return r or defecto


def confirmar(texto: str, defecto: bool, auto: bool) -> bool:
    r = preguntar(f"{texto} ({'S/n' if defecto else 's/N'})", "", auto).lower()
    return defecto if not r else r.startswith(("s", "y"))


def preguntar_colaborar(texto: str) -> str:
    """Sí o No, sin opción marcada: repite hasta tener una respuesta (sin terminal cuenta como No)."""
    print("\n" + texto)
    while True:
        try:
            r = input("\nResponde «si» o «no»: ").strip().lower()
        except EOFError:
            print("Sin respuesta: cuenta como No.")
            return "no"
        if r in ("si", "sí", "s"):
            return "si"
        if r in ("no", "n"):
            return "no"
        print("No hay opción por defecto: escribe «si» o «no».")


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="instalar.py", description="Asistente de instalación de uxyngraphar (sin argumentos abre la pantalla en el navegador).")
    ap.add_argument("--consola", action="store_true", help="usar este asistente de texto en lugar del navegador")
    ap.add_argument("--proyecto", default="", help="carpeta raíz del proyecto")
    ap.add_argument("--proyecto2", default="", help="con --pack ambos en repos distintos: carpeta del repo del cliente")
    ap.add_argument("--pack", choices=("servidor", "cliente", "ambos"), default="")
    ap.add_argument("--mismo-repo", action="store_true", help="con --pack ambos: los dos en el mismo repositorio")
    ap.add_argument("--sub-servidor", default=None, help="subcarpeta de la app servidor (apps/api); vacío = raíz")
    ap.add_argument("--sub-cliente", default=None, help="subcarpeta de la app cliente (apps/web); vacío = raíz")
    ap.add_argument("--propietario", default="", help="usuario de GitHub para CODEOWNERS (@usuario)")
    ap.add_argument("--estricto", action="store_true")
    ap.add_argument("--sin-proteger", action="store_true")
    ap.add_argument("--colaborar", choices=("si", "no"), default=None,
                    help="respuesta a «¿Te gustaría colaborar en la mejora de uxyngraphar?» (con --si y sin esta opción cuenta como No; en CI o con un agente queda pendiente)")
    ap.add_argument("--si", action="store_true", help="no preguntar: usa los valores por defecto (una actualización no se aplica sola)")
    return ap


def main(a: argparse.Namespace) -> int:
    auto = a.si
    print("=== uxyngraphar — asistente de instalación ===\n")
    ruta = a.proyecto or preguntar("Carpeta raíz de tu proyecto", "", auto)
    info = api.inspeccionar(ruta)
    if not info["ok"]:
        print(f"ERROR: {info['error']}")
        return 2
    print(f"Proyecto: {info['ruta']}  ·  git: {'sí' if info['git'] else 'no (se inicializará)'}  ·  pila: {', '.join(info['pila']) or 'no detectada'}")
    if not info["git"] and not info["git_disponible"]:
        print("ERROR: no encuentro git instalado (git-scm.com).")
        return 2
    pack = a.pack
    if not pack:
        print("\n¿Qué quieres instalar?\n  1 = Servidor (API, servicios, workers, CLI, librerías)\n  2 = Cliente (web, móvil, escritorio)\n  3 = Los dos")
        r = preguntar("Elige 1, 2 o 3", "1" if info["rol_sugerido"] == "servidor" else "2", auto)
        pack = {"1": "servidor", "2": "cliente", "3": "ambos"}.get(r, info["rol_sugerido"])
    s = {"proyecto": info["ruta"], "pack": pack, "proteger": not a.sin_proteger, "propietario": a.propietario, "estricto": a.estricto}
    if pack == "ambos":
        s["mismo_repo"] = a.mismo_repo or (not a.proyecto2 and confirmar("\n¿Los dos en el MISMO repositorio (monorepo)? Si dices que no, cada uno va en su repositorio", True, auto))
        if s["mismo_repo"]:
            s["sub_servidor"] = a.sub_servidor if a.sub_servidor is not None else preguntar("Carpeta de la app servidor dentro del repo", info["sub_servidor"] or "apps/api", auto)
            s["sub_cliente"] = a.sub_cliente if a.sub_cliente is not None else preguntar("Carpeta de la app cliente dentro del repo", info["sub_cliente"] or "apps/web", auto)
        else:
            s["proyecto2"] = a.proyecto2 or preguntar("Carpeta del repositorio del cliente", "", auto)
    else:
        sub = a.sub_servidor if pack == "servidor" else a.sub_cliente
        s["sub"] = sub if sub is not None else preguntar("¿Subcarpeta de app dentro del repo? (monorepo, p. ej. apps/api; Enter = raíz)", "", auto)
    if not a.sin_proteger and not a.propietario and not auto:
        s["propietario"] = preguntar("¿Quién debe aprobar los cambios al núcleo? Tu usuario de GitHub con @ (p. ej. @juanperez) o un equipo; Enter = decidirlo después", "", auto)

    if a.colaborar:
        s["colaborar"] = a.colaborar
    elif info.get("colaboracion_pendiente") and not auto:
        s["colaborar"] = preguntar_colaborar(api.feedback.texto_colaboracion())

    plan = api.planificar(s)
    for e in plan["errores"]:
        print(f"ERROR: {e}")
    print("\n--- Plan (todavía no se ha escrito nada) ---")
    for d in plan["destinos"]:
        print(f"\n{d['titulo']} [{d['modo']}]")
        for l in d["lineas"]:
            print(f"  • {l}")
    if not plan["ok"]:
        return 2
    actualiza = any(d["modo"] == "actualizar" for d in plan["destinos"])
    if not confirmar("\n¿" + ("Aplicar la actualización" if actualiza else "Instalar ahora") + "?", not actualiza, auto):
        print("Sin cambios aplicados: no se escribió nada.")
        return 0
    res = api.ejecutar({**s, "aplicar_actualizacion": True})
    for d in res["destinos"]:
        print(f"\n=== {d['titulo']} ===")
        for p in d["pasos"]:
            print(f"  {ICONO[p['estado']]} {p['texto']}")
            if p["detalle"]:
                print(f"      {p['detalle']}")
        if d["diagnostico"]:
            n = len(d["diagnostico"])
            print(f"  Te {'queda' if n == 1 else 'quedan'} {n} {'cosa' if n == 1 else 'cosas'} por hacer:")
            for p in d["diagnostico"]:
                print(f"   ! {p['texto']}" + (f"\n       → {p['detalle']}" if p["detalle"] else ""))
    print("\n=== Qué sigue ===")
    for i, t in enumerate(api.siguientes_pasos(s), 1):
        print(f" {i}. {t}")
    return 0 if res["ok"] else 1


def arrancar(argv: list[str] | None = None) -> int:
    for f in (sys.stdout, sys.stderr):
        try:
            f.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        except (AttributeError, ValueError):
            pass
    return main(parser().parse_args(argv))
