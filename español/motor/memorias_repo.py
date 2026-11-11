"""Memorias del proyecto vistas desde el motor (panel y CLI): por sistema instalado, las de
`uxyngraphar/trabajo/<id>/memorias/`. Quien llama ya es una persona (el panel la acredita con su sesión), así que puede
crear memorias vigentes, aprobar las propuestas del agente y archivarlas."""

from __future__ import annotations

from pathlib import Path

import especificacion as esp
import generar
import repo
import uxyn_memorias as memorias

base = esp.base


def _sistema(raiz_app: Path, pid: str) -> Path:
    carpeta = repo.carpeta_instalada(Path(raiz_app), pid)
    if not (carpeta / base.MANIFIESTO).is_file():
        raise FileNotFoundError(f"«{pid}» no está instalado")
    return carpeta


def _datos(m: memorias.Memoria, trabajo: Path) -> dict:
    return {"id": m.id, "status": m.status, "autor": m.autor, "fecha": m.fecha, "valida_hasta": m.valida_hasta,
            "titulo": m.titulo, "caducada": memorias.caducada(m), "ruta": m.ruta.resolve().relative_to(trabajo.resolve()).as_posix(),
            "contenido": m.ruta.read_text(encoding="utf-8")}


def listar(raiz_app: Path) -> list[dict]:
    """Por sistema instalado: sus memorias y cuántas propuestas esperan a la persona."""
    raiz_app = Path(raiz_app)
    salida = []
    for man in generar.instalados(raiz_app):
        sistema = repo.carpeta_instalada(raiz_app, man["id"])
        trabajo = raiz_app / base.CARPETA_TRABAJO
        lista = [_datos(m, trabajo) for m in memorias.listar(sistema)]
        salida.append({"id": man["id"], "titulo": man.get("titulo", man["id"]), "memorias": lista,
                       "propuestas": sum(1 for m in lista if m["status"] == "propuesta")})
    return salida


def propuestas(raiz_app: Path) -> int:
    """Memorias propuestas por el agente que esperan a que la persona las apruebe o archive."""
    return sum(s["propuestas"] for s in listar(raiz_app))


def crear(raiz_app: Path, pid: str, slug: str, titulo: str, texto: str = "", motivo: str = "", fuente: str = "",
          valida_hasta: str | None = None) -> str:
    ruta = memorias.crear(_sistema(raiz_app, pid), slug, titulo, texto, motivo, fuente or "panel", valida_hasta or None,
                          por_humano=True, persona_verificada=True)
    return memorias.leer(ruta).id


def aprobar(raiz_app: Path, pid: str, mid: str) -> str:
    memorias.cambiar_estado(_sistema(raiz_app, pid), mid, "vigente", por_humano=True, persona_verificada=True)
    return mid


def archivar(raiz_app: Path, pid: str, mid: str) -> str:
    memorias.cambiar_estado(_sistema(raiz_app, pid), mid, "archivada", por_humano=True, persona_verificada=True)
    return mid
