"""Reglas del ciclo compartidas por ciclo.py y verificar-ciclo.py: anclas, alcance, fechas y pregunta citada."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

RANGO = re.compile(r"^(.*?):(\d+)(?:-(\d+))?$")
STATUS = re.compile(r"^status:\s*(\S+)", re.MULTILINE)
PREGUNTAS = "preguntas-de-clarificacion"
EXT_CODIGO = {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".vue", ".svelte", ".go", ".rs", ".java", ".kt", ".rb",
              ".php", ".cs", ".swift", ".dart", ".c", ".cc", ".cpp", ".h", ".hpp", ".css", ".scss", ".sql", ".sh"}


def ahora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def lista(valor) -> list[str]:
    if valor is None:
        return []
    return [str(x) for x in valor] if isinstance(valor, list) else [str(valor)]


def separar_ancla(ancla: str) -> tuple[str, int | None, int | None]:
    texto = ancla.strip().strip("`")
    m = RANGO.match(texto)
    if not m:
        return texto, None, None
    inicio = int(m.group(2))
    return m.group(1), inicio, int(m.group(3) or inicio)


def archivos_codigo(fm: dict) -> list[str]:
    rutas = {separar_ancla(a)[0] for a in lista(fm.get("anclas_codigo"))}
    return sorted(r for r in rutas if Path(r).suffix.lower() in EXT_CODIGO)


def problemas_alcance(fm: dict, ajustes: dict) -> list[str]:
    """Incumplimientos de alcance (vacío = dentro de lo permitido)."""
    maximo = int(ajustes.get("max_archivos_codigo", 5))
    tope_factor = float(ajustes.get("ampliacion_factor_max", 2.0))
    codigo = archivos_codigo(fm)
    problemas = []
    factor = fm.get("ampliacion_factor")
    if factor not in (None, "", "null"):
        try:
            factor = float(factor)
        except ValueError:
            return [f"ampliacion_factor no numérico: {factor}"]
        if not 1.5 <= factor <= tope_factor:
            problemas.append(f"ampliacion_factor {factor} fuera de 1.5–{tope_factor}")
        if not str(fm.get("ampliacion_justificacion") or "").strip() or fm.get("ampliacion_justificacion") == "null":
            problemas.append("ampliacion_factor sin ampliacion_justificacion")
        maximo = int(maximo * factor)
    if len(codigo) > maximo:
        problemas.append(f"{len(codigo)} archivos de código en anclas (máximo {maximo}); fracciona o justifica una ampliación")
    docs = lista(fm.get("lectura_minima"))
    if len(docs) > int(ajustes.get("max_docs", 8)):
        problemas.append(f"{len(docs)} documentos en lectura_minima (máximo {ajustes.get('max_docs', 8)})")
    return problemas


def aviso_pregunta(trabajo_preguntas: Path, pid) -> str | None:
    """Aviso sobre la pregunta citada en `preguntas_id`; None si todo cuadra o si el trabajo de PREGUNTAS no existe."""
    if pid in (None, "", "null") or not trabajo_preguntas.is_dir():
        return None
    halladas = sorted(trabajo_preguntas.rglob(f"{pid}.md"))
    if not halladas:
        return f"preguntas_id {pid} no está en {PREGUNTAS}"
    m = STATUS.search(halladas[0].read_text(encoding="utf-8"))
    if m and m.group(1) == "en-curso":
        return f"preguntas_id {pid} sigue en-curso en {PREGUNTAS}: ciérrala al enlazarla"
    return None
