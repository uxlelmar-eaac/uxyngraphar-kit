"""R-21 — ampliación del alcance de archivos de código. Fuente única de la regla para todo el tooling.

Estándar: 5 archivos de código por instrucción. Si la tarea necesita más, el agente decide primero si la
ampliación es *sumamente necesaria* (¿hay un subconjunto de ≤5 archivos entregable solo, compilando y sin
contratos rotos?):

- **No lo es** → fraccionar en instrucciones de ≤5 (`fraccion_de`, `depende_de`), sin exceder el estándar.
- **Sí lo es** → `ampliacion_factor` 1.5–2 (tope `floor(5 × factor)`: 7–10), `ampliacion_justificacion`
  y aprobación humana explícita (`ampliacion_aprobada_at`) **antes** de tocar código.

Uso desde el tooling:
  problemas(fm)  qué impide **aprobar** la ficha tal cual (validador en 01-pendientes, `decisiones.py apply`)
  bloqueos(fm)   qué impide **ejecutar o cerrar** (problemas + falta de aprobación de la ampliación)
  resumen(fm)    línea para el revisor humano si la ficha pide ampliación ("" si no la pide)
  leer(fm)       datos normalizados (archivos, factor, tope…)
Detalle: docs/00-nucleo/ampliacion-alcance.md
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any

ESTANDAR = 5
FACTOR_MIN = 1.5
FACTOR_MAX = 2.0
RANGO_RE = re.compile(r":\d+(?:-\d+)?$")


@dataclass
class Alcance:
    archivos: list[str] = field(default_factory=list)   # anclas_codigo normalizadas (sin rango, sin duplicados)
    declarado: int | None = None                         # presupuesto_max_archivos_codigo, si es un entero
    factor: float | None = None                          # ampliacion_factor válido (1.5–2); None si no hay o es inválido
    factor_crudo: Any = None                             # valor tal cual, para explicar errores
    justificacion: str = ""
    aprobada_at: str = ""
    fraccion_de: str = ""
    depende_de: list[str] = field(default_factory=list)

    @property
    def requeridos(self) -> int:
        """Archivos de código que la ficha dice necesitar: el mayor entre anclas y presupuesto declarado."""
        return max(len(self.archivos), self.declarado or 0)

    @property
    def maximo(self) -> int:
        """Tope de archivos de código que la ficha puede tocar."""
        return math.floor(ESTANDAR * self.factor) if self.factor is not None else ESTANDAR

    @property
    def pide_ampliacion(self) -> bool:
        return self.factor_crudo not in (None, "", [])


def _texto(v: Any) -> str:
    return "" if v in (None, [], "null") else str(v).strip()


def _lista(v: Any) -> list[str]:
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    return [str(v).strip()] if _texto(v) else []


def _archivo(ancla: str) -> str:
    return RANGO_RE.sub("", ancla.strip().strip("`").replace("\\", "/"))


def leer(fm: dict[str, Any]) -> Alcance:
    a = Alcance()
    a.archivos = list(dict.fromkeys(_archivo(x) for x in _lista(fm.get("anclas_codigo")) if _archivo(x)))
    try:
        a.declarado = int(str(fm.get("presupuesto_max_archivos_codigo")).strip())
    except (TypeError, ValueError):
        a.declarado = None
    a.factor_crudo = fm.get("ampliacion_factor")
    if a.pide_ampliacion:
        try:
            f = float(str(a.factor_crudo).strip())
        except ValueError:
            f = None
        a.factor = f if f is not None and FACTOR_MIN <= f <= FACTOR_MAX else None
    a.justificacion = _texto(fm.get("ampliacion_justificacion"))
    a.aprobada_at = _texto(fm.get("ampliacion_aprobada_at"))
    a.fraccion_de = _texto(fm.get("fraccion_de"))
    a.depende_de = _lista(fm.get("depende_de"))
    return a


def problemas(fm: dict[str, Any]) -> list[str]:
    """Lo que impide aprobar la ficha tal cual (no incluye la falta de aprobación, que es justo lo que se pide)."""
    a = leer(fm)
    sal: list[str] = []
    if a.pide_ampliacion and a.factor is None:
        sal.append(f"ampliacion_factor «{a.factor_crudo}» fuera de {FACTOR_MIN}–{FACTOR_MAX:g} (máximo 2×)")
        return sal
    if a.factor is None:
        if a.requeridos > ESTANDAR:
            sal.append(f"{a.requeridos} archivos de código > estándar {ESTANDAR}: si la ampliación no es sumamente necesaria, "
                       f"fracciona en instrucciones de ≤{ESTANDAR} (fraccion_de, depende_de); si lo es, declara "
                       f"ampliacion_factor {FACTOR_MIN}–{FACTOR_MAX:g} con ampliacion_justificacion")
        if a.fraccion_de and a.requeridos > ESTANDAR:
            sal.append(f"fracción de {a.fraccion_de} con {a.requeridos} archivos: cada fracción respeta el estándar de {ESTANDAR}")
        return sal
    if not a.justificacion:
        sal.append("ampliacion_factor sin ampliacion_justificacion (por qué es sumamente necesaria: qué se rompe al entregar en partes de ≤5)")
    if a.requeridos <= ESTANDAR:
        sal.append(f"ampliacion_factor declarado con {a.requeridos} archivos de código: no hace falta ampliar (estándar {ESTANDAR}); quítalo")
    if a.requeridos > a.maximo:
        sal.append(f"{a.requeridos} archivos de código > tope {a.maximo} ({ESTANDAR} × {a.factor:g}): ni con la ampliación alcanza; "
                   f"fracciona en bloques de ≤{a.maximo}")
    return sal


def bloqueos(fm: dict[str, Any]) -> list[str]:
    """Lo que impide ejecutar o cerrar: problemas + ampliación sin aprobación humana registrada."""
    sal = problemas(fm)
    a = leer(fm)
    if a.factor is not None and not a.aprobada_at:
        sal.append("ampliación de alcance sin aprobación humana (falta ampliacion_aprobada_at): no toques código hasta que se apruebe")
    return sal


def resumen(fm: dict[str, Any]) -> str:
    """Línea para el revisor. Empieza por «R-21 pide» (el escáner la marca con `+`)."""
    a = leer(fm)
    if not a.pide_ampliacion:
        return ""
    tope = f"{ESTANDAR} × {a.factor:g} = tope {a.maximo}" if a.factor is not None else f"factor inválido «{a.factor_crudo}»"
    just = a.justificacion or "SIN JUSTIFICACIÓN"
    return f"R-21 pide ampliar a {a.requeridos} archivos de código ({tope}): {just}"
