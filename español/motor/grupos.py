"""Grupos de proyectos (M-18): varios repos que forman un sistema (p. ej. backend, frontend y landing) y se gestionan a la
vez: actualizar, verificar (con la comparación de contratos entre ellos) y aplicar un flujo guardado. Se guardan en
`grupos.json` de la carpeta de uxyngraphar, aparte de `proyectos.json`, así que una versión anterior no los pierde."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import casa
import fuentes
import flujos_guardados
import generar
import proyectos
import repo

ARCHIVO = "grupos.json"
NOMBRE = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")
CONTRATOS = "contratos-entre-repositorios"


def listar() -> dict[str, list[str]]:
    datos = casa.leer_json(ARCHIVO, {})
    grupos = datos.get("grupos", {}) if isinstance(datos, dict) else {}
    return {n: [str(r) for r in rutas if isinstance(r, str)] for n, rutas in grupos.items() if isinstance(rutas, list)}


def _guardar(grupos: dict[str, list[str]]) -> None:
    casa.escribir_json(ARCHIVO, {"formato": 1, "grupos": dict(sorted(grupos.items()))})


def miembros(nombre: str) -> list[str]:
    grupos = listar()
    if nombre not in grupos:
        raise FileNotFoundError(f"no existe el grupo «{nombre}»")
    return grupos[nombre]


def guardar(nombre: str, rutas: list[str]) -> list[str]:
    """Crea o reemplaza un grupo. Sus miembros tienen que estar en «Mis proyectos» (registrar es una acción aparte)."""
    if not NOMBRE.match(str(nombre or "")):
        raise ValueError("nombre del grupo: minúsculas, dígitos y guiones (p. ej. «uxyngraphar»)")
    registrados = proyectos.listar()
    limpias = []
    for r in rutas:
        ruta = str(Path(str(r)).expanduser().resolve())
        if not proyectos.registrado(ruta, registrados):
            raise ValueError(f"{ruta} no está en «Mis proyectos»: añádelo antes de agruparlo")
        limpias.append(ruta)
    if len(set(limpias)) < 2:
        raise ValueError("un grupo necesita al menos dos proyectos distintos")
    _guardar({**listar(), nombre: list(dict.fromkeys(limpias))})
    return limpias


def borrar(nombre: str) -> None:
    grupos = listar()
    if grupos.pop(nombre, None) is None:
        raise FileNotFoundError(f"no existe el grupo «{nombre}»")
    _guardar(grupos)


def _por_miembro(nombre: str, hacer) -> list[dict]:
    salida = []
    for ruta in miembros(nombre):
        fila = {"ruta": ruta, "nombre": Path(ruta).name, "error": ""}
        try:
            fila.update(hacer(Path(ruta)))
        except Exception as e:  # noqa: BLE001 - un repo que falla no impide seguir con los demás del grupo
            fila["error"] = f"{type(e).__name__}: {e}" if not isinstance(e, (ValueError, FileNotFoundError)) else str(e)
        salida.append(fila)
    return salida


def actualizar(nombre: str) -> list[dict]:
    """Actualiza (o repara) los sistemas de todos los repos del grupo; un único informe."""
    return _por_miembro(nombre, lambda raiz: {"actualizados": repo.actualizar(raiz)})


def aplicar_flujo(nombre: str, fid: str) -> list[dict]:
    return flujos_guardados.aplicar(fid, miembros(nombre))


def _comparar_contratos(raiz: Path, otros: list[str]) -> dict:
    script = repo.carpeta_instalada(raiz, CONTRATOS) / "scripts" / "contratos.py"
    if not script.is_file():
        return {"contratos": "no instalado"}
    relativos = [str(Path(o).resolve()) for o in otros]
    r = subprocess.run([sys.executable, "-B", "-X", "utf8", str(script), "comparar", *relativos], cwd=raiz, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=repo.SEGUNDOS_VERIFICAR)
    return {"contratos": "alineados" if r.returncode == 0 else "divergentes", "contratos_salida": (r.stdout + r.stderr).strip()}


def verificar(nombre: str, trabajos: int = 4) -> list[dict]:
    """Verificaciones de cada repo y, donde esté instalado contratos-entre-repositorios, la comparación con los demás
    repos del grupo. «codigo» por repo: 0 bien, 1 problemas, 2 error de ejecución."""
    todos = miembros(nombre)

    def hacer(raiz: Path) -> dict:
        resultados = repo.verificar(raiz, trabajos=trabajos)
        datos = {"resultados": resultados, "codigo": repo.codigo_verificacion(resultados)}
        datos.update(_comparar_contratos(raiz, [o for o in todos if Path(o).resolve() != raiz.resolve()]))
        if datos.get("contratos") == "divergentes":
            datos["codigo"] = max(datos["codigo"], 1)
        return datos
    return _por_miembro(nombre, hacer)


def matriz(nombre: str) -> dict:
    """Repo × sistema: versión instalada, versión del catálogo e integridad, para la vista del grupo."""
    versiones = fuentes.versiones()
    filas = []
    sistemas: set[str] = set()
    for ruta in miembros(nombre):
        raiz = Path(ruta)
        celdas = {}
        if raiz.is_dir():
            for e in repo.estado(raiz, versiones=versiones):
                celdas[e["id"]] = {"version": e["version"], "catalogo": e["catalogo"], "integro": e["integro"],
                                   "actualizable": e["actualizable"]}
                sistemas.add(e["id"])
        filas.append({"ruta": ruta, "nombre": raiz.name,
                      "existe": raiz.is_dir(), "sistemas": celdas, "flujo": generar.ruta_flujo(raiz).is_file()})
    return {"grupo": nombre, "sistemas": sorted(sistemas), "repos": filas}
