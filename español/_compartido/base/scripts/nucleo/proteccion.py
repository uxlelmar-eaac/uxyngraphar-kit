"""Genera la protección del núcleo para agentes y revisores: deny, Cursor fail-closed, FS solo lectura y CODEOWNERS."""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

import clasificacion as cl
import lock

MARCA_INI, MARCA_FIN = "# >>> uxyngraphar núcleo", "# <<< uxyngraphar núcleo"
# Carpetas 100 % núcleo: se protegen enteras (también impide crear archivos nuevos dentro).
CARPETAS_PURAS = ("10-guias", "55-automatizaciones", "scripts")
# Mecanismos de protección: editarlos equivale a desactivar la protección.
EXTRAS_CURSOR = (
    ".cursor/hooks.json",
    ".cursor/hooks/uxyngraphar-guardia-nucleo.py",
    ".cursor/uxyngraphar-protegido.json",
    ".cursor/rules/uxyngraphar-nucleo.mdc",
)
EXTRAS = (".claude/settings.json", ".github/CODEOWNERS", ".github/workflows/**", ".git/hooks/**", *EXTRAS_CURSOR)

MANIFIESTO_REL = ".cursor/uxyngraphar-protegido.json"
GUARDIA_REL = ".cursor/hooks/uxyngraphar-guardia-nucleo.py"
HOOKS_JSON_REL = ".cursor/hooks.json"
REGLA_MDC_REL = ".cursor/rules/uxyngraphar-nucleo.mdc"
GUARDIA_CMD = ".cursor/hooks/uxyngraphar-guardia-nucleo.py"

# Credenciales (R-12): un agente no lee ni escribe estos archivos; `.env.example` queda libre.
SECRETOS_RUTAS = (".env", ".env.local", ".env.production", ".env.development", ".env.staging", ".env.test", "**/.env", "**/.env.*.local",
                  "**/*.pem", "**/*.key", "**/*.p12", "**/*.pfx", "**/id_rsa", "**/id_ed25519", "**/credentials.json", "**/*.tfstate",
                  "**/.npmrc", "**/.netrc", "~/.ssh/**", "~/.aws/**", "~/.config/gcloud/**", "~/.kube/**")

_MSG_DENY = ("Núcleo de uxyngraphar inviolable (R-20): no se edita en el proyecto. "
             "Mejora → ficha EVO-* en 46-evolucion-documentacion/. Actualizar → panel o actualizar-pack.py.")


def rutas_protegidas(repo: Path, docs: str) -> list[str]:
    datos = lock.leer(repo, docs) or {"archivos": {}}
    docs = docs.strip("/")
    salida = {f"{docs}/{c}/**" for c in CARPETAS_PURAS} | set(EXTRAS) | {f"{docs.strip('/')}/{lock.LOCK_NOMBRE}", f"{docs.strip('/')}/uxyngraphar.config.json"}
    for rel, info in datos["archivos"].items():
        if info["clase"] == "N" and not rel.startswith(tuple(c + "/" for c in CARPETAS_PURAS)):
            salida.add(cl.destino(rel, docs))
    return sorted(salida)


def rutas_respaldo(docs: str) -> list[str]:
    """Copias de seguridad (10-guias/respaldos.md): el agente no las lee ni las toca; restaurar o borrar es humano."""
    return [".uxyngraphar-respaldo/**", f"{docs.strip('/')}/.depuracion/respaldo/**"]   # la de actualización vive en la raíz del repo git


def rutas_reglas_solo_humano(repo: Path, docs: str) -> list[str]:
    """Reglas del proyecto con `cambios_reglas: solo_humano`: el agente no las crea, edita ni borra (las lee igual)."""
    try:
        import uxyngraphar_config as cfgmod
        modo = (cfgmod.cargar(repo, docs.strip("/"))[0].get("reglas_proyecto") or {}).get("cambios_reglas")
    except Exception:  # noqa: BLE001 - sin configuración legible se aplica el modo por defecto
        modo = ""
    return [f"{docs.strip('/')}/96-reglas-proyecto/**"] if modo == "solo_humano" else []


def rutas_memoria(docs: str) -> list[str]:
    """Memoria del sistema (R-24): el agente no la lee ni la toca; solo el humano, con memoria.py."""
    return [f"{docs.strip('/')}/95-memoria/**"]


