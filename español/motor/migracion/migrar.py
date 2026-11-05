"""Migración 1.x → 2.0: del pack numerado (00–97) a paquetes en `uxyngraphar/` + trabajo en `uxyngraphar-work/`.

Por defecto solo simula. Al aplicar: respaldo completo → copia del contenido del proyecto → verificación sha256 →
retirada del pack y de sus protecciones → instalación de los paquetes equivalentes. Ante cualquier fallo, reversión.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI), str(AQUI.parent)]

import clasificacion_1x as cl1x  # noqa: E402
import especificacion as esp  # noqa: E402
import limpieza  # noqa: E402
import repo  # noqa: E402

base = esp.base
TRABAJO = base.CARPETA_TRABAJO
LEGADO = "_legado-1x"
RESPALDOS = ".uxyngraphar-respaldos"
SALTAR = {"node_modules", ".git", TRABAJO, RESPALDOS, "dist", "build", ".next", "vendor", ".venv", "venv", "coverage"}
DESTINOS = (
    ("03-preguntas/", "ciclo-instrucciones", "preguntas/"),
    ("05-instrucciones/", "ciclo-instrucciones", "instrucciones/"),
    ("15-rutas/", "<rutas>", ""),
    ("20-decisiones/", "decisiones-adr", ""),
    ("25-areas/", "areas-modulos", ""),
    ("30-manuales/", "manuales", ""),
    ("35-herramientas/autorizadas/", "herramientas-autorizadas", "autorizadas/"),
    ("35-herramientas/propuestas/", "herramientas-autorizadas", "propuestas/"),
    ("40-auditorias/", "auditorias", ""),
    ("45-mejoras-propuestas/", "mejoras-pendientes", ""),
    ("50-sistema-integral/", "espejo-sistema", ""),
    ("90-archivo/", "memoria-archivo", "archivo/"),
    ("95-memoria/", "memoria-archivo", "memoria/"),
)
ESTADO_1X = re.compile(r"^0[1-9]-(?:listas-)?([a-z-]+)/(\d{4}-\d{2}-\d{2})/(.+)$")
COMUNES = ["ciclo-instrucciones", "calidad-codigo", "secretos", "decisiones-adr", "areas-modulos", "espejo-sistema",
           "herramientas-autorizadas", "auditorias", "mejoras-pendientes", "manuales", "memoria-archivo"]


def sha256(ruta: Path) -> str:
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


@dataclass
class Plan:
    app: Path
    carpeta: Path
    pack: str
    copias: list[tuple[Path, Path, str]] = field(default_factory=list)
    omitidos: list[str] = field(default_factory=list)
    bloqueos: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    paquetes: list[str] = field(default_factory=list)
    ajustes: dict[str, dict] = field(default_factory=dict)
    borrar_raiz: list[Path] = field(default_factory=list)

    def resumen(self) -> dict:
        trabajo = self.app / TRABAJO
        return {"app": str(self.app), "carpeta": self.carpeta.name, "pack": self.pack, "paquetes": self.paquetes,
                "migrar": len(self.copias), "legado": sum(1 for _, d, _ in self.copias if LEGADO in d.relative_to(trabajo).parts[:1]),
                "omitidos_nucleo": len(self.omitidos), "bloqueos": self.bloqueos, "avisos": self.avisos,
                "destinos": sorted({d.relative_to(trabajo).parts[0] for _, d, _ in self.copias})}


def detectar(raiz: Path) -> list[tuple[Path, Path]]:
    """(raíz de la app, carpeta del pack) de cada instalación 1.x bajo `raiz` (hasta 4 niveles)."""
    raiz = Path(raiz).resolve()
    hallazgos = []
    for actual, dirs, _ in os.walk(raiz):
        profundidad = len(Path(actual).relative_to(raiz).parts)
        dirs[:] = [d for d in dirs if d not in SALTAR and profundidad < 4]
        for d in list(dirs):
            c = Path(actual) / d
            if d in ("docs", base.CARPETA_PAQUETES) and ((c / ".uxyngraphar.lock").is_file()
                                                        or ((c / "00-nucleo").is_dir() and (c / "05-instrucciones").is_dir())):
                hallazgos.append((Path(actual), Path(actual) / d))
                dirs.remove(d)
    return hallazgos


def _tipo_pack(lock: dict, carpeta: Path) -> str:
    if lock.get("pack") in ("servidor", "cliente"):
        return lock["pack"]
    agentes = carpeta / "AGENTES.md"
    primera = agentes.read_text(encoding="utf-8").splitlines()[0] if agentes.is_file() else ""
    return "cliente" if "cliente" in primera else "servidor"


def _destino(rel: str, pack: str) -> tuple[str, str, str]:
    """(paquete, ruta dentro de su trabajo, fecha 1.x). `0N-estado/<fecha>/x.md` pasa a `estado/x.md`."""
    for prefijo, pid, sub in DESTINOS:
        if rel.startswith(prefijo):
            pid = ("mapa-rutas-ui" if pack == "cliente" else "mapa-rutas-api") if pid == "<rutas>" else pid
            resto = rel[len(prefijo):]
            m = ESTADO_1X.match(resto)
            return (pid, f"{sub}{m[1]}/{m[3]}", m[2]) if m else (pid, sub + resto, "")
    return LEGADO, rel, ""


def _sin_choques(plan: Plan, fechas: dict[Path, str]) -> None:
    """Si dos fichas 1.x de fechas distintas acaban con el mismo nombre, se les antepone su fecha."""
    cuenta: dict[Path, int] = {}
    for _, d, _ in plan.copias:
        cuenta[d] = cuenta.get(d, 0) + 1
    for i, (o, d, h) in enumerate(plan.copias):
        if cuenta[d] > 1 and fechas.get(o):
            plan.copias[i] = (o, d.with_name(f"{fechas[o]}-{d.name}"), h)
    destinos = [d for _, d, _ in plan.copias]
    for d in sorted({d for d in destinos if destinos.count(d) > 1}):
        plan.bloqueos.append(f"dos archivos irían a {d.relative_to(plan.app / TRABAJO)}: renombra uno antes de migrar")


def _ajustes(cfg: dict) -> dict[str, dict]:
    codigo = cfg.get("codigo", {})
    calidad = {k: v for k, v in {"raices": codigo.get("raices"), "extensiones": codigo.get("extensiones"),
                                 "excluir": codigo.get("excluir"), "limite_lineas": cfg.get("limite_lineas"),
                                 "exenciones_lineas": cfg.get("exenciones_lineas")}.items() if v is not None}
    salida = {"calidad-codigo": calidad, "espejo-sistema": {k: calidad[k] for k in ("raices", "extensiones") if k in calidad}}
    if cfg.get("secretos_permitir"):
        salida["secretos"] = {"permitir": cfg["secretos_permitir"]}
    return {k: v for k, v in salida.items() if v}


def planificar(app: Path, carpeta: Path) -> Plan:
    ruta_lock = carpeta / ".uxyngraphar.lock"
    lock = json.loads(ruta_lock.read_text(encoding="utf-8")) if ruta_lock.is_file() else {}
    registrados = lock.get("archivos", {})
    plan = Plan(app, carpeta, _tipo_pack(lock, carpeta))
    if not lock:
        plan.bloqueos.append(f"{carpeta.name}/ tiene numeración 1.x pero no .uxyngraphar.lock: no puedo comprobar si el núcleo "
                             "fue editado; reinstala el lock con el kit 1.x o mueve tú el contenido propio")
    trabajo = app / TRABAJO
    if trabajo.exists() and any(trabajo.iterdir()):
        plan.bloqueos.append(f"{TRABAJO}/ ya existe y no está vacío: muévelo o vacíalo antes de migrar")
    if (app / base.CARPETA_PAQUETES).exists() and carpeta.name != base.CARPETA_PAQUETES:
        plan.bloqueos.append(f"existe {base.CARPETA_PAQUETES}/ además de {carpeta.name}/: resuélvelo a mano antes de migrar")
    usados, fechas = set(), {}
    for p in sorted(carpeta.rglob("*")):
        rel = p.relative_to(carpeta).as_posix()
        if not p.is_file() or "__pycache__" in p.parts:
            continue
        clase = cl1x.clasificar(rel)
        if clase is None:
            plan.bloqueos.append(f"sin clasificar (no sé dónde va): {rel}")
        elif clase == "X":
            plan.copias.append((p, trabajo / LEGADO / rel, sha256(p)))
        elif clase == "N":
            esperado = registrados.get(rel, {}).get("sha256")
            if esperado and esperado != sha256(p):
                plan.bloqueos.append(f"núcleo editado localmente (difiere del lock): {rel}")
            plan.omitidos.append(rel)
        else:
            pid, sub, fechas[p] = _destino(rel, plan.pack)
            usados.add(pid)
            plan.copias.append((p, trabajo / pid / sub, sha256(p)))
    _sin_choques(plan, fechas)
    for nombre in cl1x.EN_RAIZ:
        f = app / nombre
        if f.is_file() and not f.is_symlink():
            esperado = registrados.get(nombre, {}).get("sha256")
            if esperado and esperado != sha256(f):
                plan.copias.append((f, trabajo / LEGADO / "raiz" / nombre, sha256(f)))
                plan.avisos.append(f"{nombre} tenía cambios propios: se conserva en {TRABAJO}/{LEGADO}/raiz/{nombre}")
            plan.borrar_raiz.append(f)
    for nombre in (".gitignore", ".gitattributes"):
        f = app / nombre
        if f.is_file() and any(l.strip().startswith(carpeta.name + "/") for l in f.read_text(encoding="utf-8").splitlines()):
            plan.avisos.append(f"{nombre} tiene líneas con «{carpeta.name}/» del 1.x: revísalas a mano (no se tocan)")
    rutas = "mapa-rutas-ui" if plan.pack == "cliente" else "mapa-rutas-api"
    plan.paquetes = COMUNES[:4] + [rutas] + COMUNES[4:]
    config = carpeta / "uxyngraphar.config.json"
    if config.is_file():
        plan.ajustes = _ajustes(json.loads(config.read_text(encoding="utf-8")))
    if usados - set(plan.paquetes) - {LEGADO}:
        plan.bloqueos.append(f"destinos sin paquete: {sorted(usados - set(plan.paquetes) - {LEGADO})}")
    return plan


def _respaldar(plan: Plan, destino: Path) -> dict:
    shutil.copytree(plan.carpeta, destino / plan.carpeta.name, symlinks=True)
    extras = {}
    for f in limpieza.extras_a_respaldar(plan.app):
        rel = f.relative_to(plan.app).as_posix()
        (destino / "raiz" / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, destino / "raiz" / rel)
        extras[rel] = str(f)
    for g in limpieza.ganchos_1x(plan.app):
        (destino / "git-hooks").mkdir(parents=True, exist_ok=True)
        shutil.copy2(g, destino / "git-hooks" / g.name)
        extras[f"git-hooks/{g.name}"] = str(g)
    (destino / "RESPALDO.json").write_text(json.dumps({"carpeta": str(plan.carpeta), "extras": extras}, indent=2, ensure_ascii=False),
                                           encoding="utf-8")
    return extras


def _revertir(plan: Plan, respaldo: Path, extras: dict) -> None:
    for creada in (plan.app / base.CARPETA_PAQUETES, plan.app / TRABAJO, plan.carpeta):
        limpieza.escribible(creada)
        repo.borrar_arbol(creada)
    shutil.copytree(respaldo / plan.carpeta.name, plan.carpeta, symlinks=True)
    for rel, original in extras.items():
        origen = respaldo / ("raiz/" + rel if not rel.startswith("git-hooks/") else rel)
        Path(original).parent.mkdir(parents=True, exist_ok=True)
        if Path(original).exists():
            limpieza.escribible(Path(original))
        shutil.copy2(origen, original)


def aplicar_plan(plan: Plan) -> dict:
    if plan.bloqueos:
        raise ValueError("migración bloqueada: " + "; ".join(plan.bloqueos))
    respaldo = plan.app / RESPALDOS / f"migracion-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    respaldo.mkdir(parents=True)
    extras = _respaldar(plan, respaldo)
    hechos = []
    try:
        for origen, destino, _ in plan.copias:
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origen, destino)
            limpieza.escribible(destino)
        malos = [str(d) for _, d, h in plan.copias if not d.is_file() or sha256(d) != h]
        if malos:
            raise RuntimeError(f"verificación sha256 fallida: {malos[:5]}")
        for pid, valores in plan.ajustes.items():
            ajustes = plan.app / TRABAJO / pid / "ajustes.json"
            ajustes.parent.mkdir(parents=True, exist_ok=True)
            ajustes.write_text(json.dumps(valores, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        limpieza.escribible(plan.carpeta)
        repo.borrar_arbol(plan.carpeta)
        for f in plan.borrar_raiz:
            limpieza.escribible(f)
            f.unlink()
        hechos += limpieza.limpiar(plan.app, plan.carpeta.name)
        repo.instalar(plan.app, plan.paquetes)
        malos = [str(d) for _, d, h in plan.copias if not d.is_file() or sha256(d) != h]
        if malos:
            raise RuntimeError(f"verificación final sha256 fallida: {malos[:5]}")
    except Exception:
        _revertir(plan, respaldo, extras)
        raise
    return {**plan.resumen(), "aplicada": True, "respaldo": str(respaldo), "limpieza": hechos}


def ejecutar(raiz: Path, aplicar: bool = False) -> dict:
    instalaciones = detectar(raiz)
    informe = {"instalaciones": [], "aplicada": False}
    planes = [planificar(app, carpeta) for app, carpeta in instalaciones]
    for plan in planes:
        if aplicar and not plan.bloqueos:
            informe["instalaciones"].append(aplicar_plan(plan))
        else:
            informe["instalaciones"].append({**plan.resumen(), "aplicada": False})
    informe["aplicada"] = bool(planes) and all(i["aplicada"] for i in informe["instalaciones"])
    return informe


def main(raiz: str, aplicar: bool = False) -> int:
    informe = ejecutar(Path(raiz), aplicar)
    if not informe["instalaciones"]:
        print("No hay instalaciones 1.x (no encontré .uxyngraphar.lock en docs/ ni uxyngraphar/).")
        return 0
    for i in informe["instalaciones"]:
        estado = "MIGRADA" if i["aplicada"] else ("BLOQUEADA" if i["bloqueos"] else "lista para migrar (simulación)")
        print(f"\n{i['app']}/{i['carpeta']} · pack {i['pack']} · {estado}")
        print(f"  contenido del proyecto a {TRABAJO}/: {i['migrar']} archivos ({i['legado']} a {LEGADO}/) → {', '.join(i['destinos'])}")
        print(f"  núcleo 1.x sin cambios locales (lo sustituyen los paquetes): {i['omitidos_nucleo']}")
        print(f"  paquetes a instalar: {', '.join(i['paquetes'])}")
        for b in i["bloqueos"]:
            print(f"  BLOQUEO: {b}")
        for a in i["avisos"]:
            print(f"  aviso: {a}")
        for h in i.get("limpieza", []):
            print(f"  limpieza: {h}")
        if i.get("respaldo"):
            print(f"  respaldo: {i['respaldo']}")
    if not aplicar:
        print("\nSimulación: no se cambió nada. Para migrar (con respaldo y reversión automática): añade --aplicar.")
    return 1 if any(i["bloqueos"] for i in informe["instalaciones"]) else 0
