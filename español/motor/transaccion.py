"""Cambios en un proyecto como una transacción: antes de instalar, actualizar, quitar o retirar sistemas se respalda todo
lo que el motor toca en el repo (fuera del repo, en `respaldos/proyectos/` de la carpeta de uxyngraphar) y, si algo
falla a mitad, se restaura tal cual. Un respaldo con `"en_curso": true` es una transacción interrumpida (corte de luz,
proceso matado): `reparar` la restaura.

Un candado por proyecto (`.bloqueo` junto a sus respaldos, creado con O_EXCL) impide que dos procesos (el panel y la
CLI, o dos CLIs) cambien el mismo proyecto a la vez: si uno fallara, su restauración borraría lo que hizo el otro. Un
candado cuyo proceso ya no vive se considera abandonado y se retira."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import sys
import tempfile
import threading
import time
from contextlib import contextmanager
from pathlib import Path

import casa
import especificacion as esp

base = esp.base
GUARDADOS = 3
MANIFIESTO = "transaccion.json"
CANDADO = ".bloqueo"


class ProyectoOcupado(RuntimeError):
    """Otro proceso está cambiando este proyecto ahora mismo."""


def elementos() -> list[str]:
    """Rutas (relativas a la raíz de la app) que el motor puede cambiar en un proyecto."""
    import protecciones
    return [base.CARPETA_SISTEMAS_DE_GOBERNANZA, f"{base.CARPETA_RAIZ}/{esp.INDICE}", f"{base.CARPETA_RAIZ}/{esp.FLUJO}",
            "AGENTES.md", "AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md", protecciones.CLAUDE,
            *protecciones.EXCLUSIONES]


def _forzar_escritura(funcion, ruta, _exc):
    os.chmod(ruta, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
    funcion(ruta)


def borrar(ruta: Path) -> None:
    ruta = Path(ruta)
    if ruta.is_symlink() or ruta.is_file():
        try:
            ruta.unlink()
        except PermissionError:
            os.chmod(ruta, stat.S_IWRITE | stat.S_IREAD)
            ruta.unlink()
    elif ruta.is_dir():
        if sys.version_info >= (3, 12):
            shutil.rmtree(ruta, onexc=_forzar_escritura)
        else:
            shutil.rmtree(ruta, onerror=_forzar_escritura)


def carpeta_respaldos(raiz_app: Path) -> Path:
    raiz_app = Path(raiz_app).resolve()
    clave = hashlib.sha256(str(raiz_app).encode("utf-8")).hexdigest()[:12]
    return casa.carpeta() / "respaldos" / "proyectos" / f"{raiz_app.name}-{clave}"


def _enlazar(origen: str, destino: str) -> None:
    """Enlace duro si el sistema de archivos lo permite; si no, copia. Solo para sistemas instalados: son de solo
    lectura y el motor los sustituye por renombrado, nunca escribiendo encima, así que el respaldo conserva su contenido."""
    try:
        os.link(origen, destino)
    except OSError:
        shutil.copy2(origen, destino)


def _copiar(origen: Path, destino: Path, enlazar: bool = False) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    if origen.is_dir():
        shutil.copytree(origen, destino, ignore=shutil.ignore_patterns(".construyendo-*", ".*.anterior", "__pycache__"),
                        copy_function=_enlazar if enlazar else shutil.copy2)
    else:
        shutil.copy2(origen, destino)


def respaldar(raiz_app: Path, motivo: str, sistemas: list[str] | None = None) -> Path:
    """Copia fuera del repo lo que el motor puede tocar. Con `sistemas`, de `uxyngraphar/sistemas-de-gobernanza/` solo esos (los que la
    operación va a cambiar): el resto no se respalda ni se toca al restaurar (M-10)."""
    raiz_app = Path(raiz_app).resolve()
    carpeta = carpeta_respaldos(raiz_app) / time.strftime("%Y%m%d-%H%M%S")
    n = 1
    while carpeta.exists():
        n += 1
        carpeta = carpeta.with_name(f"{carpeta.name.split('~')[0]}~{n:03d}")
    presentes, parciales = [], []
    for rel in elementos():
        origen = raiz_app / rel
        if origen.is_symlink():
            continue
        if rel == base.CARPETA_SISTEMAS_DE_GOBERNANZA and sistemas is not None:
            for pid in sistemas:
                if (origen / pid).is_dir():
                    _copiar(origen / pid, carpeta / "copia" / rel / pid, enlazar=True)
                    parciales.append(pid)
            continue
        if origen.exists():
            _copiar(origen, carpeta / "copia" / rel, enlazar=rel == base.CARPETA_SISTEMAS_DE_GOBERNANZA)
            presentes.append(rel)
    carpeta.mkdir(parents=True, exist_ok=True)
    trabajo = raiz_app / base.CARPETA_TRABAJO
    previas = sorted(d.name for d in trabajo.iterdir() if d.is_dir()) if trabajo.is_dir() else []
    datos = {"raiz": str(raiz_app), "motivo": motivo, "presentes": presentes, "trabajo": previas,
             "trabajo_existia": trabajo.is_dir(), "en_curso": True,
             **({"sistemas_parcial": list(sistemas), "sistemas_presentes": parciales} if sistemas is not None else {}),
             "fecha": time.strftime("%Y-%m-%dT%H:%M:%S")}
    (carpeta / MANIFIESTO).write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return carpeta


def restaurar(raiz_app: Path, respaldo: Path) -> None:
    """Deja en el proyecto exactamente lo que había al respaldar (lo que no existía, se quita)."""
    raiz_app = Path(raiz_app).resolve()
    datos = json.loads((Path(respaldo) / MANIFIESTO).read_text(encoding="utf-8"))
    for rel in elementos():
        actual = raiz_app / rel
        if actual.is_symlink():
            continue
        if rel == base.CARPETA_SISTEMAS_DE_GOBERNANZA and "sistemas_parcial" in datos:   # respaldo ligero: solo los sistemas tocados
            for pid in datos["sistemas_parcial"]:
                borrar(actual / pid)
                borrar(actual / f".{pid}.anterior")
                if pid in datos["sistemas_presentes"]:
                    _copiar(Path(respaldo) / "copia" / rel / pid, actual / pid)
            for resto in actual.glob(".construyendo-*") if actual.is_dir() else []:
                borrar(resto)
            if actual.is_dir() and not any(actual.iterdir()):
                actual.rmdir()
            continue
        borrar(actual)
        if rel in datos["presentes"]:
            _copiar(Path(respaldo) / "copia" / rel, actual)
    # El trabajo no se respalda, pero las carpetas vacías que creó la transacción fallida (trabajo/<id>/) sobran.
    trabajo = raiz_app / base.CARPETA_TRABAJO
    if "trabajo" in datos and trabajo.is_dir():
        for d in trabajo.iterdir():
            if d.is_dir() and d.name not in datos["trabajo"] and not any(d.iterdir()):
                d.rmdir()
        if not datos.get("trabajo_existia", True) and not any(trabajo.iterdir()):
            trabajo.rmdir()
    raiz = raiz_app / base.CARPETA_RAIZ
    if raiz.is_dir() and not any(raiz.iterdir()):
        raiz.rmdir()
    import generar
    generar.registrar_huella_flujo(raiz_app)   # el FLUJO.json restaurado también lo escribió el motor
    _cerrar(respaldo)


def _cerrar(respaldo: Path) -> None:
    ruta = Path(respaldo) / MANIFIESTO
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    datos["en_curso"] = False
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _orden(carpeta: Path) -> tuple[str, int]:
    """Orden cronológico de los respaldos: por fecha y, dentro del mismo segundo, por el número tras «~» (como número:
    «~10» va después de «~2»)."""
    fecha, _, n = carpeta.name.partition("~")
    return fecha, int(n) if n.isdigit() else 1


def respaldos(raiz_app: Path) -> list[Path]:
    """Respaldos de un proyecto, del más antiguo al más reciente."""
    return sorted((d for d in carpeta_respaldos(raiz_app).glob("*") if (d / MANIFIESTO).is_file()), key=_orden)


def guardados() -> int:
    """Respaldos que se conservan por proyecto: «respaldos_por_proyecto» de casa.json (por defecto GUARDADOS, mínimo 1)."""
    valor = casa.leer_json(casa.ARCHIVO_FORMATO, {}).get("respaldos_por_proyecto", GUARDADOS)
    return valor if isinstance(valor, int) and valor >= 1 else GUARDADOS


def _podar(raiz_app: Path) -> None:
    hechos = respaldos(raiz_app)
    for d in hechos[:max(0, len(hechos) - guardados())]:
        borrar(d)


def listar(raiz_app: Path) -> list[dict]:
    """Respaldos del proyecto, del más reciente al más antiguo: {nombre, fecha, motivo} (el estado de antes de ese cambio)."""
    salida = []
    for d in reversed(respaldos(raiz_app)):
        try:
            datos = json.loads((d / MANIFIESTO).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not datos.get("en_curso"):
            salida.append({"nombre": d.name, "fecha": datos.get("fecha", ""), "motivo": datos.get("motivo", "")})
    return salida


def deshacer(raiz_app: Path, nombre: str | None = None) -> dict:
    """Devuelve el proyecto al estado de antes del cambio `nombre` (por defecto, el último) dentro de una transacción
    nueva: deshacer también se puede deshacer. Nunca toca `uxyngraphar/trabajo/` (salvo carpetas vacías de un sistema)."""
    raiz_app = Path(raiz_app).resolve()
    disponibles = {r["nombre"]: r for r in listar(raiz_app)}
    if not disponibles:
        raise ValueError("no hay cambios que deshacer en este proyecto")
    elegido = nombre or next(iter(disponibles))
    if elegido not in disponibles:
        raise ValueError(f"no existe el respaldo «{elegido}»; disponibles: {', '.join(disponibles)}")
    origen = carpeta_respaldos(raiz_app) / elegido
    with transaccion(raiz_app, f"deshacer {disponibles[elegido]['motivo']} ({elegido})"):
        temporal = Path(tempfile.mkdtemp(prefix="uxy-deshacer-"))
        copia = temporal / elegido
        shutil.copytree(origen, copia)   # restaurar() cierra el manifiesto: se trabaja sobre una copia
        try:
            restaurar(raiz_app, copia)
        finally:
            borrar(temporal)
    return {"deshecho": elegido, **disponibles[elegido]}


def interrumpida(raiz_app: Path) -> Path | None:
    """El respaldo de una transacción que no terminó (ni bien ni con restauración), si lo hay."""
    for d in reversed(respaldos(raiz_app)):
        try:
            if json.loads((d / MANIFIESTO).read_text(encoding="utf-8")).get("en_curso"):
                return d
        except (OSError, ValueError):
            continue
    return None


def ultimo(raiz_app: Path) -> Path | None:
    hechos = respaldos(raiz_app)
    return hechos[-1] if hechos else None


_hilo = threading.local()   # por hilo: el panel atiende cada pedido en su propio hilo


def _de_este_hilo(nombre: str) -> dict[str, int]:
    if not hasattr(_hilo, nombre):
        setattr(_hilo, nombre, {})
    return getattr(_hilo, nombre)


def _abandonado(ruta: Path) -> bool:
    """El candado no tiene dueño vivo (proceso muerto, o archivo ilegible de hace más de un minuto)."""
    import procesos
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        return not procesos.vivo(datos.get("pid"))
    except FileNotFoundError:
        return True
    except (OSError, ValueError, AttributeError):
        try:
            return time.time() - ruta.stat().st_mtime > 60
        except OSError:
            return True


def ocupado(raiz_app: Path) -> dict | None:
    """Quién tiene el candado del proyecto ({pid, fecha, motivo}), si lo tiene alguien vivo."""
    ruta = carpeta_respaldos(raiz_app) / CANDADO
    if not ruta.is_file() or _abandonado(ruta):
        return None
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


@contextmanager
def candado(raiz_app: Path, motivo: str = ""):
    """Exclusión entre procesos e hilos para cambiar un proyecto. Reentrante dentro del mismo hilo."""
    clave = str(Path(raiz_app).resolve())
    tomados = _de_este_hilo("candados")
    if tomados.get(clave):
        tomados[clave] += 1
        try:
            yield
        finally:
            tomados[clave] -= 1
        return
    ruta = carpeta_respaldos(raiz_app) / CANDADO
    ruta.parent.mkdir(parents=True, exist_ok=True)
    for _ in range(3):
        try:
            fd = os.open(ruta, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            if _abandonado(ruta):
                ruta.unlink(missing_ok=True)
                continue
            datos = ocupado(raiz_app) or {}
            raise ProyectoOcupado(f"hay otro cambio en curso en este proyecto ({datos.get('motivo') or 'otro proceso'}, "
                                  f"pid {datos.get('pid', '?')}, desde {datos.get('fecha', '?')}); espera a que termine "
                                  "y vuelve a intentarlo") from None
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"pid": os.getpid(), "hilo": threading.get_ident(), "motivo": motivo,
                       "fecha": time.strftime("%Y-%m-%dT%H:%M:%S")}, f)
        break
    else:
        raise ProyectoOcupado("no pude tomar el candado del proyecto; vuelve a intentarlo")
    tomados[clave] = 1
    try:
        yield
    finally:
        tomados.pop(clave, None)
        ruta.unlink(missing_ok=True)


@contextmanager
def transaccion(raiz_app: Path, motivo: str, sistemas: list[str] | None = None):
    """Respalda, ejecuta el bloque y, si lanza cualquier excepción, restaura el proyecto antes de propagarla. Toma el
    candado del proyecto mientras dura."""
    clave = str(Path(raiz_app).resolve())
    activas = _de_este_hilo("transacciones")
    if clave in activas:   # anidada (p. ej. desinstalar llama a quitar): la exterior ya respalda
        yield None
        return
    with candado(raiz_app, motivo):
        activas[clave] = 1
        try:
            respaldo = respaldar(raiz_app, motivo, sistemas)
            try:
                yield respaldo
            except BaseException:
                restaurar(raiz_app, respaldo)
                raise
            _cerrar(respaldo)
            _podar(raiz_app)
        finally:
            activas.pop(clave, None)
