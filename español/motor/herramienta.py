"""La herramienta uxyngraphar en este equipo: versión, última publicada, actualizar, cambiar de versión, accesos
directos y desinstalar. Lo usan el panel y los comandos `version`, `autoactualizar`, `usar` y `desinstalar`."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

import casa
import proyectos
import repo
from casa import ar

MOTOR = Path(__file__).resolve().parent
CACHE_ULTIMA = 3600
_ultima: dict = {"cuando": 0.0, "version": "", "error": ""}
_trabajo: dict = {"estado": "inactivo", "lineas": [], "version": "", "codigo": None}
_candado = threading.Lock()


def version() -> str:
    return (MOTOR / "VERSION").read_text(encoding="utf-8").strip()


def instalada() -> bool:
    """True si este motor es una versión instalada (no la copia del repositorio)."""
    return MOTOR.parents[1] == (casa.carpeta() / "versiones").resolve()


def lanzador() -> str:
    """El comando «uxyngraphar» que creó el instalador (vacío si no hay instalación)."""
    candidatos = [os.environ.get("UXYNGRAPHAR_LANZADOR", ""), casa.leer_json("ultima-instalacion.json", {}).get("lanzador", "")]
    candidatos += [x for x in casa.leer_json("instalacion.json", {}).get("lanzadores", []) if not x.endswith(".cmd")]
    return next((c for c in candidatos if c and os.path.isfile(c)), "")


def info() -> dict:
    home = str(casa.carpeta())
    registro = ar.leer_registro(home)
    return {"version": version(), "instalada": instalada(), "carpeta": home, "activa": ar.version_activa(home),
            "guardadas": ar.versiones_guardadas(home), "anterior": registro.get("anterior", ""),
            "ultima_buena": registro.get("ultima_buena", ""), "lanzador": lanzador(), "python": sys.executable}


def ultima(forzar: bool = False) -> dict:
    """Última versión publicada (consulta la red como mucho una vez por hora; sin red no falla)."""
    if forzar or time.time() - _ultima["cuando"] > CACHE_ULTIMA:
        with tempfile.TemporaryDirectory() as t:
            destino = os.path.join(t, "SHA256SUMS")
            try:
                ar.descargar(ar.url_ultima("SHA256SUMS"), destino, intentos=1, espera=8)
                _ultima.update(version=ar.version_de_sumas(ar.leer_sumas(destino)), error="")
            except (ar.ErrorInstalacion, OSError) as e:
                _ultima.update(version="", error=str(e))
        _ultima["cuando"] = time.time()
    actual = version()
    nueva = bool(_ultima["version"]) and ar.VERSION_RE.match(_ultima["version"]) is not None and \
        tuple(map(int, _ultima["version"].split("."))) > tuple(map(int, actual.split(".")))
    return {"actual": actual, "ultima": _ultima["version"], "hay_nueva": nueva, "error": _ultima["error"]}


def descargar_instalador(version_pedida: str, carpeta: str) -> str:
    """Descarga el instalador de una línea de esa versión (o de la última) a `carpeta`."""
    v = version_pedida.lstrip("v")
    url = ar.url_de(v, "instalar-uxyngraphar.py") if v else ar.url_ultima("instalar-uxyngraphar.py")
    destino = os.path.join(carpeta, "instalar-uxyngraphar.py")
    ar.descargar(url, destino)
    return destino


def argumentos_instalador() -> list[str]:
    return ["--sin-path"] if not ar.leer_registro(str(casa.carpeta())).get("perfil") and not ar.ES_WINDOWS else []


def _anotar(linea: str) -> None:
    with _candado:
        _trabajo["lineas"].append(linea)


def _actualizar_en_fondo(version_pedida: str) -> None:
    """Pase lo que pase (sin red, disco lleno, permisos…), el trabajo termina en «hecho» o «error»: nunca se queda
    «en_curso» y se puede volver a intentar."""
    home = casa.carpeta()
    codigo = 1
    try:
        home.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=home) as t:
            _anotar("Descargando el instalador…")
            instalador = descargar_instalador(version_pedida, t)
            env = dict(os.environ, UXYNGRAPHAR_CONSOLA="1", UXYNGRAPHAR_SIN_ACCESOS="1", PYTHONIOENCODING="utf-8", NO_COLOR="1")
            proc = subprocess.Popen([sys.executable, instalador, "--consola", *argumentos_instalador()],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                    env=env, text=True, encoding="utf-8", errors="replace")
            with proc:
                for linea in proc.stdout:
                    if linea.strip():
                        _anotar(linea.rstrip())
                codigo = proc.wait()
    except ar.ErrorInstalacion as e:
        _anotar(str(e))
    except Exception as e:  # noqa: BLE001 - el panel tiene que ver el error y poder reintentar
        _anotar(f"error inesperado: {type(e).__name__}: {e}")
    finally:
        try:
            activa = ar.version_activa(str(home))
        except Exception:  # noqa: BLE001
            activa = ""
        with _candado:
            _trabajo.update(codigo=codigo, estado="hecho" if codigo == 0 else "error", version=activa)


def actualizar(version_pedida: str = "") -> dict:
    """Arranca la actualización en segundo plano; el panel consulta `progreso()`."""
    with _candado:
        en_curso = _trabajo["estado"] == "en_curso"
        if not en_curso:
            _trabajo.update(estado="en_curso", lineas=[], version="", codigo=None)
    if en_curso:
        return progreso()
    threading.Thread(target=_actualizar_en_fondo, args=(version_pedida,), daemon=True).start()
    return progreso()


def progreso() -> dict:
    with _candado:
        copia = {**_trabajo, "lineas": list(_trabajo["lineas"])}
    return {**copia, "reiniciar": copia["estado"] == "hecho" and copia["version"] != version()}


def usar(v: str) -> dict:
    """Activa una versión guardada (respaldando y adaptando los datos, y comprobando que arranca; si algo falla, todo
    queda como estaba). Si no está guardada, la descarga en segundo plano."""
    v = str(v or "").lstrip("v")
    if not ar.VERSION_RE.match(v):
        raise ValueError("versión no válida (formato X.Y.Z)")
    home = str(casa.carpeta())
    if v in ar.versiones_guardadas(home):
        with ar.Candado(home):
            try:
                ar.activar_version(home, v, lanzador())
            except ar.ErrorInstalacion as e:
                raise ValueError(str(e)) from e
        return {"estado": "hecho", "version": v, "lineas": [f"Versión activa: {v} (comprobada)."], "reiniciar": v != version()}
    return actualizar(v)


def volver_anterior() -> dict:
    anterior = ar.leer_registro(str(casa.carpeta())).get("anterior", "")
    if not anterior:
        raise ValueError("no hay una versión anterior registrada")
    return usar(anterior)


def reparar(con_proyectos: bool = False) -> dict:
    import reparacion
    try:
        return reparacion.reparar(con_proyectos)
    except ar.ErrorInstalacion as e:
        raise ValueError(str(e)) from e


def actualizar_proyectos() -> list[dict]:
    """Actualiza (o repara) los sistemas de todos los proyectos registrados."""
    resultados = []
    for ruta in proyectos.listar():
        fila = {"ruta": ruta, "nombre": Path(ruta).name, "actualizados": [], "error": ""}
        try:
            if not Path(ruta).is_dir():
                raise FileNotFoundError("la carpeta ya no existe")
            fila["actualizados"] = repo.actualizar(Path(ruta))
        except (ValueError, FileNotFoundError) as e:
            fila["error"] = str(e)
        except Exception as e:  # noqa: BLE001 - un proyecto que falla no impide actualizar los demás
            fila["error"] = f"{type(e).__name__}: {e}"
        resultados.append(fila)
    return resultados


def accesos() -> dict:
    registro = ar.leer_registro(str(casa.carpeta()))
    creados = {a.get("tipo") for a in registro.get("accesos", [])}
    return {"disponibles": [{**d, "creado": d["tipo"] in creados} for d in ar.accesos_disponibles()],
            "lanzador": lanzador()}


def cambiar_accesos(tipos: list[str]) -> dict:
    """Deja exactamente los accesos directos pedidos (crea los que falten y quita los demás)."""
    home = str(casa.carpeta())
    lanza = lanzador()
    if not lanza:
        raise ValueError("los accesos directos necesitan la herramienta instalada (comando de instalación de una línea)")
    registro = ar.leer_registro(home)
    avisos = ar.quitar_accesos(registro)
    if tipos:
        avisos += ar.crear_accesos(home, lanza, list(tipos), registro)
    ar.escribir_atomico(os.path.join(home, "instalacion.json"), ar.json.dumps(registro, indent=2, ensure_ascii=True) + "\n")
    return {**accesos(), "avisos": avisos}


def agregar_path() -> str:
    home = str(casa.carpeta())
    registro = ar.leer_registro(home)
    aviso = ar.asegurar_path(home, registro)
    ar.escribir_atomico(os.path.join(home, "instalacion.json"), ar.json.dumps(registro, indent=2, ensure_ascii=True) + "\n")
    return aviso or "El comando uxyngraphar ya estaba en tu PATH."


def desinstalar(alcance: str = "herramienta", rutas: list[str] | None = None, con_trabajo: bool = False,
                simular: bool = False) -> dict:
    """Desinstala por alcance (ver desinstalacion.py). Con `simular`, solo dice qué se quitaría."""
    import desinstalacion
    informe = desinstalacion.ejecutar(alcance, rutas or None, con_trabajo, simular, desde_panel_pid=os.getpid())
    return {**informe, "texto": desinstalacion.texto_informe(informe)}