# Otros agentes y editores con IA: cada uno lee su propio archivo de exclusión en la raíz del repo.
EXCLUSIONES = (".cursorignore", ".geminiignore", ".aiexclude")
EXC_INI, EXC_FIN = "# >>> uxyngraphar: fuera del alcance de la IA", "# <<< uxyngraphar"


def exclusiones_agentes(repo: Path, docs: str) -> list[str]:
    """Escribe (o pone al día) el bloque de uxyngraphar en cada archivo de exclusión. Devuelve los que cambiaron."""
    rutas = [r.replace("/**", "/") for r in (*rutas_memoria(docs), *rutas_respaldo(docs))] + [".env", "**/.env", "*.pem", "*.key"]
    cambiados = []
    for nombre in EXCLUSIONES:
        f = repo / nombre
        actual = f.read_text(encoding="utf-8") if f.is_file() else ""
        bloque = "\n".join([EXC_INI, *rutas, EXC_FIN])
        if EXC_INI in actual and EXC_FIN in actual:
            antes, resto = actual.split(EXC_INI, 1)
            otras = sorted({l for l in resto.split(EXC_FIN, 1)[0].splitlines() if l.strip()} - set(rutas))
            bloque = "\n".join([EXC_INI, *rutas, *otras, EXC_FIN])   # conserva rutas de otros packs del mismo repo
            nuevo = antes + bloque + resto.split(EXC_FIN, 1)[1]
        else:
            nuevo = (actual.rstrip("\n") + "\n\n" if actual.strip() else "") + bloque + "\n"
        if nuevo != actual:
            f.write_text(nuevo, encoding="utf-8", newline="\n")
            cambiados.append(nombre)
    return cambiados


def reglas_agente(repo: Path, docs: str) -> Path:
    """Fusiona reglas `deny` (Edit/Write/NotebookEdit) en .claude/settings.json sin tocar lo demás."""
    descongelar_mecanismos(repo)
    f = repo / ".claude" / "settings.json"
    cfg = json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {}
    deny = cfg.setdefault("permissions", {}).setdefault("deny", [])
    for ruta in (*rutas_protegidas(repo, docs), *rutas_reglas_solo_humano(repo, docs)):
        for herramienta in ("Edit", "Write"):
            regla = f"{herramienta}({ruta})"
            if regla not in deny:
                deny.append(regla)
    for ruta in (*SECRETOS_RUTAS, *rutas_respaldo(docs), *rutas_memoria(docs)):
        for herramienta in ("Read", "Edit", "Write"):
            regla = f"{herramienta}({ruta})"
            if regla not in deny:
                deny.append(regla)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return f


def marcas_codeowners(docs: str) -> tuple[str, str]:
    """El pack en la raíz del repo usa las marcas simples; el de una app del monorepo las lleva con su ruta."""
    d = docs.strip("/")
    return (MARCA_INI, MARCA_FIN) if "/" not in d else (f"{MARCA_INI} [{d}]", f"{MARCA_FIN} [{d}]")


def propietario_actual(repo: Path, docs: str) -> str:
    """Propietario ya escrito en el bloque de este pack en CODEOWNERS ("" si no hay bloque)."""
    f = repo / ".github" / "CODEOWNERS"
    texto = f.read_text(encoding="utf-8") if f.is_file() else ""
    ini = marcas_codeowners(docs)[0]
    if ini not in texto:
        return ""
    for linea in texto.split(ini, 1)[1].splitlines()[1:]:
        partes = linea.split()
        if len(partes) >= 2 and not linea.startswith("#"):
            return partes[-1]
    return ""


def codeowners(repo: Path, docs: str, propietario: str) -> Path:
    descongelar_mecanismos(repo)
    f = repo / ".github" / "CODEOWNERS"
    actual = f.read_text(encoding="utf-8") if f.is_file() else ""
    ini, fin = marcas_codeowners(docs)
    if ini in actual and fin in actual:   # sustituye solo el bloque de este pack (puede haber varios packs en el repo)
        antes, resto = actual.split(ini, 1)
        despues = resto.split(fin, 1)[1].lstrip("\n")
        actual = (antes.rstrip("\n") + "\n" if antes.strip() else "") + despues
        actual = actual.rstrip("\n") + ("\n" if actual.strip() else "")
    rutas = [*rutas_protegidas(repo, docs), *rutas_memoria(docs)]
    lineas = [ini] + [f"/{r.replace('/**', '/')} {propietario}" for r in rutas if not r.startswith(".git/")] + [fin]
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text((actual + "\n" if actual else "") + "\n".join(lineas) + "\n", encoding="utf-8", newline="\n")
    return f


