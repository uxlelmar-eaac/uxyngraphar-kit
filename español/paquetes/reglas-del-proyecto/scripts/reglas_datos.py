"""Datos de reglas, excepciones y ajustes locales; compartido por reglas.py y verificar-reglas.py."""

from __future__ import annotations

import fnmatch
import os
import re
import subprocess
from datetime import date
from pathlib import Path

import uxyn_base as base
import uxyn_fichas as fichas

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)
NIVELES = ("bloqueante", "aviso")
VACIO = (None, "", "null")


def raiz() -> Path:
    return base.raiz_app(PAQUETE)


def lista(valor) -> list[str]:
    if isinstance(valor, list):
        return [str(x).strip() for x in valor if str(x).strip()]
    return [] if valor in VACIO else [str(valor).strip()]


def coincide(ruta: str, globs: list[str]) -> bool:
    """`src/**/*.ts` también cubre `src/a.ts` (el `**` puede ser vacío)."""
    ruta = ruta.replace("\\", "/")
    return any(fnmatch.fnmatch(ruta, g) or fnmatch.fnmatch(ruta, g.replace("/**/", "/")) for g in globs)


def ruta_de_ancla(ancla: str) -> str:
    """`src/a.ts:40-80` → `src/a.ts`."""
    ruta, _, rango = ancla.rpartition(":")
    return ruta if ruta and rango.replace("-", "").isdigit() else ancla


def fichas_de(tipo: str) -> list[tuple[fichas.Ficha, dict, str]]:
    salida = []
    for f in fichas.listar(PAQUETE, tipo):
        fm, cuerpo = base.leer_frontmatter(f.ruta.read_text(encoding="utf-8"))
        salida.append((f, fm, cuerpo))
    return salida


def problemas_regla(fm: dict) -> list[str]:
    problemas = []
    if fm.get("nivel") not in NIVELES:
        problemas.append(f"nivel «{fm.get('nivel')}»: {' | '.join(NIVELES)}")
    if not lista(fm.get("aplica_a")):
        problemas.append("aplica_a vacío: lista de globs de código (p. ej. src/**/*.ts)")
    if fm.get("resumen") in VACIO:
        problemas.append("falta resumen (una línea)")
    for clave in ("comprobacion_prohibido", "comprobacion_obligatorio"):
        if fm.get(clave) not in VACIO:
            try:
                re.compile(str(fm[clave]))
            except re.error as e:
                problemas.append(f"{clave}: regex inválida ({e})")
    return problemas


def activas() -> list[tuple[fichas.Ficha, dict, str]]:
    return [(f, fm, c) for f, fm, c in fichas_de("regla") if f.status == "activa" and not problemas_regla(fm)]


def para_rutas(rutas: list[str]) -> list[tuple[fichas.Ficha, dict, str]]:
    rutas = [ruta_de_ancla(r) for r in rutas]
    return [(f, fm, c) for f, fm, c in activas() if any(coincide(r, lista(fm.get("aplica_a"))) for r in rutas)]


def excepciones_aprobadas(hoy: date | None = None) -> list[tuple[str, list[str]]]:
    """(regla, globs de archivos) de las excepciones aprobadas y vigentes."""
    hoy = hoy or date.today()
    salida = []
    for f, fm, _ in fichas_de("excepcion"):
        hasta = fm.get("hasta")
        if f.status != "aprobada" or (hasta not in VACIO and str(hasta) < hoy.isoformat()):
            continue
        salida.append((str(fm.get("regla", "")), lista(fm.get("archivos"))))
    return salida


def excusado(regla: str, rel: str, excepciones: list[tuple[str, list[str]]]) -> bool:
    return any(r == regla and (not globs or coincide(rel, globs)) for r, globs in excepciones)


def _git(*args: str) -> list[str]:
    r = subprocess.run(["git", *args], cwd=raiz(), capture_output=True, text=True)
    return [x for x in r.stdout.splitlines() if x.strip()] if r.returncode == 0 else []


def archivos(rutas: list[str] | None = None, git: bool = False) -> list[str]:
    """Archivos a comprobar, relativos a la raíz de la app."""
    ajustes = base.leer_ajustes(PAQUETE)
    excluir = set(ajustes.get("excluir", []))
    if git:
        rutas = sorted(set(_git("diff", "--name-only", "HEAD") + _git("diff", "--name-only", "--cached")
                           + _git("ls-files", "--others", "--exclude-standard")))
    candidatos: list[Path] = []
    for r in rutas or ajustes.get("raices", ["."]):
        p = raiz() / r
        if p.is_file():
            candidatos.append(p)
        for actual, dirs, nombres in os.walk(p) if p.is_dir() else []:
            dirs[:] = [d for d in dirs if d not in excluir]
            candidatos += [Path(actual) / n for n in nombres]
    salida = []
    for p in candidatos:
        rel = p.relative_to(raiz()).as_posix()
        if p.is_file() and not set(Path(rel).parts) & excluir and p.stat().st_size <= int(ajustes.get("max_kb", 512)) * 1024:
            salida.append(rel)
    return sorted(set(salida))


def incumplimiento(fm: dict, texto: str) -> str:
    prohibido, obligatorio = fm.get("comprobacion_prohibido"), fm.get("comprobacion_obligatorio")
    if prohibido not in VACIO:
        for n, linea in enumerate(texto.splitlines(), 1):
            if re.search(str(prohibido), linea):
                return f"línea {n} contiene lo prohibido ({prohibido})"
    if obligatorio not in VACIO and not re.search(str(obligatorio), texto, re.M):
        return f"falta lo obligatorio ({obligatorio})"
    return ""


def comprobar(rutas: list[str] | None = None, git: bool = False) -> list[dict]:
    """Incumplimientos de las reglas activas con comprobación: {regla, nivel, archivo, motivo, excusado}."""
    reglas = [(f, fm) for f, fm, _ in activas()
              if fm.get("comprobacion_prohibido") not in VACIO or fm.get("comprobacion_obligatorio") not in VACIO]
    if not reglas:
        return []
    excepciones = excepciones_aprobadas()
    salida = []
    for rel in archivos(rutas, git):
        aplicables = [(f, fm) for f, fm in reglas if coincide(rel, lista(fm.get("aplica_a")))]
        if not aplicables:
            continue
        try:
            texto = (raiz() / rel).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for f, fm in aplicables:
            motivo = incumplimiento(fm, texto)
            if motivo:
                salida.append({"regla": f.id, "nivel": fm.get("nivel"), "archivo": rel, "motivo": motivo,
                               "excusado": excusado(f.id, rel, excepciones)})
    return salida


def objetivo_ajuste(fm: dict) -> Path:
    return raiz() / base.CARPETA_PAQUETES / str(fm.get("paquete")) / str(fm.get("aplica_a") or base.ENTRADA)


def estado_ajuste(fm: dict) -> str:
    """«vigente», «por revisar» (el archivo del paquete cambió) o «sin paquete»."""
    objetivo = objetivo_ajuste(fm)
    if not objetivo.is_file():
        return "sin paquete"
    return "vigente" if fm.get("huella") == base.sha256(objetivo) else "por revisar"
