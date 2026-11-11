"""Barreras pasivas que el motor mantiene en un repo al instalar, actualizar o quitar sistemas.

- Reglas `deny` para agentes en `.claude/settings.json`: los sistemas, FLUJO.json, INDICE.md, los `ajustes.json` del
  trabajo, lo que cada sistema declara en «permisos.rutas.protegidas» y la variable que acredita a una persona.
- Exclusiones de IA (`.cursorignore` y, si existen, `.geminiignore` y `.aiexclude`) para lo que cada sistema declara en
  «permisos.rutas.fuera_de_ia».

No ejecutan nada: solo impiden que un agente escriba o lea lo que es de la persona. Las reglas propias del proyecto se
respetan; las de uxyngraphar se reescriben cada vez.
"""

from __future__ import annotations

import json
from pathlib import Path

import especificacion as esp

base = esp.base
CLAUDE = ".claude/settings.json"
EXC_INI, EXC_FIN = "# >>> uxyngraphar (sistemas): fuera del alcance de la IA", "# <<< uxyngraphar (sistemas)"
EXCLUSIONES = (".cursorignore", ".geminiignore", ".aiexclude")
SIEMPRE = (".cursorignore",)
FIJAS = ("sistemas-de-gobernanza/**", "FLUJO.json", "INDICE.md", "trabajo/*/ajustes.json")
BASH = (f"Bash({base.VARIABLE_HUMANO}=1:*)", f"Bash(export {base.VARIABLE_HUMANO}:*)")
# Freno parcial a escrituras por la shell en lo que es de la persona: las reglas Bash de Claude Code comparan el prefijo
# del comando, así que solo paran las formas más directas (no `cd uxyngraphar && rm -rf sistemas`).
# Solo órdenes en las que la ruta va justo detrás (en `chmod MODO ruta` o `sed -i EXPR ruta` el prefijo nunca coincide).
_RUTAS_SHELL = ("sistemas-de-gobernanza", "FLUJO.json", "INDICE.md")
BASH_ESCRITURA = tuple(f"Bash({orden} {base.CARPETA_RAIZ}/{ruta}:*)"
                       for ruta in _RUTAS_SHELL for orden in ("rm", "rm -r", "rm -rf", "mv", "tee", "truncate -s 0"))


def _conocidas(manifiestos: list[dict]) -> set[str]:
    """Toda regla que el motor puede haber escrito: las fijas y las de cualquier sistema del catálogo o instalado. Las demás son de la persona y no se tocan, aunque mencionen uxyngraphar/."""
    try:
        import catalogo
        todos = [m for _, m in catalogo._sistemas(None).values()]
    except (OSError, ValueError, ImportError):
        todos = []
    rutas = [f"{base.CARPETA_RAIZ}/{r}" for r in FIJAS]
    for m in [*manifiestos, *todos]:
        propias = [*base.rutas_permiso(m, "protegidas"), *base.rutas_permiso(m, "fuera_de_ia")]
        rutas += [f"{base.CARPETA_TRABAJO}/{m['id']}/{r}" for r in propias]
    return {f"{accion}({r})" for r in rutas for accion in ("Edit", "Write", "Read")} | set(BASH) | set(BASH_ESCRITURA)


def _propia(regla: str, conocidas: set[str] | None = None) -> bool:
    """La regla es del motor (se reescribe) y no de la persona (se conserva)."""
    return regla in (conocidas if conocidas is not None else _conocidas([])) or base.VARIABLE_HUMANO in regla


def reglas_deny(manifiestos: list[dict]) -> list[str]:
    if not manifiestos:
        return []
    rutas = [f"{base.CARPETA_RAIZ}/{r}" for r in FIJAS]
    for m in manifiestos:
        rutas += [f"{base.CARPETA_TRABAJO}/{m['id']}/{r}" for r in base.rutas_permiso(m, "protegidas")]
    lectura = [f"Read({r})" for r in rutas_fuera_de_ia(manifiestos)]   # lo que el sistema deja fuera de la IA (M-15)
    return [f"{accion}({r})" for r in rutas for accion in ("Edit", "Write")] + lectura + list(BASH) + list(BASH_ESCRITURA)


