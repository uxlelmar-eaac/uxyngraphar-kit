"""Catálogo de paquetes (fuente en `paquetes/<id>/`): listar, crear, editar, versionar y construir.

Editar un paquete solo ocurre aquí. Cada paquete fuente es completo; construido = fuente + INTEGRIDAD.json.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import entrada
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


PIEZAS_AL_CREAR = ("plantillas", "cambios")
SEMILLAS = esp.PLANTILLA / "piezas"
FRAGMENTO = "manifiesto.json"


def _escribir_manifiesto(c: Path, m: dict) -> None:
    (c / base.MANIFIESTO).write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def crear(pid: str, titulo: str, descripcion: str = "", raiz: Path | None = None, familia: str = "proceso",
          piezas: list[str] | tuple[str, ...] | None = None) -> Path:
    """Paquete nuevo (versión 0.1.0): núcleo de `!base` más las `piezas` pedidas, con nombres según NOMENCLATURA.md.

    Deja marcadores {{…}} en el núcleo (PAQUETE.md y alcance): el paquete no valida hasta que el autor los rellena.
    """
    piezas = list(PIEZAS_AL_CREAR if piezas is None else piezas)
    errores = nomenclatura.problemas_id(pid) + nomenclatura.problemas_titulo(pid, titulo)
    if familia not in nomenclatura.NORMA["familias"]:
        errores.append(f"familia «{familia}»: una de {', '.join(nomenclatura.NORMA['familias'])}")
    errores += [f"pieza «{p}»: una de {', '.join(base.PIEZAS)}" for p in piezas if p not in base.PIEZAS]
    paquetes = _paquetes(raiz)
    errores += [f"id «{pid}»: choca con «{otro}» (uno es prefijo del otro)" for otro in paquetes
                if otro != pid and (otro.startswith(pid + "-") or pid.startswith(otro + "-"))]
    if errores:
        raise ValueError("; ".join(errores))
    c = catalogo(raiz) / pid
    if c.exists():
        raise FileExistsError(f"ya existe {c}")
    shutil.copytree(esp.PLANTILLA, c, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "piezas"))
    m = base.leer_manifiesto(c)
    resto = {k: v for k, v in m.items() if k not in ("id", "titulo", "descripcion", "familia", "activacion")}
    _escribir_manifiesto(c, {"manifiesto_formato": m["manifiesto_formato"], "id": pid, "version": m["version"], "titulo": titulo,
                             "descripcion": descripcion or titulo, "familia": familia, **resto,
                             "activacion": [pid, pid.replace("-", " ")]})
    for nombre in (base.ENTRADA, base.DESCRIPCION):
        ruta = c / nombre
        ruta.write_text(ruta.read_text(encoding="utf-8").replace("{{titulo}}", titulo).replace("{{id}}", pid), encoding="utf-8")
    usados = {d.get("prefijo") for _, mm in paquetes.values() for d in mm.get("fichas", {}).values()}
    for p in piezas:
        _agregar_pieza(c, p, usados)
    entrada.actualizar(c)
    return c


def _agregar_pieza(c: Path, pieza: str, usados: set | None = None) -> None:
    m = base.leer_manifiesto(c)
    if pieza not in base.PIEZAS:
        raise ValueError(f"pieza «{pieza}»: una de {', '.join(base.PIEZAS)}")
    if pieza in (m.get("piezas") or []) or (c / base.PIEZAS[pieza]).exists():
        raise FileExistsError(f"{m['id']}: ya tiene la pieza «{pieza}»")
    semilla = SEMILLAS / pieza
    for origen in sorted(semilla.rglob("*")):
        rel = origen.relative_to(semilla)
        if origen.is_file() and rel.as_posix() != FRAGMENTO and not base.IGNORAR.search(rel.as_posix()):
            destino = c / rel
            destino.parent.mkdir(parents=True, exist_ok=True)
            texto = origen.read_text(encoding="utf-8")
            destino.write_text(texto.replace("{{version}}", m["version"]) if pieza == "cambios" else texto, encoding="utf-8")
    fragmento = json.loads((semilla / FRAGMENTO).read_text(encoding="utf-8")) if (semilla / FRAGMENTO).is_file() else {}
    if pieza == "plantillas":
        tipo = nomenclatura.singular(m["id"].split("-")[0])
        (ficha,) = fragmento["fichas"].values()
        ficha.update(prefijo=nomenclatura.proponer_prefijo(m["id"], usados or set()), plantilla=f"plantillas/{tipo}.md")
        (c / "plantillas" / "ficha.md").rename(c / "plantillas" / f"{tipo}.md")
        fragmento = {"fichas": {tipo: ficha}}
    orden = list(base.PIEZAS)
    m["piezas"] = sorted([*(m.get("piezas") or []), pieza], key=orden.index)
    for clave, valor in fragmento.items():
        m.setdefault(clave, valor)
    _escribir_manifiesto(c, m)


def agregar_pieza(pid: str, pieza: str, raiz: Path | None = None) -> list[str]:
    """Añade una pieza estándar desde `!base` (con marcadores para rellenar); devuelve los errores del paquete después."""
    c = carpeta(pid, raiz)
    usados = {d.get("prefijo") for otro, (_, mm) in _paquetes(raiz).items() if otro != pid for d in mm.get("fichas", {}).values()}
    _agregar_pieza(c, pieza, usados)
    entrada.actualizar(c)
    return esp.validar_paquete(c)


def quitar_pieza(pid: str, pieza: str, raiz: Path | None = None) -> list[str]:
    """Retira una pieza (su ruta y su entrada en el manifiesto); devuelve los errores del paquete después."""
    c = carpeta(pid, raiz)
    m = base.leer_manifiesto(c)
    if pieza not in (m.get("piezas") or []):
        raise ValueError(f"{pid}: no tiene la pieza «{pieza}»")
    if pieza == "plantillas" and m.get("fichas"):
        raise ValueError(f"{pid}: «fichas» usa plantillas/; quita los tipos de ficha del manifiesto antes")
    ruta = c / base.PIEZAS[pieza]
    if ruta.is_dir():
        shutil.rmtree(ruta)
    elif ruta.exists():
        ruta.unlink()
    m["piezas"] = [p for p in m["piezas"] if p != pieza]
    if pieza in ("proceso", "andamiaje"):
        m.pop(pieza, None)
    _escribir_manifiesto(c, m)
    entrada.actualizar(c)
    return esp.validar_paquete(c)


def indice_paquete(pid: str, raiz: Path | None = None) -> bool:
    """Regenera el bloque de entrada del README del paquete a partir de su manifiesto."""
    return entrada.actualizar(carpeta(pid, raiz))


def completitud(pid: str, raiz: Path | None = None) -> dict:
    import piezas
    c = carpeta(pid, raiz)
    return piezas.completitud(c, base.leer_manifiesto(c))


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
    if destino.name == base.MANIFIESTO and destino.parent == carpeta(pid, raiz).resolve():
        entrada.actualizar(carpeta(pid, raiz))
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
