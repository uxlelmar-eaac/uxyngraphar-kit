"""Acciones del panel sobre la herramienta de este equipo: versiones (usar otra), PATH, limpieza del registro,
desinstalar y reiniciar el panel en la versión recién activada.

Todo lo que cambia algo exige una persona delante (api_panel.persona_presente), igual que el resto del panel.
"""

from __future__ import annotations

import json
import os
import secrets
import subprocess
import sys
import time
from pathlib import Path

import api
import api_panel as panel
import sistema

ar = sistema.ar
REINICIO_DESDE = (1, 2, 0)   # primera versión cuyo panel sabe arrancar en segundo plano y avisar de su dirección
CANDADO_MINUTOS = 15         # como arranque.Candado: más viejo que esto, la instalación se abandonó
_HIJOS: list = []            # paneles arrancados en segundo plano: no se esperan (siguen vivos al cerrar este)


def _sin_persona() -> dict | None:
    motivo = panel.persona_presente()
    return {"ok": False, "error": motivo} if motivo else None


def _instalada() -> bool:
    """True si este panel corre desde una versión instalada (versiones/X.Y.Z), no desde una copia del repositorio."""
    return sistema.ES.parent.name == "versiones"


def _candado() -> dict:
    archivo = sistema.home() / ".instalando"
    if not archivo.is_file():
        return {"existe": False}
    minutos = int((time.time() - archivo.stat().st_mtime) // 60)
    return {"existe": True, "minutos": minutos, "abandonado": minutos >= CANDADO_MINUTOS, "ruta": str(archivo)}


def _rotos() -> list[dict]:
    """Proyectos registrados que ya no existen o ya no tienen uxyngraphar."""
    salida = []
    for ruta in sistema.leer_proyectos():
        if not Path(ruta).is_dir():
            salida.append({"ruta": ruta, "motivo": "la carpeta ya no existe"})
        elif not api.inspeccionar(ruta).get("instalados"):
            salida.append({"ruta": ruta, "motivo": "ya no tiene uxyngraphar"})
    return salida


def info() -> dict:
    h = str(sistema.home())
    registro = ar.leer_registro(h)
    bin_dir = ar.carpeta_bin(h)
    return {"ok": True, "version": sistema.version_herramienta(), "activa": ar.version_activa(h), "guardadas": ar.versiones_guardadas(h),
            "carpeta": h, "bin": bin_dir, "en_path": ar.en_path(bin_dir), "home_propio": ar.home_propio(),
            "path_nuestro": bool(registro.get("perfil") or registro.get("path_windows")), "perfil": registro.get("perfil", ""),
            "instalada": _instalada(), "candado": _candado(), "rotos": _rotos(), "windows": ar.ES_WINDOWS,
            "sin_persona": panel.persona_presente()}


def usar(version: str) -> dict:
    """Activa otra versión guardada (o la descarga). Los proyectos no cambian."""
    if (no := _sin_persona()):
        return no
    version = (version or "").strip().lstrip("v")
    if not ar.VERSION_RE.match(version):
        return {"ok": False, "error": "Versión no válida: usa el formato X.Y.Z."}
    h = str(sistema.home())
    if version in ar.versiones_guardadas(h):
        ar.escribir_atomico(os.path.join(h, "actual"), version + "\n")
        salida = f"Versión activa: {version}."
    else:
        r = panel.ejecutar_herramienta(["autoactualizar", "--version", version])
        if not r["ok"]:
            return r
        salida = r["salida"]
    return {"ok": True, "version": version, "salida": salida, "reiniciable": sistema.tupla(version) >= REINICIO_DESDE}


def path(agregar: bool) -> dict:
    """Añade o quita la carpeta del comando del PATH (bloque marcado en el perfil, o PATH de usuario en Windows)."""
    if (no := _sin_persona()):
        return no
    h = str(sistema.home())
    registro, bin_dir = ar.leer_registro(h), ar.carpeta_bin(h)
    if agregar:
        if ar.home_propio():
            return {"ok": False, "error": f"Usas una carpeta propia (UXYNGRAPHAR_HOME): no toco tu PATH. Añade {bin_dir} tú si lo quieres."}
        texto = ar.asegurar_path(h, registro) or "El comando ya estaba en tu PATH."
    else:
        texto = "No había nada que quitar: el PATH no lo añadió uxyngraphar."
        if ar.quitar_de_perfil(registro.pop("perfil", "")):
            texto = "Quité el bloque de uxyngraphar de tu archivo de inicio de la terminal. Abre una terminal nueva."
        if registro.get("path_windows"):
            ar._path_windows(registro.pop("path_windows"), False)
            texto = "Quité la carpeta del comando de tu PATH de usuario. Abre una terminal nueva."
    ar.escribir_atomico(os.path.join(h, "instalacion.json"), json.dumps(registro, indent=2, ensure_ascii=True) + "\n")
    return {"ok": True, "texto": texto}


def limpiar(aplicar: bool) -> dict:
    """Quita del registro los proyectos rotos y el candado de una instalación abandonada. Sin `aplicar`, solo los lista."""
    rotos, candado = _rotos(), _candado()
    if not aplicar:
        return {"ok": True, "rotos": rotos, "candado": candado}
    if (no := _sin_persona()):
        return no
    quitar = {r["ruta"] for r in rotos}
    sistema.guardar_proyectos([p for p in sistema.leer_proyectos() if p not in quitar])
    if candado.get("abandonado"):
        Path(candado["ruta"]).unlink(missing_ok=True)
    return {"ok": True, "quitados": sorted(quitar), "candado_quitado": bool(candado.get("abandonado"))}


def desinstalar(confirmacion: str) -> dict:
    if (no := _sin_persona()):
        return no
    if (confirmacion or "").strip().lower() != "desinstalar":
        return {"ok": False, "error": "Escribe «desinstalar» para confirmar."}
    return {"ok": True, "hecho": sistema.desinstalar()}


def reiniciar(espera: float = 25) -> dict:
    """Arranca el panel de la versión activa en segundo plano y devuelve su dirección (este se cierra después)."""
    if (no := _sin_persona()):
        return no
    h = sistema.home()
    v = ar.version_activa(str(h))
    cli = h / "versiones" / v / "uxyngraphar.py"
    if not cli.is_file() or sistema.tupla(v) < REINICIO_DESDE:
        return {"ok": False, "error": f"Cierra este panel y vuelve a abrirlo con «uxyngraphar» para usar la {v or 'versión nueva'}."}
    nombre = f".panel-{secrets.token_hex(6)}"
    aviso, registro = h / f"{nombre}.url", h / f"{nombre}.log"   # el log guarda los errores del panel nuevo si no arranca
    env = {**os.environ, "UXYNGRAPHAR_HOME": str(h), "UXYNGRAPHAR_PANEL_URL": str(aviso)}
    opciones = ({"creationflags": 0x00000008 | 0x00000200} if ar.ES_WINDOWS   # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
                else {"start_new_session": True})   # sigue vivo cuando este proceso y su terminal terminen
    try:
        with open(registro, "wb") as err:
            hijo = subprocess.Popen([sys.executable, str(cli), "panel", "--fondo"], cwd=str(h), env=env, stdin=subprocess.DEVNULL,
                                    stdout=subprocess.DEVNULL, stderr=err, **opciones)
    except OSError as exc:
        _borrar(registro)
        return {"ok": False, "error": f"No pude abrir el panel nuevo ({exc}). Ciérralo y vuelve a abrirlo con «uxyngraphar»."}
    _HIJOS.append(hijo)
    limite = time.time() + espera
    while True:
        terminado = hijo.poll() is not None   # antes de mirar el aviso: uno que lo escribe y sale enseguida también vale
        if aviso.is_file() and aviso.read_text(encoding="utf-8").strip():
            url = aviso.read_text(encoding="utf-8").strip()
            aviso.unlink(missing_ok=True)
            _borrar(registro)   # en Windows sigue abierto por el panel nuevo: se queda (es pequeño)
            return {"ok": True, "url": url, "version": v}
        if terminado or time.time() >= limite:
            break
        time.sleep(0.2)
    if hijo.poll() is None:   # no respondió: que no se quede colgado en segundo plano
        hijo.kill()
    try:
        hijo.wait(timeout=10)
    except subprocess.TimeoutExpired:
        pass
    _HIJOS.remove(hijo)
    detalle = registro.read_text(encoding="utf-8", errors="replace").strip()[-800:] if registro.is_file() else ""
    _borrar(aviso)
    _borrar(registro)
    error = f"El panel de la {v} no respondió a tiempo. Cierra este y ábrelo con «uxyngraphar»."
    return {"ok": False, "error": error + (f"\n\n{detalle}" if detalle else "")}


def _borrar(ruta: Path) -> None:
    try:
        ruta.unlink(missing_ok=True)
    except OSError:
        pass
