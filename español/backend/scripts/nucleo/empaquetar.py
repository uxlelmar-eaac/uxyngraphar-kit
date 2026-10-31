"""Empaquetado (release) de un pack en un .zip con manifiesto y apertura transparente de packs .zip."""

from __future__ import annotations

import json
import tempfile
import zipfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import lock

MANIFIESTO = "uxyngraphar-manifiesto.json"


def empaquetar(pack: Path, salida: Path) -> Path:
    inv = lock.inventario(pack)   # solo N, P y M: nunca contenido de proyectos
    manifiesto = {"formato": 1, "pack": lock.tipo_pack(pack), "version": lock.version_de(pack), "archivos": inv}
    destino = salida / f"uxyngraphar-{manifiesto['pack']}-{manifiesto['version']}.zip"
    salida.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in inv:
            z.write(pack / rel, rel)
        z.writestr(MANIFIESTO, json.dumps(manifiesto, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    return destino


@contextmanager
def abrir_pack(ruta: Path) -> Iterator[Path]:
    """Carpeta de pack utilizable: la misma ruta, o un .zip extraído a un directorio temporal (verificando el manifiesto)."""
    if ruta.is_dir():
        yield ruta
        return
    if not zipfile.is_zipfile(ruta):
        raise ValueError(f"{ruta} no es una carpeta de pack ni un .zip")
    with tempfile.TemporaryDirectory() as tmp, zipfile.ZipFile(ruta) as z:
        base = Path(tmp).resolve()
        for nombre in z.namelist():
            if not (base / nombre).resolve().is_relative_to(base):
                raise ValueError(f"entrada insegura en el zip: {nombre}")
        z.extractall(base)
        man = base / MANIFIESTO
        if not man.is_file():
            raise ValueError("el .zip no trae manifiesto de uxyngraphar")
        for rel, info in json.loads(man.read_text(encoding="utf-8"))["archivos"].items():
            if not (base / rel).is_file() or lock.sha(base / rel) != info["sha256"]:
                raise ValueError(f"el .zip está dañado o alterado: {rel}")
        yield base
