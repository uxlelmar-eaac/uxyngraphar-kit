"""Actualización de tres vías del núcleo: base (lock) · local (disco) · nueva (pack). Nunca toca contenido (C).

Garantías (10-guias/actualizar-nucleo.md § Garantías): todo o nada aunque se corte a mitad (transaccion.py), migraciones
automáticas entre versiones (migraciones.py) y, con `probar=True`, vuelta atrás si las herramientas del proyecto dejan de
arrancar tras actualizar (contrato.py)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import clasificacion as cl
import contrato
import lock
import migraciones
import respaldos
import transaccion
import zonas


class ErrorActualizacion(RuntimeError):
    pass


@dataclass
class Accion:
    rel: str
    clase: str
    tipo: str   # añadir · reemplazar · zona · conflicto · modificado-local · plantilla-cambiada · retirado · restaurar
    detalle: str = ""


@dataclass
class Plan:
    adoptada: str
    nueva: str
    acciones: list[Accion] = field(default_factory=list)
    sin_lock: bool = False
    restaurar: bool = False
    avisos: list[str] = field(default_factory=list)
    migraciones: list[str] = field(default_factory=list)   # «id — descripción» de las que se aplicarán
    hechas: list[tuple[str, list[str]]] = field(default_factory=list)   # tras aplicar: (id, qué hizo)

    def de(self, *tipos: str) -> list[Accion]:
        return [a for a in self.acciones if a.tipo in tipos]


def planificar(pack: Path, repo: Path, docs: str, restaurar: bool = False) -> Plan:
    docs = docs.strip("/")
    datos = lock.leer(repo, docs)
    base = (datos or {}).get("archivos", {})
    perfil = (datos or {}).get("perfil", "completo")
    nuevo = lock.inventario(pack, perfil)
    sin_base = datos is None or (bool(datos.get("danado")) and not base)
    plan = Plan((datos or {}).get("version", "desconocida"), lock.version_de(pack), sin_lock=sin_base, restaurar=restaurar)
    if datos and datos.get("danado"):
        plan.avisos.append(datos["danado"])
    if transaccion.interrumpidas(repo):
        plan.avisos.append("Hay una actualización anterior que se cortó a mitad: se deshará automáticamente antes de aplicar esta.")
    hechas = set((datos or {}).get("migraciones", []))
    plan.migraciones = [f"{m.id} — {m.descripcion}" for m in migraciones.pendientes(plan.adoptada, plan.nueva, hechas)]
    for rel, info in sorted(nuevo.items()):
        clase, local = info["clase"], repo / cl.destino(rel, docs)
        h_base = base.get(rel, {}).get("sha256")
        if not local.exists():
            plan.acciones.append(Accion(rel, clase, "añadir"))
            continue
        h_local, h_nuevo = lock.sha(local), info["sha256"]
        if h_local == h_nuevo:
            continue
        if clase in ("P", "M") and h_base and h_local == h_base:   # el proyecto nunca lo tocó: se puede reemplazar entero sin perder nada
            plan.acciones.append(Accion(rel, clase, "reemplazar", "no lo habías modificado"))
            continue
        if clase == "M" and _fusion(local, pack / rel) is not None:
            plan.acciones.append(Accion(rel, clase, "zona", "solo se actualiza la parte del pack (entre marcadores); lo tuyo se conserva"))
            continue
        if clase in ("P", "M"):
            if h_base and h_base != h_nuevo:
                plan.acciones.append(Accion(rel, clase, "plantilla-cambiada", "la plantilla del pack cambió; revisar novedades a mano"))
            continue
        if h_base == h_nuevo:  # el pack no cambió pero el proyecto sí: el núcleo fue editado
            plan.acciones.append(Accion(rel, clase, "restaurar" if restaurar else "modificado-local", "el núcleo fue editado en el proyecto"))
        elif h_base is not None and h_local == h_base:
            plan.acciones.append(Accion(rel, clase, "reemplazar"))
        else:
            plan.acciones.append(Accion(rel, clase, "restaurar" if restaurar else "conflicto", "cambió en ambos lados" if h_base else "sin línea base"))
    for rel, info in sorted(base.items()):
        if rel not in nuevo and info["clase"] == "N" and (repo / cl.destino(rel, docs)).exists():
            plan.acciones.append(Accion(rel, "N", "retirado", "ya no existe en el pack; revisar y borrar a mano"))
    return plan


def _fusion(local: Path, nuevo: Path) -> str | None:
    """Texto fusionado si cambia algo dentro de las zonas del pack; None si no hay zonas comparables o nada que cambiar."""
    actual = local.read_text(encoding="utf-8", errors="replace")
    fusion = zonas.fusionar(actual, nuevo.read_text(encoding="utf-8", errors="replace"))
    return fusion if fusion is not None and fusion != actual else None


def _migracion_vigente(repo: Path, docs: str, ident: str) -> bool:
    patron = re.compile(r"^id:\s*[\"']?" + re.escape(ident), re.M)
    estado = re.compile(r"^status:\s*(approved|executing|done)\b", re.M)
    for md in (repo / docs / "05-instrucciones").rglob("*.md"):
        if md.name.startswith("_") or "/01-pendientes/" in md.as_posix():
            continue
        cab = md.read_text(encoding="utf-8", errors="replace")[:2000]
        if patron.search(cab) and estado.search(cab):
            return True
    return False


def aplicar(pack: Path, repo: Path, docs: str, plan: Plan, migracion: str = "", probar: bool = False) -> Path | None:
    """Ejecuta el plan como una transacción. Devuelve la carpeta de respaldo (o None si no hubo nada que escribir)."""
    docs = docs.strip("/")
    recuperadas = transaccion.recuperar(repo)
    if recuperadas:   # el disco cambió al deshacer la interrumpida: el plan se rehace sobre el estado real
        plan.__dict__.update(planificar(pack, repo, docs, plan.restaurar).__dict__)
        plan.avisos[:0] = recuperadas
    if not plan.sin_lock and lock.es_degradacion(plan.adoptada, plan.nueva):
        raise ErrorActualizacion(f"el proyecto tiene {plan.adoptada}, más nueva que este pack ({plan.nueva}): usa un pack igual o más reciente; no se escribe nada")
    if lock.mayor(plan.nueva) != lock.mayor(plan.adoptada) and not plan.sin_lock:
        if not migracion or not _migracion_vigente(repo, docs, migracion):
            raise ErrorActualizacion(f"salto MAYOR {plan.adoptada} → {plan.nueva}: exige --migracion-aprobada <id> de una instrucción approved/executing/done en 05-instrucciones")
    escribir, fusiones, conflictos = plan.de("añadir", "reemplazar", "restaurar"), plan.de("zona"), plan.de("conflicto")
    pendientes = migraciones.pendientes(plan.adoptada, plan.nueva, set((lock.leer(repo, docs) or {}).get("migraciones", [])))
    if not escribir and not fusiones and not conflictos and not pendientes and plan.nueva == plan.adoptada:
        return None
    antes = {contrato.clave(f) for f in contrato.probar(repo, docs)} if probar else set()
    tx = transaccion.Transaccion(repo, docs, version_antes=plan.adoptada, version_despues=plan.nueva)
    try:
        for a in escribir:
            tx.copiar(cl.destino(a.rel, docs), pack / a.rel)
        for a in fusiones:
            texto = _fusion(repo / cl.destino(a.rel, docs), pack / a.rel)
            if texto is not None:
                tx.escribir(cl.destino(a.rel, docs), texto.encode("utf-8"))
        for a in conflictos:
            tx.copiar(cl.destino(a.rel, docs) + ".uxyngraphar-nuevo", pack / a.rel)
        plan.hechas = migraciones.ejecutar(pendientes, repo, docs, tx)
        for extra in (lock.ruta_lock(repo, docs), repo / docs / "90-archivo" / "cambios-pack.md"):
            tx.preparar(extra.relative_to(repo).as_posix())
        _actualizar_lock(pack, repo, docs, plan, [m.id for m in pendientes])
        _anotar(repo, docs, plan)
        if probar:
            rotas = [f for f in contrato.probar(repo, docs) if contrato.clave(f) not in antes]
            if rotas:
                raise ErrorActualizacion("con la versión nueva, las herramientas de este proyecto dejan de funcionar; se deshizo la actualización y "
                                         "todo quedó como estaba. Avisa al equipo de uxyngraphar con este detalle:\n  " + "\n  ".join(rotas))
    except BaseException as exc:   # también Ctrl+C: nada queda a medias
        tx.deshacer(f"{type(exc).__name__}: {exc}"[:300])
        raise
    carpeta = tx.confirmar()
    respaldos.podar_automatico(repo, docs)
    return carpeta


def _actualizar_lock(pack: Path, repo: Path, docs: str, plan: Plan, migradas: list[str] | None = None) -> None:
    datos = lock.leer(repo, docs) or {"formato": lock.FORMATO, "pack": lock.tipo_pack(pack), "perfil": "completo", "docs": docs,
                                       "instalado": datetime.now().date().isoformat(), "archivos": {}}
    nuevo = lock.inventario(pack, datos.get("perfil", "completo"))
    sin_resolver = {a.rel for a in plan.de("conflicto", "modificado-local")}
    for rel, info in nuevo.items():
        if rel in sin_resolver:
            datos["archivos"].setdefault(rel, info)   # la base solo avanza al resolver el conflicto
        else:
            datos["archivos"][rel] = info
    datos["version"] = plan.nueva
    if migradas or datos.get("migraciones"):
        datos["migraciones"] = sorted(set(datos.get("migraciones", [])) | set(migradas or []))
    datos["actualizado"] = datetime.now().date().isoformat()
    lock.escribir(repo, docs, datos)


def _anotar(repo: Path, docs: str, plan: Plan) -> None:
    f = repo / docs / "90-archivo" / "cambios-pack.md"
    f.parent.mkdir(parents=True, exist_ok=True)
    cab = "# Cambios del pack aplicados en este proyecto\n\nRegistro automático de `actualizar-pack.py`.\n\n" if not f.is_file() else ""
    linea = (f"- {datetime.now().date().isoformat()} · {plan.adoptada} → {plan.nueva} · "
             f"añadidos {len(plan.de('añadir'))}, reemplazados {len(plan.de('reemplazar', 'restaurar'))}, zonas del pack {len(plan.de('zona'))}, "
             f"conflictos {len(plan.de('conflicto'))}\n")
    with f.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(cab + linea)


def formatear(plan: Plan) -> str:
    if not plan.acciones and plan.adoptada == plan.nueva and not plan.migraciones and not plan.avisos:
        return f"Núcleo al día (versión {plan.nueva})."
    l = [f"Versión adoptada: {plan.adoptada} → pack: {plan.nueva}" + (" · SIN lock (todo cambio se trata como conflicto)" if plan.sin_lock else "")]
    l += [f"! {x}" for x in plan.avisos]
    if plan.migraciones:
        l.append(f"\nmigraciones automáticas ({len(plan.migraciones)}):")
        l += [f"  - {m}" for m in plan.migraciones]
    for tipo in ("añadir", "reemplazar", "zona", "restaurar", "conflicto", "modificado-local", "plantilla-cambiada", "retirado"):
        items = plan.de(tipo)
        if items:
            l.append(f"\n{tipo} ({len(items)}):")
            l += [f"  - {a.rel} [{a.clase}]" + (f" — {a.detalle}" if a.detalle else "") for a in items]
    return "\n".join(l)
