"""`uxyngraphar reparar`: deja la herramienta (y, si se pide, los proyectos registrados) sanos sin cambiar de versión.

Casa: restos de cortes, candado abandonado, versiones del legado sin apartar, panel.json huérfano, versiones con
archivos dañados (se descargan de nuevo), versión activa inválida (vuelve a la última buena), datos en el formato de la
versión, comando (con un Python que exista), bloque del PATH y accesos directos. Proyectos: `repo.reparar`.
Si la herramienta está tan rota que ni arranca, el instalador de una línea con `--reparar` hace lo mismo desde fuera.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import casa
import herramienta
import proyectos
import repo
from casa import ar


def _python_del_lanzador(ruta: str) -> str:
    try:
        with open(ruta, encoding="utf-8", errors="replace") as f:
            primera = f.readline().strip()
    except OSError:
        return ""
    return primera[2:].split()[0] if primera.startswith("#!") and primera[2:].strip() else ""


def reparar_casa(descargar: bool = True) -> dict:
    home = str(casa.carpeta())
    hechos: list[str] = []
    problemas: list[str] = []
    os.makedirs(home, exist_ok=True)
    with ar.Candado(home):
        if ar.apartar_legado(home):
            hechos.append("versiones del legado apartadas en legado/")
        ar.limpiar_restos(home)
        import panel
        if (casa.carpeta() / panel.ESTADO).is_file() and not panel.panel_abierto():
            (casa.carpeta() / panel.ESTADO).unlink(missing_ok=True)
            hechos.append("panel.json huérfano retirado")
        for v in ar.versiones_guardadas(home):
            malos = ar.archivos_alterados(os.path.join(home, "versiones", v))
            if not malos:
                continue
            if not descargar:
                problemas.append(f"versión {v}: {len(malos)} archivos dañados ({', '.join(malos[:3])}…)")
                continue
            try:
                ar.instalar_version(home, v, forzar=True)
                hechos.append(f"versión {v}: {len(malos)} archivos dañados; descargada y comprobada de nuevo")
            except ar.ErrorInstalacion as e:
                problemas.append(f"versión {v}: dañada y no se pudo descargar de nuevo ({e})")
        registro = ar.leer_registro(home)
        activa = ar.version_activa(home)
        if not activa and not ar.versiones_guardadas(home) and not registro.get("lanzadores"):
            return {"hechos": hechos, "problemas": problemas, "activa": "",
                    "nota": f"no hay ninguna herramienta instalada en {home} (esta es la copia del repositorio)"}
        if activa and descargar and ar.VERSION_RE.match(activa) and not ar.version_completa(os.path.join(home, "versiones", activa)):
            try:
                ar.instalar_version(home, activa, forzar=True)
                hechos.append(f"versión activa {activa}: estaba incompleta; descargada y comprobada de nuevo")
            except ar.ErrorInstalacion as e:
                hechos.append(f"versión activa {activa}: incompleta y no se pudo descargar de nuevo ({e}); busco otra")
        if not ar.version_completa(os.path.join(home, "versiones", activa or "-")):
            guardadas = ar.versiones_guardadas(home)
            opciones = [v for v in [registro.get("ultima_buena"), registro.get("anterior")] if v in guardadas] + guardadas[::-1]
            for v in opciones:
                try:
                    registro = ar.activar_version(home, v)
                    hechos.append(f"la versión activa ({activa or 'ninguna'}) no estaba completa; activa ahora la {v}")
                    activa = v
                    break
                except ar.ErrorInstalacion as e:
                    problemas.append(f"no pude activar la {v}: {e}")
            else:
                problemas.append("no hay ninguna versión completa: ejecuta el instalador de una línea con --reparar")
        else:
            codigo, salida = ar.ejecutar_motor(os.path.join(home, "versiones", activa), home, "_casa", "migrar")
            if codigo != 0:
                problemas.append(f"datos de la casa: {salida.strip()}")
        if herramienta.instalada() or ar.versiones_guardadas(home):
            antes = {r: _python_del_lanzador(r) for r in registro.get("lanzadores", []) if os.path.isfile(r)}
            lanzador, archivos = ar.crear_lanzadores(home, registro)
            registro["lanzadores"] = sorted(set([r for r in registro.get("lanzadores", []) if os.path.isfile(r)] + archivos))
            if lanzador not in antes:
                hechos.append(f"comando rehecho: {lanzador}")
            for r, python in antes.items():
                if python and python != "/usr/bin/env" and not os.path.isfile(python):
                    hechos.append(f"{r}: usaba un Python que ya no existe ({python}); ahora usa {sys.executable}")
            perfil = registro.get("perfil")
            if perfil and os.path.isfile(perfil):
                with open(perfil, encoding="utf-8", errors="replace") as f:
                    if ar.BLOQUE_INI not in f.read():
                        ar.agregar_a_perfil(ar.carpeta_bin(home))
                        hechos.append(f"PATH: bloque repuesto en {perfil}")
            tipos = sorted({a.get("tipo") for a in registro.get("accesos", []) if a.get("tipo")})
            rotos = [a for a in registro.get("accesos", []) if a.get("ruta") and not os.path.lexists(a["ruta"])]
            if rotos and tipos:
                ar.quitar_accesos(registro)
                avisos = ar.crear_accesos(home, lanzador, tipos, registro)
                hechos.append(f"accesos directos rehechos: {', '.join(tipos)}")
                problemas += avisos
            ar.escribir_registro(home, registro)
            if activa:
                try:
                    ar._probar_lanzador(lanzador, activa)
                except ar.ErrorInstalacion as e:
                    problemas.append(str(e))
    return {"hechos": hechos, "problemas": problemas, "activa": ar.version_activa(home)}


def reparar_proyectos() -> list[dict]:
    salida = []
    for ruta in proyectos.listar():
        fila = {"ruta": ruta, "nombre": Path(ruta).name, "hechos": [], "error": ""}
        try:
            if not Path(ruta).is_dir():
                raise FileNotFoundError("la carpeta ya no existe")
            fila["hechos"] = repo.reparar(Path(ruta))
        except (ValueError, OSError, repo.transaccion.ProyectoOcupado) as e:
            fila["error"] = str(e)
        salida.append(fila)
    return salida


def reparar(con_proyectos: bool = False, descargar: bool = True) -> dict:
    informe = reparar_casa(descargar)
    if con_proyectos:
        informe["proyectos"] = reparar_proyectos()
    return informe
