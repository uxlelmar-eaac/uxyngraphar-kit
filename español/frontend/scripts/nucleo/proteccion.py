"""Genera la protección del núcleo para agentes y revisores: reglas `deny` y bloque CODEOWNERS."""

from __future__ import annotations

import json
from pathlib import Path

import clasificacion as cl
import lock

MARCA_INI, MARCA_FIN = "# >>> uxyngraphar núcleo", "# <<< uxyngraphar núcleo"
# Carpetas 100 % núcleo: se protegen enteras (también impide crear archivos nuevos dentro).
CARPETAS_PURAS = ("10-guias", "55-automatizaciones", "scripts")
# Mecanismos de protección: editarlos equivale a desactivar la protección.
EXTRAS = (".claude/settings.json", ".github/CODEOWNERS", ".github/workflows/**", ".git/hooks/**")


# Credenciales (R-12): un agente no lee ni escribe estos archivos; `.env.example` queda libre.
SECRETOS_RUTAS = (".env", ".env.local", ".env.production", ".env.development", ".env.staging", ".env.test", "**/.env", "**/.env.*.local",
                  "**/*.pem", "**/*.key", "**/*.p12", "**/*.pfx", "**/id_rsa", "**/id_ed25519", "**/credentials.json", "**/*.tfstate",
                  "**/.npmrc", "**/.netrc", "~/.ssh/**", "~/.aws/**", "~/.config/gcloud/**", "~/.kube/**")


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


def propietario_actual(repo: Path, docs: str) -> str:
    """Propietario ya escrito en el bloque de este pack en CODEOWNERS ("" si no hay bloque)."""
    f = repo / ".github" / "CODEOWNERS"
    texto = f.read_text(encoding="utf-8") if f.is_file() else ""
    ini = MARCA_INI if docs.strip("/") == "docs" else f"{MARCA_INI} [{docs.strip('/')}]"
    if ini not in texto:
        return ""
    for linea in texto.split(ini, 1)[1].splitlines()[1:]:
        partes = linea.split()
        if len(partes) >= 2 and not linea.startswith("#"):
            return partes[-1]
    return ""


def codeowners(repo: Path, docs: str, propietario: str) -> Path:
    f = repo / ".github" / "CODEOWNERS"
    actual = f.read_text(encoding="utf-8") if f.is_file() else ""
    ini, fin = (MARCA_INI, MARCA_FIN) if docs.strip("/") == "docs" else (f"{MARCA_INI} [{docs.strip('/')}]", f"{MARCA_FIN} [{docs.strip('/')}]")
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
