#!/usr/bin/env python3
"""Instala el núcleo de un pack (servidor o cliente) en un proyecto.

Uso:  python3 instalar-pack.py RUTA_PACK --repo RUTA_PROYECTO [--docs docs] [--perfil completo|minimo]
                               [--adoptar] [--dry-run] [--proteger [--propietario @usuario]]
Con --adoptar, si ya existe documentación, nunca se pisa nada: lo distinto queda como «<archivo>.uxyngraphar-nuevo».
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "nucleo"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "control"))

import flujo  # noqa: E402
from uxyngraphar_config import normalizar  # noqa: E402
import lock  # noqa: E402
from analizar import analizar, formatear as formatear_analisis  # noqa: E402
from empaquetar import abrir_pack  # noqa: E402
from instalar import ErrorInstalacion, instalar  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pack", help="carpeta raíz del pack (p. ej. español/backend de un clon de uxyngraphar) o un .zip de empaquetar-pack.py")
    ap.add_argument("--repo", default=".", help="raíz del proyecto (default: carpeta actual)")
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--perfil", choices=("completo", "minimo"), default="completo")
    ap.add_argument("--adoptar", action="store_true", help="el proyecto ya tiene docs/: instalar sin pisar")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--analizar", action="store_true", help="solo informe: dónde encajaría la documentación que el proyecto ya tiene (no escribe nada)")
    ap.add_argument("--claude-md", action="store_true", help="crear CLAUDE.md en la raíz apuntando a AGENTES.md (si no existe)")
    ap.add_argument("--estricto", action="store_true", help="puerta de control con todos los niveles bloqueantes (por defecto: secretos y núcleo bloquean; el resto avisa)")
    ap.add_argument("--sin-git", action="store_true", help="no exigir repositorio git")
    ap.add_argument("--proteger", action="store_true", help="generar reglas deny para agentes (.claude/settings.json), CODEOWNERS y el workflow de CI (.github/workflows/uxyngraphar.yml)")
    ap.add_argument("--propietario", default="@CAMBIAR-PROPIETARIO", help="usuario/equipo de GitHub para CODEOWNERS")
    a = ap.parse_args(argv)
    repo = Path(a.repo).resolve()
    raiz, docs_raiz = normalizar(repo, a.docs)
    if raiz != repo:
        print(f"Aviso: {repo.name} está dentro del repositorio git de «{raiz.name}». Se instalará como app del monorepo, con la documentación en «{docs_raiz}/»\n(git ejecuta los ganchos desde la raíz del repositorio y ahí viven CODEOWNERS y el CI).\n")
        repo, a.docs = raiz, docs_raiz
    if a.analizar:
        print(formatear_analisis(analizar(repo, a.docs)))
        return 0
    try:
        with abrir_pack(Path(a.pack).resolve()) as pack:
            return _instalar(a, pack, repo)
    except (ErrorInstalacion, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


def _instalar(a: argparse.Namespace, pack: Path, repo: Path) -> int:
    if not (pack / "VERSION.md").is_file() or not (pack / "AGENTES.md").is_file():
        print(f"ERROR: {pack} no parece un pack (faltan VERSION.md/AGENTES.md).", file=sys.stderr)
        return 2
    rol = lock.tipo_pack(pack)
    print(f"uxyngraphar {lock.version_de(pack)} (pack {rol}) → {repo}\nLa documentación irá a «{a.docs}/» y AGENTES.md junto a ella.\n")
    if a.dry_run:
        try:
            p = flujo.plan_instalacion(pack, repo, a.docs, a.adoptar, a.perfil)
        except ErrorInstalacion as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        print(f"Simulación: se copiarían {p['nuevos']} archivos nuevos ({p['iguales']} ya idénticos).")
        for c in p["conflictos"]:
            print(f"  ! {c} ya existe y es distinto: se conservaría el tuyo y el de uxyngraphar quedaría como {c}.uxyngraphar-nuevo")
        print("\nNo se escribió nada. Para instalar, ejecuta el mismo comando sin --dry-run.")
        return 0
    r = flujo.instalar_completo(pack, repo, a.docs, adoptar=a.adoptar, proteger=a.proteger, propietario=a.propietario if a.propietario != "@CAMBIAR-PROPIETARIO" else "",
                                estricto=a.estricto, claude_md=a.claude_md, ganchos=False, perfil=a.perfil, fuente=a.pack, exigir_git=not a.sin_git)
    icono = {"ok": "✓", "aviso": "!", "error": "✗"}
    for p in r.pasos:
        print(f" {icono[p.estado]} {p.texto}" + (f"\n     → {p.detalle}" if p.detalle else ""))
    if not r.ok:
        return 2
    val = repo / a.docs / "scripts" / "validar-documentacion.py"
    if val.is_file():
        out = subprocess.run([sys.executable, "-X", "utf8", "-I", str(val), str(repo / a.docs)], capture_output=True, text=True, encoding="utf-8", errors="replace")
        resumen = (out.stdout + out.stderr).strip().splitlines()
        print(" ✓ Comprobación de la documentación: " + (resumen[-1] if resumen else "sin salida"))
    print(f"""
Qué sigue:
  1. Rellena {a.docs}/00-nucleo/configuracion-proyecto.md (nombre, repositorio, rutas de código) y revisa {a.docs}/uxyngraphar.config.json.
  2. Activa la verificación en cada commit:  python3 {a.docs}/scripts/instalar-ganchos.py --docs {a.docs}
  3. Comprueba que todo esté sano:         python3 {a.docs}/scripts/doctor.py --docs {a.docs}
  4. Haz commit de lo nuevo y pide a tu agente su primera tarea: leerá solo AGENTES.md.""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
