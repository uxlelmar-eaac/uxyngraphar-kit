"""Sistemas en un repo: instalar, actualizar, quitar y verificar. Nunca toca el trabajo de `uxyngraphar/trabajo/<id>/`
salvo que se pida quitarlo explícitamente."""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

import fuentes
import especificacion as esp
import generar
import protecciones
import transaccion

base = esp.base


def _forzar_escritura(funcion, ruta, _exc):
    os.chmod(ruta, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
    funcion(ruta)


def borrar_arbol(ruta: Path) -> None:
    if Path(ruta).exists():
        if sys.version_info >= (3, 12):
            shutil.rmtree(ruta, onexc=_forzar_escritura)
        else:
            shutil.rmtree(ruta, onerror=_forzar_escritura)


def solo_lectura(carpeta: Path) -> None:
    for p in Path(carpeta).rglob("*"):
        if p.is_file():
            p.chmod(stat.S_IREAD | (stat.S_IXUSR if p.suffix == ".py" else 0) | stat.S_IRGRP | stat.S_IROTH)


def carpeta_instalada(raiz_app: Path, pid: str) -> Path:
    return Path(raiz_app) / base.CARPETA_SISTEMAS_DE_GOBERNANZA / pid


def _colocar(raiz_app: Path, pid: str, cat: Path | None) -> Path:
    """Construye desde el catálogo y reemplaza `uxyngraphar/sistemas-de-gobernanza/<id>/` de forma atómica (con vuelta atrás)."""
    sistemas = Path(raiz_app) / base.CARPETA_SISTEMAS_DE_GOBERNANZA
    sistemas.mkdir(parents=True, exist_ok=True)
    destino = sistemas / pid
    with tempfile.TemporaryDirectory(dir=sistemas, prefix=".construyendo-") as tmp:
        nuevo = fuentes.construir(pid, Path(tmp), cat)
        anterior = sistemas / f".{pid}.anterior"
        borrar_arbol(anterior)
        if destino.exists():
            destino.rename(anterior)
        try:
            nuevo.rename(destino)
        except OSError:
            if anterior.exists():
                anterior.rename(destino)
            raise
        borrar_arbol(anterior)
    solo_lectura(destino)
    return destino


def instalar(raiz_app: Path, ids: list[str], cat: Path | None = None, sistema_base: str | None = None) -> list[str]:
    """Instala `ids`. Con `sistema_base`, FLUJO.json pasa a `trabajar_con` ese sistema (se aplica en cada pedido)."""
    with transaccion.transaccion(raiz_app, "instalar", sistemas=list(ids)):
        raiz_app = Path(raiz_app).resolve()
        if sistema_base and sistema_base not in ids and not carpeta_instalada(raiz_app, sistema_base).exists():
            raise ValueError(f"--base {sistema_base}: instálalo en la misma orden o antes")
        hechos = []
        for pid in ids:
            if carpeta_instalada(raiz_app, pid).exists():
                raise FileExistsError(f"«{pid}» ya está instalado; usa actualizar")
            _colocar(raiz_app, pid, cat)
            base.carpeta_trabajo(carpeta_instalada(raiz_app, pid))
            hechos.append(pid)
        generar.regenerar(raiz_app)
        if sistema_base:
            errores = generar.guardar_flujo(raiz_app, {**generar.leer_flujo(raiz_app), "modo": "trabajar_con", "trabajar_con": sistema_base})
            if errores:
                raise ValueError("FLUJO.json no cambió: " + "; ".join(errores))
        return hechos


def estado(raiz_app: Path, cat: Path | None = None, versiones: dict[str, str] | None = None) -> list[dict]:
    """Por sistema instalado: versión, versión del catálogo, integridad y si hay actualización."""
    disponibles = versiones if versiones is not None else fuentes.versiones(cat)
    salida = []
    for m in generar.instalados(raiz_app):
        informe = base.comprobar_integridad(carpeta_instalada(raiz_app, m["id"]))
        en_catalogo = disponibles.get(m["id"])
        actualizable = bool(en_catalogo) and m.get("version") != "?" and esp.version_tupla(str(en_catalogo)) > esp.version_tupla(m["version"])
        salida.append({"id": m["id"], "titulo": m.get("titulo", ""), "descripcion": m.get("descripcion", ""),
                       "version": m.get("version"), "catalogo": en_catalogo,
                       "integro": base.integro(informe), "informe": informe, "actualizable": actualizable})
    return salida


def actualizar(raiz_app: Path, ids: list[str] | None = None, cat: Path | None = None, forzar: bool = False) -> list[str]:
    """Actualiza (o repara si está alterado) los sistemas indicados; sin ids, todos los instalados."""
    with transaccion.transaccion(raiz_app, "actualizar", sistemas=list(ids) if ids else None):
        raiz_app = Path(raiz_app).resolve()
        hechos = []
        anteriores = generar.instalados(raiz_app)
        for e in estado(raiz_app, cat):
            if ids and e["id"] not in ids:
                continue
            if not e["catalogo"]:
                continue
            retroceso = esp.version_tupla(e["catalogo"]) < esp.version_tupla(e["version"]) if e["version"] != "?" else False
            if retroceso and not forzar:
                raise ValueError(f"«{e['id']}»: el catálogo ({e['catalogo']}) es más antiguo que lo instalado ({e['version']}); usa --forzar")
            if e["actualizable"] or not e["integro"] or forzar:
                _colocar(raiz_app, e["id"], cat)
                hechos.append(e["id"])
        for pid in ids or []:
            if not carpeta_instalada(raiz_app, pid).exists():
                raise FileNotFoundError(f"«{pid}» no está instalado")
        generar.regenerar(raiz_app, anteriores)
        return hechos


def quitar(raiz_app: Path, pid: str, con_trabajo: bool = False) -> None:
    with transaccion.transaccion(raiz_app, "quitar", sistemas=[pid]):
        raiz_app = Path(raiz_app).resolve()
        carpeta = carpeta_instalada(raiz_app, pid)
        if not (carpeta / base.MANIFIESTO).is_file():
            raise FileNotFoundError(f"«{pid}» no está instalado")
        anteriores = [base.leer_manifiesto(carpeta)]
        borrar_arbol(carpeta)
        ruta_flujo = generar.ruta_flujo(raiz_app)
        if ruta_flujo.is_file():
            flujo = generar.leer_flujo(raiz_app)
            flujo["leer_por_defecto"] = [x for x in flujo.get("leer_por_defecto", []) if x != pid]
            flujo["secuencia"] = [x for x in flujo.get("secuencia", []) if x != pid]
            if flujo.get("trabajar_con") == pid:
                flujo["trabajar_con"] = None
            if esp.validar_flujo(flujo):
                flujo["modo"] = "manual"
            generar.guardar_flujo(raiz_app, flujo)
        generar.regenerar(raiz_app, anteriores)
    if con_trabajo:   # el trabajo no se respalda: se borra solo cuando todo lo demás salió bien
        borrar_arbol(raiz_app / base.CARPETA_TRABAJO / pid)


def desinstalar(raiz_app: Path, con_trabajo: bool = False) -> list[str]:
    """Quita uxyngraphar del proyecto: sistemas, INDICE.md, FLUJO.json, el bloque de AGENTES.md/AGENTS.md/CLAUDE.md y las
    protecciones. `uxyngraphar/trabajo/` se conserva salvo `con_trabajo`. Devuelve los ids quitados."""
    with transaccion.transaccion(raiz_app, "retirar"):
        raiz_app = Path(raiz_app).resolve()
        anteriores = generar.instalados(raiz_app)
        ids = [m["id"] for m in anteriores]
        borrar_arbol(raiz_app / base.CARPETA_SISTEMAS_DE_GOBERNANZA)
        for ruta in (raiz_app / base.CARPETA_RAIZ / esp.INDICE, generar.ruta_flujo(raiz_app)):
            ruta.unlink(missing_ok=True)
        for nombre in (*generar.ARCHIVOS_AGENTE, *generar.OPCIONALES):
            ruta = raiz_app / nombre
            if ruta.is_file() and not ruta.is_symlink():
                texto = generar.quitar_bloque(ruta.read_text(encoding="utf-8"))
                if texto.strip():
                    ruta.write_text(texto, encoding="utf-8")
                else:
                    ruta.unlink()
        protecciones.aplicar(raiz_app, [], anteriores)
        claude = raiz_app / protecciones.CLAUDE
        if claude.is_file() and protecciones.leer_ajustes_claude(claude) in ({}, {"permissions": {}},
                                                                              {"permissions": {"deny": []}}):
            claude.unlink()
    raiz_app = Path(raiz_app).resolve()
    import integracion
    integracion.quitar_todas(raiz_app)   # el workflow y el gancho opcionales de «verificar» (M-16)
    if con_trabajo:   # el trabajo no se respalda: se borra solo cuando todo lo demás salió bien
        borrar_arbol(raiz_app / base.CARPETA_TRABAJO)
    for carpeta in (raiz_app / protecciones.CLAUDE).parent, raiz_app / base.CARPETA_RAIZ:
        if carpeta.is_dir() and not any(carpeta.iterdir()):
            carpeta.rmdir()
    return ids


def reparar(raiz_app: Path, cat: Path | None = None) -> list[str]:
    """Deja un proyecto sano sin actualizar nada: restaura una transacción interrumpida, recoge los restos de un cambio
    de sistema cortado, reconstruye los sistemas alterados (si el catálogo tiene su misma versión) y regenera INDICE.md,
    el bloque de AGENTES.md/AGENTS.md/CLAUDE.md y las protecciones. FLUJO.json inválido vuelve al último respaldo o a «manual»."""
    raiz_app = Path(raiz_app).resolve()
    with transaccion.candado(raiz_app, "reparar"):   # nunca toma por interrumpida la transacción viva de otro proceso
        return _reparar(raiz_app, cat)


def _reparar(raiz_app: Path, cat: Path | None) -> list[str]:
    hechos = []
    cortada = transaccion.interrumpida(raiz_app)
    if cortada:
        transaccion.restaurar(raiz_app, cortada)
        hechos.append(f"cambio interrumpido deshecho (respaldo {cortada.name})")
    sistemas = raiz_app / base.CARPETA_SISTEMAS_DE_GOBERNANZA
    for resto in sorted(sistemas.glob(".*")) if sistemas.is_dir() else []:
        if resto.name.endswith(".anterior") and not (sistemas / resto.name[1:-len(".anterior")]).exists():
            resto.rename(sistemas / resto.name[1:-len(".anterior")])
            hechos.append(f"{resto.name[1:-len('.anterior')]}: recuperado de un cambio cortado")
        elif resto.is_dir():
            borrar_arbol(resto)
            hechos.append(f"{resto.name}: resto de un cambio cortado retirado")
    if not sistemas.is_dir():
        return hechos
    previo = transaccion.ultimo(raiz_app)   # el de antes de esta reparación: el suyo propio ya trae el FLUJO.json malo
    with transaccion.transaccion(raiz_app, "reparar"):
        disponibles = fuentes.versiones(cat)
        for e in estado(raiz_app, cat, disponibles):
            if e["integro"]:
                continue
            if e["catalogo"] == e["version"]:
                _colocar(raiz_app, e["id"], cat)
                hechos.append(f"{e['id']}: reconstruido (estaba alterado)")
            else:
                hechos.append(f"{e['id']}: alterado; el catálogo trae la {e['catalogo'] or '—'} y no la {e['version']}: "
                              "actualízalo para rehacerlo")
        ruta = generar.ruta_flujo(raiz_app)
        flujo_malo = False
        if ruta.is_file():
            try:
                flujo_malo = bool(esp.validar_flujo(generar.leer_flujo(raiz_app), {m["id"] for m in generar.instalados(raiz_app)}))
            except ValueError:
                flujo_malo = True
        if flujo_malo:
            copia = previo / "copia" / base.CARPETA_RAIZ / esp.FLUJO if previo else None
            texto = copia.read_text(encoding="utf-8") if copia and copia.is_file() else ""
            try:
                bueno = json.loads(texto) if texto else None
            except ValueError:
                bueno = None
            if bueno is not None and not esp.validar_flujo(bueno, {m["id"] for m in generar.instalados(raiz_app)}):
                ruta.write_text(texto, encoding="utf-8")
                hechos.append("FLUJO.json: inválido; restaurado del último respaldo")
            else:
                ruta.unlink()
                hechos.append("FLUJO.json: inválido; vuelve a modo manual")
        generar.regenerar(raiz_app)
    return hechos


SEGUNDOS_VERIFICAR = 300
AGOTADO = 124   # código de salida de una verificación que excede su tiempo (como timeout(1))


def _texto(salida) -> str:
    return salida.decode("utf-8", "replace") if isinstance(salida, bytes) else (salida or "")


def ejecutar_verificacion(raiz_app: Path, pid: str, v: str, segundos: float = SEGUNDOS_VERIFICAR) -> dict:
    """Una verificación en su propio proceso, con límite de tiempo: si se agota, código 124."""
    carpeta = carpeta_instalada(Path(raiz_app), pid)
    try:
        r = subprocess.run([sys.executable, "-B", "-X", "utf8", str(carpeta / v)], cwd=raiz_app, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=segundos)
        codigo, salida = r.returncode, (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired as e:
        codigo = AGOTADO
        salida = (_texto(e.stdout) + _texto(e.stderr)).strip() + f"\nexcedió {segundos:g} s"
    return {"sistema": pid, "verificacion": v, "codigo": codigo, "salida": salida.strip()}


def verificar(raiz_app: Path, segundos: float = SEGUNDOS_VERIFICAR, trabajos: int = 1) -> list[dict]:
    """Ejecuta, por sistema instalado, sus `verificaciones` (cada una en su propio proceso y con límite de tiempo). Con
    `trabajos` > 1, varias a la vez; el resultado sale siempre en el mismo orden."""
    tareas = [(m["id"], v) for m in generar.instalados(raiz_app) for v in m.get("verificaciones", [])]
    if trabajos <= 1:
        return [ejecutar_verificacion(raiz_app, pid, v, segundos) for pid, v in tareas]
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=trabajos) as grupo:
        return list(grupo.map(lambda t: ejecutar_verificacion(raiz_app, t[0], t[1], segundos), tareas))


def codigo_verificacion(resultados: list[dict]) -> int:
    """0: todo bien; 1: alguna verificación encontró problemas; 2: alguna no se pudo ejecutar (agotó su tiempo o no
    arrancó)."""
    def no_corrio(r: dict) -> bool:
        return r["codigo"] == AGOTADO or r["codigo"] < 0 or "Traceback (most recent call last)" in r["salida"]
    if any(no_corrio(r) for r in resultados):
        return 2
    return 1 if any(r["codigo"] for r in resultados) else 0
