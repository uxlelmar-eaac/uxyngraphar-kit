"""Una actualización es todo o nada, también si se corta a mitad (Ctrl+C, cierre de la terminal, apagón o error).

Antes de tocar cada archivo se guarda su copia en la carpeta de respaldo y se anota en un diario (`_diario.jsonl`).
Si el proceso muere, el diario queda abierto: la siguiente actualización (o `doctor.py --fix`) lo encuentra y deja
el proyecto exactamente como estaba antes de empezar. Las rutas del diario son relativas a la raíz del repo.
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import respaldos


class Transaccion:
    def __init__(self, repo: Path, docs: str, **info: str) -> None:
        self.repo, self.docs, self.info = repo, docs, info
        self.carpeta = respaldos.nueva_carpeta(repo, docs, "actualizacion")
        self.carpeta.mkdir(parents=True)
        self.copiados: list[str] = []
        self.añadidos: list[str] = []
        self._anotar({"op": "inicio", **info})

    def _anotar(self, entrada: dict) -> None:
        with (self.carpeta / respaldos.DIARIO).open("a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(entrada, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())   # el apunte llega al disco ANTES de tocar el archivo

    def preparar(self, rel: str) -> None:
        """Llamar antes de crear, cambiar o borrar `rel`: guarda cómo estaba para poder volver atrás."""
        if rel in self.copiados or rel in self.añadidos:
            return
        actual = self.repo / rel
        if actual.is_file():
            copia = self.carpeta / rel
            copia.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(actual, copia)
            self._anotar({"op": "copia", "rel": rel})
            self.copiados.append(rel)
        else:
            self._anotar({"op": "nuevo", "rel": rel})
            self.añadidos.append(rel)

    def escribir(self, rel: str, datos: bytes) -> None:
        self.preparar(rel)
        destino = self.repo / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        tmp = destino.with_name(destino.name + ".uxyngraphar-tmp")
        tmp.write_bytes(datos)
        os.replace(tmp, destino)

    def copiar(self, rel: str, origen: Path) -> None:
        self.escribir(rel, origen.read_bytes())

    def borrar(self, rel: str) -> None:
        self.preparar(rel)
        (self.repo / rel).unlink(missing_ok=True)

    def confirmar(self, **extra: str) -> Path:
        respaldos.escribir_manifiesto(self.carpeta, "actualizacion", self.copiados, self.añadidos, estado="completa", **self.info, **extra)
        self._anotar({"op": "fin"})
        return self.carpeta

    def deshacer(self, motivo: str = "") -> None:
        deshacer_carpeta(self.repo, self.carpeta, motivo)


def deshacer_carpeta(repo: Path, carpeta: Path, motivo: str = "") -> list[str]:
    """Devuelve el repo al estado anterior según el diario. Idempotente: repetirlo no cambia nada más."""
    entradas = []
    for linea in (carpeta / respaldos.DIARIO).read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            entradas.append(json.loads(linea))
        except ValueError:
            continue
    info = next((e for e in entradas if e.get("op") == "inicio"), {})
    copiados = [e["rel"] for e in entradas if e.get("op") == "copia"]
    añadidos = [e["rel"] for e in entradas if e.get("op") == "nuevo"]
    for rel in reversed(añadidos):
        (repo / rel).unlink(missing_ok=True)
        (repo / rel).with_name(Path(rel).name + ".uxyngraphar-tmp").unlink(missing_ok=True)
    for rel in reversed(copiados):
        destino, tmp = repo / rel, (repo / rel).with_name(Path(rel).name + ".uxyngraphar-tmp")
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(carpeta / rel, tmp)
        os.replace(tmp, destino)
    extra = {k: v for k, v in info.items() if k != "op" and isinstance(v, str)}
    respaldos.escribir_manifiesto(carpeta, "actualizacion", copiados, añadidos, estado="deshecha", motivo=motivo or "actualización interrumpida", **extra)
    with (carpeta / respaldos.DIARIO).open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"op": "deshecha", "motivo": motivo}, ensure_ascii=False) + "\n")
    return copiados + añadidos


def interrumpidas(repo: Path) -> list[Path]:
    raiz = repo / ".uxyngraphar-respaldo"
    return sorted((c for c in raiz.iterdir() if c.is_dir() and respaldos.diario_abierto(c)), reverse=True) if raiz.is_dir() else []


def recuperar(repo: Path) -> list[str]:
    """Deshace las actualizaciones que se cortaron a mitad (la más reciente primero). Devuelve un mensaje por cada una."""
    mensajes = []
    for carpeta in interrumpidas(repo):
        tocados = deshacer_carpeta(repo, carpeta, "actualización interrumpida: se deshizo al volver a ejecutar")
        mensajes.append(f"Se encontró una actualización interrumpida ({carpeta.name}); se deshizo ({len(tocados)} archivos vuelven a como estaban).")
    return mensajes
