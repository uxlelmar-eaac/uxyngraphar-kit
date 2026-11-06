"""Retira, al migrar, lo que el 1.x instaló fuera de la carpeta del pack: reglas deny, CODEOWNERS, guardia de Cursor,
bloques de exclusión, ganchos git y CLAUDE.md. Todo lo que toca está antes en el respaldo (`extras_a_respaldar`)."""

from __future__ import annotations

import json
import os
import stat
import subprocess
from pathlib import Path

MARCA_GANCHO = "# uxyngraphar-gancho"
CODEOWNERS_INI, CODEOWNERS_FIN = "# >>> uxyngraphar núcleo", "# <<< uxyngraphar núcleo"
EXC_INI, EXC_FIN = "# >>> uxyngraphar: fuera del alcance de la IA", "# <<< uxyngraphar"
EXCLUSIONES = (".cursorignore", ".geminiignore", ".aiexclude")
CURSOR_1X = (".cursor/hooks/uxyngraphar-guardia-nucleo.py", ".cursor/uxyngraphar-protegido.json", ".cursor/rules/uxyngraphar-nucleo.mdc")
HOOKS_JSON = ".cursor/hooks.json"
GUARDIA = "uxyngraphar-guardia-nucleo"
CLAUDE_1X = "Este proyecto usa uxyngraphar. Lee **solo** [AGENTES.md](AGENTES.md)"
CLAUDE_2X = ("# CLAUDE.md\n\nEste proyecto usa paquetes de gobernanza uxyngraphar 2.0. Lee [AGENTES.md](AGENTES.md) al empezar "
             "y sigue su bloque «uxyngraphar»: ningún paquete se aplica si el pedido no lo nombra o `uxyngraphar/FLUJO.json` no lo indica.\n")
DENY_2X = tuple(f"{accion}(uxyngraphar/{ruta})" for ruta in ("paquetes/**", "FLUJO.json", "INDICE.md") for accion in ("Edit", "Write"))


def escribible(ruta: Path) -> None:
    """Quita el congelamiento del 1.x (solo lectura) de un archivo o de un árbol completo."""
    ruta = Path(ruta)
    if not ruta.exists():
        return
    objetivos = [ruta, *ruta.rglob("*")] if ruta.is_dir() else [ruta]
    for p in objetivos:
        if not p.is_symlink():
            os.chmod(p, p.stat().st_mode | stat.S_IWUSR | (stat.S_IXUSR if p.is_dir() else 0))


def dir_ganchos(app: Path) -> Path | None:
    r = subprocess.run(["git", "rev-parse", "--git-path", "hooks"], cwd=app, capture_output=True, text=True)
    if r.returncode != 0:
        return None
    ruta = Path(r.stdout.strip())
    return ruta if ruta.is_absolute() else (app / ruta).resolve()


def ganchos_1x(app: Path) -> list[Path]:
    d = dir_ganchos(app)
    if not d or not d.is_dir():
        return []
    return [p for p in sorted(d.iterdir()) if p.is_file() and not p.name.endswith(".sample")
            and MARCA_GANCHO in p.read_text(encoding="utf-8", errors="replace")]


def extras_a_respaldar(app: Path) -> list[Path]:
    """Archivos fuera del pack que la migración puede modificar o borrar."""
    nombres = ["AGENTES.md", "AGENTS.md", "CLAUDE.md", ".claude/settings.json", ".github/CODEOWNERS", HOOKS_JSON, *CURSOR_1X, *EXCLUSIONES]
    return [app / n for n in nombres if (app / n).is_file()]


def _quitar_bloque(texto: str, inicio: str, fin: str) -> str:
    while inicio in texto and fin in texto.split(inicio, 1)[1]:
        antes, resto = texto.split(inicio, 1)
        despues = resto.split(fin, 1)[1]
        if despues.startswith(" ["):
            despues = despues.split("]", 1)[1]
        texto = antes.rstrip("\n") + ("\n" if antes.strip() else "") + despues.lstrip("\n")
    return texto


def _deny(app: Path, carpeta_rel: str) -> str | None:
    f = app / ".claude" / "settings.json"
    if not f.is_file():
        return None
    cfg = json.loads(f.read_text(encoding="utf-8"))
    deny = cfg.get("permissions", {}).get("deny", [])
    prefijo = f"({carpeta_rel.strip('/')}/"
    filtrado = [r for r in deny if prefijo not in r]
    retiradas = len(deny) - len(filtrado)
    if not retiradas:
        return None
    cfg["permissions"]["deny"] = filtrado + [r for r in DENY_2X if r not in filtrado]
    escribible(f)
    f.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return f".claude/settings.json: {retiradas} reglas del 1.x retiradas; protegidos uxyngraphar/paquetes/**, FLUJO.json e INDICE.md"


def _cursor(app: Path) -> list[str]:
    hechos = []
    for rel in CURSOR_1X:
        if (app / rel).is_file():
            escribible(app / rel)
            (app / rel).unlink()
            hechos.append(f"{rel}: retirado")
    f = app / HOOKS_JSON
    if f.is_file():
        cfg = json.loads(f.read_text(encoding="utf-8"))
        hooks = cfg.get("hooks", {})
        for evento, lista in list(hooks.items()):
            if isinstance(lista, list):
                hooks[evento] = [h for h in lista if GUARDIA not in json.dumps(h)]
                if not hooks[evento]:
                    del hooks[evento]
        escribible(f)
        if hooks:
            f.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        else:
            f.unlink()
        hechos.append(f"{HOOKS_JSON}: guardia del 1.x retirada")
    return hechos


def limpiar(app: Path, carpeta_rel: str) -> list[str]:
    """Aplica la limpieza y devuelve lo hecho (una línea por acción)."""
    hechos = []
    r = _deny(app, carpeta_rel)
    if r:
        hechos.append(r)
    owners = app / ".github" / "CODEOWNERS"
    if owners.is_file() and CODEOWNERS_INI in owners.read_text(encoding="utf-8"):
        escribible(owners)
        nuevo = _quitar_bloque(owners.read_text(encoding="utf-8"), CODEOWNERS_INI, CODEOWNERS_FIN)
        owners.unlink() if not nuevo.strip() else owners.write_text(nuevo, encoding="utf-8")
        hechos.append(".github/CODEOWNERS: bloque del 1.x retirado")
    for nombre in EXCLUSIONES:
        f = app / nombre
        if f.is_file() and EXC_INI in f.read_text(encoding="utf-8"):
            escribible(f)
            nuevo = _quitar_bloque(f.read_text(encoding="utf-8"), EXC_INI, EXC_FIN)
            f.unlink() if not nuevo.strip() else f.write_text(nuevo, encoding="utf-8")
            hechos.append(f"{nombre}: bloque del 1.x retirado")
    hechos += _cursor(app)
    for g in ganchos_1x(app):
        escribible(g)
        g.unlink()
        hechos.append(f"gancho git {g.name}: retirado (2.0 no ejecuta nada sin invocación)")
    claude = app / "CLAUDE.md"
    if claude.is_file() and CLAUDE_1X in claude.read_text(encoding="utf-8"):
        escribible(claude)
        claude.write_text(CLAUDE_2X, encoding="utf-8")
        hechos.append("CLAUDE.md: apunta al bloque 2.0 de AGENTES.md")
    return hechos
