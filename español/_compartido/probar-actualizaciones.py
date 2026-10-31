#!/usr/bin/env python3
"""Prueba que un proyecto instalado con cada versión publicada se actualiza a la actual sin romperse.

Uso:  python3 español/_compartido/probar-actualizaciones.py [--desde vX.Y.Z …] [--ultimas N] [--git RUTA]
Por defecto prueba las etiquetas vX.Y.Z del repositorio anteriores a la versión actual (las --ultimas N, 10 por defecto).
Por cada versión y cada pack (servidor y cliente):
  1. instala esa versión, con su propio instalador, en un proyecto git nuevo, y le añade contenido propio;
  2. lo actualiza con la versión actual (actualizar.py --si), como haría una persona;
  3. comprueba que termina bien, que el lock queda en la versión actual, que el contenido del proyecto no cambió ni un
     byte, que las herramientas arrancan (contrato), que un commit pasa los ganchos y que actualizar otra vez no cambia nada.
Lo ejecuta el CI antes de publicar (.github/workflows/publicar.yml): una versión que rompa una actualización no se publica.
Salida: 0 todo bien · 1 algún salto falla · 2 error de uso.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ES = Path(__file__).resolve().parent.parent              # carpeta «español/» de la versión actual
sys.path.insert(0, str(ES / "backend" / "scripts" / "nucleo"))

import contrato  # noqa: E402
import lock  # noqa: E402

PACKS = {"servidor": ("go.mod", "module example.com/app\n"), "cliente": ("package.json", '{"name": "app", "dependencies": {"react": "18.3.1"}}\n')}
ETIQUETA = re.compile(r"^v(\d+\.\d+\.\d+)$")
ENTORNO = {**os.environ, "GIT_AUTHOR_NAME": "prueba", "GIT_AUTHOR_EMAIL": "prueba@example.com", "GIT_COMMITTER_NAME": "prueba",
           "GIT_COMMITTER_EMAIL": "prueba@example.com", "PYTHONIOENCODING": "utf-8", "UXYNGRAPHAR_SIN_PATH": "1"}
# Contenido propio del proyecto (no es del pack): tras actualizar debe seguir idéntico.
PROPIO = {
    "src/app.py": "def main() -> None:\n    print('hello')\n",
    "docs/25-areas/pagos/CONTEXTO.md": "# Pagos\n\nContexto propio del proyecto.\n",
}


def correr(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENTORNO,
                          stdin=subprocess.DEVNULL, timeout=600)


def huellas(raiz: Path, rutas: list[str]) -> dict[str, str]:
    return {r: hashlib.sha256((raiz / r).read_bytes()).hexdigest() if (raiz / r).is_file() else "falta" for r in rutas}


def foto_docs(proyecto: Path) -> dict[str, str]:
    return {p.relative_to(proyecto).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((proyecto / "docs").rglob("*")) if p.is_file() and "__pycache__" not in p.parts}


def extraer(git: Path, ref: str, destino: Path) -> Path:
    r = subprocess.run(["git", "archive", "--format=tar", ref, "español"], cwd=git, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git archive {ref}: {r.stderr.decode(errors='replace').strip()}")
    with tarfile.open(fileobj=io.BytesIO(r.stdout)) as t:
        t.extractall(destino, filter="data") if sys.version_info >= (3, 12) else t.extractall(destino)  # noqa: S202 - repo propio
    return destino / "español"


def preparar_proyecto(carpeta: Path, rol: str) -> None:
    carpeta.mkdir(parents=True)
    correr(["git", "init", "-q"], carpeta)
    marcador, texto = PACKS[rol]
    (carpeta / marcador).write_text(texto, encoding="utf-8")


def anadir_contenido(proyecto: Path) -> list[str]:
    for rel, texto in PROPIO.items():
        (proyecto / rel).parent.mkdir(parents=True, exist_ok=True)
        (proyecto / rel).write_text(texto, encoding="utf-8")
    plantilla = proyecto / "docs/00-nucleo/configuracion-proyecto.md"
    plantilla.write_text(plantilla.read_text(encoding="utf-8") + "\n- Nota propia del equipo.\n", encoding="utf-8")
    cfg = proyecto / "docs/uxyngraphar.config.json"
    datos = json.loads(cfg.read_text(encoding="utf-8"))
    datos["limite_lineas"] = 300
    cfg.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    correr(["git", "add", "-A"], proyecto)
    correr(["git", "commit", "-q", "--no-verify", "-m", "chore: initial project"], proyecto)
    return [*PROPIO, "docs/00-nucleo/configuracion-proyecto.md", "docs/uxyngraphar.config.json"]


def probar_salto(vieja: Path, version: str, rol: str, tmp: Path) -> list[str]:
    """Fallos de actualizar de `vieja` a la actual para un pack (vacío = bien)."""
    proyecto = tmp / f"{version}-{rol}"
    preparar_proyecto(proyecto, rol)
    r = correr([sys.executable, str(vieja / "instalar.py"), "--consola", "--proyecto", str(proyecto), "--pack", rol, "--si"], tmp)
    if r.returncode != 0 or not (proyecto / "docs" / lock.LOCK_NOMBRE).is_file():
        return [f"no se pudo instalar {version} con su instalador: {(r.stdout + r.stderr).strip()[-400:]}"]
    propios = anadir_contenido(proyecto)
    antes = huellas(proyecto, propios)
    fallos: list[str] = []
    r = correr([sys.executable, str(ES / "actualizar.py"), str(proyecto), "--si"], tmp)
    salida = r.stdout + r.stderr
    if r.returncode != 0 or "Traceback" in salida:
        return [f"actualizar terminó con {r.returncode}: {salida.strip()[-600:]}"]
    actual = lock.version_de(ES / "backend")
    if (lock.leer(proyecto, "docs") or {}).get("version") != actual:
        fallos.append(f"el lock no quedó en {actual}")
    cambiados = [k for k, v in huellas(proyecto, propios).items() if v != antes[k]]
    if cambiados:
        fallos.append(f"se tocó contenido del proyecto: {', '.join(cambiados)}")
    nuevos = sorted(p.relative_to(proyecto).as_posix() for p in proyecto.rglob("*.uxyngraphar-nuevo"))
    if nuevos:
        fallos.append(f"conflictos sin haber editado el núcleo: {', '.join(nuevos)}")
    fallos += [f"herramienta rota: {f}" for f in contrato.probar(proyecto, "docs")]
    r = correr([sys.executable, "docs/scripts/verificar-nucleo.py", "--docs", "docs"], proyecto)
    if r.returncode != 0:
        fallos.append(f"verificar-nucleo falla tras actualizar: {(r.stdout + r.stderr).strip()[-300:]}")
    (proyecto / "src/app.py").write_text(PROPIO["src/app.py"] + "\n\nmain()\n", encoding="utf-8")
    correr(["git", "add", "-A"], proyecto)
    r = correr(["git", "commit", "-q", "-m", "chore: update app"], proyecto)
    if r.returncode != 0:
        fallos.append(f"un commit normal no pasa los ganchos tras actualizar: {(r.stdout + r.stderr).strip()[-400:]}")
    foto = foto_docs(proyecto)
    r = correr([sys.executable, str(ES / "actualizar.py"), str(proyecto), "--si"], tmp)
    if r.returncode != 0 or foto_docs(proyecto) != foto:
        fallos.append("actualizar por segunda vez cambió algo (debería estar al día)")
    return fallos


def etiquetas(git: Path, actual: str) -> list[str]:
    r = subprocess.run(["git", "tag", "-l", "v*"], cwd=git, capture_output=True, text=True)
    validas = [t for t in r.stdout.split() if ETIQUETA.match(t) and lock._tupla(t[1:]) < lock._tupla(actual)]
    return sorted(validas, key=lambda t: lock._tupla(t[1:]), reverse=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--desde", nargs="*", default=None, help="etiquetas o commits a probar (por defecto: las etiquetas vX.Y.Z anteriores)")
    ap.add_argument("--ultimas", type=int, default=10, help="cuántas etiquetas anteriores probar como máximo")
    ap.add_argument("--git", default=str(ES.parent), help="repositorio del que se leen las versiones anteriores")
    a = ap.parse_args(argv)
    actual = lock.version_de(ES / "backend")
    refs = a.desde if a.desde is not None else etiquetas(Path(a.git), actual)[: a.ultimas]
    if not refs:
        print(f"No hay versiones anteriores a {actual} publicadas: nada que probar todavía.")
        return 0
    errores = 0
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        for ref in refs:
            try:
                vieja = extraer(Path(a.git), ref, tmp / f"fuente-{ref}")
            except RuntimeError as exc:
                print(f"✗ {ref}: {exc}")
                errores += 1
                continue
            version = lock.version_de(vieja / "backend")
            for rol in PACKS:
                fallos = probar_salto(vieja, version, rol, tmp)
                errores += bool(fallos)
                print(f"{'✗' if fallos else '✓'} {ref} ({version}) → {actual} · {rol}")
                for f in fallos:
                    print(f"    {f}")
    print(f"\n{len(refs) * len(PACKS) - errores} de {len(refs) * len(PACKS)} actualizaciones probadas sin problemas.")
    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main())
