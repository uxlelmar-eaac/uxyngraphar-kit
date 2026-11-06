"""Catálogo de paquetes (fuente en `paquetes/<id>/`): listar, crear, editar, versionar y construir.

Editar un paquete solo ocurre aquí. Un paquete construido = fuente + scripts comunes en `scripts/comun/` + INTEGRIDAD.json.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import especificacion as esp

base = esp.base
NIVELES = ("mayor", "menor", "parche")


def catalogo(raiz: Path | None = None) -> Path:
    return Path(raiz) if raiz else esp.CATALOGO


def listar(raiz: Path | None = None) -> list[dict]:
    """Manifiestos del catálogo (con «errores» de validación de cada paquete)."""
    salida = []
    for carpeta in sorted(catalogo(raiz).iterdir()):
        if carpeta.is_dir() and not carpeta.name.startswith(("_", ".")) and (carpeta / base.MANIFIESTO).is_file():
            m = base.leer_manifiesto(carpeta)
            m["errores"] = esp.validar_paquete(carpeta)
            salida.append(m)
    return salida


def carpeta(pid: str, raiz: Path | None = None) -> Path:
    if not base.ID_VALIDO.match(pid):
        raise ValueError(f"id inválido «{pid}»")
    c = catalogo(raiz) / pid
    if not (c / base.MANIFIESTO).is_file():
        raise FileNotFoundError(f"el catálogo no tiene el paquete «{pid}»")
    return c


def crear(pid: str, titulo: str, descripcion: str = "", raiz: Path | None = None) -> Path:
    """Esqueleto mínimo de un paquete nuevo (versión 0.1.0)."""
    if not base.ID_VALIDO.match(pid):
        raise ValueError("id: kebab-case ASCII (a-z, 0-9, guiones)")
    c = catalogo(raiz) / pid
    if c.exists():
        raise FileExistsError(f"ya existe {c}")
    m = {"manifiesto_formato": 1, "id": pid, "version": "0.1.0", "titulo": titulo, "descripcion": descripcion or titulo,
         "motor": ">=2.0", "activacion": [pid], "entrada": base.ENTRADA, "verificaciones": [f"{esp.DESTINO_COMUN}/verificar.py"],
         "fichas": {"ficha": {"carpeta": ".", "prefijo": "FIC", "plantilla": "plantillas/ficha.md", "inicial": "abierta",
                              "estados": {"abierta": "pendientes", "en-curso": "en-progreso", "cerrada": "completadas"}}},
         "ajustes": {}}
    (c / "plantillas").mkdir(parents=True)
    (c / base.MANIFIESTO).write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    s = f"{base.CARPETA_PAQUETES}/{pid}/{esp.DESTINO_COMUN}"
    (c / base.ENTRADA).write_text(
        f"# {titulo}\n\nAntes de actuar: `python3 {s}/verificar-integridad.py`.\n\n"
        f"1. Lee las **Reglas** (al final de este archivo).\n"
        f"2. Trabaja solo en `{base.CARPETA_TRABAJO}/{pid}/` (`python3 {s}/fichas.py …`).\n"
        f"3. Antes de terminar: `python3 {s}/verificar.py`.\n\n## Reglas\n\n1. …\n", encoding="utf-8")
    (c / "plantillas" / "ficha.md").write_text("---\nid: {{id}}\nstatus: {{status}}\nfecha: {{fecha}}\n---\n\n# {{titulo}}\n\n…\n",
                                               encoding="utf-8")
    return c


def _ruta_segura(pid: str, rel: str, raiz: Path | None) -> Path:
    c = carpeta(pid, raiz).resolve()
    destino = (c / rel).resolve()
    if c not in destino.parents or base.IGNORAR.search(rel) or rel == base.INTEGRIDAD:
        raise ValueError(f"ruta fuera del paquete o reservada: {rel}")
    return destino


def archivos(pid: str, raiz: Path | None = None) -> list[str]:
    return base.archivos_del_paquete(carpeta(pid, raiz))


def leer_archivo(pid: str, rel: str, raiz: Path | None = None) -> str:
    return _ruta_segura(pid, rel, raiz).read_text(encoding="utf-8")


def guardar_archivo(pid: str, rel: str, contenido: str, raiz: Path | None = None) -> list[str]:
    """Guarda un archivo del catálogo y devuelve los errores de validación del paquete tras el cambio."""
    destino = _ruta_segura(pid, rel, raiz)
    if not rel.isascii() or " " in rel:
        raise ValueError("nombre de archivo: ASCII y sin espacios")
    if destino.name == base.MANIFIESTO:
        errores = base.validar_manifiesto(json.loads(contenido))
        if errores:
            return [f"no guardado: {e}" for e in errores]
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(contenido, encoding="utf-8")
    return esp.validar_paquete(carpeta(pid, raiz))


def borrar_archivo(pid: str, rel: str, raiz: Path | None = None) -> None:
    destino = _ruta_segura(pid, rel, raiz)
    if destino.name in (base.MANIFIESTO, *esp.OBLIGATORIOS) and destino.parent == carpeta(pid, raiz).resolve():
        raise ValueError(f"{destino.name} es obligatorio")
    destino.unlink()


def versionar(pid: str, nivel: str, raiz: Path | None = None) -> str:
    if nivel not in NIVELES:
        raise ValueError(f"nivel: {', '.join(NIVELES)}")
    c = carpeta(pid, raiz)
    m = base.leer_manifiesto(c)
    mayor, menor, parche = esp.version_tupla(m["version"])
    nueva = {"mayor": (mayor + 1, 0, 0), "menor": (mayor, menor + 1, 0), "parche": (mayor, menor, parche + 1)}[nivel]
    m["version"] = ".".join(map(str, nueva))
    (c / base.MANIFIESTO).write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return m["version"]


def construir(pid: str, destino: Path, raiz: Path | None = None) -> Path:
    """Construye el paquete en `destino/<id>/` (reemplaza si existe) y lo valida como construido."""
    fuente = carpeta(pid, raiz)
    errores = esp.validar_paquete(fuente)
    if errores:
        raise ValueError(f"{pid}: el catálogo no valida: {'; '.join(errores)}")
    salida = Path(destino) / pid
    if salida.exists():
        shutil.rmtree(salida)
    shutil.copytree(fuente, salida, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    comun = salida / esp.DESTINO_COMUN
    comun.mkdir(parents=True)
    for script in sorted(p for p in esp.COMUN.glob("*.py") if not p.name.startswith("test_")):
        shutil.copy2(script, comun / script.name)
    (salida / base.INTEGRIDAD).write_text(json.dumps(base.calcular_integridad(salida), ensure_ascii=False, indent=2) + "\n",
                                          encoding="utf-8")
    errores = esp.validar_paquete(salida, construido=True)
    if errores:
        raise ValueError(f"{pid}: la construcción no valida: {'; '.join(errores)}")
    return salida
