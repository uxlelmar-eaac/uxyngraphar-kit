"""Catálogo de paquetes (fuente en `paquetes/<id>/`): listar, crear, editar, versionar y construir.

Editar un paquete solo ocurre aquí. Cada paquete fuente es completo; construido = fuente + INTEGRIDAD.json.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import especificacion as esp
import nomenclatura

base = esp.base
NIVELES = ("mayor", "menor", "parche")


def catalogo(raiz: Path | None = None) -> Path:
    return Path(raiz) if raiz else esp.CATALOGO


def _paquetes(raiz: Path | None) -> dict[str, tuple[Path, dict]]:
    return {c.name: (c, base.leer_manifiesto(c)) for c in sorted(catalogo(raiz).iterdir())
            if c.is_dir() and not c.name.startswith(("_", ".", "!")) and (c / base.MANIFIESTO).is_file()}


def listar(raiz: Path | None = None) -> list[dict]:
    """Manifiestos del catálogo (con «errores» de validación y nomenclatura, «avisos» y status «heredados»)."""
    paquetes = _paquetes(raiz)
    nombres = nomenclatura.revisar_catalogo(paquetes)
    salida = []
    for pid, (carpeta, m) in paquetes.items():
        errores, heredados = nombres[pid]
        m["errores"] = esp.validar_paquete(carpeta) + [f"nomenclatura: {e}" for e in errores]
        m["avisos"] = esp.avisos_paquete(carpeta)
        m["heredados"] = heredados
        salida.append(m)
    return salida


def carpeta(pid: str, raiz: Path | None = None) -> Path:
    if not base.ID_VALIDO.match(pid):
        raise ValueError(f"id inválido «{pid}»")
    c = catalogo(raiz) / pid
    if not (c / base.MANIFIESTO).is_file():
        raise FileNotFoundError(f"el catálogo no tiene el paquete «{pid}»")
    return c


def crear(pid: str, titulo: str, descripcion: str = "", raiz: Path | None = None, familia: str = "proceso") -> Path:
    """Esqueleto mínimo de un paquete nuevo (versión 0.1.0) con nombres según NOMENCLATURA.md."""
    errores = nomenclatura.problemas_id(pid) + nomenclatura.problemas_titulo(pid, titulo)
    if familia not in nomenclatura.NORMA["familias"]:
        errores.append(f"familia «{familia}»: una de {', '.join(nomenclatura.NORMA['familias'])}")
    paquetes = _paquetes(raiz)
    errores += [f"id «{pid}»: choca con «{otro}» (uno es prefijo del otro)" for otro in paquetes
                if otro != pid and (otro.startswith(pid + "-") or pid.startswith(otro + "-"))]
    if errores:
        raise ValueError("; ".join(errores))
    c = catalogo(raiz) / pid
    if c.exists():
        raise FileExistsError(f"ya existe {c}")
    usados = {d.get("prefijo") for _, m in paquetes.values() for d in m.get("fichas", {}).values()}
    tipo = nomenclatura.singular(pid.split("-")[0])
    shutil.copytree(esp.PLANTILLA, c, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    m = base.leer_manifiesto(c)
    (ficha,) = m["fichas"].values()
    ficha.update(prefijo=nomenclatura.proponer_prefijo(pid, usados), plantilla=f"plantillas/{tipo}.md")
    (c / "plantillas" / "ficha.md").rename(c / "plantillas" / f"{tipo}.md")
    resto = {k: v for k, v in m.items() if k not in ("id", "titulo", "descripcion", "familia", "activacion", "fichas")}
    m = {"manifiesto_formato": m["manifiesto_formato"], "id": pid, "version": m["version"], "titulo": titulo,
         "descripcion": descripcion or titulo, "familia": familia, **resto,
         "activacion": [pid, pid.replace("-", " ")], "fichas": {tipo: ficha}}
    (c / base.MANIFIESTO).write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    entrada = c / base.ENTRADA
    entrada.write_text(entrada.read_text(encoding="utf-8").replace("{{titulo}}", titulo).replace("{{id}}", pid), encoding="utf-8")
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
    (salida / base.INTEGRIDAD).write_text(json.dumps(base.calcular_integridad(salida), ensure_ascii=False, indent=2) + "\n",
                                          encoding="utf-8")
    errores = esp.validar_paquete(salida, construido=True)
    if errores:
        raise ValueError(f"{pid}: la construcción no valida: {'; '.join(errores)}")
    return salida
