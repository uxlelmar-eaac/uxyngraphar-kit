#!/usr/bin/env python3
"""Genera los archivos de una release de uxyngraphar (los sube el workflow .github/workflows/publicar.yml).

Uso:  python3 español/_compartido/publicar.py [--salida dist] [--etiqueta vX.Y.Z]
Crea en --salida:
  uxyngraphar-X.Y.Z.zip       el contenido de español/ (sin _compartido/ ni cachés), dentro de «uxyngraphar-X.Y.Z/»
  instalar-uxyngraphar.py     el instalador de una línea: arranque_descarga.py + arranque.py, con la versión fija y solo ASCII
  SHA256SUMS                  huellas de los dos anteriores (el instalador las comprueba antes de instalar)
Falla (2) si las versiones de los packs no coinciden entre sí o con la etiqueta, o si los packs tienen deriva.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import io
import re
import subprocess
import sys
import tokenize
import zipfile
from pathlib import Path

ES = Path(__file__).resolve().parent.parent          # carpeta «español/»
EXCLUIR_DIRS = {"_compartido", "__pycache__", ".decisiones", ".atl", "dist", ".git"}
FECHA_FIJA = (1980, 1, 1, 0, 0, 0)                    # zip reproducible: mismo contenido, misma huella
BLOQUE_REPO = re.compile(r"^# <solo-repositorio>.*?^# </solo-repositorio>[^\n]*\n", re.M | re.S)
VERSION_RE = re.compile(r"^version:\s*(\S+)", re.M)


class ErrorPublicacion(Exception):
    pass


def version_de(carpeta: Path) -> str:
    m = VERSION_RE.search((carpeta / "VERSION.md").read_text(encoding="utf-8"))
    if not m:
        raise ErrorPublicacion(f"{carpeta}/VERSION.md no tiene «version:»")
    return m.group(1)


def comprobar_versiones(etiqueta: str) -> str:
    versiones = {c: version_de(ES / c) for c in ("backend", "frontend", "_compartido/base")}
    if len(set(versiones.values())) != 1:
        raise ErrorPublicacion(f"Las versiones no coinciden: {versiones}")
    version = versiones["backend"]
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        raise ErrorPublicacion(f"Versión no válida en VERSION.md: {version}")
    if etiqueta and etiqueta != f"v{version}":
        raise ErrorPublicacion(f"La etiqueta {etiqueta} no coincide con VERSION.md ({version}). Etiqueta v{version} o corrige VERSION.md.")
    return version


def archivos_publicables() -> list[Path]:
    return sorted(p for p in ES.rglob("*") if p.is_file() and not (set(p.relative_to(ES).parts) & EXCLUIR_DIRS) and p.suffix != ".pyc")


def construir_zip(version: str, destino: Path) -> Path:
    raiz = f"uxyngraphar-{version}/"
    salida = destino / f"uxyngraphar-{version}.zip"
    with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in archivos_publicables():
            info = zipfile.ZipInfo(raiz + p.relative_to(ES).as_posix(), FECHA_FIJA)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, p.read_bytes())
    return salida


def a_ascii(codigo: str) -> str:
    """Escribe los caracteres no ASCII como \\uXXXX. Solo vale dentro de cadenas normales y comentarios."""
    for tok in tokenize.generate_tokens(io.StringIO(codigo).readline):
        if tok.string.isascii():
            continue
        nombre = tokenize.tok_name[tok.type]
        if nombre not in ("STRING", "COMMENT", "FSTRING_MIDDLE"):
            raise ErrorPublicacion(f"línea {tok.start[0]}: carácter no ASCII fuera de una cadena o comentario")
        if nombre == "STRING" and "r" in re.match(r"[rRbBuUfF]*", tok.string).group(0).lower():
            raise ErrorPublicacion(f"línea {tok.start[0]}: cadena r\"...\" con acentos (no se puede escapar)")
    return "".join(c if ord(c) < 128 else (f"\\u{ord(c):04x}" if ord(c) <= 0xFFFF else f"\\U{ord(c):08x}") for c in codigo)


def construir_instalador(version: str, destino: Path) -> Path:
    parte1 = (ES / "instalador" / "arranque_descarga.py").read_text(encoding="utf-8")
    parte2 = (ES / "instalador" / "arranque.py").read_text(encoding="utf-8")
    if parte1.count('VERSION = "__VERSION__"') != 1:
        raise ErrorPublicacion('arranque_descarga.py debe contener exactamente una vez: VERSION = "__VERSION__"')
    if len(BLOQUE_REPO.findall(parte2)) != 1:
        raise ErrorPublicacion("arranque.py debe tener exactamente un bloque <solo-repositorio>")
    codigo = parte1.replace('VERSION = "__VERSION__"', f'VERSION = "{version}"') + "\n\n" + BLOQUE_REPO.sub("", parte2)
    codigo = a_ascii(codigo)
    ast.parse(codigo, feature_version=(3, 6))   # que un Python viejo pueda leerlo y avisar con claridad
    if not codigo.rstrip().endswith("sys.exit(main())"):
        raise ErrorPublicacion("el instalador debe terminar llamando a main() en su última línea")
    salida = destino / "instalar-uxyngraphar.py"
    salida.write_bytes(codigo.encode("ascii"))
    return salida


def sha256(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def publicar(destino: Path, etiqueta: str = "", verificar_packs: bool = True) -> list[Path]:
    version = comprobar_versiones(etiqueta)
    if verificar_packs:
        r = subprocess.run([sys.executable, str(ES / "_compartido" / "construir-packs.py"), "--verificar"], capture_output=True, text=True)
        if r.returncode != 0:
            raise ErrorPublicacion("Los packs tienen deriva respecto a _compartido/base:\n" + r.stdout + r.stderr)
    destino.mkdir(parents=True, exist_ok=True)
    archivos = [construir_zip(version, destino), construir_instalador(version, destino)]
    sumas = destino / "SHA256SUMS"
    sumas.write_text("".join(f"{sha256(a)}  {a.name}\n" for a in archivos), encoding="ascii", newline="\n")
    return archivos + [sumas]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--salida", default="dist")
    ap.add_argument("--etiqueta", default="", help="etiqueta de git (vX.Y.Z); debe coincidir con VERSION.md")
    a = ap.parse_args(argv)
    try:
        for f in publicar(Path(a.salida).resolve(), a.etiqueta):
            print(f"{f}  ({f.stat().st_size} bytes)")
    except ErrorPublicacion as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
