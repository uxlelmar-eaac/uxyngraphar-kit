"""Validadores de las piezas estándar: uno por pieza, registrados en VALIDADORES.

Cada validador recibe (carpeta del sistema, manifiesto) y devuelve (errores, avisos). Solo se ejecuta si la pieza está
declarada en «piezas». Añadir una pieza estándar al protocolo = añadir su ruta en `uxyn_base.PIEZAS` y su validador aquí.
"""

from __future__ import annotations

import re
from pathlib import Path
from collections.abc import Callable

import especificacion as esp

base = esp.base
Resultado = tuple[list[str], list[str]]
MARCADOR = re.compile(r"\{\{[^}]*\}\}")
REGLA_NUMERADA = re.compile(r"^\d+\. \S", re.M)
SECCIONES_FASE = ("Objetivo", "Pasos", "Criterio de salida")
SECCIONES_SKILL = ("Cuándo usarla", "Pasos")
SECCIONES_SISTEMA = ("Qué resuelve", "Problemas que cubre", "Fuera de alcance", "Cuándo usarlo", "Entradas y salidas")
SECCIONES_MEMORIAS = ("Qué recordar", "Qué no recordar")
SECCIONES_LIMITES = ("Cuándo detenerse y preguntar",)


def secciones(texto: str) -> set[str]:
    return {linea[3:].strip() for linea in texto.splitlines() if linea.startswith("## ")}


def leer(ruta: Path) -> str:
    return ruta.read_text(encoding="utf-8")


def _faltan_secciones(rel: str, texto: str, requeridas: tuple[str, ...]) -> list[str]:
    presentes = secciones(texto)
    return [f"{rel}: falta la sección «## {s}»" for s in requeridas if s not in presentes]


def _titulo(rel: str, texto: str, esperado: str | None = None) -> list[str]:
    primera = texto.lstrip().split("\n", 1)[0]
    if not primera.startswith("# "):
        return [f"{rel}: la primera línea es «# {esperado or '<título>'}»"]
    if esperado and primera[2:].strip() != esperado:
        return [f"{rel}: la primera línea es «# {esperado}»"]
    return []


def _marcadores(rel: str, texto: str) -> list[str]:
    return [f"{rel}: marcadores sin rellenar ({', '.join(sorted(set(MARCADOR.findall(texto)))[:3])})"] if MARCADOR.search(texto) else []


def _md(carpeta: Path, rel: str) -> list[Path]:
    return sorted(p for p in (carpeta / rel).rglob("*.md") if p.is_file())


def _referencias_problemas(rel: str, valores, conocidos: set[str]) -> list[str]:
    if valores in (None, ""):
        return []
    if not isinstance(valores, list):
        return [f"{rel}: «resuelve» es una lista de ids de alcance.problemas"]
    return [f"{rel}: «resuelve» cita «{v}», que no está en alcance.problemas" for v in valores if v not in conocidos]


def skills_declaradas(carpeta: Path) -> dict[str, dict]:
    salida = {}
    raiz = carpeta / base.PIEZAS["skills"]
    if raiz.is_dir():
        for d in sorted(raiz.iterdir()):
            if d.is_dir() and (d / "SKILL.md").is_file():
                salida[d.name] = base.leer_frontmatter(leer(d / "SKILL.md"))[0]
    return salida


def proceso(carpeta: Path, m: dict) -> Resultado:
    errores, avisos = [], []
    fases = m.get("proceso") or []
    conocidos = base.ids_problemas(m)
    disponibles = set(skills_declaradas(carpeta)) if "skills" in (m.get("piezas") or []) else set()
    for fase in fases:
        rel = f"proceso/{fase}.md"
        if not (carpeta / rel).is_file():
            errores.append(f"{rel}: la fase está en «proceso» pero falta su archivo")
            continue
        texto = leer(carpeta / rel)
        fm, cuerpo = base.leer_frontmatter(texto)
        if fm.get("fase") != fase:
            errores.append(f"{rel}: el frontmatter dice «fase: {fm.get('fase')}», debe ser «{fase}»")
        errores += _titulo(rel, cuerpo) + _faltan_secciones(rel, cuerpo, SECCIONES_FASE)
        errores += _referencias_problemas(rel, fm.get("resuelve"), conocidos)
        citadas = fm.get("skills") or []
        if not isinstance(citadas, list):
            errores.append(f"{rel}: «skills» es una lista de nombres de skills/")
        else:
            errores += [f"{rel}: cita la skill «{s}», que no existe en skills/" for s in citadas if s not in disponibles]
        avisos += _marcadores(rel, cuerpo)
    sobrantes = sorted(p.stem for p in (carpeta / "proceso").glob("*.md") if p.stem not in fases)
    errores += [f"proceso/{s}.md: no está en «proceso» del manifiesto (añádelo o bórralo)" for s in sobrantes]
    return errores, avisos


