"""Configuración legible por máquina del proyecto: docs/uxyngraphar.config.json (clase P: la edita el proyecto).

Una sola fuente para las herramientas (puerta de control, espejo, doctor). Se rellena sola al instalar
(`detectar`) y el proyecto la ajusta. Sin dependencias; ausente o corrupta ⇒ valores por defecto seguros.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

NOMBRE = "uxyngraphar.config.json"
NIVELES = ("bloqueante", "aviso", "apagado")
CONTROLES = ("lineas", "instruccion", "secretos", "nucleo", "espejo", "idioma", "commits", "memoria", "reglas_proyecto")
# Reglas del proyecto (96-reglas-proyecto/_PROTOCOLO.md): cómo se aprueban excepciones y cambios.
MODOS_EXCEPCION = ("en_instruccion", "ficha_aparte", "prohibidas")
MODOS_CAMBIO_REGLAS = ("instruccion_aprobada", "solo_humano")
EXCLUIR_BASE = ["node_modules/**", "vendor/**", "dist/**", "build/**", "target/**", ".venv/**", "venv/**", "__pycache__/**", "*.min.js", "*.lock",
                "package-lock.json", "*.generated.*", "*.snap", "migrations/**"]
# Marcador de pila → (nombre, extensiones de código, raíces típicas)
PILAS = [
    ("package.json", "node", [".ts", ".tsx", ".js", ".jsx", ".mjs", ".vue", ".svelte"], ["src", "app", "lib", "pages", "components"]),
    ("pyproject.toml", "python", [".py"], ["src", "app"]),
    ("requirements.txt", "python", [".py"], ["src", "app"]),
    ("go.mod", "go", [".go"], ["cmd", "internal", "pkg"]),
    ("Cargo.toml", "rust", [".rs"], ["src"]),
    ("pom.xml", "java", [".java", ".kt"], ["src"]),
    ("build.gradle", "java", [".java", ".kt"], ["src"]),
    ("pubspec.yaml", "dart", [".dart"], ["lib"]),
    ("composer.json", "php", [".php"], ["src", "app"]),
    ("Gemfile", "ruby", [".rb"], ["app", "lib"]),
    ("mix.exs", "elixir", [".ex", ".exs"], ["lib"]),
]
# R-22: idioma de los artefactos del producto (00-nucleo/politica-idioma.md).
IDIOMA_DEFECTO = {
    "artefactos": "en",            # idioma del código del producto, archivos, commits y ramas (único valor soportado: en)
    "conversacion": "espejo",      # el agente responde en el idioma del humano ("espejo") o en uno fijo ("es", "en"…)
    "glosario": "00-nucleo/glosario-dominio.md",   # términos de dominio permitidos (relativo a docs/)
    "excluir": ["**/generated/**", "**/__generated__/**", "*.generated.*", "*.pb.*", "*.g.dart", "*.freezed.dart", "migrations/**"],
    "legacy": [],                  # rutas con código legacy en otro idioma: sus hallazgos solo avisan
    "locales": ["**/locales/**", "**/locale/**", "**/i18n/**", "**/lang/**", "*.po", "*.pot", "*.arb"],   # traducciones: no son código (R-21)
    "commits": "conventional",     # conventional | libre
    "ramas": "",                   # regex de nombres de rama; vacío = tipo/alcance-descripcion (control/idioma.py)
}
# Pistas de cliente (UI); el resto de pilas se asume servidor.
PISTAS_CLIENTE = ("react", "vue", "svelte", "next", "angular", "expo", "react-native", "electron", "flutter", "@ionic", "vite")


def por_defecto(rol: str = "servidor") -> dict:
    return {
        "version": 1,
        "rol": rol,
        "pila": [],
        "codigo": {"raices": [], "extensiones": [], "excluir": list(EXCLUIR_BASE)},
        "limite_lineas": 350,
        "exenciones_lineas": [],
        "secretos_permitir": [],
        "niveles": {"lineas": "aviso", "instruccion": "aviso", "secretos": "bloqueante", "nucleo": "bloqueante", "espejo": "aviso",
                    "idioma": "aviso", "commits": "aviso", "memoria": "bloqueante", "reglas_proyecto": "bloqueante"},
        "idioma": json.loads(json.dumps(IDIOMA_DEFECTO)),
        "respaldos": {"conservar_dias": 30, "conservar_minimo": 3, "limpieza_automatica": True},
        "memoria": {"archivadas_a_memoria_dias": 180, "listas_a_memoria_dias": 30, "permitir_purgar": True},   # R-24
        # Reglas del proyecto: excepción declarada en la instrucción aprobada; cambios de reglas solo con instrucción aprobada.
        "reglas_proyecto": {"excepciones": "en_instruccion", "cambios_reglas": "instruccion_aprobada"},
        # Envío voluntario de las fichas EVO a quien mantiene uxyngraphar (10-guias/envio-sugerencias.md). Apagado salvo que una persona lo active.
        # `respondido` ("", "si", "no"), `respondido_en` y `origen` guardan la respuesta a la pregunta del instalador/actualizador.
        "feedback": {"activo": False, "url": "", "consentimiento": "", "id_instalacion": "", "ocultar": [],
                     "respondido": "", "respondido_en": "", "origen": ""},
    }


def _fusionar(base: dict, extra: dict) -> dict:
    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _fusionar(base[k], v)
        else:
            base[k] = v
    return base


def validar(cfg: dict) -> list[str]:
    errores: list[str] = []
    for k, v in cfg.get("niveles", {}).items():
        if k not in CONTROLES:
            errores.append(f"niveles.{k}: control desconocido (válidos: {', '.join(CONTROLES)})")
        elif v not in NIVELES:
            errores.append(f"niveles.{k}={v!r}: use {', '.join(NIVELES)}")
    if not isinstance(cfg.get("limite_lineas"), int) or cfg["limite_lineas"] < 50:
        errores.append("limite_lineas: entero ≥ 50")
    r = cfg.get("respaldos", {})
    for k in ("conservar_dias", "conservar_minimo"):
        if not isinstance(r.get(k), int) or isinstance(r.get(k), bool) or r[k] < 0:
            errores.append(f"respaldos.{k}: entero ≥ 0")
    if not isinstance(r.get("limpieza_automatica"), bool):
        errores.append("respaldos.limpieza_automatica: true o false")
    mem = cfg.get("memoria", {})
    for k in ("archivadas_a_memoria_dias", "listas_a_memoria_dias"):
        if not isinstance(mem.get(k), int) or isinstance(mem.get(k), bool) or mem[k] < 0:
            errores.append(f"memoria.{k}: entero ≥ 0 (días)")
    if not isinstance(mem.get("permitir_purgar"), bool):
        errores.append("memoria.permitir_purgar: true o false")
    errores += _validar_feedback(cfg.get("feedback"))
    rp = cfg.get("reglas_proyecto", {})
    if not isinstance(rp, dict):
        errores.append("reglas_proyecto: debe ser un objeto")
    else:
        if rp.get("excepciones") not in MODOS_EXCEPCION:
            errores.append(f"reglas_proyecto.excepciones: {' | '.join(MODOS_EXCEPCION)}")
        if rp.get("cambios_reglas") not in MODOS_CAMBIO_REGLAS:
            errores.append(f"reglas_proyecto.cambios_reglas: {' | '.join(MODOS_CAMBIO_REGLAS)}")
    i = cfg.get("idioma", {})
    if not isinstance(i, dict):
        errores.append("idioma: debe ser un objeto")
    else:
        if i.get("artefactos") != "en":
            errores.append("idioma.artefactos: único valor soportado 'en' (cambiarlo es un cambio del núcleo: ficha EVO)")
        if not isinstance(i.get("conversacion"), str) or not i["conversacion"]:
            errores.append("idioma.conversacion: 'espejo' o un código de idioma ('es', 'en'…)")
        if i.get("commits") not in ("conventional", "libre"):
            errores.append("idioma.commits: 'conventional' o 'libre'")
        for k in ("excluir", "legacy", "locales"):
            if not isinstance(i.get(k), list) or not all(isinstance(x, str) for x in i[k]):
                errores.append(f"idioma.{k}: lista de patrones")
        if i.get("ramas"):
            try:
                re.compile(i["ramas"])
            except re.error as e:
                errores.append(f"idioma.ramas: regex inválida ({e})")
    if cfg.get("rol") not in ("servidor", "cliente"):
        errores.append("rol: 'servidor' o 'cliente'")
    return errores


def url_permitida(url: str) -> bool:
    """HTTPS siempre; HTTP solo hacia este mismo equipo (pruebas con un backend de uxyngraphar local)."""
    return bool(re.match(r"^https://[^\s/@]+(?:/\S*)?$", url) or re.match(r"^http://(?:127\.0\.0\.1|localhost)(?::\d+)?(?:/\S*)?$", url))


def _validar_feedback(fb: object) -> list[str]:
    if not isinstance(fb, dict):
        return ["feedback: debe ser un objeto"]
    errores = []
    if not isinstance(fb.get("activo"), bool):
        errores.append("feedback.activo: true o false")
    for k in ("url", "consentimiento", "id_instalacion", "respondido_en", "origen"):
        if not isinstance(fb.get(k, ""), str):
            errores.append(f"feedback.{k}: texto")
    if fb.get("respondido", "") not in ("", "si", "no"):
        errores.append("feedback.respondido: '', 'si' o 'no' (lo escriben el instalador, el actualizador y feedback.py)")
    if not isinstance(fb.get("ocultar"), list) or not all(isinstance(x, str) for x in fb["ocultar"]):
        errores.append("feedback.ocultar: lista de nombres a quitar antes de enviar (cliente, producto…)")
    if fb.get("activo") is True:
        if not url_permitida(str(fb.get("url", ""))):
            errores.append("feedback.url: https://… (http solo hacia 127.0.0.1/localhost)")
        if not fb.get("consentimiento") or not fb.get("id_instalacion"):
            errores.append("feedback.activo=true sin consentimiento registrado: actívalo con «feedback.py activar», no a mano")
    return errores


def cargar(repo: Path, docs: str = "docs") -> tuple[dict, list[str]]:
    """(config efectiva, problemas). Nunca lanza: ante error devuelve los valores por defecto + el problema."""
    archivo = repo / docs / NOMBRE
    cfg = por_defecto()
    if not archivo.is_file():
        return cfg, []
    try:
        extra = json.loads(archivo.read_text(encoding="utf-8"))
        if not isinstance(extra, dict):
            raise ValueError("la raíz debe ser un objeto")
    except (ValueError, OSError) as e:
        return cfg, [f"{NOMBRE} ilegible ({e}); se usan los valores por defecto"]
    cfg = _fusionar(cfg, extra)
    return cfg, validar(cfg)


def detectar(repo: Path, rol: str = "servidor") -> dict:
    """Propone la configuración mirando los marcadores de pila del repo (no escribe)."""
    cfg = por_defecto(rol)
    exts: list[str] = []
    raices: list[str] = []
    for marcador, nombre, e, r in PILAS:
        if (repo / marcador).is_file():
            if nombre not in cfg["pila"]:
                cfg["pila"].append(nombre)
            exts += [x for x in e if x not in exts]
            raices += [x for x in r if (repo / x).is_dir() and x not in raices]
    for csproj in ("*.csproj", "*.sln"):
        if next(repo.glob(csproj), None):
            cfg["pila"].append("dotnet")
            exts += [".cs"]
            break
    pkg = repo / "package.json"
    if pkg.is_file() and rol == "servidor":
        try:
            texto = pkg.read_text(encoding="utf-8").lower()
            if any(p in texto for p in PISTAS_CLIENTE):
                cfg["rol"] = "cliente"
        except OSError:
            pass
    cfg["codigo"]["extensiones"] = exts
    cfg["codigo"]["raices"] = raices
    return cfg


def escribir(repo: Path, docs: str, cfg: dict, sobrescribir: bool = False) -> Path | None:
    archivo = repo / docs / NOMBRE
    if archivo.exists() and not sobrescribir:
        return None
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return archivo


def raiz_git(carpeta: Path) -> Path | None:
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=carpeta, capture_output=True, text=True)
    except OSError:
        return None
    return Path(r.stdout.strip()).resolve() if r.returncode == 0 and r.stdout.strip() else None


def normalizar(repo: Path, docs: str) -> tuple[Path, str]:
    """(raíz del repo git, docs relativo a esa raíz). Si `repo` es una subcarpeta del repo (monorepo), todo se expresa desde la raíz de git,
    que es desde donde git ejecuta los ganchos y donde viven .github/CODEOWNERS y el CI."""
    repo, docs = repo.resolve(), docs.strip("/")
    raiz = raiz_git(repo)
    if raiz is None or raiz == repo:
        return repo, docs
    try:
        return raiz, (repo / docs).resolve().relative_to(raiz).as_posix()
    except ValueError:
        return repo, docs
