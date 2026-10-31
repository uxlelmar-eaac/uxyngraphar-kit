"""Costo en tokens de cada instrucción, por fases (análisis · instrucción · implementación · verificación · cierre).

Cómo se mide (de mejor a peor):
  medido    Lee las transcripciones de Claude Code (~/.claude/projects/**.jsonl, o $CLAUDE_CONFIG_DIR/projects, o --transcripciones)
            y suma el `usage` real de cada respuesta del agente cuyo `cwd` está dentro del repo, repartido por fases según las marcas.
  manual    Lo que se registra a mano con `costo-tokens.py registrar` (otras herramientas que muestran su consumo).
  estimado  Si no hay nada de lo anterior: ~4 caracteres/token de la ficha y del paquete de contexto (solo lectura; no incluye razonamiento).
Marcas: `<docs>/.decisiones/tokens/<id>.json` (fuera de git). Cada marca abre una fase que dura hasta la siguiente; se puede volver
a una fase (p. ej. verificación → implementación) y se suman todos sus tramos. Sin marca de análisis, el análisis va desde el inicio
de la sesión (o desde el cierre de la instrucción anterior) hasta la primera marca.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from estimar import tokens as estimar_tokens

FASES = ("analisis", "instruccion", "implementacion", "verificacion", "cierre")
NOMBRES = {"analisis": "Análisis", "instruccion": "Creación de la instrucción", "implementacion": "Implementación",
           "verificacion": "Verificación", "cierre": "Cierre (docs y espejo)"}
CAMPOS = ("entrada", "cache_lectura", "cache_escritura", "salida")
USAGE = {"entrada": "input_tokens", "cache_lectura": "cache_read_input_tokens", "cache_escritura": "cache_creation_input_tokens", "salida": "output_tokens"}
INI, FIN = "<!-- tokens:inicio -->", "<!-- tokens:fin -->"
DATOS_RE = re.compile(r"<!-- tokens:datos (\{.*?\}) -->", re.S)


def ahora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _ts(texto: str) -> datetime:
    return datetime.fromisoformat(texto.replace("Z", "+00:00"))


# ---------- marcas ----------

def ruta_marcas(docs: Path, ident: str) -> Path:
    return docs / ".decisiones" / "tokens" / f"{re.sub(r'[^A-Za-z0-9._-]', '_', ident)}.json"


def leer_marcas(docs: Path, ident: str) -> dict:
    f = ruta_marcas(docs, ident)
    if f.is_file():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            pass
    return {"id": ident, "marcas": [], "manual": [], "fin": None}


def _guardar(docs: Path, ident: str, datos: dict) -> None:
    f = ruta_marcas(docs, ident)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(datos, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def marcar(docs: Path, ident: str, fase: str, cuando: str | None = None, solo_si_falta: bool = False) -> bool:
    if fase not in FASES:
        raise ValueError(f"fase desconocida «{fase}»; use: {', '.join(FASES)}")
    datos = leer_marcas(docs, ident)
    if solo_si_falta and any(m["fase"] == fase for m in datos["marcas"]):
        return False
    datos["marcas"].append({"fase": fase, "desde": cuando or ahora()})
    _guardar(docs, ident, datos)
    return True


def registrar(docs: Path, ident: str, fase: str, **valores: int) -> None:
    if fase not in FASES:
        raise ValueError(f"fase desconocida «{fase}»; use: {', '.join(FASES)}")
    datos = leer_marcas(docs, ident)
    datos["manual"].append({"fase": fase, **{c: int(valores.get(c, 0) or 0) for c in CAMPOS}})
    _guardar(docs, ident, datos)


def terminar(docs: Path, ident: str, cuando: str | None = None) -> None:
    datos = leer_marcas(docs, ident)
    datos["fin"] = cuando or ahora()
    _guardar(docs, ident, datos)


def _cierres_previos(docs: Path, ident: str, antes_de: datetime) -> datetime | None:
    """Último cierre de OTRA instrucción anterior a `antes_de` (límite inferior del análisis)."""
    previos = []
    for f in (docs / ".decisiones" / "tokens").glob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if d.get("id") != ident and d.get("fin") and _ts(d["fin"]) < antes_de:
            previos.append(_ts(d["fin"]))
    return max(previos) if previos else None


# ---------- transcripciones ----------

def carpetas_transcripciones(extra: str | None = None) -> list[Path]:
    if extra:
        return [Path(extra).expanduser()]
    if os.environ.get("UXYNGRAPHAR_TRANSCRIPCIONES"):
        return [Path(os.environ["UXYNGRAPHAR_TRANSCRIPCIONES"]).expanduser()]
    base = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude")).expanduser()
    return [base / "projects"]


def registros(repo: Path, carpetas: list[Path]) -> list[dict]:
    """Respuestas del agente con su consumo, dentro del repo. Deduplicadas por id de mensaje (se queda el máximo de cada campo)."""
    raiz = str(repo.resolve())
    vistos: dict[str, dict] = {}
    for carpeta in carpetas:
        if not carpeta.is_dir():
            continue
        for f in carpeta.rglob("*.jsonl"):
            try:
                lineas = f.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for linea in lineas:
                if '"usage"' not in linea:
                    continue
                try:
                    e = json.loads(linea)
                except ValueError:
                    continue
                msg = e.get("message") or {}
                uso, cwd = msg.get("usage"), str(e.get("cwd") or "")
                if e.get("type") != "assistant" or not uso or not e.get("timestamp") or not (cwd == raiz or cwd.startswith(raiz + os.sep)):
                    continue
                clave = msg.get("id") or e.get("uuid") or f"{f}:{e['timestamp']}"
                r = vistos.setdefault(clave, {"ts": _ts(e["timestamp"]), "sesion": e.get("sessionId", ""), **{c: 0 for c in CAMPOS}})
                for c in CAMPOS:
                    r[c] = max(r[c], int(uso.get(USAGE[c]) or 0))
    return sorted(vistos.values(), key=lambda r: r["ts"])


# ---------- medición ----------

def _vacio() -> dict[str, dict[str, int]]:
    return {f: {c: 0 for c in CAMPOS} for f in FASES}


def medir(repo: Path, docs: Path, ident: str, ficha: Path | None = None, transcripciones: str | None = None) -> dict:
    datos = leer_marcas(docs, ident)
    marcas = sorted(({"fase": m["fase"], "desde": _ts(m["desde"])} for m in datos["marcas"]), key=lambda m: m["desde"])
    fin = _ts(datos["fin"]) if datos.get("fin") else datetime.now(timezone.utc)
    fases, fuentes, sesiones = _vacio(), [], set()
    if marcas:
        todos = registros(repo, carpetas_transcripciones(transcripciones))
        primera = marcas[0]["desde"]
        if marcas[0]["fase"] != "analisis":
            ses = next((r["sesion"] for r in todos if r["ts"] >= primera), None)
            inicio = min((r["ts"] for r in todos if r["sesion"] == ses), default=primera)
            corte = _cierres_previos(docs, ident, primera)
            marcas.insert(0, {"fase": "analisis", "desde": max(inicio, corte) if corte else inicio})
        for r in todos:
            if not (marcas[0]["desde"] <= r["ts"] <= fin):
                continue
            fase = [m for m in marcas if m["desde"] <= r["ts"]][-1]["fase"]
            sesiones.add(r["sesion"])
            for c in CAMPOS:
                fases[fase][c] += r[c]
        if sesiones:
            fuentes.append(f"medido en {len(sesiones)} sesión(es) de Claude Code")
    for m in datos["manual"]:
        for c in CAMPOS:
            fases[m["fase"]][c] += int(m.get(c, 0))
    if datos["manual"]:
        fuentes.append(f"{len(datos['manual'])} registro(s) manual(es)")
    if not fuentes and ficha is not None and ficha.is_file():
        fases["instruccion"]["salida"] = estimar_tokens(ficha.read_text(encoding="utf-8", errors="replace"))
        try:
            from paquete import construir
            fases["implementacion"]["entrada"] = construir(docs, ficha, 10**9, repo).total
        except Exception:  # noqa: BLE001 - la estimación es orientativa
            pass
        fuentes.append("estimado (~4 caracteres/token; solo ficha y contexto leído, sin razonamiento ni salida real)")
    return {"id": ident, "fases": fases, "fuente": " + ".join(fuentes) or "sin datos", "medido": ahora()}


def total(f: dict[str, int]) -> int:
    return sum(f[c] for c in CAMPOS)


def _n(x: int) -> str:
    return f"{x:,}".replace(",", " ") if x else "—"


def render(m: dict) -> str:
    gran = sum(total(v) for v in m["fases"].values())
    filas = ["| Fase | Entrada | Caché leída | Caché escrita | Salida | Total | % |", "|------|--------:|--------:|--------:|------:|------:|--:|"]
    for f in FASES:
        v = m["fases"][f]
        filas.append(f"| {NOMBRES[f]} | {_n(v['entrada'])} | {_n(v['cache_lectura'])} | {_n(v['cache_escritura'])} | {_n(v['salida'])} | "
                     f"{_n(total(v))} | {round(100 * total(v) / gran) if gran else 0}% |")
    suma = {c: sum(v[c] for v in m["fases"].values()) for c in CAMPOS}
    filas.append(f"| **Total** | **{_n(suma['entrada'])}** | **{_n(suma['cache_lectura'])}** | **{_n(suma['cache_escritura'])}** | "
                 f"**{_n(suma['salida'])}** | **{_n(gran)}** | 100% |")
    nuevos = gran - suma["cache_lectura"]
    datos = json.dumps({"id": m["id"], "fases": m["fases"], "fuente": m["fuente"], "medido": m["medido"]}, ensure_ascii=False, separators=(",", ":"))
    return "\n".join([INI, *filas, "",
                      f"Tokens nuevos (sin caché leída): **{_n(nuevos)}** · Fuente: {m['fuente']} · Medido: {m['medido']}",
                      f"<!-- tokens:datos {datos} -->", FIN])


SECCION = "## Costo en tokens"


def escribir(ficha: Path, m: dict) -> None:
    texto = ficha.read_text(encoding="utf-8")
    bloque = render(m)
    if INI in texto and FIN in texto:
        texto = re.sub(re.escape(INI) + r".*?" + re.escape(FIN), lambda _x: bloque, texto, count=1, flags=re.S)
    else:
        nuevo = f"{SECCION}\n\n{bloque}\n"
        pos = texto.find("\n## Anexo — Checklist")
        texto = (texto[:pos] + "\n" + nuevo + texto[pos:]) if pos >= 0 else texto.rstrip("\n") + "\n\n" + nuevo
    ficha.write_text(texto, encoding="utf-8", newline="\n")


def leer_datos(ficha: Path) -> dict | None:
    m = DATOS_RE.search(ficha.read_text(encoding="utf-8", errors="replace"))
    try:
        return json.loads(m.group(1)) if m else None
    except ValueError:
        return None