def rutas_congelar_fs(repo: Path, docs: str) -> list[Path]:
    """Archivos clase N (+ lock) que se marcan solo lectura en disco."""
    docs = docs.strip("/")
    datos = lock.leer(repo, docs) or {"archivos": {}}
    salidos: list[Path] = []
    vistos: set[Path] = set()
    for rel, info in datos["archivos"].items():
        if info.get("clase") != "N":
            continue
        p = repo / cl.destino(rel, docs)
        if p.is_file() and p not in vistos:
            vistos.add(p)
            salidos.append(p)
    lk = lock.ruta_lock(repo, docs)
    if lk.is_file() and lk not in vistos:
        salidos.append(lk)
    return salidos


def rutas_dirs_congelar(repo: Path, docs: str) -> list[Path]:
    """Carpetas del núcleo: sin bit de escritura no se pueden crear ni borrar entradas (R-20 ampliación)."""
    docs = docs.strip("/")
    dirs = [repo / docs / c for c in (*CARPETAS_PURAS, "00-nucleo")]
    return [d for d in dirs if d.is_dir()]


def rutas_mecanismos(repo: Path) -> list[Path]:
    """Artefactos de protección: congelarlos evita que alguien los desactive a mano en el IDE."""
    rels = (*EXTRAS_CURSOR, ".claude/settings.json", ".github/CODEOWNERS")
    return [repo / r for r in rels if (repo / r).is_file()]


def _sin_escritura(p: Path) -> bool:
    """Quita bits de escritura; en directorios conserva ejecución para poder atravesarlos."""
    modo = stat.S_IMODE(p.stat().st_mode)
    nuevo = modo & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
    if p.is_dir():
        nuevo |= stat.S_IXUSR | stat.S_IRUSR
    if nuevo != modo:
        os.chmod(p, nuevo)
        return True
    return False


def _con_escritura(p: Path) -> bool:
    modo = stat.S_IMODE(p.stat().st_mode)
    if modo & stat.S_IWUSR:
        return False
    extra = stat.S_IWUSR
    if p.is_dir():
        extra |= stat.S_IXUSR
    os.chmod(p, modo | extra)
    return True


def _dirs_mecanismos(repo: Path) -> list[Path]:
    return [d for d in (repo / ".cursor", repo / ".cursor" / "hooks", repo / ".cursor" / "rules", repo / ".claude") if d.is_dir()]


def congelar_fs(repo: Path, docs: str) -> int:
    """Congela núcleo (archivos N + carpetas puras/00-nucleo) y archivos-mecanismo. Devuelve cuántos tocó.

    No congela los directorios `.cursor`/`.claude` enteros: las herramientas oficiales crean temporales ahí.
    """
    n = 0
    for p in (*rutas_congelar_fs(repo, docs), *rutas_dirs_congelar(repo, docs), *rutas_mecanismos(repo)):
        if _sin_escritura(p):
            n += 1
    return n


def descongelar_fs(repo: Path, docs: str) -> int:
    """Devuelve escritura al dueño (actualizar-pack, doctor --fix, mover)."""
    n = 0
    for p in (*_dirs_mecanismos(repo), *rutas_dirs_congelar(repo, docs), *rutas_congelar_fs(repo, docs), *rutas_mecanismos(repo)):
        if _con_escritura(p):
            n += 1
    return n


def descongelar_mecanismos(repo: Path) -> int:
    """Solo mecanismos (hooks/deny/CODEOWNERS) para regenerarlos sin tocar el resto del núcleo."""
    n = 0
    for p in rutas_mecanismos(repo):
        if _con_escritura(p):
            n += 1
    # Directorio .cursor/hooks debe aceptar reescritura del script
    for d in (repo / ".cursor", repo / ".cursor" / "hooks", repo / ".cursor" / "rules", repo / ".claude", repo / ".github"):
        if d.is_dir() and _con_escritura(d):
            n += 1
    return n


