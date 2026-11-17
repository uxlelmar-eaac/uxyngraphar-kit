"""Publicar un sistema del catálogo local al servidor (CLI y panel del kit)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import artefacto
import catalogo
import especificacion as esp
import remoto

base = esp.base


def _manifiesto(pid: str, raiz: Path | None = None) -> tuple[Path, dict]:
    c = catalogo.carpeta(pid, raiz)
    return c, base.leer_manifiesto(c)


def editor_actual(pid: str, raiz: Path | None = None) -> str:
    _, m = _manifiesto(pid, raiz)
    return m.get("editor") or artefacto.EDITOR_POR_DEFECTO


def fijar_editor(pid: str, editor: str, raiz: Path | None = None) -> str:
    """Escribe `editor` en sistema.json. Devuelve el valor anterior (o el por defecto)."""
    editor = (editor or "").strip().lstrip("@")
    if not editor or not base.ID_VALIDO.match(editor):
        raise ValueError(f"editor inválido «{editor}»")
    c, m = _manifiesto(pid, raiz)
    anterior = m.get("editor") or artefacto.EDITOR_POR_DEFECTO
    if anterior == editor:
        return anterior
    m["editor"] = editor
    (c / base.MANIFIESTO).write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return anterior


def _exigir_sin_errores(pid: str, raiz: Path | None = None) -> dict:
    fila = next((m for m in catalogo.listar(raiz) if m["id"] == pid), None)
    if fila is None:
        raise FileNotFoundError(f"el catálogo no tiene el sistema «{pid}»")
    if fila.get("errores"):
        raise ValueError("el sistema tiene errores:\n" + "\n".join(fila["errores"]))
    return fila


def usuario_sesion() -> str | None:
    """Slug del @usuario de la sesión del kit, o None si no hay sesión usable."""
    datos = remoto.sesion()
    usuario = (datos.get("usuario") or "").strip().lstrip("@")
    if usuario:
        return usuario
    if not remoto.token():
        return None
    try:
        yo = remoto.quien_soy()
    except (PermissionError, remoto.SinServidor):
        return None
    return (yo.get("usuario") or "").strip().lstrip("@") or None


def publicar_local(pid: str, *, simular: bool = False, alinear_editor: bool = False,
                   raiz: Path | None = None) -> dict:
    """Empaqueta el sistema y, si no simula, lo publica en el Mercado.

    Si `alinear_editor`, escribe en sistema.json el @usuario de la sesión antes de empaquetar.
    """
    _exigir_sin_errores(pid, raiz)
    editor = editor_actual(pid, raiz)
    alineado = False
    if alinear_editor:
        usuario = usuario_sesion()
        if not usuario:
            raise PermissionError("sin sesión: inicia sesión en Herramienta")
        if editor != usuario:
            fijar_editor(pid, usuario, raiz)
            editor = usuario
            alineado = True
            _exigir_sin_errores(pid, raiz)

    with tempfile.TemporaryDirectory(prefix="uxy-publicar-") as tmp:
        z = artefacto.empaquetar(pid, Path(tmp), raiz)
        tamano = z.stat().st_size
        sha = artefacto.sha256_de(z)
        _, m = artefacto.leer(z)
        version = m.get("version") or ""
        if simular:
            return {"simulado": True, "id": pid, "version": version, "editor": editor,
                    "tamano": tamano, "sha256": sha, "alineado": alineado}
        r = remoto.publicar(z)
        return {**r, "id": r.get("id", pid), "editor": r.get("editor", editor),
                "version": r.get("version", version), "alineado": alineado,
                "tamano": tamano, "sha256": sha}
