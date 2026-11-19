#!/usr/bin/env python3
"""uxyngraphar: catálogo e instalación de sistemas de gobernanza para tus repos.

  uxyngraphar                       abre el panel (si hay una persona delante; si no, esta ayuda)
  uxyngraphar <comando> …           comandos de sistemas: catalogo, crear, instalar, actualizar, quitar, estado,
                                    verificar, indice, flujo, panel…  (uxyngraphar --help)

La herramienta en este equipo (cada uno con --help):
  uxyngraphar version               versión activa y versiones guardadas
  uxyngraphar autoactualizar [--version X.Y.Z] [--reparar]   descarga, comprueba e instala la última (o esa) versión
  uxyngraphar usar X.Y.Z            vuelve a una versión guardada (la descarga si falta); «usar anterior» vuelve a la previa
  uxyngraphar reparar [--proyectos] [--sin-descargar]   arregla la herramienta (y los proyectos registrados)
  uxyngraphar desinstalar [--alcance todo|herramienta|proyectos|accesos] [--proyectos RUTA,RUTA] [--con-trabajo]
                          [--con-catalogo] [--simular] [--si]       sin --alcance pregunta qué quitar

Los sistemas que escribes (crear, generar, Taller) viven en el catálogo local, fuera de las versiones:
~/.uxyngraphar/catalogo/ (o UXYNGRAPHAR_CATALOGO). Reparar, actualizar o cambiar de versión no los tocan.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent   # versiones/X.Y.Z/motor/ (instalada) o español/motor/ (repositorio)
sys.path[:0] = [str(RAIZ), str(RAIZ / "distribucion")]

import arranque as ar  # noqa: E402
import casa  # noqa: E402
import cli  # noqa: E402
import herramienta  # noqa: E402

HERRAMIENTA = ("version", "autoactualizar", "usar", "reparar", "desinstalar", "_autocomprobar", "_casa")
MODULOS = ("andamiaje", "artefacto", "auditoria", "casa", "catalogo", "cli", "completado", "desinstalacion", "diagnostico", "entrada", "especificacion", "flujos_guardados",
           "fuentes", "generador", "generar", "grupos", "herramienta", "integracion", "nomenclatura", "panel", "piezas", "procesos", "protecciones", "vocabulario", "proyectos", "remoto", "reparacion", "repo",
           "rutas_panel", "transaccion", "memorias_repo", "accesos", "arranque")
ALCANCES = ("todo", "herramienta", "proyectos", "accesos")   # los de desinstalacion.ALCANCES
DESCRIPCIONES = {
    "version": "Versión activa de la herramienta y versiones guardadas. (Con <id> mayor|menor|parche sube la versión de "
               "un sistema del catálogo: uxyngraphar version <id> parche --help.)",
    "autoactualizar": "Descarga, comprueba e instala la última versión publicada (o la pedida). Tus proyectos y los "
                      "sistemas que escribiste no se tocan.",
    "usar": "Activa una versión guardada (la descarga si falta). «anterior» vuelve a la previa.",
    "reparar": "Arregla la herramienta sin cambiar de versión (y, con --proyectos, los proyectos registrados).",
    "desinstalar": "Quita uxyngraphar de este equipo por alcance. Sin --alcance pregunta qué quitar. Antes de borrar "
                   "sistemas que escribiste, avisa y pide confirmación.",
    "_autocomprobar": "Uso interno del instalador: comprueba que esta versión arranca.",
    "_casa": "Uso interno del instalador: adapta los datos de la casa a esta versión.",
}


def version() -> str:
    return (RAIZ / "VERSION").read_text(encoding="utf-8").strip()


def home() -> Path:
    return Path(ar.carpeta_home())


def analizador(cmd: str) -> argparse.ArgumentParser:
    """Opciones de cada comando de la herramienta (argparse en español): --help nunca ejecuta nada y una opción mal
    escrita se rechaza en vez de ignorarse."""
    ar.traducir_argparse()
    p = argparse.ArgumentParser(prog=f"uxyngraphar {cmd}", description=DESCRIPCIONES[cmd])
    if cmd == "autoactualizar":
        p.add_argument("--version", default="", metavar="X.Y.Z", help="esa versión en vez de la última publicada")
        p.add_argument("--reparar", action="store_true", help="la descarga y comprueba de nuevo aunque ya esté instalada")
    elif cmd == "usar":
        p.add_argument("version", metavar="X.Y.Z|anterior", help="versión guardada (si falta, se descarga) o «anterior»")
    elif cmd == "reparar":
        p.add_argument("--proyectos", action="store_true", help="repara también los proyectos registrados")
        p.add_argument("--sin-descargar", action="store_true", help="no descargar de nuevo las versiones dañadas (solo avisar)")
    elif cmd == "desinstalar":
        p.add_argument("--alcance", choices=ALCANCES, help="qué quitar (sin él, pregunta)")
        p.add_argument("--proyectos", default="", metavar="RUTA,RUTA", help="con --alcance proyectos: solo esos proyectos")
        p.add_argument("--con-trabajo", action="store_true", help="borra también uxyngraphar/trabajo/ de cada proyecto")
        p.add_argument("--con-catalogo", action="store_true", help="confirma que se borren los sistemas que escribiste")
        p.add_argument("--simular", action="store_true", help="solo dice qué se quitaría")
        p.add_argument("--si", action="store_true", help="no preguntar (sin --alcance: solo la herramienta)")
    elif cmd == "_casa":
        p.add_argument("accion", choices=("migrar",))
    return p


def cmd_version(_a: argparse.Namespace) -> int:
    print(f"uxyngraphar {version()}")
    guardadas = ar.versiones_guardadas(str(home()))
    if guardadas:
        activa = ar.version_activa(str(home()))
        registro = ar.leer_registro(str(home()))
        print(f"Carpeta: {home()}\nVersiones guardadas: " + ", ".join(f"{v} (activa)" if v == activa else v for v in guardadas))
        if registro.get("anterior"):
            print(f"Anterior: {registro['anterior']}  (volver:  uxyngraphar usar anterior)")
    return 0


def _autoactualizar(v: str, reparar: bool = False) -> int:
    v = v.lstrip("v")
    if v and not ar.VERSION_RE.match(v):
        print(f"error: versión no válida «{v}»: usa el formato X.Y.Z (por ejemplo --version 1.5.16)", file=sys.stderr)
        return 2
    home().mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=home()) as t:
        try:
            destino = herramienta.descargar_instalador(v, t)
        except ar.ErrorInstalacion as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        objetivo = v or herramienta.version_del_instalador(destino)
        extra = ["--version", v] if v else []
        carpeta = home() / "versiones" / objetivo if objetivo else None
        if reparar:
            extra.append("--reparar")
        elif carpeta and ar.version_completa(str(carpeta)) and not ar.coincide_con_publicada(str(carpeta), objetivo):
            extra.append("--reparar")
        return subprocess.call([sys.executable, destino, *herramienta.argumentos_instalador(), *extra])


def cmd_autoactualizar(a: argparse.Namespace) -> int:
    return _autoactualizar(a.version, a.reparar)


def cmd_usar(a: argparse.Namespace) -> int:
    pedida = a.version.lstrip("v")
    if pedida == "anterior":
        pedida = ar.leer_registro(str(home())).get("anterior", "")
        if not pedida:
            print("No hay una versión anterior registrada.  (versiones guardadas:  uxyngraphar version)", file=sys.stderr)
            return 1
    if not ar.VERSION_RE.match(pedida):
        print("Uso:  uxyngraphar usar X.Y.Z | anterior   (versiones guardadas:  uxyngraphar version)", file=sys.stderr)
        return 2
    try:
        r = herramienta.usar(pedida)
    except (ValueError, ar.ErrorInstalacion) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if r.get("estado") == "en_curso":   # no estaba guardada: la descarga el instalador
        return _autoactualizar(pedida)
    print("\n".join(r["lineas"]))
    return 0


def cmd_reparar(a: argparse.Namespace) -> int:
    import reparacion
    try:
        informe = reparacion.reparar(a.proyectos, descargar=not a.sin_descargar)
    except ar.ErrorInstalacion as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for h in informe["hechos"]:
        print(f"  arreglado: {h}")
    for p in informe["problemas"]:
        print(f"  PROBLEMA: {p}")
    filas = informe.get("proyectos", [])
    for fila in filas:
        estado = f"ERROR: {fila['error']}" if fila["error"] else ("; ".join(fila["hechos"]) or "sano")
        print(f"  {fila['nombre']}: {estado}")
    if informe.get("nota"):
        print(f"  nota: {informe['nota']}")
    errores = [f for f in filas if f["error"]]
    if not informe["hechos"] and not informe["problemas"] and not errores and not any(f["hechos"] for f in filas):
        print("Todo estaba bien: no hubo nada que reparar.")
    elif not informe["problemas"] and not errores:
        print("Reparación terminada: todo queda bien.")
    if informe["problemas"]:
        print("\nSi la herramienta no arranca, el instalador de una línea con --reparar la rehace sin tocar tus proyectos.")
    return 1 if informe["problemas"] or errores else 0


def _confirmar(pregunta: str, validas: tuple[str, ...] = ("s", "si", "sí", "y", "yes")) -> bool:
    try:
        return input(pregunta).strip().lower() in validas
    except (EOFError, KeyboardInterrupt):
        return False


def cmd_desinstalar(a: argparse.Namespace) -> int:
    import desinstalacion as des
    alcance = a.alcance or ""
    rutas = [r for r in a.proyectos.split(",") if r]
    con_trabajo = a.con_trabajo
    if not alcance:
        if a.si:
            alcance = "herramienta"   # «desinstalar --si» de siempre: solo la herramienta
        elif des.esp.base.terminal_interactiva():
            elegido = des.preguntar()
            if not elegido:
                print("Sin cambios.")
                return 0
            alcance, rutas, con_trabajo = elegido
        else:
            print("Indica qué quitar con --alcance " + "|".join(des.ALCANCES) + " (y --si para no preguntar).", file=sys.stderr)
            return 2
    try:
        plan = des.ejecutar(alcance, rutas or None, con_trabajo, simular=True)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(des.texto_informe(plan))
    if a.simular:
        return 0
    interactiva = des.esp.base.terminal_interactiva()
    if not a.si:
        if not interactiva:
            print("Sin cambios: sin terminal no puedo preguntar; repite con --si para desinstalar.", file=sys.stderr)
            return 2
        if not _confirmar("¿Seguir con la desinstalación? [s/N] "):
            print("Sin cambios.")
            return 0
    con_catalogo = a.con_catalogo
    if plan.get("catalogo") and not con_catalogo:
        if a.si or not interactiva:
            print(f"Sin cambios: se borrarían {len(plan['catalogo'])} sistemas que escribiste. Muévelos antes fuera de "
                  f"{home()} o añade --con-catalogo para borrarlos también.", file=sys.stderr)
            return 2
        con_catalogo = _confirmar(f"Se borrarán también {len(plan['catalogo'])} sistemas que escribiste (lista de arriba). "
                                  "Escribe «borrar» para confirmarlo: ", ("borrar",))
        if not con_catalogo:
            print("Sin cambios: tus sistemas siguen donde estaban.")
            return 0
    informe = des.ejecutar(alcance, rutas or None, con_trabajo, con_catalogo=con_catalogo)
    print(des.texto_informe(informe))
    if informe.get("informe"):
        print(f"Informe guardado en {informe['informe']}")
    return 1 if informe["pendiente"] else 0


def cmd__autocomprobar(_a: argparse.Namespace) -> int:
    """Lo que el instalador ejecuta antes de activar una versión: arranca, importa todo y valida el catálogo que trae
    (no el de la persona: un borrador a medias no puede impedir actualizar)."""
    import importlib
    for m in MODULOS:
        importlib.import_module(m)
    import catalogo
    malos = {m["id"]: m["errores"] for m in catalogo.listar(catalogo.esp.CATALOGO) if m["errores"]}
    if malos:
        print(f"catálogo con errores: {malos}")
        return 1
    print(f"ok {version()}")
    return 0


def cmd__casa(_a: argparse.Namespace) -> int:
    codigo, mensaje = casa.migrar()
    print(mensaje)
    return codigo


def _ejecutar(cmd: str, a: argparse.Namespace) -> int:
    try:
        return globals()["cmd_" + cmd](a)
    except OSError as e:   # permisos, disco lleno…: un mensaje en español, no un traceback
        print(f"error: {casa.mensaje_de_error(e)}", file=sys.stderr)
        return 1


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
    catalogo_version = argv[0] == "version" and len(argv) > 1 and argv[1] not in ("-h", "--help")
    if argv[0] in HERRAMIENTA and not catalogo_version:
        a = analizador(argv[0]).parse_args(argv[1:])   # --help o una opción mal escrita terminan aquí, sin ejecutar nada
        if argv[0] in ("version", "_autocomprobar", "_casa") or getattr(a, "simular", False):
            return _ejecutar(argv[0], a)
        import auditoria
        try:
            codigo = _ejecutar(argv[0], a)
        except BaseException as e:
            auditoria.registrar(argv[0], error=f"{type(e).__name__}: {e}", argumentos=argv[1:])
            raise
        auditoria.registrar(argv[0], error="" if codigo == 0 else f"código {codigo}", argumentos=argv[1:])
        return codigo
    return cli.main(argv)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130) from None
