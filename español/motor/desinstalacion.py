"""Desinstalar uxyngraphar por alcance, igual desde la CLI que desde el panel.

  todo         la herramienta y uxyngraphar de todos los proyectos registrados
  herramienta  núcleo, panel, comando, PATH, accesos directos y la carpeta de uxyngraphar; los proyectos se conservan
  proyectos    uxyngraphar de todos los proyectos registrados o de los elegidos; la herramienta se conserva
  accesos      solo los accesos directos del panel (menú, escritorio, barra)

En cada proyecto se conserva `uxyngraphar/trabajo/` salvo
`con_trabajo`. `simular` devuelve lo que se haría sin tocar nada. Los proyectos se procesan antes que la herramienta, el
panel abierto se cierra y al final se comprueba que no queda nada; el informe se guarda fuera de la carpeta borrada.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import time
from pathlib import Path

import casa
import especificacion as esp
import generar
import proyectos
import repo
from casa import ar

ALCANCES = ("todo", "herramienta", "proyectos", "accesos")
DESCRIPCIONES = {
    "todo": "la herramienta y uxyngraphar de todos los proyectos registrados",
    "herramienta": "solo la herramienta (núcleo, panel, comando, PATH y accesos directos); tus proyectos no se tocan",
    "proyectos": "uxyngraphar de tus proyectos (todos o los que elijas); la herramienta se queda",
    "accesos": "solo los accesos directos del panel (menú, escritorio, barra)",
}
base = esp.base


def _tipo(ruta: Path) -> str:
    if not ruta.is_dir():
        return "no_existe"
    if (ruta / base.CARPETA_RAIZ).is_dir():
        return "actual"
    return "sin_uxyngraphar"


def _plan_proyecto(ruta: str, con_trabajo: bool) -> dict:
    raiz = Path(ruta)
    fila = {"ruta": ruta, "nombre": raiz.name, "tipo": _tipo(raiz), "quitar": [], "conservar": []}
    if fila["tipo"] == "actual":
        ids = [m["id"] for m in generar.instalados(raiz)]
        fila["quitar"] = [f"{base.CARPETA_SISTEMAS_DE_GOBERNANZA}/{i}/" for i in ids] + [
            f"{base.CARPETA_RAIZ}/{esp.INDICE}", f"{base.CARPETA_RAIZ}/{esp.FLUJO}",
            "bloque uxyngraphar de AGENTES.md/AGENTS.md/CLAUDE.md", "protecciones de uxyngraphar (.claude/settings.json, .cursorignore…)"]
        trabajo = f"{base.CARPETA_TRABAJO}/"
        (fila["quitar"] if con_trabajo else fila["conservar"]).append(trabajo)
    return fila


def _de_esta_casa(ruta: str, home: str) -> bool:
    """El lanzador es nuestro y apunta a esta carpeta de uxyngraphar (no a otra instalación con UXYNGRAPHAR_HOME propio)."""
    if not ar.es_nuestro(ruta):
        return False
    try:
        with open(ruta, encoding="utf-8", errors="replace") as f:
            texto = f.read(4000)
    except OSError:
        return False
    return home in texto or repr(home)[1:-1] in texto


def candidatos_lanzador(home: str) -> list[str]:
    registro = ar.leer_registro(home)
    rutas = list(registro.get("lanzadores", []))
    carpetas = {ar.carpeta_bin(home), os.path.join(home, "bin")}
    if not ar.home_propio():
        carpetas.add(os.path.expanduser(os.path.join("~", ".local", "bin")))
    for d in carpetas:
        for nombre in ("uxyngraphar", "uxyngraphar-lanzador.py", "uxyngraphar.cmd"):
            rutas.append(os.path.join(d, nombre))
    return sorted({r for r in rutas if os.path.isfile(r) and _de_esta_casa(r, home)})


def perfiles_con_bloque() -> list[str]:
    """Archivos de inicio de la terminal con nuestro bloque PATH (solo en la instalación normal: una carpeta propia no
    toca los perfiles)."""
    if ar.home_propio():
        return []
    casa_usuario = os.path.expanduser("~")
    candidatos = [".bashrc", ".bash_profile", ".profile", ".zshrc", os.path.join(".config", "fish", "config.fish")]
    zdot = os.environ.get("ZDOTDIR")
    rutas = [os.path.join(casa_usuario, c) for c in candidatos] + ([os.path.join(zdot, ".zshrc")] if zdot else [])
    salida = []
    for r in sorted(set(rutas)):
        try:
            with open(r, encoding="utf-8", errors="replace") as f:
                if ar.BLOQUE_INI in f.read():
                    salida.append(r)
        except OSError:
            continue
    return salida


def planificar(alcance: str, rutas: list[str] | None = None, con_trabajo: bool = False) -> dict:
    """Lo que se quitaría con ese alcance. `rutas`: proyectos elegidos (solo con «proyectos»; por defecto, todos)."""
    if alcance not in ALCANCES:
        raise ValueError(f"alcance no válido: {alcance} (usa {', '.join(ALCANCES)})")
    home = str(casa.carpeta())
    registro = ar.leer_registro(home)
    plan = {"alcance": alcance, "descripcion": DESCRIPCIONES[alcance], "con_trabajo": con_trabajo, "proyectos": [],
            "herramienta": [], "accesos": [a.get("ruta", "") for a in registro.get("accesos", [])]}
    if alcance in ("todo", "proyectos"):
        elegidos = [str(Path(r).expanduser().resolve()) for r in rutas] if (alcance == "proyectos" and rutas) else proyectos.listar()
        plan["proyectos"] = [_plan_proyecto(r, con_trabajo) for r in elegidos]
    if alcance in ("todo", "herramienta"):
        plan["herramienta"] = [home] + candidatos_lanzador(home) + [f"bloque PATH en {p}" for p in perfiles_con_bloque()]
        if registro.get("path_windows"):
            plan["herramienta"].append(f"PATH de usuario de Windows: {registro['path_windows']}")
    return plan


def cerrar_panel(excepto_pid: int | None = None) -> str:
    """Cierra el panel abierto en este equipo (si no es este mismo proceso)."""
    import panel
    abierto = panel.cerrar_abierto(excepto_pid)
    return f"panel cerrado (puerto {abierto['puerto']})" if abierto else ""


def _quitar_proyecto(fila: dict, con_trabajo: bool) -> dict:
    raiz = Path(fila["ruta"])
    resultado = {"ruta": fila["ruta"], "nombre": fila["nombre"], "tipo": fila["tipo"], "hechos": [], "error": ""}
    try:
        if fila["tipo"] == "actual":
            ids = repo.desinstalar(raiz, con_trabajo)
            resultado["hechos"].append(f"sistemas retirados: {', '.join(ids) or '(ninguno)'}")
        elif fila["tipo"] == "no_existe":
            resultado["hechos"].append("la carpeta ya no existe")
        else:
            resultado["hechos"].append("no tenía uxyngraphar")
    except Exception as e:  # noqa: BLE001 - un proyecto que falla no impide seguir con los demás
        resultado["error"] = str(e)
    return resultado


def retirar_de_proyecto(ruta: str, con_trabajo: bool = False) -> dict:
    """Quita uxyngraphar de un proyecto, (`retirar` y su botón en el panel)."""
    fila = _plan_proyecto(str(Path(ruta).resolve()), con_trabajo)
    if fila["tipo"] == "no_existe":
        raise FileNotFoundError(f"no existe la carpeta {ruta}")
    resultado = _quitar_proyecto(fila, con_trabajo)
    if resultado["error"]:
        raise ValueError(resultado["error"])
    return resultado


def _borrar_casa(home: str) -> str:
    if not os.path.isdir(home):
        return ""
    if ar.ES_WINDOWS:   # los archivos de la versión en uso están abiertos: se borra al salir este proceso
        orden = f'ping -n 3 127.0.0.1 >nul & rmdir /s /q "{home}"'
        subprocess.Popen(["cmd", "/c", orden], creationflags=0x00000008 | 0x00000200, close_fds=True)   # DETACHED, NEW_GROUP
        return f"{home}: se borrará en unos segundos, al cerrarse uxyngraphar"
    repo.borrar_arbol(Path(home))
    return f"{home}: borrada"


def ejecutar(alcance: str, rutas: list[str] | None = None, con_trabajo: bool = False, simular: bool = False,
             desde_panel_pid: int | None = None) -> dict:
    plan = planificar(alcance, rutas, con_trabajo)
    if simular:
        return {**plan, "simulado": True}
    home = str(casa.carpeta())
    informe = {**plan, "simulado": False, "resultados": [], "hechos": [], "pendiente": []}
    if alcance in ("todo", "herramienta"):
        cerrado = cerrar_panel(desde_panel_pid)
        if cerrado:
            informe["hechos"].append(cerrado)
    for fila in plan["proyectos"]:
        informe["resultados"].append(_quitar_proyecto(fila, con_trabajo))
    if alcance == "proyectos":
        hechos = {r["ruta"] for r in informe["resultados"] if not r["error"]}
        for ruta in hechos:
            proyectos.quitar(ruta)
    registro = ar.leer_registro(home)
    if alcance in ("todo", "herramienta", "accesos"):
        informe["hechos"] += ar.quitar_accesos(registro)
        informe["hechos"].append("accesos directos retirados")
        if alcance == "accesos":
            ar.escribir_registro(home, registro)
    if alcance in ("todo", "herramienta"):
        for lanza in candidatos_lanzador(home):
            os.remove(lanza)
            informe["hechos"].append(f"comando retirado: {lanza}")
        for perfil in set(perfiles_con_bloque() + [registro.get("perfil", "")]) - {""}:
            if ar.quitar_de_perfil(perfil):
                informe["hechos"].append(f"PATH: bloque retirado de {perfil}")
        if registro.get("path_windows"):
            ar._path_windows(registro["path_windows"], False)
            informe["hechos"].append(f"PATH de Windows: {registro['path_windows']} retirado")
        informe["hechos"].append(_borrar_casa(home))
        informe["pendiente"] += [f"queda el comando {linea}" for linea in candidatos_lanzador(home)]
        informe["pendiente"] += [f"queda el bloque PATH en {p}" for p in perfiles_con_bloque()]
        if not ar.ES_WINDOWS and os.path.exists(home):
            informe["pendiente"].append(f"queda la carpeta {home}")
    informe["pendiente"] += [f"{r['nombre']}: {r['error']}" for r in informe["resultados"] if r["error"]]
    informe["informe"] = guardar_informe(informe)
    return informe


def texto_informe(informe: dict) -> str:
    lineas = [f"uxyngraphar: desinstalación «{informe['alcance']}» — {informe['descripcion']}",
              "(simulación: no se ha tocado nada)" if informe.get("simulado") else time.strftime("%Y-%m-%d %H:%M:%S")]
    filas = informe.get("resultados") or informe.get("proyectos") or []
    if filas:
        lineas.append("\nProyectos:")
    for f in filas:
        lineas.append(f"  {f['nombre']} ({f['tipo']}): {f['ruta']}")
        for q in f.get("quitar", [])[:15]:
            lineas.append(f"    - quitar: {q}")
        if len(f.get("quitar", [])) > 15:
            lineas.append(f"    - … y {len(f['quitar']) - 15} más")
        if f.get("conservar"):
            lineas.append(f"    · se conservan {len(f['conservar'])} archivos propios")
        lineas += [f"    {h}" for h in f.get("hechos", [])]
        if f.get("error"):
            lineas.append(f"    ERROR: {f['error']}")
    if informe.get("herramienta"):
        lineas.append("\nHerramienta:" if informe.get("simulado") else "\nHerramienta quitada:")
        lineas += [f"  - {h}" for h in informe["herramienta"]]
    if informe.get("accesos") and informe["alcance"] != "proyectos":
        lineas.append("\nAccesos directos:")
        lineas += [f"  - {a}" for a in informe["accesos"]]
    if informe.get("hechos"):
        lineas.append("\nHecho:")
        lineas += [f"  {h}" for h in informe["hechos"] if h]
    if not informe.get("simulado"):
        lineas.append("\nComprobación final: " + ("no queda nada." if not informe.get("pendiente") else "quedan cosas:"))
        lineas += [f"  ! {p}" for p in informe.get("pendiente", [])]
    return "\n".join(lineas) + "\n"


def guardar_informe(informe: dict) -> str:
    ruta = Path(tempfile.gettempdir()) / f"uxyngraphar-desinstalacion-{time.strftime('%Y%m%d-%H%M%S')}.txt"
    try:
        ruta.write_text(texto_informe(informe), encoding="utf-8")
    except OSError:
        return ""
    return str(ruta)


def preguntar(entrada=input, salida=print) -> tuple[str, list[str], bool] | None:
    """Menú interactivo de la CLI: alcance, proyectos y trabajo. None si se cancela."""
    salida("¿Qué quieres desinstalar?")
    for i, a in enumerate(ALCANCES, 1):
        salida(f"  {i}. {a}: {DESCRIPCIONES[a]}")
    salida("  0. nada (cancelar)")
    eleccion = entrada("Elige un número [0]: ").strip()
    if eleccion not in {str(i) for i in range(1, len(ALCANCES) + 1)}:
        return None
    alcance = ALCANCES[int(eleccion) - 1]
    rutas: list[str] = []
    if alcance == "proyectos":
        registrados = proyectos.listar()
        if not registrados:
            salida("No hay proyectos registrados.")
            return None
        for i, r in enumerate(registrados, 1):
            salida(f"  {i}. {r}")
        texto = entrada("Números separados por comas, o «todos» [todos]: ").strip().lower()
        if texto and texto != "todos":
            try:
                rutas = [registrados[int(n) - 1] for n in texto.replace(" ", "").split(",") if n]
            except (ValueError, IndexError):
                salida("Selección no válida.")
                return None
    con_trabajo = False
    if alcance in ("todo", "proyectos"):
        r = entrada("¿Borrar también el trabajo de cada proyecto (uxyngraphar/trabajo/)? [s/N] ")
        con_trabajo = r.strip().lower() in ("s", "si", "sí", "y", "yes")
    return alcance, rutas, con_trabajo
