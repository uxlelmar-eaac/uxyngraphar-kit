#!/usr/bin/env python3
"""uxyngraphar: la herramienta que instala y actualiza el pack en tus proyectos.

  uxyngraphar panel                        abre el panel del navegador: tus proyectos, su configuración y tu plantilla
  uxyngraphar instalar [RUTA] [opciones]   siembra el pack en un proyecto (sin argumentos abre la pantalla del navegador)
  uxyngraphar actualizar [RUTA…] [--todos] lleva proyectos a la versión de la herramienta (con respaldo; --consola, --si)
  uxyngraphar estado [RUTA]                versión del proyecto, de la herramienta y la última publicada
  uxyngraphar proyectos [--agregar RUTA | --quitar RUTA | --salud]   proyectos registrados en este equipo
  uxyngraphar configuracion [RUTA]        el archivo de configuración del proyecto (docs/uxyngraphar.config.json): efectiva y problemas
  uxyngraphar autoactualizar [--version X.Y.Z]   descarga e instala la última versión de la herramienta
  uxyngraphar usar X.Y.Z                   vuelve a una versión (la descarga si hace falta)
  uxyngraphar version                      versión activa y versiones guardadas
  uxyngraphar desinstalar [--si]           quita la herramienta de este equipo (tus proyectos no se tocan)
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent   # versiones/X.Y.Z/ (instalada) o español/ (copia del repositorio)
sys.path.insert(0, str(RAIZ / "instalador"))

import arranque as ar  # noqa: E402
import sistema  # noqa: E402  (carpeta de la herramienta, registro de proyectos, plantilla)

COMANDOS = ("panel", "instalar", "actualizar", "estado", "proyectos", "configuracion", "autoactualizar", "usar", "version", "desinstalar")


def home() -> Path:
    return sistema.home()


def version_herramienta() -> str:
    return sistema.version_herramienta()


_tupla = sistema.tupla


def _api():
    import api   # carga el núcleo del pack; solo cuando hace falta (el arranque de la herramienta queda rápido)
    return api


# ---------- registro de proyectos (proyectos.json en la carpeta de la herramienta) ----------

def leer_proyectos() -> list[str]:
    return sistema.leer_proyectos()


def guardar_proyectos(lista: list[str]) -> None:
    sistema.guardar_proyectos(lista)


def registrar(rutas: list[str]) -> list[str]:
    """Anota las rutas que tienen el pack instalado. Devuelve las que se añadieron."""
    actuales, nuevas = leer_proyectos(), []
    for r in rutas:
        p = Path(r).expanduser()
        if p.is_dir() and _api().inspeccionar(str(p)).get("instalados") and str(p.resolve()) not in actuales:
            nuevas.append(str(p.resolve()))
    if nuevas:
        guardar_proyectos(actuales + nuevas)
    return nuevas


# ---------- comandos ----------

def _correr(script: str, args: list[str]) -> int:
    return subprocess.call([sys.executable, str(RAIZ / script), *args])


def cmd_panel(args: list[str]) -> int:
    """Panel del navegador. --bienvenida: primera pantalla tras el instalador de una línea (qué se hizo y qué decidir)."""
    import servidor
    try:
        return servidor.servir(modo="panel", bienvenida="--bienvenida" in args)
    except OSError as exc:
        print(f"No pude abrir el panel ({exc}). En texto:  uxyngraphar proyectos  ·  uxyngraphar configuracion [RUTA]")
        return 1


def cmd_instalar(args: list[str]) -> int:
    if args and not args[0].startswith("-"):
        args = ["--proyecto", args[0], *args[1:]]
    codigo = _correr("instalar.py", args)
    candidatas = [args[i + 1] for i, a in enumerate(args[:-1]) if a in ("--proyecto", "--proyecto2")] or [os.getcwd()]
    if codigo == 0:
        for r in registrar(candidatas):
            print(f"Proyecto registrado: {r}  (uxyngraphar proyectos para verlos todos)")
        if not args:
            print("Si lo instalaste en otra carpeta, regístrala con:  uxyngraphar proyectos --agregar RUTA")
    return codigo


def cmd_actualizar(args: list[str]) -> int:
    ultima, propia = ultima_publicada(espera=3), version_herramienta()
    if ultima and _tupla(ultima) > _tupla(propia):
        print(f"Aviso: ya está publicada la {ultima} (tu herramienta es la {propia}). Para llevar tus proyectos a ella: uxyngraphar autoactualizar y luego uxyngraphar actualizar.\n")
    colaborar: list[str] = []
    if "--colaborar" in args:   # opción con valor (si|no): no es una ruta
        i = args.index("--colaborar")
        colaborar, args = args[i:i + 2], args[:i] + args[i + 2:]
    flags = [a for a in args if a.startswith("-") and a != "--todos"] + colaborar
    rutas = [a for a in args if not a.startswith("-")]
    if "--todos" in args:
        rutas += [p for p in leer_proyectos() if Path(p).is_dir()]
        if not rutas:
            print("No hay proyectos registrados. Regístralos con:  uxyngraphar proyectos --agregar RUTA")
            return 1
    elif not rutas and _api().inspeccionar(os.getcwd()).get("instalados"):
        rutas = [os.getcwd()]
    codigo = _correr("actualizar.py", rutas + flags)
    registrar(rutas)
    return codigo


def ultima_publicada(espera: int = 5) -> str:
    return sistema.ultima_publicada(espera)


def cmd_estado(args: list[str]) -> int:
    propia, ultima = version_herramienta(), ultima_publicada()
    print(f"Herramienta: {propia}" + (f" · última publicada: {ultima}" if ultima else " · (sin conexión: no sé cuál es la última)"))
    if ultima and _tupla(ultima) > _tupla(propia):
        print("  Hay una versión más nueva:  uxyngraphar autoactualizar")
    ruta = args[0] if args else os.getcwd()
    info = _api().inspeccionar(ruta)
    if not info["ok"]:
        print(info["error"])
        return 2
    if not info["instalados"]:
        print(f"«{info['nombre']}» no tiene uxyngraphar. Para sembrarlo:  uxyngraphar instalar")
        return 1
    for inst in info["instalados"]:
        v = inst["version"]
        if _tupla(v) < _tupla(propia):
            nota = "puedes actualizarlo:  uxyngraphar actualizar"
        elif _tupla(v) > _tupla(propia):
            nota = "usa una versión más nueva que tu herramienta:  uxyngraphar autoactualizar"
        else:
            nota = "al día"
        print(f"{info['nombre']} · {inst['docs']} · pack {inst['pack']} · versión {v} → {nota}")
    return 0


def _salud(ruta: str, docs: str) -> str:
    sys.path.insert(0, str(RAIZ / "backend" / "scripts"))
    import importlib
    flota = importlib.import_module("flota")
    f = flota.revisar(Path(ruta), docs, "")
    return f.get("error") or ("sano" if not f["motivos"] else f"{f['errores']} errores, {f['avisos']} avisos")


def cmd_proyectos(args: list[str]) -> int:
    lista = leer_proyectos()
    if args[:1] == ["--agregar"] and len(args) > 1:
        nuevas = registrar(args[1:])
        print("Registrado: " + ", ".join(nuevas) if nuevas else "Nada que registrar: esa carpeta no tiene uxyngraphar o ya estaba.")
        return 0 if nuevas or all(str(Path(a).resolve()) in lista for a in args[1:]) else 1
    if args[:1] == ["--quitar"] and len(args) > 1:
        quitar = {str(Path(a).expanduser().resolve()) for a in args[1:]}
        guardar_proyectos([p for p in lista if p not in quitar])
        print("Quitado del registro (la carpeta no se toca).")
        return 0
    if not lista:
        print("No hay proyectos registrados. Se registran solos con  uxyngraphar instalar  o con  uxyngraphar proyectos --agregar RUTA")
        return 0
    propia = version_herramienta()
    for p in lista:
        if not Path(p).is_dir():
            print(f"✗ {p}  (ya no existe; quítalo con  uxyngraphar proyectos --quitar {p})")
            continue
        for inst in _api().inspeccionar(p).get("instalados", []):
            estado = "al día" if inst["version"] == propia else ("actualizable" if _tupla(inst["version"]) < _tupla(propia) else "más nuevo que tu herramienta")
            salud = f" · {_salud(p, inst['docs'])}" if "--salud" in args else ""
            print(f"• {Path(p).name} · {inst['docs']} · {inst['version']} ({estado}){salud}\n    {p}")
    return 0


def _modulo_config(repo: Path, docs: str):
    return sistema.modulo_config(repo, docs)


def cmd_configuracion(args: list[str]) -> int:
    info = _api().inspeccionar(args[0] if args else os.getcwd())
    if not info["ok"]:
        print(info["error"])
        return 2
    if not info["instalados"]:
        print(f"«{info['nombre']}» no tiene uxyngraphar. Para sembrarlo:  uxyngraphar instalar")
        return 1
    codigo = 0
    for inst in info["instalados"]:
        repo = Path(info["ruta"])
        cfgmod = _modulo_config(repo, inst["docs"])
        archivo = repo / inst["docs"] / cfgmod.NOMBRE
        cfg, problemas = cfgmod.cargar(repo, inst["docs"])
        print(f"{archivo}" + ("" if archivo.is_file() else "  (no existe: se usan los valores por defecto)"))
        for p in problemas:
            print(f"  ✗ {p}")
        codigo = codigo or (1 if problemas else 0)
        print(json.dumps(cfg, ensure_ascii=False, indent=2))
        print(f"Qué significa cada sección y cómo cambiarla: {inst['docs']}/10-guias/configuracion-uxyngraphar.md  ·  en pantalla: uxyngraphar panel\n")
    return codigo


def cmd_autoactualizar(args: list[str]) -> int:
    version = args[args.index("--version") + 1].lstrip("v") if "--version" in args and args.index("--version") + 1 < len(args) else ""
    url = ar.url_de(version, "instalar-uxyngraphar.py") if version else ar.url_ultima("instalar-uxyngraphar.py")
    home().mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=home()) as t:
        destino = os.path.join(t, "instalar-uxyngraphar.py")
        try:
            ar.descargar(url, destino)
        except ar.ErrorInstalacion as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        extra = ["--sin-path"] if not ar.leer_registro(str(home())).get("perfil") and not ar.ES_WINDOWS else []
        return subprocess.call([sys.executable, destino, *extra])


def cmd_usar(args: list[str]) -> int:
    if not args or not ar.VERSION_RE.match(args[0].lstrip("v")):
        print("Uso:  uxyngraphar usar X.Y.Z   (versiones guardadas:  uxyngraphar version)")
        return 2
    v = args[0].lstrip("v")
    if v in ar.versiones_guardadas(str(home())):
        ar.escribir_atomico(str(home() / "actual"), v + "\n")
        print(f"Versión activa: {v}. Tus proyectos no cambian hasta que ejecutes  uxyngraphar actualizar.")
        return 0
    return cmd_autoactualizar(["--version", v])


def cmd_version(_args: list[str]) -> int:
    h = str(home())
    print(f"uxyngraphar {version_herramienta()}")
    print(f"Carpeta: {h}")
    guardadas = ar.versiones_guardadas(h)
    if guardadas:
        activa = ar.version_activa(h)
        print("Versiones guardadas: " + ", ".join(f"{v} (activa)" if v == activa else v for v in guardadas))
    return 0


def cmd_desinstalar(args: list[str]) -> int:
    h = home()
    if "--si" not in args:
        r = input(f"Se borrará {h} y el comando uxyngraphar. Tus proyectos no se tocan. ¿Seguir? [s/N] ").strip().lower()
        if r not in ("s", "si", "sí", "y", "yes"):
            print("Sin cambios.")
            return 0
    registro = ar.leer_registro(str(h))
    for archivo in registro.get("lanzadores", []):
        if os.path.isfile(archivo) and ar.es_nuestro(archivo):
            os.remove(archivo)
    if ar.quitar_de_perfil(registro.get("perfil", "")):
        print(f"Quité la línea del PATH de {registro['perfil']}.")
    if registro.get("path_windows"):
        ar._path_windows(registro["path_windows"], False)
    shutil.rmtree(h, ignore_errors=True)
    print("uxyngraphar se desinstaló de este equipo. Los proyectos conservan su copia del pack en docs/.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ar.preparar_consola()
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help", "ayuda"):
        print(__doc__)
        return 0
    if argv[0] in ("--version", "-V"):
        argv[0] = "version"
    if argv[0] not in COMANDOS:
        print(f"Comando desconocido: {argv[0]}\n{__doc__}", file=sys.stderr)
        return 2
    return globals()["cmd_" + argv[0]](argv[1:])


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
