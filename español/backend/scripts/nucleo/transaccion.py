"""Una actualización es todo o nada, también si se corta a mitad (Ctrl+C, cierre de la terminal, apagón o error).

Antes de tocar cada archivo se guarda su copia en la carpeta de respaldo y se anota en un diario (`_diario.jsonl`).
Si el proceso muere, el diario queda abierto: la siguiente actualización (o `doctor.py --fix`) lo encuentra y deja
el proyecto exactamente como estaba antes de empezar. Las rutas del diario son relativas a la raíz del repo.
"""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
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
        if destino.is_file():   # conserva los permisos (un gancho de git debe seguir siendo ejecutable)
            modo = stat.S_IMODE(destino.stat().st_mode)
            if not (modo & stat.S_IWUSR):   # núcleo congelado (R-20): hace falta escribir aunque el archivo sea solo lectura
                os.chmod(destino, modo | stat.S_IWUSR)
            os.chmod(tmp, modo)
        os.replace(tmp, destino)

    def copiar(self, rel: str, origen: Path) -> None:
        self.escribir(rel, origen.read_bytes())

    def borrar(self, rel: str) -> None:
        self.preparar(rel)
        (self.repo / rel).unlink(missing_ok=True)

    def mover(self, desde: str, hacia: str, git: bool = False) -> None:
        """Renombra una carpeta entera (con `git mv` si git la sigue). Se anota antes: deshacer la devuelve a su sitio."""
        self._anotar({"op": "mover", "desde": desde, "hacia": hacia, "git": git})
        _renombrar(self.repo, desde, hacia, git)

    def confirmar(self, **extra: str) -> Path:
        respaldos.escribir_manifiesto(self.carpeta, "actualizacion", self.copiados, self.añadidos, estado="completa", **self.info, **extra)
        self._anotar({"op": "fin"})
        return self.carpeta

    def deshacer(self, motivo: str = "") -> None:
        deshacer_carpeta(self.repo, self.carpeta, motivo)


def _escribible(p: Path) -> None:
    """R-20: permite sustituir/borrar aunque el archivo o su carpeta estén en solo lectura (p. ej. Windows)."""
    if p.exists():
        modo = stat.S_IMODE(p.stat().st_mode)
        if not (modo & stat.S_IWUSR):
            os.chmod(p, modo | stat.S_IWUSR | (stat.S_IXUSR if p.is_dir() else 0))
    padre = p.parent
    if padre.is_dir():
        modo = stat.S_IMODE(padre.stat().st_mode)
        if not (modo & stat.S_IWUSR):
            os.chmod(padre, modo | stat.S_IWUSR | stat.S_IXUSR)


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
        destino = repo / rel
        _escribible(destino)
        destino.unlink(missing_ok=True)
        tmp = destino.with_name(Path(rel).name + ".uxyngraphar-tmp")
        _escribible(tmp)
        tmp.unlink(missing_ok=True)
    for rel in reversed(copiados):
        destino, tmp = repo / rel, (repo / rel).with_name(Path(rel).name + ".uxyngraphar-tmp")
        destino.parent.mkdir(parents=True, exist_ok=True)
        _escribible(destino)
        shutil.copy2(carpeta / rel, tmp)
        os.replace(tmp, destino)
    for e in reversed([e for e in entradas if e.get("op") == "mover"]):   # carpetas movidas: vuelven a su sitio
        if (repo / e["hacia"]).exists() and not (repo / e["desde"]).exists():
            _renombrar(repo, e["hacia"], e["desde"], bool(e.get("git")))
    extra = {k: v for k, v in info.items() if k != "op" and isinstance(v, str)}
    respaldos.escribir_manifiesto(carpeta, "actualizacion", copiados, añadidos, estado="deshecha", motivo=motivo or "actualización interrumpida", **extra)
    with (carpeta / respaldos.DIARIO).open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"op": "deshecha", "motivo": motivo}, ensure_ascii=False) + "\n")
    return copiados + añadidos


def _renombrar(repo: Path, desde: str, hacia: str, git: bool) -> None:
    (repo / hacia).parent.mkdir(parents=True, exist_ok=True)
    if git:
        r = subprocess.run(["git", "mv", "-k", desde, hacia], cwd=repo, capture_output=True, text=True)
        if r.returncode == 0 and (repo / hacia).exists() and not (repo / desde).exists():
            return
    os.replace(repo / desde, repo / hacia)


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
