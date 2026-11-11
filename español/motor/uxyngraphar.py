#!/usr/bin/env python3
"""uxyngraphar: catálogo e instalación de sistemas de gobernanza para tus repos.

  uxyngraphar                       abre el panel (si hay una persona delante; si no, esta ayuda)
  uxyngraphar <comando> …           comandos de sistemas: catalogo, crear, instalar, actualizar, quitar, estado,
                                    verificar, indice, flujo, panel…  (uxyngraphar --help)

La herramienta en este equipo:
  uxyngraphar version               versión activa y versiones guardadas
  uxyngraphar autoactualizar [--version X.Y.Z]   descarga, comprueba e instala la última (o esa) versión
  uxyngraphar usar X.Y.Z            vuelve a una versión guardada (la descarga si falta); «usar anterior» vuelve a la previa
  uxyngraphar reparar [--proyectos] [--sin-descargar]   arregla la herramienta (y los proyectos registrados)
  uxyngraphar desinstalar [--alcance todo|herramienta|proyectos|accesos] [--proyectos RUTA,RUTA] [--con-trabajo]
                          [--simular] [--si]       sin --alcance pregunta qué quitar
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent   # versiones/X.Y.Z/motor/ (instalada) o español/motor/ (repositorio)
sys.path[:0] = [str(RAIZ), str(RAIZ / "distribucion")]

import arranque as ar  # noqa: E402
import cli  # noqa: E402
import herramienta  # noqa: E402

HERRAMIENTA = ("version", "autoactualizar", "usar", "reparar", "desinstalar", "_autocomprobar", "_casa")
MODULOS = ("andamiaje", "artefacto", "auditoria", "casa", "catalogo", "cli", "completado", "desinstalacion", "diagnostico", "entrada", "especificacion", "flujos_guardados",
           "fuentes", "generador", "generar", "grupos", "herramienta", "integracion", "nomenclatura", "panel", "piezas", "procesos", "protecciones", "vocabulario", "proyectos", "remoto", "reparacion", "repo",
           "rutas_panel", "transaccion", "memorias_repo", "accesos", "arranque")


def version() -> str:
    return (RAIZ / "VERSION").read_text(encoding="utf-8").strip()


def home() -> Path:
    return Path(ar.carpeta_home())


def _opcion(args: list[str], nombre: str) -> str:
    return args[args.index(nombre) + 1] if nombre in args and args.index(nombre) + 1 < len(args) else ""


def cmd_version(_args: list[str]) -> int:
    print(f"uxyngraphar {version()}")
    guardadas = ar.versiones_guardadas(str(home()))
    if guardadas:
        activa = ar.version_activa(str(home()))
        registro = ar.leer_registro(str(home()))
        print(f"Carpeta: {home()}\nVersiones guardadas: " + ", ".join(f"{v} (activa)" if v == activa else v for v in guardadas))
        if registro.get("anterior"):
            print(f"Anterior: {registro['anterior']}  (volver:  uxyngraphar usar anterior)")
    return 0


def cmd_autoactualizar(args: list[str]) -> int:
    v = _opcion(args, "--version").lstrip("v")
    home().mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=home()) as t:
        try:
            destino = herramienta.descargar_instalador(v, t)
        except ar.ErrorInstalacion as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        extra = ["--reparar"] if "--reparar" in args else []
        return subprocess.call([sys.executable, destino, *herramienta.argumentos_instalador(), *extra])


def cmd_usar(args: list[str]) -> int:
    pedida = args[0].lstrip("v") if args else ""
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
        return cmd_autoactualizar(["--version", pedida])
    print("\n".join(r["lineas"]))
    return 0


def cmd_reparar(args: list[str]) -> int:
    import reparacion
    try:
        informe = reparacion.reparar("--proyectos" in args, descargar="--sin-descargar" not in args)
    except ar.ErrorInstalacion as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for h in informe["hechos"]:
        print(f"  arreglado: {h}")
    for p in informe["problemas"]:
        print(f"  PROBLEMA: {p}")
    for fila in informe.get("proyectos", []):
        estado = f"ERROR: {fila['error']}" if fila["error"] else ("; ".join(fila["hechos"]) or "sano")
        print(f"  {fila['nombre']}: {estado}")
    if informe.get("nota"):
        print(f"  nota: {informe['nota']}")
    if not informe["hechos"] and not informe["problemas"]:
        print("Todo estaba bien: no hubo nada que reparar.")
    if informe["problemas"]:
        print("\nSi la herramienta no arranca, el instalador de una línea con --reparar la rehace sin tocar tus proyectos.")
    return 1 if informe["problemas"] or any(f["error"] for f in informe.get("proyectos", [])) else 0


def cmd_desinstalar(args: list[str]) -> int:
    import desinstalacion as des
    alcance = _opcion(args, "--alcance")
    rutas = [r for r in _opcion(args, "--proyectos").split(",") if r]
    con_trabajo = "--con-trabajo" in args
    if not alcance:
        if "--si" in args:
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
    if "--simular" in args:
        return 0
    if "--si" not in args:
        if not des.esp.base.terminal_interactiva():
            print("Sin cambios: sin terminal no puedo preguntar; repite con --si para desinstalar.", file=sys.stderr)
            return 2
        try:
            r = input("¿Seguir con la desinstalación? [s/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            r = ""
        if r not in ("s", "si", "sí", "y", "yes"):
            print("Sin cambios.")
            return 0
    informe = des.ejecutar(alcance, rutas or None, con_trabajo)
    print(des.texto_informe(informe))
    if informe.get("informe"):
        print(f"Informe guardado en {informe['informe']}")
    return 1 if informe["pendiente"] else 0


def cmd__autocomprobar(_args: list[str]) -> int:
    """Lo que el instalador ejecuta antes de activar una versión: arranca, importa todo y valida el catálogo."""
    import importlib
    for m in MODULOS:
        importlib.import_module(m)
    import catalogo
    malos = {m["id"]: m["errores"] for m in catalogo.listar() if m["errores"]}
    if malos:
        print(f"catálogo con errores: {malos}")
        return 1
    print(f"ok {version()}")
    return 0


def cmd__casa(args: list[str]) -> int:
    import casa
    if args[:1] != ["migrar"]:
        print("Uso: uxyngraphar _casa migrar", file=sys.stderr)
        return 2
    codigo, mensaje = casa.migrar()
    print(mensaje)
    return codigo


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
    if argv[0] in HERRAMIENTA and not (argv[0] == "version" and len(argv) > 1):
        if argv[0] in ("version", "_autocomprobar", "_casa") or "--simular" in argv:
            return globals()["cmd_" + argv[0]](argv[1:])
        import auditoria
        try:
            codigo = globals()["cmd_" + argv[0]](argv[1:])
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