def archivos_n_escribibles(repo: Path, docs: str) -> list[str]:
    """Rutas relativas del núcleo/mecanismos que aún son escribibles (el doctor marca ERROR)."""
    mal: list[str] = []
    for p in (*rutas_congelar_fs(repo, docs), *rutas_dirs_congelar(repo, docs), *rutas_mecanismos(repo)):
        if stat.S_IMODE(p.stat().st_mode) & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH):
            mal.append(p.relative_to(repo).as_posix())
    return mal


def _globs_manifiesto(repo: Path, docs: str) -> list[str]:
    docs = docs.strip("/")
    globs = set(rutas_protegidas(repo, docs)) | set(rutas_reglas_solo_humano(repo, docs))
    for rel in ("AGENTES.md", "AGENTS.md"):
        globs.add(cl.destino(rel, docs))
    return sorted(globs)


def escribir_manifiesto(repo: Path, docs: str) -> Path:
    """Manifiesto de rutas protegidas (varios packs en monorepo se fusionan por clave docs)."""
    docs = docs.strip("/")
    f = repo / MANIFIESTO_REL
    f.parent.mkdir(parents=True, exist_ok=True)
    datos: dict = {"version": 1, "packs": {}}
    if f.is_file():
        try:
            leido = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(leido, dict) and isinstance(leido.get("packs"), dict):
                datos["packs"] = leido["packs"]
        except ValueError:
            pass
    datos["packs"][docs] = {"globs": _globs_manifiesto(repo, docs)}
    unidos: list[str] = []
    vistos: set[str] = set()
    for pack in datos["packs"].values():
        for g in pack.get("globs") or []:
            if g not in vistos:
                vistos.add(g)
                unidos.append(g)
    datos["protegidas"] = unidos
    f.write_text(json.dumps(datos, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return f


_GUARDIA_SRC = r'''#!/usr/bin/env python3
"""Guardia fail-closed del núcleo uxyngraphar (R-20). No editar a mano: la regenera doctor.py --fix."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

MSG = ("Núcleo de uxyngraphar inviolable (R-20): no se edita en el proyecto. "
       "Mejora → ficha EVO-* . Actualizar → panel o actualizar-pack.py.")
MANIFIESTO = Path(__file__).resolve().parent.parent / "uxyngraphar-protegido.json"
EDIT_TOOLS = frozenset({
    "Write", "Edit", "StrReplace", "Delete", "NotebookEdit", "ApplyPatch",
    "search_replace", "write", "edit_file", "delete_file",
})
MUT = re.compile(
    r"(?:^|[;&|]\s*|\n)\s*(?:"
    r"rm\b|mv\b|unlink\b|rmdir\b|truncate\b|chmod\b|chown\b|install\b|"
    r"sed\s+-i|perl\s+-i|ruby\s+-i|"
    r"tee\b|cp\b|install\b|"
    r"git\s+(?:add|commit|rm|mv)\b"
    r")|(?:>>?|>>)\s*|:\s*>\s*",
    re.I,
)
RUN_OK = re.compile(
    r"^\s*(?:python3?|py(?:\s+-3)?)\s+[\"']?[\w./\\-]*(?:scripts[/\\])"
    r"(?:doctor|verificar-nucleo|controlar|contexto|presupuesto|costo-tokens|"
    r"decisiones(?:[/\\]decisiones)?|actualizar-pack|instalar-ganchos|respaldos|"
    r"memoria|feedback|ajustes|espejo-mapa|exportar-evo)\.py\b",
    re.I,
)


def _norm(p: str) -> str:
    return p.replace("\\", "/").lstrip("./")


def _carga() -> list[str]:
    if not MANIFIESTO.is_file():
        return []
    try:
        d = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return []
    return list(d.get("protegidas") or [])


def _cubre(ruta: str, globs: list[str]) -> bool:
    r = _norm(ruta)
    for g in globs:
        g = _norm(g)
        if g.endswith("/**"):
            pref = g[:-3]
            if r == pref.rstrip("/") or r.startswith(pref if pref.endswith("/") else pref + "/"):
                return True
        elif g.endswith("/***") or g.endswith("/*"):
            pref = g.rsplit("/", 1)[0]
            if r == pref or r.startswith(pref + "/"):
                return True
        elif r == g or r.endswith("/" + g):
            return True
    return False


def _paths_input(tool_input: dict) -> list[str]:
    out = []
    for k in ("path", "file_path", "target_file", "filePath", "targetFile", "notebook_path"):
        v = tool_input.get(k)
        if isinstance(v, str) and v.strip():
            out.append(v)
    return out


def _deny() -> dict:
    return {"permission": "deny", "user_message": MSG, "agent_message": MSG}


def _allow() -> dict:
    return {"permission": "allow"}


def _shell_toca(cmd: str, globs: list[str]) -> bool:
    if not cmd or not globs:
        return False
    if RUN_OK.search(cmd) and not MUT.search(cmd):
        return False
    menciona = any(g.rstrip("/*") in cmd.replace("\\", "/") for g in globs if len(g.rstrip("/*")) >= 8)
    if not menciona:
        # rutas cortas tipo AGENTES.md
        for g in globs:
            base = g.rstrip("/*").rsplit("/", 1)[-1]
            if base and re.search(r"(^|[\s\"'/])" + re.escape(base) + r"([\s\"']|$)", cmd):
                menciona = True
                break
    if not menciona:
        return False
    if MUT.search(cmd):
        return True
    if re.search(r"(?:>>?|>>)\s*[\"']?[\w./\\-]*(?:uxyngraphar|docs|/10-guias|/scripts|AGENTES|PROTOCOLO|REGLAS)", cmd, re.I):
        return True
    return False


def main() -> int:
    raw = sys.stdin.read()
    try:
        ev = json.loads(raw) if raw.strip() else {}
    except ValueError:
        print(json.dumps(_deny(), ensure_ascii=False))
        return 0
    globs = _carga()
    if not globs:
        print(json.dumps(_deny() if not MANIFIESTO.is_file() else _allow(), ensure_ascii=False))
        return 0
    nombre = (ev.get("hook_event_name") or ev.get("event") or "").strip()
    tool = (ev.get("tool_name") or "").strip()
    tin = ev.get("tool_input") if isinstance(ev.get("tool_input"), dict) else {}
    cmd = ev.get("command") if isinstance(ev.get("command"), str) else ""
    if not cmd and isinstance(tin.get("command"), str):
        cmd = tin["command"]

    if nombre == "beforeShellExecution" or tool == "Shell":
        print(json.dumps(_deny() if _shell_toca(cmd, globs) else _allow(), ensure_ascii=False))
        return 0

    if tool in EDIT_TOOLS or nombre == "preToolUse" and tool in EDIT_TOOLS:
        for p in _paths_input(tin):
            if _cubre(p, globs):
                print(json.dumps(_deny(), ensure_ascii=False))
                return 0
        print(json.dumps(_allow(), ensure_ascii=False))
        return 0

    if tool in EDIT_TOOLS:
        for p in _paths_input(tin):
            if _cubre(p, globs):
                print(json.dumps(_deny(), ensure_ascii=False))
                return 0

    print(json.dumps(_allow(), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _escribir_guardia(repo: Path) -> Path:
    f = repo / GUARDIA_REL
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(_GUARDIA_SRC.lstrip("\n"), encoding="utf-8", newline="\n")
    modo = stat.S_IMODE(f.stat().st_mode)
    os.chmod(f, modo | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return f


def _fusionar_hooks_json(repo: Path) -> Path:
    f = repo / HOOKS_JSON_REL
    f.parent.mkdir(parents=True, exist_ok=True)
    cfg: dict = {"version": 1, "hooks": {}}
    if f.is_file():
        try:
            leido = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(leido, dict):
                cfg["version"] = leido.get("version", 1)
                hooks = leido.get("hooks")
                if isinstance(hooks, dict):
                    cfg["hooks"] = hooks
        except ValueError:
            pass
    hooks = cfg.setdefault("hooks", {})
    entradas = [
        {"command": GUARDIA_CMD, "failClosed": True, "matcher": "Write|Edit|StrReplace|Delete|NotebookEdit|ApplyPatch|Shell"},
    ]
    shell = [
        {"command": GUARDIA_CMD, "failClosed": True},
    ]
    for evento, lista in (("preToolUse", entradas), ("beforeShellExecution", shell)):
        actual = hooks.get(evento)
        if not isinstance(actual, list):
            actual = []
        sin_nuestra = [e for e in actual if not (isinstance(e, dict) and e.get("command") == GUARDIA_CMD)]
        hooks[evento] = sin_nuestra + (lista if evento == "preToolUse" else shell)
    f.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return f


_REGLA_MDC = """---
description: Núcleo uxyngraphar inviolable (R-20) — no editar en el proyecto
alwaysApply: true
---

# Núcleo uxyngraphar (solo lectura)

El pack instalado es un **framework de gobernanza humano–IA**. Nadie del proyecto (agente ni persona) edita, borra, renombra ni amplía el núcleo (clase N): `AGENTES.md`, `PROTOCOLO.md`, `REGLAS.md`, `00-nucleo/` (salvo plantillas P), `10-guias/`, `scripts/`, lock, ni los mecanismos de protección (`.claude/`, `.cursor/hooks*`, CODEOWNERS, CI, ganchos).

- Si el IDE u OS niega la escritura: **no intentes bypass** (`chmod`, shell, `--no-verify`).
- Mejora del sistema → solo ficha `EVO-*` en `46-evolucion-documentacion/`.
- Actualizar el núcleo → panel uxyngraphar o `actualizar-pack.py` (humano).
- Núcleo alterado → detente y avisa; restaura con `--restaurar-nucleo`.
"""


def _escribir_regla_mdc(repo: Path) -> Path:
    f = repo / REGLA_MDC_REL
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(_REGLA_MDC.lstrip("\n"), encoding="utf-8", newline="\n")
    return f


def hooks_cursor(repo: Path, docs: str) -> list[str]:
    """Manifiesto + guardia fail-closed + hooks.json + regla .mdc. Devuelve artefactos tocados."""
    docs = docs.strip("/")
    descongelar_mecanismos(repo)
    tocar = [
        escribir_manifiesto(repo, docs).relative_to(repo).as_posix(),
        _escribir_guardia(repo).relative_to(repo).as_posix(),
        _fusionar_hooks_json(repo).relative_to(repo).as_posix(),
        _escribir_regla_mdc(repo).relative_to(repo).as_posix(),
    ]
    return tocar


def cursor_hooks_ok(repo: Path) -> bool:
    """True si hooks.json declara la guardia con failClosed."""
    f = repo / HOOKS_JSON_REL
    if not f.is_file() or not (repo / GUARDIA_REL).is_file() or not (repo / MANIFIESTO_REL).is_file():
        return False
    try:
        cfg = json.loads(f.read_text(encoding="utf-8"))
    except ValueError:
        return False
    hooks = cfg.get("hooks") or {}
    for evento in ("preToolUse", "beforeShellExecution"):
        lista = hooks.get(evento) or []
        if not any(isinstance(e, dict) and e.get("command") == GUARDIA_CMD and e.get("failClosed") is True for e in lista):
            return False
    return True


def decidir_guardia(evento: dict, repo: Path | None = None) -> dict:
    """API de prueba: ejecuta la lógica de la guardia sobre un evento (sin subprocess)."""
    # Importa el archivo escrito o evalúa con manifiesto del repo.
    man = (repo or Path(".")) / MANIFIESTO_REL
    if not man.is_file():
        return {"permission": "deny", "user_message": _MSG_DENY, "agent_message": _MSG_DENY}
    guardia = (repo or Path(".")) / GUARDIA_REL
    if not guardia.is_file():
        return {"permission": "deny", "user_message": _MSG_DENY, "agent_message": _MSG_DENY}
    import subprocess
    r = subprocess.run([sys_executable(), str(guardia)], input=json.dumps(evento), capture_output=True, text=True, cwd=str(repo or Path(".")))
    try:
        return json.loads(r.stdout.strip() or "{}")
    except ValueError:
        return {"permission": "deny", "user_message": _MSG_DENY, "agent_message": _MSG_DENY}


def sys_executable() -> str:
    import sys
    return sys.executable


def proteger_completo(repo: Path, docs: str, *, propietario: str = "") -> list[str]:
    """Activa todas las capas de protección del pack (Claude, Cursor, FS, CODEOWNERS opc.)."""
    hechos: list[str] = []
    reglas_agente(repo, docs)
    hechos.append(".claude/settings.json")
    hechos += exclusiones_agentes(repo, docs)
    hechos += hooks_cursor(repo, docs)
    if propietario or propietario_actual(repo, docs):
        codeowners(repo, docs, propietario or propietario_actual(repo, docs) or "@CAMBIAR-PROPIETARIO")
        hechos.append(".github/CODEOWNERS")
    congelar_fs(repo, docs)
    hechos.append("fs:núcleo-solo-lectura")
    return hechos