def skills(carpeta: Path, m: dict) -> Resultado:
    errores, avisos = [], []
    conocidos = base.ids_problemas(m)
    raiz = carpeta / "skills"
    nombres = [d for d in sorted(raiz.iterdir()) if d.is_dir() and not base.IGNORAR.search(d.name)]
    if not nombres:
        errores.append("skills/: al menos una skill (skills/<nombre>/SKILL.md)")
    for d in nombres:
        rel = f"skills/{d.name}/SKILL.md"
        if not base.ID_VALIDO.match(d.name):
            errores.append(f"skills/{d.name}: nombre kebab-case")
        if not (d / "SKILL.md").is_file():
            errores.append(f"{rel}: falta")
            continue
        fm, cuerpo = base.leer_frontmatter(leer(d / "SKILL.md"))
        if fm.get("name") != d.name:
            errores.append(f"{rel}: «name» debe ser «{d.name}»")
        if not isinstance(fm.get("description"), str) or not fm["description"].strip():
            errores.append(f"{rel}: «description» obligatoria (qué hace y cuándo usarla)")
        errores += _titulo(rel, cuerpo) + _faltan_secciones(rel, cuerpo, SECCIONES_SKILL)
        if not fm.get("resuelve"):
            avisos.append(f"{rel}: sin «resuelve» (¿qué problema del alcance atiende?)")
        errores += _referencias_problemas(rel, fm.get("resuelve"), conocidos)
        avisos += _marcadores(rel, leer(d / "SKILL.md"))
    for f in sorted(p for p in raiz.iterdir() if p.is_file()):
        errores.append(f"skills/{f.name}: en skills/ solo van carpetas skills/<nombre>/")
    return errores, avisos


def componentes(carpeta: Path, m: dict) -> Resultado:
    texto = leer(carpeta / "COMPONENTES.md")
    errores = _titulo("COMPONENTES.md", texto, "Componentes")
    if not secciones(texto):
        errores.append("COMPONENTES.md: una sección «## <componente>» por componente")
    return errores, _marcadores("COMPONENTES.md", texto)


def es_herramienta(script: Path) -> bool:
    return "__main__" in leer(script)


def herramientas(carpeta: Path, m: dict) -> Resultado:
    texto = leer(carpeta / "HERRAMIENTAS.md")
    avisos = _marcadores("HERRAMIENTAS.md", texto)
    for script in sorted((carpeta / base.SCRIPTS).glob("*.py")):
        if es_herramienta(script) and script.name not in texto:
            avisos.append(f"HERRAMIENTAS.md: no documenta scripts/{script.name}")
    return _titulo("HERRAMIENTAS.md", texto, "Herramientas"), avisos


def andamiaje(carpeta: Path, m: dict) -> Resultado:
    errores = []
    declaradas = set(m.get("andamiaje") or {})
    raiz = carpeta / "andamiaje"
    presentes = {d.name for d in raiz.iterdir() if d.is_dir()}
    for v in sorted(declaradas - presentes):
        errores.append(f"andamiaje/{v}/: la variante está en el manifiesto pero falta su carpeta")
    for v in sorted(presentes - declaradas):
        errores.append(f"andamiaje/{v}/: carpeta sin variante en «andamiaje» del manifiesto")
    for v in sorted(declaradas & presentes):
        if not any(p.is_file() for p in (raiz / v).rglob("*")):
            errores.append(f"andamiaje/{v}/: vacía")
    for p in sorted(raiz.rglob("*")):
        if p.is_file() and p.suffix not in (".md", ".plantilla") and not base.IGNORAR.search(p.as_posix()):
            errores.append(f"{p.relative_to(carpeta).as_posix()}: los archivos del andamiaje que no son .md llevan el sufijo "
                           f"«.plantilla» (el typecheck y los linters del proyecto los tomarían por código)")
    return errores, []


