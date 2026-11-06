"""Barreras pasivas que el motor mantiene en un repo al instalar, actualizar o quitar paquetes.

- Reglas `deny` para agentes en `.claude/settings.json`: los paquetes, FLUJO.json, INDICE.md, los `ajustes.json` del
  trabajo, lo que cada paquete declara en «protegidos» y la variable que acredita a una persona.
- Exclusiones de IA (`.cursorignore` y, si existen, `.geminiignore` y `.aiexclude`) para lo que cada paquete declara en
  «fuera_de_ia».

No ejecutan nada: solo impiden que un agente escriba o lea lo que es de la persona. Las reglas propias del proyecto se
respetan; las de uxyngraphar se reescriben cada vez.
"""

from __future__ import annotations

import json
from pathlib import Path

import especificacion as esp

base = esp.base
CLAUDE = ".claude/settings.json"
EXC_INI, EXC_FIN = "# >>> uxyngraphar 2.0: fuera del alcance de la IA", "# <<< uxyngraphar 2.0"
EXCLUSIONES = (".cursorignore", ".geminiignore", ".aiexclude")
SIEMPRE = (".cursorignore",)
FIJAS = ("paquetes/**", "FLUJO.json", "INDICE.md", "trabajo/*/ajustes.json")
BASH = (f"Bash({base.VARIABLE_HUMANO}=1:*)", f"Bash(export {base.VARIABLE_HUMANO}:*)")


def _propia(regla: str) -> bool:
    return f"({base.CARPETA_RAIZ}/" in regla or base.VARIABLE_HUMANO in regla


def reglas_deny(manifiestos: list[dict]) -> list[str]:
    if not manifiestos:
        return []
    rutas = [f"{base.CARPETA_RAIZ}/{r}" for r in FIJAS]
    for m in manifiestos:
        rutas += [f"{base.CARPETA_TRABAJO}/{m['id']}/{r}" for r in m.get("protegidos", [])]
    return [f"{accion}({r})" for r in rutas for accion in ("Edit", "Write")] + list(BASH)


def rutas_fuera_de_ia(manifiestos: list[dict]) -> list[str]:
    return [f"{base.CARPETA_TRABAJO}/{m['id']}/{r}" for m in manifiestos for r in m.get("fuera_de_ia", [])]


def _deny(raiz_app: Path, reglas: list[str]) -> str | None:
    ruta = raiz_app / CLAUDE
    if not ruta.is_file() and not reglas:
        return None
    cfg = json.loads(ruta.read_text(encoding="utf-8")) if ruta.is_file() else {}
    permisos = cfg.setdefault("permissions", {})
    actuales = permisos.get("deny", [])
    nuevas = [r for r in actuales if not _propia(r)] + reglas
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


def aplicar(raiz_app: Path, manifiestos: list[dict]) -> list[str]:
    """Deja las barreras de acuerdo con los paquetes instalados; devuelve lo que cambió."""
    raiz_app = Path(raiz_app)
    hechos = [h for h in [_deny(raiz_app, reglas_deny(manifiestos))] if h]
    return hechos + _exclusiones(raiz_app, rutas_fuera_de_ia(manifiestos))
