"""Puerta de control de construcción: hace cumplir en cada cambio cómo se construye sobre la aplicación.

Controles (cada uno bloqueante | aviso | apagado, configurable en uxyngraphar.config.json):
  lineas       archivos de código tocados que superan limite_lineas (R-19), salvo exenciones.
  instruccion  todo código tocado cubierto por una instrucción activa (anclas_codigo) (R-03).
  secretos     archivos de llaves/.env y credenciales en las líneas añadidas, también en docs (R-12).
  nucleo       integridad del núcleo del pack (R-20), delegando en verificar-nucleo.
  espejo       espejo_actualizar de las instrucciones tocadas realmente cambiado.
  idioma       artefactos del producto en inglés y ASCII (R-22); lo heurístico solo avisa (control/idioma.py).
  commits      Conventional Commits en inglés y nombre de rama (R-22); se revisan en commit-msg y en CI.
  memoria      la memoria del sistema solo cambia con memoria.py: nada editado, borrado ni añadido a mano (R-24).
  reglas_proyecto  reglas del proyecto (96-reglas-proyecto/): comprobaciones, excepciones aprobadas y cambios de reglas.
"""

from __future__ import annotations

import fnmatch
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

_AQUI = Path(__file__).resolve().parent
for p in (_AQUI.parent / "espejo", _AQUI.parent / "nucleo", _AQUI.parent / "decisiones"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import idioma  # noqa: E402
import reglas_control  # noqa: E402
import secretos as sec  # noqa: E402
from verificar_espejo import analizar, instrucciones_del_cambio  # noqa: E402

@dataclass
class Hallazgo:
    control: str
    nivel: str      # bloqueante | aviso
    mensaje: str


def _coincide(ruta: str, patrones: list[str]) -> bool:
    nombre = Path(ruta).name
    return any(fnmatch.fnmatch(ruta, p) or fnmatch.fnmatch(nombre, p) or (p.endswith("/**") and f"/{p[:-3]}/" in f"/{ruta}") for p in patrones)


def es_codigo(ruta: str, cfg: dict, docs: str) -> bool:
    """Código del producto = bajo `docs/` no, no excluido, con extensión de la pila (o cualquiera si no se detectó pila)."""
    if ruta.startswith(docs + "/") or ruta.startswith(".github/") or ruta.startswith(".claude/"):
        return False
    c = cfg["codigo"]
    if _coincide(ruta, c["excluir"]) or idioma.coincide(ruta, cfg.get("idioma", {}).get("locales", [])):   # traducciones: no son código
        return False
    if c["extensiones"] and Path(ruta).suffix not in c["extensiones"]:
        return False
    if c["raices"] and not any(ruta.startswith(r.rstrip("/") + "/") for r in c["raices"]):
        return False
    return bool(c["extensiones"]) or Path(ruta).suffix in {".py", ".js", ".ts", ".go", ".rs", ".java", ".kt", ".cs", ".php", ".rb", ".dart", ".vue", ".tsx", ".jsx"}


def control_lineas(repo: Path, codigo: list[str], cfg: dict) -> list[Hallazgo]:
    limite, nivel = cfg["limite_lineas"], cfg["niveles"]["lineas"]
    salida = []
    for ruta in codigo:
        if _coincide(ruta, cfg["exenciones_lineas"]):
            continue
        f = repo / ruta
        try:
            n = sum(1 for _ in f.open("rb"))
        except OSError:
            continue
        if n > limite:
            salida.append(Hallazgo("lineas", nivel, f"{ruta}: {n} líneas (> {limite}, R-19). Divide el módulo o añádelo a exenciones_lineas con motivo en una decisión."))
    return salida


def lineas_anadidas(repo: Path, base: str | None, staged: bool) -> dict[str, list[str]]:
    args = ["diff", "--cached", "-U0", "--no-color", "--diff-filter=ACMR"] if staged else ["diff", f"{base}...HEAD", "-U0", "--no-color", "--diff-filter=ACMR"]
    r = subprocess.run(["git", "-c", "core.quotePath=false", *args], cwd=repo, capture_output=True)   # rutas con acentos sin escapar
    if r.returncode != 0 and not staged:
        r = subprocess.run(["git", "-c", "core.quotePath=false", "diff", base or "HEAD", "-U0", "--no-color", "--diff-filter=ACMR"], cwd=repo, capture_output=True)
    por_archivo: dict[str, list[str]] = {}
    actual = None
    for linea in r.stdout.decode("utf-8", "replace").splitlines():
        if linea.startswith("+++ b/"):
            actual = linea[6:]
        elif linea.startswith("+") and not linea.startswith("+++") and actual:
            por_archivo.setdefault(actual, []).append(linea[1:])
    return por_archivo


def control_secretos(anadidas: dict[str, list[str]], cambiados: list[str], cfg: dict) -> list[Hallazgo]:
    """Todo el diff (también docs y .md, R-12): nombres de archivo prohibidos + credenciales en líneas añadidas."""
    nivel, salida = cfg["niveles"]["secretos"], []
    for ruta in cambiados:
        if sec.archivo_prohibido(ruta):
            salida.append(Hallazgo("secretos", nivel, f"{ruta}: archivo de credenciales/llaves no debe versionarse. Quítalo del índice (git rm --cached), añádelo a .gitignore y rota lo que contenga."))
    for ruta, lineas in anadidas.items():
        if _coincide(ruta, cfg.get("secretos_permitir", [])):
            continue
        for h in sec.escanear_texto(ruta, "\n".join(lineas)):
            salida.append(Hallazgo("secretos", nivel, f"{ruta}: posible {h.tipo} ({h.muestra}) en una línea añadida. Usa un placeholder <NOMBRE> o variable de entorno; si ya salió, rota la credencial."))
    return salida


def control_nucleo(repo: Path, docs: str, cfg: dict) -> list[Hallazgo]:
    script = repo / docs / "scripts" / "verificar-nucleo.py"
    if not script.is_file() or not (repo / docs / ".uxyngraphar.lock").is_file():
        return []
    r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(script), "--docs", docs], cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode == 0:
        return []
    primera = next((l for l in (r.stdout + r.stderr).splitlines() if l.strip()), "núcleo alterado")
    return [Hallazgo("nucleo", cfg["niveles"]["nucleo"], f"Núcleo alterado (R-20): {primera[:160]}. Restaura con actualizar-pack.py --restaurar-nucleo; mejoras solo vía 46-evolucion-documentacion.")]