def _carpeta_con_md(nombre: str) -> Callable[[Path, dict], Resultado]:
    def validar(carpeta: Path, m: dict) -> Resultado:
        archivos = _md(carpeta, nombre)
        if not archivos:
            return [f"{nombre}/: al menos un archivo .md"], []
        avisos = []
        if nombre != "plantillas":
            for p in archivos:
                avisos += _marcadores(p.relative_to(carpeta).as_posix(), leer(p))
        return [], avisos
    return validar


def pruebas(carpeta: Path, m: dict) -> Resultado:
    if not list((carpeta / "pruebas").glob("test_*.py")):
        return ["pruebas/: al menos un test_*.py (unittest, solo librería estándar)"], []
    return [], []


def cambios(carpeta: Path, m: dict) -> Resultado:
    texto = leer(carpeta / "CHANGELOG.md")
    avisos = [] if f"## {m.get('version')}" in texto else [f"CHANGELOG.md: sin entrada «## {m.get('version')}»"]
    return _titulo("CHANGELOG.md", texto, "Cambios"), avisos + _marcadores("CHANGELOG.md", texto)


VALIDADORES: dict[str, Callable[[Path, dict], Resultado]] = {
    "proceso": proceso,
    "skills": skills,
    "componentes": componentes,
    "herramientas": herramientas,
    "andamiaje": andamiaje,
    "plantillas": _carpeta_con_md("plantillas"),
    "referencia": _carpeta_con_md("referencia"),
    "ejemplos": _carpeta_con_md("ejemplos"),
    "pruebas": pruebas,
    "cambios": cambios,
}

# Piezas que conviene tener según la familia (solo avisos).
RECOMENDADAS = {
    "arquitectura": ("proceso", "componentes", "ejemplos"),
    "codigo": ("herramientas", "ejemplos"),
    "seguridad": ("proceso", "herramientas"),
    "proceso": ("proceso", "skills"),
    "documentacion": ("proceso", "plantillas"),
    "producto": ("proceso", "referencia"),
    "plataforma": ("proceso",),
}
COMUNES = ("cambios",)
MAX_PROBLEMAS = 5


def validar(carpeta: Path, m: dict) -> Resultado:
    """Errores y avisos de todas las piezas declaradas, de la estructura de primer nivel y de la especialización."""
    carpeta = Path(carpeta)
    errores, avisos = [], []
    declaradas = [p for p in m.get("piezas") or [] if p in base.PIEZAS]
    extensiones = m.get("extensiones") or {}
    for pieza in declaradas:
        if not (carpeta / base.PIEZAS[pieza]).exists():
            errores.append(f"pieza «{pieza}»: declarada pero falta {base.PIEZAS[pieza]}")
            continue
        e, a = VALIDADORES[pieza](carpeta, m)
        errores += e
        avisos += a
    for pieza, ruta in base.PIEZAS.items():
        if pieza not in declaradas and (carpeta / ruta).exists():
            errores.append(f"{ruta}: existe pero «{pieza}» no está en «piezas»")
    for ruta in extensiones:
        if not (carpeta / ruta.strip("/")).exists():
            errores.append(f"extensiones.{ruta}: declarada pero no existe")
    permitidos = base.RESERVADOS | {r.strip("/") for r in extensiones}
    for p in sorted(carpeta.iterdir()):
        if p.name not in permitidos and not base.IGNORAR.search(p.name) and not p.name.startswith("."):
            errores.append(f"{p.name}: no es parte del núcleo ni una pieza estándar; declárala en «extensiones» o usa una pieza")
    avisos += especializacion(carpeta, m, declaradas)
    return errores, avisos


