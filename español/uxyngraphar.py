#!/usr/bin/env python3
"""uxyngraphar: catálogo e instalación de paquetes de gobernanza para tus repos.

  uxyngraphar                       abre el panel (si hay una persona delante; si no, esta ayuda)
  uxyngraphar <comando> …           comandos de paquetes: catalogo, crear, instalar, actualizar, quitar, estado,
                                    verificar, indice, flujo, migrar, panel…  (uxyngraphar --help)

La herramienta en este equipo:
  uxyngraphar version               versión activa y versiones guardadas
  uxyngraphar autoactualizar [--version X.Y.Z]   descarga e instala la última (o esa) versión
  uxyngraphar usar X.Y.Z            vuelve a una versión guardada (la descarga si falta)
  uxyngraphar desinstalar [--si]    quita la herramienta; tus repos no se tocan
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent   # versiones/X.Y.Z/ (instalada) o español/ (repositorio)
sys.path[:0] = [str(RAIZ / "motor"), str(RAIZ / "distribucion")]

import arranque as ar  # noqa: E402
import cli  # noqa: E402

HERRAMIENTA = ("version", "autoactualizar", "usar", "desinstalar")


def version() -> str:
    return (RAIZ / "VERSION").read_text(encoding="utf-8").strip()


def home() -> Path:
    return Path(ar.carpeta_home())


def cmd_version(_args: list[str]) -> int:
    print(f"uxyngraphar {version()}")
    guardadas = ar.versiones_guardadas(str(home()))
    if guardadas:
        activa = ar.version_activa(str(home()))
        print(f"Carpeta: {home()}\nVersiones guardadas: " + ", ".join(f"{v} (activa)" if v == activa else v for v in guardadas))
    return 0


def cmd_autoactualizar(args: list[str]) -> int:
    v = args[args.index("--version") + 1].lstrip("v") if "--version" in args and args.index("--version") + 1 < len(args) else ""
    url = ar.url_de(v, "instalar-uxyngraphar.py") if v else ar.url_ultima("instalar-uxyngraphar.py")
    home().mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=home()) as t:
        destino = os.path.join(t, "instalar-uxyngraphar.py")
        try:
            ar.descargar(url, destino)
        except ar.ErrorInstalacion as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        extra = ["--sin-path"] if not ar.leer_registro(str(home())).get("perfil") and not ar.ES_WINDOWS else []
        return subprocess.call([sys.executable, destino, *extra])


def cmd_usar(args: list[str]) -> int:
    if not args or not ar.VERSION_RE.match(args[0].lstrip("v")):
        print("Uso:  uxyngraphar usar X.Y.Z   (versiones guardadas:  uxyngraphar version)", file=sys.stderr)
        return 2
    v = args[0].lstrip("v")
    if v in ar.versiones_guardadas(str(home())):
        ar.escribir_atomico(str(home() / "actual"), v + "\n")
        print(f"Versión activa: {v}.")
        return 0
    return cmd_autoactualizar(["--version", v])


def cmd_desinstalar(args: list[str]) -> int:
    h = home()
    if "--si" not in args:
        try:
            r = input(f"Se borrará {h} y el comando uxyngraphar. Tus repos no se tocan. ¿Seguir? [s/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            r = ""
        if r not in ("s", "si", "sí", "y", "yes"):
            print("Sin cambios.")
            return 0
    registro = ar.leer_registro(str(h))
    for archivo in registro.get("lanzadores", []):
        if os.path.isfile(archivo) and ar.es_nuestro(archivo):
            os.remove(archivo)
    ar.quitar_de_perfil(registro.get("perfil", ""))
    if registro.get("path_windows"):
        ar._path_windows(registro["path_windows"], False)
    shutil.rmtree(h, ignore_errors=True)
    print("uxyngraphar se desinstaló de este equipo. Los repos conservan uxyngraphar/ y uxyngraphar-work/.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ar.preparar_consola()
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        if ar.puede_abrir_panel():
            return cli.main(["panel"])
        print(__doc__)
        return 0
    if argv[0] in ("--version", "-V"):
        argv[0] = "version"
    if argv[0] in ("ayuda", "-h", "--help"):
        print(__doc__)
        return cli.main(["--help"]) if argv[0] != "ayuda" else 0
    if argv[0] in HERRAMIENTA:
        return globals()["cmd_" + argv[0]](argv[1:])
    return cli.main(argv)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