def control_memoria(repo: Path, cambiados: list[str], docs: str, cfg: dict) -> list[Hallazgo]:
    """R-24: si el cambio toca 95-memoria/, el catálogo y las huellas deben cuadrar (solo memoria.py la cambia)."""
    script = repo / docs / "scripts" / "memoria.py"
    if not script.is_file() or not any(c.startswith(f"{docs}/95-memoria/") for c in cambiados):
        return []
    r = subprocess.run([sys.executable, "-X", "utf8", "-I", str(script), "--repo", str(repo), "--docs", docs, "verificar"], cwd=repo, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode == 0:
        return []
    nivel = cfg["niveles"].get("memoria", "bloqueante")
    return [Hallazgo("memoria", nivel, f"Memoria del sistema alterada fuera de memoria.py (R-24): {l.strip()}") for l in r.stdout.splitlines() if l.strip()][:10]


def control_config(cambiados: list[str], docs: str, cfg: dict) -> list[Hallazgo]:
    """La configuración fija los niveles de la puerta: tocarla puede relajarla, así que se señala siempre para revisión humana."""
    if f"{docs}/uxyngraphar.config.json" not in cambiados:
        return []
    return [Hallazgo("config", "aviso", f"{docs}/uxyngraphar.config.json cambió: puede relajar niveles, exenciones o secretos_permitir. Debe aprobarlo el propietario (CODEOWNERS); un agente no edita este archivo.")]


def control_commits(textos: list[str], rama: str, cfg: dict) -> list[Hallazgo]:
    """R-22: asuntos de commit (Conventional Commits en inglés) y nombre de rama."""
    nivel = cfg["niveles"].get("commits", "aviso")
    if nivel == "apagado":
        return []
    msgs = [] if cfg.get("idioma", {}).get("commits") == "libre" else [m for t in textos for m in idioma.revisar_mensaje(t)]
    return [Hallazgo("commits", nivel, f"{m} (R-22)") for m in msgs + idioma.revisar_rama(rama, cfg)]


def evaluar(repo: Path, cambiados: list[str], anadidas: dict[str, list[str]], cfg: dict, docs: str, nuevos: list[str] | None = None) -> list[Hallazgo]:
    n = cfg["niveles"]
    codigo = [c for c in cambiados if es_codigo(c, cfg, docs)]
    h: list[Hallazgo] = []
    if n["lineas"] != "apagado":
        h += control_lineas(repo, codigo, cfg)
    if n["secretos"] != "apagado":
        h += control_secretos(anadidas, cambiados, cfg)
    if n["nucleo"] != "apagado":
        h += control_nucleo(repo, docs, cfg)
        h += control_config(cambiados, docs, cfg)
    if n.get("memoria", "bloqueante") != "apagado":
        h += control_memoria(repo, cambiados, docs, cfg)
    if n.get("idioma", "aviso") != "apagado":
        h += [Hallazgo("idioma", nv, m) for nv, m in idioma.control_idioma(repo, cambiados, nuevos or [], anadidas, cfg, docs, lambda r: es_codigo(r, cfg, docs))]
    h += [Hallazgo("reglas_proyecto", nv, m) for nv, m in reglas_control.evaluar(repo, cambiados, cfg, docs, lambda r: es_codigo(r, cfg, docs))]
    if codigo and (n["instruccion"] != "apagado" or n["espejo"] != "apagado"):
        instr = instrucciones_del_cambio(repo, cambiados, docs)
        relevantes = codigo + [c for c in cambiados if c.startswith(docs + "/")]
        for x in analizar(relevantes, instr, docs):
            clave = "espejo" if x.regla == "espejo" else "instruccion"
            if n[clave] != "apagado":
                h.append(Hallazgo(clave, n[clave], x.mensaje))
    return h