def especializacion(carpeta: Path, m: dict, declaradas: list[str]) -> list[str]:
    avisos = []
    problemas = base.ids_problemas(m)
    if len(problemas) > MAX_PROBLEMAS:
        avisos.append(f"alcance: {len(problemas)} problemas (más de {MAX_PROBLEMAS}); posible sistema generalista, valora dividirlo")
    cubiertos = set()
    if "skills" in declaradas:
        for fm in skills_declaradas(carpeta).values():
            cubiertos |= set(fm.get("resuelve") or [])
    if "proceso" in declaradas:
        for fase in m.get("proceso") or []:
            ruta = carpeta / "proceso" / f"{fase}.md"
            if ruta.is_file():
                cubiertos |= set(base.leer_frontmatter(leer(ruta))[0].get("resuelve") or [])
    if "skills" in declaradas or "proceso" in declaradas:
        for p in sorted(problemas - cubiertos):
            avisos.append(f"alcance: el problema «{p}» no lo cubre ninguna fase ni skill")
    faltan = [p for p in (*RECOMENDADAS.get(m.get("familia"), ()), *COMUNES) if p not in declaradas]
    if faltan:
        avisos.append(f"completitud: piezas recomendadas para «{m.get('familia')}» que faltan: {', '.join(faltan)}")
    return avisos


def completitud(carpeta: Path, m: dict) -> dict:
    """Resumen para `validar --completitud`: piezas presentes, recomendadas que faltan y extensiones."""
    declaradas = [p for p in m.get("piezas") or [] if p in base.PIEZAS]
    recomendadas = [*RECOMENDADAS.get(m.get("familia"), ()), *COMUNES]
    return {"piezas": declaradas, "faltan_recomendadas": [p for p in recomendadas if p not in declaradas],
            "otras_disponibles": [p for p in base.PIEZAS if p not in declaradas and p not in recomendadas],
            "extensiones": sorted(m.get("extensiones") or {}), "problemas": sorted(base.ids_problemas(m))}


def limites_y_permisos(carpeta: Path, m: dict) -> list[str]:
    """Errores de LIMITES.md (reglas numeradas y «Cuándo detenerse y preguntar») y PERMISOS.md (bloque al día y
    scripts de «permisos.acciones» que existen)."""
    import uxyn_permisos as permisos
    errores = []
    ruta = carpeta / base.LIMITES
    if ruta.is_file():
        texto = leer(ruta)
        errores += _titulo(base.LIMITES, texto, "Límites")
        if not REGLA_NUMERADA.search(texto):
            errores.append(f"{base.LIMITES}: al menos una regla numerada («1. …»)")
        errores += _faltan_secciones(base.LIMITES, texto, SECCIONES_LIMITES)
        errores += _marcadores(base.LIMITES, texto)
    ruta = carpeta / base.PERMISOS
    if ruta.is_file():
        texto = leer(ruta)
        errores += _titulo(base.PERMISOS, texto, "Permisos")
        errores += _marcadores(base.PERMISOS, texto)
        if not permisos.al_dia(carpeta):
            errores.append(f"{base.PERMISOS}: el bloque de permisos no corresponde al manifiesto; "
                           f"ejecuta «uxyngraphar indice-sistema {m['id']}»")
    errores += [f"permisos.acciones: no existe {s}" for s in permisos.scripts_que_faltan(carpeta, m, esp.COMUN)]
    return errores


def nucleo(carpeta: Path, m: dict) -> list[str]:
    """Errores de SISTEMA.md, MEMORIAS.md, LIMITES.md, PERMISOS.md, README.md y marcadores en el núcleo."""
    errores = []
    ruta = carpeta / base.DESCRIPCION
    if ruta.is_file():
        texto = leer(ruta)
        errores += _titulo(base.DESCRIPCION, texto, m.get("titulo"))
        errores += _faltan_secciones(base.DESCRIPCION, texto, SECCIONES_SISTEMA)
        errores += _marcadores(base.DESCRIPCION, texto)
        for p in sorted(base.ids_problemas(m)):
            if f"`{p}`" not in texto:
                errores.append(f"{base.DESCRIPCION}: «Problemas que cubre» no menciona `{p}`")
    ruta = carpeta / base.MEMORIAS
    if ruta.is_file():
        texto = leer(ruta)
        errores += _titulo(base.MEMORIAS, texto, "Memorias")
        errores += _faltan_secciones(base.MEMORIAS, texto, SECCIONES_MEMORIAS)
        errores += _marcadores(base.MEMORIAS, texto)
    errores += limites_y_permisos(carpeta, m)
    for rel in (base.ENTRADA, base.MANIFIESTO):
        if (carpeta / rel).is_file():
            errores += _marcadores(rel, leer(carpeta / rel))
    return errores
