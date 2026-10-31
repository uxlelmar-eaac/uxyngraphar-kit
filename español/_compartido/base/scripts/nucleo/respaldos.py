"""Copias de seguridad de uxyngraphar: dónde están, cuánto se conservan, cómo se restauran y cómo se limpian.

Dos orígenes, cada uno en su carpeta (ambas en .gitignore; nunca entran en git ni las leen los agentes):
  actualizacion  <repo>/.uxyngraphar-respaldo/<AAAAMMDD-HHMMSS>/     rutas relativas a la raíz del repo
  depuracion     <repo>/<docs>/.depuracion/respaldo/<AAAAMMDD-HHMMSS>/ rutas relativas a docs/
Cada copia lleva `_respaldo.json` (origen, fecha, versiones, archivos copiados y añadidos). Las copias antiguas sin
manifiesto también se listan y restauran (se infiere todo de la carpeta).
Política (uxyngraphar.config.json → "respaldos"): conservar_dias (30), conservar_minimo (3: las N más recientes de cada
origen nunca se borran) y limpieza_automatica (true: se poda al terminar cada actualización o depuración).
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "control"))

MANIFIESTO = "_respaldo.json"
DIARIO = "_diario.jsonl"   # diario de una actualización en curso (ver transaccion.py)
FORMATO_FECHA = "%Y%m%d-%H%M%S"
POLITICA = {"conservar_dias": 30, "conservar_minimo": 3, "limpieza_automatica": True}


@dataclass
class Respaldo:
    id: str            # «actualizacion/20261026-090000» o «depuracion/20261026-090000»
    origen: str
    carpeta: Path
    base: Path         # a qué se refieren las rutas de dentro (repo o docs)
    fecha: datetime
    archivos: list[str] = field(default_factory=list)
    añadidos: list[str] = field(default_factory=list)
    info: dict = field(default_factory=dict)

    @property
    def dias(self) -> int:
        return (datetime.now() - self.fecha).days


def raices(repo: Path, docs: str) -> dict[str, tuple[Path, Path]]:
    """origen → (carpeta de copias, base de las rutas)."""
    d = repo / docs.strip("/")
    return {"actualizacion": (repo / ".uxyngraphar-respaldo", repo), "depuracion": (d / ".depuracion" / "respaldo", d)}


def politica(repo: Path, docs: str) -> dict:
    try:
        import uxyngraphar_config as cfgmod
        cfg, _ = cfgmod.cargar(repo, docs)
        return {**POLITICA, **(cfg.get("respaldos") or {})}
    except Exception:  # noqa: BLE001 - sin config válida se usan los valores por defecto
        return dict(POLITICA)


def diario_abierto(carpeta: Path) -> bool:
    """True si la carpeta guarda una actualización que empezó y no terminó (ni se deshizo)."""
    f = carpeta / DIARIO
    if not f.is_file():
        return False
    ultima = ""
    for linea in f.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            ultima = json.loads(linea).get("op", ultima)
        except ValueError:
            continue   # una línea a medio escribir (corte durante la escritura) no cuenta
    return ultima not in ("fin", "deshecha")


def nueva_carpeta(repo: Path, docs: str, origen: str) -> Path:
    raiz, _ = raices(repo, docs)[origen]
    base = datetime.now().strftime(FORMATO_FECHA)
    carpeta, n = raiz / base, 1
    while carpeta.exists():
        carpeta, n = raiz / f"{base}-{n}", n + 1
    return carpeta


def escribir_manifiesto(carpeta: Path, origen: str, archivos: list[str], añadidos: list[str] | None = None, **extra: str) -> None:
    carpeta.mkdir(parents=True, exist_ok=True)
    datos = {"origen": origen, "fecha": datetime.now().isoformat(timespec="seconds"), "archivos": sorted(set(archivos)),
             "añadidos": sorted(set(añadidos or [])), **extra}
    (carpeta / MANIFIESTO).write_text(json.dumps(datos, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def _cargar(carpeta: Path, origen: str, base: Path) -> Respaldo:
    info: dict = {}
    m = carpeta / MANIFIESTO
    if m.is_file():
        try:
            info = json.loads(m.read_text(encoding="utf-8"))
        except ValueError:
            info = {}
    try:
        fecha = datetime.fromisoformat(info["fecha"]) if info.get("fecha") else datetime.strptime(carpeta.name[:15], FORMATO_FECHA)
    except ValueError:
        fecha = datetime.fromtimestamp(carpeta.stat().st_mtime)
    archivos = info.get("archivos") or sorted(p.relative_to(carpeta).as_posix() for p in carpeta.rglob("*") if p.is_file() and p.name not in (MANIFIESTO, DIARIO))
    return Respaldo(f"{origen}/{carpeta.name}", origen, carpeta, base, fecha, archivos, info.get("añadidos", []), info)


def listar(repo: Path, docs: str) -> list[Respaldo]:
    salida = []
    for origen, (raiz, base) in raices(repo, docs).items():
        if raiz.is_dir():
            salida += [_cargar(c, origen, base) for c in raiz.iterdir() if c.is_dir()]
    return sorted(salida, key=lambda r: r.fecha, reverse=True)


def buscar(repo: Path, docs: str, ident: str) -> Respaldo | None:
    todos = listar(repo, docs)
    return next((r for r in todos if ident in (r.id, r.carpeta.name)), None)


def caducados(repo: Path, docs: str, dias: int | None = None, minimo: int | None = None) -> list[Respaldo]:
    pol = politica(repo, docs)
    dias = pol["conservar_dias"] if dias is None else dias
    minimo = pol["conservar_minimo"] if minimo is None else minimo
    salida = []
    for origen in raices(repo, docs):
        del_origen = [r for r in listar(repo, docs) if r.origen == origen]   # más reciente primero
        salida += [r for r in del_origen[minimo:] if r.dias > dias and not diario_abierto(r.carpeta)]   # una interrumpida aún se puede deshacer
    return salida


def limpiar(repo: Path, docs: str, dias: int | None = None, minimo: int | None = None, aplicar: bool = False) -> list[Respaldo]:
    """Borra las copias caducadas (o solo las lista si aplicar=False). Devuelve las afectadas."""
    lista = caducados(repo, docs, dias, minimo)
    if aplicar:
        for r in lista:
            shutil.rmtree(r.carpeta, ignore_errors=True)
    return lista


def podar_automatico(repo: Path, docs: str) -> list[Respaldo]:
    """Limpieza tras actualizar/depurar, según la política del proyecto. Nunca falla."""
    try:
        return limpiar(repo, docs, aplicar=True) if politica(repo, docs).get("limpieza_automatica", True) else []
    except Exception:  # noqa: BLE001 - podar nunca debe romper la operación principal
        return []


def plan_restaurar(r: Respaldo, solo: list[str] | None = None) -> dict[str, list[str]]:
    """Qué haría restaurar: archivos que vuelven a su versión guardada y archivos añadidos que se retiran."""
    sel = [a for a in r.archivos if not solo or a in solo]
    fuera = [a for a in r.añadidos if not solo] if r.origen == "actualizacion" else []
    return {"restaurar": sel, "retirar": [a for a in fuera if (r.base / a).exists()], "desconocidos": [s for s in (solo or []) if s not in r.archivos]}


def restaurar(repo: Path, docs: str, r: Respaldo, solo: list[str] | None = None) -> tuple[dict[str, list[str]], Path | None]:
    """Restaura (todo o `solo`). Antes guarda el estado actual en una copia nueva (origen del respaldo), así se puede deshacer."""
    plan = plan_restaurar(r, solo)
    tocar = plan["restaurar"] + plan["retirar"]
    if not tocar:
        return plan, None
    previa = nueva_carpeta(repo, docs, r.origen)
    existentes = [a for a in tocar if (r.base / a).exists()]
    for a in existentes:
        (previa / a).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(r.base / a, previa / a)
    escribir_manifiesto(previa, r.origen, existentes, [a for a in plan["restaurar"] if not (r.base / a).exists()],
                        motivo=f"estado previo a restaurar {r.id}")
    for a in plan["restaurar"]:
        destino = r.base / a
        destino.parent.mkdir(parents=True, exist_ok=True)
        tmp = destino.with_name(destino.name + ".tmp")
        shutil.copy2(r.carpeta / a, tmp)
        os.replace(tmp, destino)
    for a in plan["retirar"]:
        (r.base / a).unlink()
    return plan, previa
