#!/usr/bin/env python3
"""Genera los archivos de una release de uxyngraphar (los sube el workflow .github/workflows/publicar.yml).

Uso:  python3 español/motor/distribucion/publicar.py [--salida dist] [--etiqueta vX.Y.Z]
Crea en --salida:
  uxyngraphar-X.Y.Z.zip       el contenido de español/ (motor/ y sistemas-de-gobernanza/_base/, sin motor/pruebas/ ni cachés),
                              dentro de «uxyngraphar-X.Y.Z/», con ARCHIVOS.sha256 (huella de cada archivo). El instalador llega
                              VACÍO: los sistemas de gobernanza no van en el zip; se buscan y se traen del servidor.
  instalar-uxyngraphar.py     el instalador de una línea: arranque_descarga.py + arranque.py, con la versión fija y solo ASCII
  SHA256SUMS                  huellas de los dos anteriores (el instalador las comprueba antes de instalar)
Con --artefactos, además:
  sistemas/<id>-<version>.zip el artefacto de cada sistema del catálogo, listo para subir al servidor
  sistemas/fichas.json        lo que el servidor indexa de cada uno (con su sha256)
Falla (2) si VERSION no coincide con la etiqueta o algún sistema del catálogo no valida.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import io
import re
import sys
import tokenize
import zipfile
from pathlib import Path

ES = Path(__file__).resolve().parents[2]            # carpeta «español/»
MOTOR = ES / "motor"
EXCLUIR_DIRS = {"__pycache__", ".decisiones", ".atl", "dist", ".git", ".mypy_cache", ".ruff_cache", "cobertura-html"}
EXCLUIR_RUTAS = ("motor/pruebas/",)
FECHA_FIJA = (1980, 1, 1, 0, 0, 0)                    # zip reproducible: mismo contenido, misma huella
ARCHIVOS = "ARCHIVOS.sha256"                          # huellas por archivo: el instalador y «reparar» las comprueban
BLOQUE_REPO = re.compile(r"^# <solo-repositorio>.*?^# </solo-repositorio>[^\n]*\n", re.M | re.S)


class ErrorPublicacion(Exception):
    pass


def comprobar_version(etiqueta: str) -> str:
    version = (MOTOR / "VERSION").read_text(encoding="utf-8").strip()
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        raise ErrorPublicacion(f"Versión no válida en VERSION: {version}")
    if etiqueta and etiqueta != f"v{version}":
        raise ErrorPublicacion(f"La etiqueta {etiqueta} no coincide con VERSION ({version}). Etiqueta v{version} o corrige VERSION.")
    if f"## {version}\n" not in (MOTOR / "CHANGELOG.md").read_text(encoding="utf-8"):
        raise ErrorPublicacion(f"CHANGELOG.md no tiene la entrada «## {version}».")
    return version


def comprobar_catalogo() -> None:
    sys.path.insert(0, str(MOTOR))
    import catalogo
    malos = {m["id"]: m["errores"] for m in catalogo.listar() if m["errores"]}
    if malos:
        raise ErrorPublicacion(f"Sistemas del catálogo que no validan: {malos}")


def _sistema_del_catalogo(rel: str) -> bool:
    """sistemas-de-gobernanza/<id>/…: fuentes de los sistemas; se publican en el servidor, no en el instalador."""
    partes = rel.split("/")
    return len(partes) > 2 and partes[0] == "sistemas-de-gobernanza" and partes[1] != "_base"


def archivos_publicables() -> list[Path]:
    return sorted(p for p in ES.rglob("*") if p.is_file() and not (set(p.relative_to(ES).parts) & EXCLUIR_DIRS)
                  and not p.relative_to(ES).as_posix().startswith(EXCLUIR_RUTAS) and p.suffix != ".pyc"
                  and not _sistema_del_catalogo(p.relative_to(ES).as_posix()))


def construir_zip(version: str, destino: Path) -> Path:
    raiz = f"uxyngraphar-{version}/"
    salida = destino / f"uxyngraphar-{version}.zip"
    huellas = []
    with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in archivos_publicables():
            rel = p.relative_to(ES).as_posix()
            datos = p.read_bytes()
            huellas.append(f"{hashlib.sha256(datos).hexdigest()}  {rel}\n")
            info = zipfile.ZipInfo(raiz + rel, FECHA_FIJA)
            info.external_attr = (0o755 if p.suffix == ".py" else 0o644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, datos)
        info = zipfile.ZipInfo(raiz + ARCHIVOS, FECHA_FIJA)
        info.external_attr = 0o644 << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, "".join(huellas).encode("utf-8"))
    return salida


def a_ascii(codigo: str) -> str:
    """Escribe los caracteres no ASCII como \\uXXXX. Solo vale dentro de cadenas normales y comentarios."""
    for tok in tokenize.generate_tokens(io.StringIO(codigo).readline):
        if tok.string.isascii():
            continue
        nombre = tokenize.tok_name[tok.type]
        if nombre not in ("STRING", "COMMENT", "FSTRING_MIDDLE"):
            raise ErrorPublicacion(f"línea {tok.start[0]}: carácter no ASCII fuera de una cadena o comentario")
        prefijo = re.match(r"[rRbBuUfF]*", tok.string)
        if nombre == "STRING" and prefijo is not None and "r" in prefijo.group(0).lower():
            raise ErrorPublicacion(f"línea {tok.start[0]}: cadena r\"...\" con acentos (no se puede escapar)")
    return "".join(c if ord(c) < 128 else (f"\\u{ord(c):04x}" if ord(c) <= 0xFFFF else f"\\U{ord(c):08x}") for c in codigo)


def construir_instalador(version: str, destino: Path) -> Path:
    parte1 = (MOTOR / "distribucion" / "arranque_descarga.py").read_text(encoding="utf-8")
    accesos = (MOTOR / "distribucion" / "accesos.py").read_text(encoding="utf-8")
    parte2 = (MOTOR / "distribucion" / "arranque.py").read_text(encoding="utf-8")
    if parte1.count('VERSION = "__VERSION__"') != 1:
        raise ErrorPublicacion('arranque_descarga.py debe contener exactamente una vez: VERSION = "__VERSION__"')
    for nombre, parte in (("accesos.py", accesos), ("arranque.py", parte2)):
        if len(BLOQUE_REPO.findall(parte)) != 1:
            raise ErrorPublicacion(f"{nombre} debe tener exactamente un bloque <solo-repositorio>")
    codigo = (parte1.replace('VERSION = "__VERSION__"', f'VERSION = "{version}"') + "\n\n" + BLOQUE_REPO.sub("", accesos) + "\n\n"
              + BLOQUE_REPO.sub("", parte2))
    codigo = a_ascii(codigo)
    ast.parse(codigo, feature_version=(3, 6))   # que un Python viejo pueda leerlo y avisar con claridad
    if not codigo.rstrip().endswith("sys.exit(main())"):
        raise ErrorPublicacion("el instalador debe terminar llamando a main() en su última línea")
    salida = destino / "instalar-uxyngraphar.py"
    salida.write_bytes(codigo.encode("ascii"))
    return salida


def sha256(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def construir_artefactos(destino: Path) -> list[Path]:
    """Artefacto zip de cada sistema del catálogo (para subirlos con «uxyngraphar publicar» o desde el panel ROOT)."""
    sys.path.insert(0, str(MOTOR))
    import json

    import artefacto
    import catalogo
    salida = destino / "sistemas"
    salida.mkdir(parents=True, exist_ok=True)
    zips, fichas = [], []
    for m in catalogo.listar():
        z = artefacto.empaquetar(m["id"], salida)
        pid, _ = artefacto.leer(z)
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            fichas.append(artefacto.ficha(artefacto.desempaquetar(z, Path(tmp)), artefacto.sha256_de(z), z.stat().st_size))
        zips.append(z)
    indice = salida / "fichas.json"
    indice.write_text(json.dumps({"formato": 1, "sistemas": fichas}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return zips + [indice]


def publicar(destino: Path, etiqueta: str = "", artefactos: bool = False) -> list[Path]:
    version = comprobar_version(etiqueta)
    comprobar_catalogo()
    destino.mkdir(parents=True, exist_ok=True)
    archivos = [construir_zip(version, destino), construir_instalador(version, destino)]
    sumas = destino / "SHA256SUMS"
    sumas.write_text("".join(f"{sha256(a)}  {a.name}\n" for a in archivos), encoding="ascii", newline="\n")
    return archivos + [sumas] + (construir_artefactos(destino) if artefactos else [])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--salida", default="dist")
    ap.add_argument("--etiqueta", default="", help="etiqueta de git (vX.Y.Z); debe coincidir con VERSION")
    ap.add_argument("--artefactos", action="store_true", help="también el zip de cada sistema en <salida>/sistemas/")
    a = ap.parse_args(argv)
    try:
        for f in publicar(Path(a.salida).resolve(), a.etiqueta, a.artefactos):
            print(f"{f}  ({f.stat().st_size} bytes)")
    except ErrorPublicacion as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
