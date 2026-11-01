#!/usr/bin/env python3
"""uxyngraphar: la herramienta que instala y actualiza el pack en tus proyectos.

La ayuda que ve la persona (uxyngraphar, uxyngraphar ayuda <comando>) se genera desde AYUDA y GRUPOS.

  uxyngraphar panel                        abre el panel del navegador: tus proyectos, su configuración y tu plantilla
  uxyngraphar instalar [RUTA] [opciones]   siembra el pack en un proyecto (sin argumentos abre la pantalla del navegador)
  uxyngraphar actualizar [RUTA…] [--todos] lleva proyectos a la versión de la herramienta (con respaldo; --consola, --si)
  uxyngraphar estado [RUTA]                versión del proyecto, de la herramienta y la última publicada
  uxyngraphar proyectos [--agregar RUTA | --quitar RUTA | --salud]   proyectos registrados en este equipo
  uxyngraphar configuracion [RUTA]        el archivo de configuración del proyecto (<carpeta del pack>/uxyngraphar.config.json): efectiva y problemas
  uxyngraphar mover-carpeta [RUTA] [--si]  mueve el pack de docs/ a uxyngraphar/ (instalaciones anteriores a 1.1.0)
  uxyngraphar autoactualizar [--version X.Y.Z]   descarga e instala la última versión de la herramienta
  uxyngraphar usar X.Y.Z                   vuelve a una versión (la descarga si hace falta)
  uxyngraphar version                      versión activa y versiones guardadas
  uxyngraphar desinstalar [--si]           quita la herramienta de este equipo (tus proyectos no se tocan)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent   # versiones/X.Y.Z/ (instalada) o español/ (copia del repositorio)
sys.path.insert(0, str(RAIZ / "instalador"))

import arranque as ar  # noqa: E402
import estilo as est  # noqa: E402  (colores, marcas y tablas de la consola)
import sistema  # noqa: E402  (carpeta de la herramienta, registro de proyectos, plantilla)

COMANDOS = ("panel", "instalar", "actualizar", "estado", "proyectos", "configuracion", "mover-carpeta", "autoactualizar", "usar", "version", "desinstalar")

# Ayuda: comando -> (sintaxis corta, qué hace en una línea, explicación larga, opciones [(opción, qué hace)]).
AYUDA = {
    "panel": ("panel", "Abre el panel del navegador: tus proyectos, su configuración y tu plantilla.",
              "Abre en tu navegador (solo en tu equipo) el panel de uxyngraphar: tus proyectos con su versión y salud, "
              "la configuración de cada uno con vista previa y copia de seguridad, y tu plantilla para proyectos nuevos.",
              [("--bienvenida", "Primera pantalla tras el instalador de una línea: qué se hizo y qué queda por decidir."),
               ("--fondo", "Sin abrir el navegador ni escribir en la terminal (lo usa el propio panel para reiniciarse tras actualizar).")]),
    "instalar": ("instalar [RUTA] [opciones]", "Siembra el pack en un proyecto (sin argumentos abre la pantalla del navegador).",
                 "Siembra el pack en un proyecto y lo registra. Sin argumentos abre la pantalla del navegador; "
                 "con RUTA u opciones funciona en texto. No borra nada: lo que choque queda como *.uxyngraphar-nuevo.",
                 [("RUTA", "Carpeta raíz del proyecto."),
                  ("--pack servidor|cliente|ambos", "Qué sembrar."),
                  ("--proyecto2 RUTA", "Con --pack ambos en repositorios distintos: el repositorio del cliente."),
                  ("--mismo-repo", "Con --pack ambos: los dos en el mismo repositorio (monorepo)."),
                  ("--sub-servidor DIR", "Subcarpeta de la app servidor (p. ej. apps/api); vacío = raíz."),
                  ("--sub-cliente DIR", "Subcarpeta de la app cliente (p. ej. apps/web); vacío = raíz."),
                  ("--propietario @usuario", "Usuario o equipo de GitHub que aprueba los cambios al núcleo (CODEOWNERS)."),
                  ("--estricto", "Protecciones estrictas."),
                  ("--sin-proteger", "No añadir reglas de agentes, CODEOWNERS, CI ni ganchos."),
                  ("--colaborar si|no", "Respuesta a «¿Te gustaría colaborar en la mejora de uxyngraphar?»."),
                  ("--si", "No preguntar: usa los valores por defecto (una actualización no se aplica sola)."),
                  ("--consola", "Todo en la terminal, sin navegador.")]),
    "actualizar": ("actualizar [RUTA…] [--todos]", "Lleva proyectos a la versión de la herramienta, con copia de seguridad.",
                   "Lleva proyectos a la versión de la herramienta: muestra qué cambiaría, respalda en .uxyngraphar-respaldo/, "
                   "toca solo el núcleo y deja los conflictos como *.uxyngraphar-nuevo. Sin RUTA usa la carpeta actual.",
                   [("RUTA…", "Una o varias carpetas de proyecto."),
                    ("--todos", "Todos los proyectos registrados en este equipo."),
                    ("--consola", "En texto, sin navegador."),
                    ("--si", "Aplicar sin preguntar (para scripts)."),
                    ("--colaborar si|no", "Respuesta a la pregunta de colaboración.")]),
    "estado": ("estado [RUTA]", "Versión del proyecto, de la herramienta y la última publicada.",
               "Compara la versión del pack del proyecto (por defecto la carpeta actual) con la de tu herramienta "
               "y con la última publicada, y dice qué hacer.", []),
    "proyectos": ("proyectos [opciones]", "Proyectos registrados en este equipo.",
                  "Lista los proyectos registrados en este equipo con su versión. Se registran solos al instalar o actualizar.",
                  [("--agregar RUTA", "Registra un proyecto que ya tiene uxyngraphar."),
                   ("--quitar RUTA", "Lo quita del registro (la carpeta no se toca)."),
                   ("--salud", "Añade un diagnóstico rápido de cada proyecto.")]),
    "configuracion": ("configuracion [RUTA]", "Configuración del proyecto (uxyngraphar.config.json) y sus problemas.",
                      "Muestra cómo queda la configuración del proyecto (uxyngraphar.config.json, en la carpeta del pack) con los valores "
                      "por defecto aplicados y qué valores son inválidos. Para editarla en pantalla: uxyngraphar panel.", []),
    "mover-carpeta": ("mover-carpeta [RUTA] [--a uxyngraphar|docs] [--si]", "Mueve el pack de docs/ a uxyngraphar/ (opcional).",
                      "Los proyectos instalados antes de la 1.1.0 tienen el pack en docs/ y siguen funcionando así. Si prefieres "
                      "uxyngraphar/, esto lo mueve con git mv y pone al día lo que escribió uxyngraphar (lock, ganchos, reglas para "
                      "agentes, CODEOWNERS, .gitignore, CLAUDE.md y CI si no los cambiaste). Primero muestra qué cambiaría y qué "
                      "enlaces tuyos revisar; con copia de seguridad y vuelta atrás si algo falla. Exige git sin cambios en la carpeta.",
                      [("RUTA", "Carpeta del proyecto (por defecto la actual)."),
                       ("--a NOMBRE", "Carpeta de destino: uxyngraphar (por defecto) o docs para volver."),
                       ("--si", "Mover sin preguntar (tras ver el plan).")]),
    "autoactualizar": ("autoactualizar [--version X.Y.Z]", "Descarga e instala la última versión de la herramienta.",
                       "Descarga e instala la última versión publicada de la herramienta (o la indicada). "
                       "No cambia ningún proyecto: después, uxyngraphar actualizar.",
                       [("--version X.Y.Z", "Instalar esa versión en lugar de la última.")]),
    "usar": ("usar X.Y.Z", "Vuelve a una versión (la descarga si hace falta).",
             "Activa una versión guardada de la herramienta, o la descarga si no está. Tus proyectos no cambian.", []),
    "version": ("version", "Versión activa y versiones guardadas.",
                "Muestra la versión activa de la herramienta, su carpeta y las versiones guardadas.", []),
    "desinstalar": ("desinstalar [--si]", "Quita la herramienta de este equipo (tus proyectos no se tocan).",
                    "Borra la carpeta de la herramienta y el comando uxyngraphar. Los proyectos conservan su copia del pack (en uxyngraphar/, o docs/ si se instalaron antes de la 1.1.0).",
                    [("--si", "Sin pedir confirmación.")]),
}
GRUPOS = (("Empezar", ("panel", "instalar")),
          ("Tus proyectos", ("actualizar", "estado", "proyectos", "configuracion", "mover-carpeta")),
          ("La herramienta", ("autoactualizar", "usar", "version", "desinstalar")))


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
        return servidor.servir(modo="panel", bienvenida="--bienvenida" in args, fondo="--fondo" in args)
    except OSError as exc:
        est.error(f"No pude abrir el panel ({exc}). En texto:  uxyngraphar proyectos  ·  uxyngraphar configuracion [RUTA]")
        return 1


def cmd_instalar(args: list[str]) -> int:
    if args and not args[0].startswith("-"):
        args = ["--proyecto", args[0], *args[1:]]
    codigo = _correr("instalar.py", args)
    candidatas = [args[i + 1] for i, a in enumerate(args[:-1]) if a in ("--proyecto", "--proyecto2")] or [os.getcwd()]
    if codigo == 0:
        for r in registrar(candidatas):
            est.ok(f"Proyecto registrado: {r}  " + est.dim("(uxyngraphar proyectos para verlos todos)"), "")
        if not args:
            print(est.dim("Si lo instalaste en otra carpeta, regístrala con:  ") + est.comando("uxyngraphar proyectos --agregar RUTA"))
    return codigo


def cmd_actualizar(args: list[str]) -> int:
    ultima, propia = ultima_publicada(espera=3), version_herramienta()
    if ultima and _tupla(ultima) > _tupla(propia):
        est.aviso(f"Ya está publicada la {ultima} (tu herramienta es la {propia}). Para llevar tus proyectos a ella: "
                  "uxyngraphar autoactualizar y luego uxyngraphar actualizar.\n", "")
    colaborar: list[str] = []
    if "--colaborar" in args:   # opción con valor (si|no): no es una ruta
        i = args.index("--colaborar")
        colaborar, args = args[i:i + 2], args[:i] + args[i + 2:]
    flags = [a for a in args if a.startswith("-") and a != "--todos"] + colaborar
    rutas = [a for a in args if not a.startswith("-")]
    if "--todos" in args:
        rutas += [p for p in leer_proyectos() if Path(p).is_dir()]
        if not rutas:
            est.aviso("No hay proyectos registrados. Regístralos con:  uxyngraphar proyectos --agregar RUTA", "")
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
    print(est.pintar("Herramienta:", "titulo") + f" {propia}" + (f" · última publicada: {ultima}" if ultima else est.dim(" · (sin conexión: no sé cuál es la última)")))
    if ultima and _tupla(ultima) > _tupla(propia):
        est.aviso("Hay una versión más nueva:  " + est.comando("uxyngraphar autoactualizar"))
    ruta = args[0] if args else os.getcwd()
    info = _api().inspeccionar(ruta)
    if not info["ok"]:
        est.error(info["error"])
        return 2
    if not info["instalados"]:
        est.aviso(f"«{info['nombre']}» no tiene uxyngraphar. Para sembrarlo:  uxyngraphar instalar", "")
        return 1
    for inst in info["instalados"]:
        v = inst["version"]
        if _tupla(v) < _tupla(propia):
            tipo, nota = "aviso", "puedes actualizarlo:  uxyngraphar actualizar"
        elif _tupla(v) > _tupla(propia):
            tipo, nota = "aviso", "usa una versión más nueva que tu herramienta:  uxyngraphar autoactualizar"
        else:
            tipo, nota = "ok", "al día"
        print(est.linea(tipo, f"{info['nombre']} · {inst['docs']} · pack {inst['pack']} · versión {v} → {nota}", ""))
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
        if nuevas:
            est.ok("Registrado: " + ", ".join(nuevas), "")
        else:
            est.aviso("Nada que registrar: esa carpeta no tiene uxyngraphar o ya estaba.", "")
        return 0 if nuevas or all(str(Path(a).resolve()) in lista for a in args[1:]) else 1
    if args[:1] == ["--quitar"] and len(args) > 1:
        quitar = {str(Path(a).expanduser().resolve()) for a in args[1:]}
        guardar_proyectos([p for p in lista if p not in quitar])
        est.ok("Quitado del registro (la carpeta no se toca).", "")
        return 0
    if not lista:
        print("No hay proyectos registrados. Se registran solos con  " + est.comando("uxyngraphar instalar")
              + "  o con  " + est.comando("uxyngraphar proyectos --agregar RUTA"))
        return 0
    propia = version_herramienta()
    for p in lista:
        if not Path(p).is_dir():
            print(est.linea("error", f"{p}  (ya no existe; quítalo con  uxyngraphar proyectos --quitar {p})", ""))
            continue
        for inst in _api().inspeccionar(p).get("instalados", []):
            estado = "al día" if inst["version"] == propia else ("actualizable" if _tupla(inst["version"]) < _tupla(propia) else "más nuevo que tu herramienta")
            salud = f" · {_salud(p, inst['docs'])}" if "--salud" in args else ""
            tipo = "ok" if estado == "al día" else "aviso"
            print(est.linea(tipo, f"{Path(p).name} · {inst['docs']} · {inst['version']} ({estado}){salud}", "") + "\n    " + est.dim(p))
    return 0


def _modulo_config(repo: Path, docs: str):
    return sistema.modulo_config(repo, docs)


def cmd_configuracion(args: list[str]) -> int:
    info = _api().inspeccionar(args[0] if args else os.getcwd())
    if not info["ok"]:
        est.error(info["error"])
        return 2
    if not info["instalados"]:
        est.aviso(f"«{info['nombre']}» no tiene uxyngraphar. Para sembrarlo:  uxyngraphar instalar", "")
        return 1
    codigo = 0
    for inst in info["instalados"]:
        repo = Path(info["ruta"])
        cfgmod = _modulo_config(repo, inst["docs"])
        archivo = repo / inst["docs"] / cfgmod.NOMBRE
        cfg, problemas = cfgmod.cargar(repo, inst["docs"])
        print(est.pintar(str(archivo), "titulo") + ("" if archivo.is_file() else est.dim("  (no existe: se usan los valores por defecto)")))
        for p in problemas:
            print(est.linea("error", p))
        codigo = codigo or (1 if problemas else 0)
        print(json.dumps(cfg, ensure_ascii=False, indent=2))
        print(est.dim("Qué significa cada sección y cómo cambiarla: ") + f"{inst['docs']}/10-guias/configuracion-uxyngraphar.md"
              + est.dim("  ·  en pantalla: ") + est.comando("uxyngraphar panel") + "\n")
    return codigo


def cmd_mover_carpeta(args: list[str]) -> int:
    nombre = ""
    if "--a" in args:
        i = args.index("--a")
        nombre, args = (args[i + 1] if i + 1 < len(args) else ""), args[:i] + args[i + 2:]
        if not nombre:
            est.error("--a necesita el nombre de la carpeta: uxyngraphar o docs")
            return 2
    rutas = [a for a in args if not a.startswith("-")]
    import api_mover
    ruta = rutas[0] if rutas else os.getcwd()
    info = _api().inspeccionar(ruta)
    if not info.get("ok"):
        est.error(info.get("error", "No pude leer la carpeta"))
        return 2
    if not info["instalados"]:
        est.aviso(f"«{info['nombre']}» no tiene uxyngraphar.", "")
        return 1
    lista = [x for x in info["instalados"] if x["docs"].rpartition("/")[2] != (nombre or _api().carpeta_pack.CARPETA)]
    if not lista:
        est.ok(f"El pack ya está en {(nombre or _api().carpeta_pack.CARPETA)}/: no hay nada que mover.", "")
        return 0
    codigo = 0
    for inst in lista:
        p = api_mover.ver(info["ruta"], inst["docs"], nombre)
        if not p["ok"]:
            est.error(p["error"])
            codigo = 1
            continue
        print(p["texto"] + "\n")
        if "--si" not in args:
            if not sys.stdin.isatty():
                est.aviso("Para mover, repite con --si.", "")
                continue
            try:
                r = input(f"¿Mover {p['desde']}/ → {p['hacia']}/? [s/N] ").strip().lower()
            except (EOFError, KeyboardInterrupt):   # stdin cerrado (p. ej. NUL en Windows) o Ctrl+C: cuenta como No
                print()
                est.aviso("Para mover, repite con --si.", "")
                continue
            if r not in ("s", "si", "sí", "y", "yes"):
                print("No se movió nada.")
                continue
        r = api_mover.aplicar(info["ruta"], inst["docs"], nombre)
        if r["ok"]:
            est.ok(f"Movido: {r['desde']}/ → {r['hacia']}/ · copia de seguridad: {r['respaldo']}", "")
            print(r["siguiente"])
        else:
            est.error(r["error"])
            codigo = 1
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
            est.error(f"ERROR: {exc}")
            return 1
        extra = ["--sin-path"] if not ar.leer_registro(str(home())).get("perfil") and not ar.ES_WINDOWS else []
        return subprocess.call([sys.executable, destino, *extra])


def cmd_usar(args: list[str]) -> int:
    if not args or not ar.VERSION_RE.match(args[0].lstrip("v")):
        est.error("Uso:  uxyngraphar usar X.Y.Z   (versiones guardadas:  uxyngraphar version)")
        return 2
    v = args[0].lstrip("v")
    if v in ar.versiones_guardadas(str(home())):
        ar.escribir_atomico(str(home() / "actual"), v + "\n")
        est.ok(f"Versión activa: {v}. Tus proyectos no cambian hasta que ejecutes  uxyngraphar actualizar.", "")
        return 0
    return cmd_autoactualizar(["--version", v])


def cmd_version(_args: list[str]) -> int:
    h = str(home())
    est.titulo(f"uxyngraphar {version_herramienta()}")
    print(est.dim("Carpeta: ") + h)
    guardadas = ar.versiones_guardadas(h)
    if guardadas:
        activa = ar.version_activa(h)
        print(est.dim("Versiones guardadas: ") + ", ".join(f"{v} (activa)" if v == activa else v for v in guardadas))
    return 0


def cmd_desinstalar(args: list[str]) -> int:
    h = home()
    if "--si" not in args:
        try:
            r = input(f"Se borrará {h} y el comando uxyngraphar. Tus proyectos no se tocan. ¿Seguir? [s/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            r = ""
        if r not in ("s", "si", "sí", "y", "yes"):
            print(est.dim("Sin cambios."))
            return 0
    for linea in sistema.desinstalar():
        if "PATH" in linea:
            est.ok(linea, "")
    est.ok("uxyngraphar se desinstaló de este equipo. Los proyectos conservan su copia del pack (en uxyngraphar/, o docs/ si se instalaron antes de la 1.1.0).", "")
    return 0


# ---------- ayuda ----------

def ayuda_general() -> list[str]:
    lineas = [est.pintar(f"uxyngraphar {version_herramienta()}", "titulo") + est.dim("  ·  instala y actualiza el pack documental en tus proyectos"),
              "", est.dim("Uso: ") + est.comando("uxyngraphar <comando> [opciones]")]
    izquierda = max(len(AYUDA[c][0]) for c in COMANDOS)
    for nombre, comandos in GRUPOS:
        lineas += ["", est.pintar(nombre, "seccion")]
        lineas += est.tabla([(AYUDA[c][0], AYUDA[c][1]) for c in comandos], izquierda=izquierda)
    lineas += ["", est.dim("Más ayuda: ") + est.comando("uxyngraphar ayuda <comando>")]
    manual = RAIZ / "documentacion" / "README.md"
    if manual.is_file():
        lineas.append(est.dim("Manual: ") + str(manual))
    return lineas


def ayuda_comando(cmd: str) -> list[str]:
    sintaxis, _, larga, opciones = AYUDA[cmd]
    lineas = [est.pintar("uxyngraphar " + sintaxis, "titulo"), ""]
    lineas += textwrap.wrap(larga, est.ancho_terminal() - 2, initial_indent="  ", subsequent_indent="  ")
    if opciones:
        lineas += ["", est.pintar("Opciones", "seccion")] + est.tabla(opciones)
    return lineas


def cmd_ayuda(args: list[str]) -> int:
    if args and args[0] not in AYUDA:
        est.error(f"No conozco el comando «{args[0]}». Comandos: {', '.join(COMANDOS)}")
        return 2
    print("\n".join(ayuda_comando(args[0]) if args else ayuda_general()))
    return 0


def main(argv: list[str] | None = None) -> int:
    ar.preparar_consola()
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help", "ayuda"):
        return cmd_ayuda(argv[1:])
    if argv[0] in ("--version", "-V"):
        argv[0] = "version"
    if argv[0] not in COMANDOS:
        est.error(f"Comando desconocido: {argv[0]}")
        print("Escribe  " + est.comando("uxyngraphar ayuda") + "  para ver los comandos.", file=sys.stderr)
        return 2
    return globals()["cmd_" + argv[0].replace("-", "_")](argv[1:])


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
