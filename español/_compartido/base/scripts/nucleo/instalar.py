"""Instalación del núcleo en un proyecto (nuevo o con `docs/` previo)."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "control"))

import clasificacion as cl  # noqa: E402
import lock  # noqa: E402
import uxyngraphar_config as cfgmod  # noqa: E402

GITIGNORE = (".decisiones/", ".uxyngraphar-respaldo/", "docs/.depuracion/respaldo/", "__pycache__/", "*.pyc",
             ".env", ".env.*", "!.env.example", "*.pem", "*.key", "*.p12", "*.pfx", "id_rsa", "id_ed25519", "credentials.json", "*.tfstate")


class ErrorInstalacion(RuntimeError):
    pass


@dataclass
class Resultado:
    version: str
    nuevos: list[str] = field(default_factory=list)
    iguales: list[str] = field(default_factory=list)
    conflictos: list[str] = field(default_factory=list)


def es_repo(repo: Path) -> bool:
    return subprocess.run(["git", "rev-parse", "--git-dir"], cwd=repo, capture_output=True).returncode == 0


def asegurar_gitignore(repo: Path, docs: str, dry_run: bool) -> list[str]:
    destino = repo / ".gitignore"
    actual = destino.read_text(encoding="utf-8").splitlines() if destino.is_file() else []
    faltan = [l.replace("docs/", docs.strip("/") + "/") for l in GITIGNORE if l.replace("docs/", docs.strip("/") + "/") not in actual]
    if faltan and not dry_run:
        texto = "\n".join(actual + ([""] if actual and actual[-1] else []) + ["# uxyngraphar (artefactos locales)"] + faltan) + "\n"
        destino.write_text(texto, encoding="utf-8", newline="\n")
    return faltan


def lineas_gitattributes(docs: str) -> list[str]:
    """Finales de línea del pack: LF en el repo y en el árbol (el hash del núcleo y los scripts lo exigen)."""
    app = cl.padre(docs)
    pref = f"{app}/" if app else ""
    return [f"{docs.strip('/')}/** text eol=lf", f"{pref}AGENTES.md text eol=lf", f"{pref}AGENTS.md text eol=lf"]


def asegurar_gitattributes(repo: Path, docs: str, dry_run: bool) -> list[str]:
    destino = repo / ".gitattributes"
    actual = destino.read_text(encoding="utf-8").splitlines() if destino.is_file() else []
    faltan = [l for l in lineas_gitattributes(docs) if l not in [x.strip() for x in actual]]
    if faltan and not dry_run:
        texto = "\n".join(actual + ([""] if actual and actual[-1] else []) + ["# uxyngraphar (finales de línea del pack)"] + faltan) + "\n"
        destino.write_text(texto, encoding="utf-8", newline="\n")
    return faltan


def instalar(pack: Path, repo: Path, docs: str = "docs", perfil: str = "completo", adoptar: bool = False,
             dry_run: bool = False, exigir_git: bool = True, fuente: str = "", estricto: bool = False) -> Resultado:
    docs = docs.strip("/")
    if docs.rpartition("/")[2] != "docs":
        raise ErrorInstalacion(f"la carpeta del pack debe llamarse «docs» (p. ej. docs o apps/api/docs); recibido: {docs}")
    if exigir_git and not es_repo(repo):
        raise ErrorInstalacion(f"{repo} no es un repositorio git (usa --sin-git para omitir la comprobación)")
    if lock.leer(repo, docs):
        raise ErrorInstalacion("este proyecto ya tiene un .uxyngraphar.lock: usa actualizar-pack.py")
    if (repo / docs).exists() and any((repo / docs).iterdir()) and not adoptar:
        raise ErrorInstalacion(f"{repo / docs} ya existe y no está vacío: usa --adoptar para instalar sin pisar nada")
    inv = lock.inventario(pack, perfil)
    res = Resultado(lock.version_de(pack))
    for rel, info in inv.items():
        origen, dest = pack / rel, repo / cl.destino(rel, docs)
        if dest.exists():
            if lock.sha(dest) == info["sha256"]:
                res.iguales.append(rel)
                continue
            res.conflictos.append(rel)
            if not dry_run:
                shutil.copyfile(origen, dest.with_name(dest.name + ".uxyngraphar-nuevo"))
            continue
        res.nuevos.append(rel)
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(origen, dest)
    if not dry_run:
        asegurar_gitignore(repo, docs, False)
        asegurar_gitattributes(repo, docs, False)
        app = cl.padre(docs)
        cfg = cfgmod.detectar(repo / app if app else repo, lock.tipo_pack(pack))
        if app:   # varias apps en un repo: el control solo mira el código de esta app
            cfg["codigo"]["raices"] = [f"{app}/{r}" for r in cfg["codigo"]["raices"]] or [app]
        if estricto:
            cfg["niveles"] = {k: "bloqueante" for k in cfg["niveles"]}
        cfgmod.escribir(repo, docs, cfg)
        lock.escribir(repo, docs, {"formato": lock.FORMATO, "pack": lock.tipo_pack(pack), "version": res.version, "perfil": perfil,
                                   "docs": docs, "instalado": date.today().isoformat(), "fuente": lock.etiqueta_fuente(fuente, res.version), "archivos": inv})
    return res