def rutas_fuera_de_ia(manifiestos: list[dict]) -> list[str]:
    return [f"{base.CARPETA_TRABAJO}/{m['id']}/{r}" for m in manifiestos for r in base.rutas_permiso(m, "fuera_de_ia")]


class AjustesClaudeInvalidos(ValueError):
    """.claude/settings.json no es JSON válido o no tiene la forma esperada."""


def leer_ajustes_claude(ruta: Path) -> dict:
    """`.claude/settings.json` como dict. Es de la persona: si no es JSON válido (o no es un objeto) no se toca y se
    dice dónde está el problema."""
    texto = Path(ruta).read_text(encoding="utf-8")
    if not texto.strip():
        return {}
    try:
        cfg = json.loads(texto)
    except ValueError as e:
        linea = getattr(e, "lineno", "?")
        raise AjustesClaudeInvalidos(f"{CLAUDE} no es JSON válido (línea {linea}): corrígelo o bórralo; uxyngraphar no lo toca") from None
    if not isinstance(cfg, dict) or not isinstance(cfg.get("permissions", {}), dict) \
            or not isinstance(cfg.get("permissions", {}).get("deny", []), list):
        raise AjustesClaudeInvalidos(f"{CLAUDE}: debe ser un objeto JSON con «permissions.deny» como lista; corrígelo o bórralo")
    return cfg


def _deny(raiz_app: Path, reglas: list[str], manifiestos: list[dict] | None = None) -> str | None:
    ruta = raiz_app / CLAUDE
    if not ruta.is_file() and not reglas:
        return None
    cfg = leer_ajustes_claude(ruta) if ruta.is_file() else {}
    permisos = cfg.setdefault("permissions", {})
    actuales = permisos.get("deny", [])
    conocidas = _conocidas(manifiestos or [])
    nuevas = [r for r in actuales if not _propia(r, conocidas)] + reglas
    if nuevas == actuales:
        return None
    permisos["deny"] = nuevas
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return f"{CLAUDE}: {len(reglas)} reglas deny de uxyngraphar"


def _sin_bloque(texto: str) -> str:
    if EXC_INI not in texto or EXC_FIN not in texto:
        return texto
    antes, _, resto = texto.partition(EXC_INI)
    despues = resto.partition(EXC_FIN)[2]
    return antes.rstrip("\n") + ("\n" if antes.strip() else "") + despues.lstrip("\n")


def _exclusiones(raiz_app: Path, rutas: list[str]) -> list[str]:
    hechos = []
    for nombre in EXCLUSIONES:
        ruta = raiz_app / nombre
        if not ruta.is_file() and not (rutas and nombre in SIEMPRE):
            continue
        actual = ruta.read_text(encoding="utf-8") if ruta.is_file() else ""
        nuevo = _sin_bloque(actual)
        if rutas:
            nuevo = nuevo + ("\n" if nuevo and not nuevo.endswith("\n") else "") + "\n".join([EXC_INI, *rutas, EXC_FIN]) + "\n"
        if nuevo == actual:
            continue
        if nuevo.strip():
            ruta.write_text(nuevo, encoding="utf-8")
        else:
            ruta.unlink()
        hechos.append(f"{nombre}: {len(rutas)} rutas fuera del alcance de la IA")
    return hechos


def aplicar(raiz_app: Path, manifiestos: list[dict], anteriores: list[dict] | None = None) -> list[str]:
    """Deja las barreras de acuerdo con los sistemas instalados; devuelve lo que cambió. `anteriores`: manifiestos de
    sistemas que estaban instalados (quitados o en su versión previa), para reconocer las reglas que escribieron."""
    raiz_app = Path(raiz_app)
    hechos = [h for h in [_deny(raiz_app, reglas_deny(manifiestos), [*manifiestos, *(anteriores or [])])] if h]
    return hechos + _exclusiones(raiz_app, rutas_fuera_de_ia(manifiestos))
