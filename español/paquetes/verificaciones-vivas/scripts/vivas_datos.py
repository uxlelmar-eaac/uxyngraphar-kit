"""Revisiones que contrastan la documentación de los paquetes instalados con el código. Solo leen, salvo «humo»."""

from __future__ import annotations

import fnmatch
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import uxyn_base as base
import uxyn_fichas as fichas

PAQUETE = base.carpeta_paquete(Path(__file__).resolve().parent)
ID = re.compile(r"\b[A-Z]{2,5}-\d{8}-[a-z0-9]+(?:-[a-z0-9]+)*\b")
RUTA_EN_TEXTO = re.compile(r"`([\w.@/-]+/[\w.@-]+|[\w-]+\.[a-z]{1,5})`")
NEST_CONTROLADOR = re.compile(r"""@Controller\(\s*(?:['"]([^'"]*)['"]|\{[^}]*?path\s*:\s*['"]([^'"]*)['"][^}]*\})?""")
NEST_METODO = re.compile(r"""@(Get|Post|Put|Patch|Delete|Options|Head|All)\(\s*(?:['"]([^'"]*)['"])?""")
EXPRESS = re.compile(r"""\b(?:app|router|server|fastify)\.(get|post|put|patch|delete)\(\s*['"](/[^'"]*)['"]""")
DECORADOR_PY = re.compile(r"""@\w+\.(get|post|put|patch|delete)\(\s*['"](/[^'"]*)['"]""")
PARAMETRO = re.compile(r":\w+|\{[^}/]+\}|\[\[?\.{0,3}[^\]/]+\]\]?")
SEVERIDADES = ("critica", "alta", "media", "baja", "info")


@dataclass
class Hallazgo:
    severidad: str
    hallazgo: str
    evidencia: str


def raiz() -> Path:
    return base.raiz_app(PAQUETE)


def ajustes() -> dict:
    return base.leer_ajustes(PAQUETE)


def instalado(pid: str) -> Path | None:
    p = raiz() / base.CARPETA_PAQUETES / pid
    return p if (p / base.MANIFIESTO).is_file() else None


def _rel(p: Path) -> str:
    return p.relative_to(raiz()).as_posix()


def codigo(a: dict) -> list[Path]:
    excluir, extensiones = set(a.get("excluir", [])), set(a.get("extensiones", []))
    salida = []
    for r in a.get("raices", ["."]):
        for actual, dirs, nombres in os.walk(raiz() / r):
            dirs[:] = [d for d in dirs if d not in excluir]
            salida += [Path(actual) / n for n in nombres if Path(n).suffix in extensiones]
    return sorted(set(salida))


def _leer(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return ""


def _linea(texto: str, pos: int) -> int:
    return texto.count("\n", 0, pos) + 1


def normalizar(path: str) -> str:
    path = PARAMETRO.sub("{}", "/" + path.strip("/"))
    return re.sub(r"/+", "/", path).rstrip("/") or "/"


def _con_frontmatter(pid: str, tipo: str | None = None) -> list[tuple[fichas.Ficha, dict, str]]:
    p = instalado(pid)
    if not p:
        return []
    salida = []
    for f in fichas.listar(p, tipo):
        fm, cuerpo = base.leer_frontmatter(_leer(f.ruta))
        salida.append((f, fm, cuerpo))
    return salida


def rutas_del_codigo(a: dict) -> dict[tuple[str, str], str]:
    """(método, path normalizado) → archivo:línea, para Nest, Express/Fastify y FastAPI/Flask."""
    prefijo = a.get("prefijo_global", "")
    salida = {}
    for p in codigo(a):
        texto = _leer(p)
        c = NEST_CONTROLADOR.search(texto)
        if c:
            base_ruta = c.group(1) or c.group(2) or ""
            for m in NEST_METODO.finditer(texto, c.end()):
                clave = (m.group(1).upper(), normalizar(f"{prefijo}/{base_ruta}/{m.group(2) or ''}"))
                salida.setdefault(clave, f"{_rel(p)}:{_linea(texto, m.start())}")
        for patron in (EXPRESS, DECORADOR_PY):
            for m in patron.finditer(texto):
                clave = (m.group(1).upper(), normalizar(f"{prefijo}/{m.group(2)}"))
                salida.setdefault(clave, f"{_rel(p)}:{_linea(texto, m.start())}")
    return salida


def rutas(a: dict) -> list[Hallazgo]:
    if not instalado("rutas-de-api"):
        return [Hallazgo("info", "rutas-de-api no está instalado", "—")]
    en_codigo = rutas_del_codigo(a)
    if not en_codigo:
        return [Hallazgo("info", "no se detectaron rutas en el código (Nest, Express, Fastify, FastAPI, Flask)", "—")]
    salida, documentadas = [], set()
    for f, fm, _ in _con_frontmatter("rutas-de-api", "ruta"):
        clave = (str(fm.get("method", "")).upper(), normalizar(str(fm.get("path", ""))))
        documentadas.add(clave)
        if fm.get("status") == "activa" and clave not in en_codigo:
            salida.append(Hallazgo("alta", f"ficha activa sin ruta en el código: {' '.join(clave)}", _rel(f.ruta)))
    for clave, donde in sorted(en_codigo.items()):
        if clave not in documentadas:
            salida.append(Hallazgo("media", f"ruta sin ficha: {' '.join(clave)}", donde))
    return salida


def paginas_del_codigo(a: dict) -> dict[str, str]:
    """path → archivo, para el App Router de Next (carpetas con page.*)."""
    salida = {}
    for p in codigo(a):
        if p.stem != "page":
            continue
        partes = _rel(p).split("/")[:-1]
        if "app" not in partes:
            continue
        partes = partes[partes.index("app") + 1:]
        if any(s.startswith("@") or s.startswith("_") for s in partes):
            continue
        salida.setdefault(normalizar("/".join(s for s in partes if not s.startswith("("))), _rel(p))
    return salida


def paginas(a: dict) -> list[Hallazgo]:
    if not instalado("paginas-de-interfaz"):
        return [Hallazgo("info", "paginas-de-interfaz no está instalado", "—")]
    en_codigo = paginas_del_codigo(a)
    if not en_codigo:
        return [Hallazgo("info", "no se detectaron páginas (carpetas app/**/page.*)", "—")]
    salida, documentadas = [], set()
    for f, fm, _ in _con_frontmatter("paginas-de-interfaz", "pagina"):
        path = normalizar(str(fm.get("path", "")))
        documentadas.add(path)
        if fm.get("status") == "activa" and path not in en_codigo:
            salida.append(Hallazgo("alta", f"ficha activa sin página en el código: {path}", _rel(f.ruta)))
    salida += [Hallazgo("media", f"página sin ficha: {path}", donde) for path, donde in sorted(en_codigo.items()) if path not in documentadas]
    return salida


def _rutas_citadas(fm: dict, cuerpo: str, campos: list[str]) -> list[str]:
    citadas = []
    for campo in campos:
        valor = fm.get(campo)
        citadas += [str(v) for v in (valor if isinstance(valor, list) else [valor]) if v not in (None, "", "null")]
    seccion = False
    for linea in cuerpo.splitlines():
        if linea.startswith("#"):
            seccion = "ancla" in linea.lower()
        elif seccion:
            citadas += RUTA_EN_TEXTO.findall(linea)
    return [c.split(":")[0].split("#")[0] for c in citadas if not re.search(r"[<>*…{}]|^https?:", c)]


def anclas(a: dict) -> list[Hallazgo]:
    salida = []
    nombres: dict[str, list[str]] | None = None
    for md in sorted((raiz() / base.CARPETA_TRABAJO).rglob("*.md")):
        fm, cuerpo = base.leer_frontmatter(_leer(md))
        for ruta in _rutas_citadas(fm, cuerpo, a.get("campos_ancla", [])):
            if (raiz() / ruta).exists():
                continue
            if nombres is None:
                nombres = {}
                for p in codigo(a):
                    nombres.setdefault(p.name, []).append(_rel(p))
            sugerencia = ", ".join(nombres.get(Path(ruta).name, [])[:3])
            salida.append(Hallazgo("media", f"ancla rota: {ruta}" + (f" (¿ahora en {sugerencia}?)" if sugerencia else ""), _rel(md)))
    return salida


def decisiones(a: dict) -> list[Hallazgo]:
    if not instalado("decisiones-de-arquitectura"):
        return [Hallazgo("info", "decisiones-de-arquitectura no está instalado", "—")]
    salida = []
    archivos = codigo(a)
    for f, fm, _ in _con_frontmatter("decisiones-de-arquitectura", "adr"):
        if fm.get("status") != "aceptada":
            continue
        patron = fm.get("comprobacion_prohibido")
        if patron in (None, "", "null"):
            salida.append(Hallazgo("info", f"{f.id}: aceptada sin «comprobacion_prohibido» (sin evidencia automática)", _rel(f.ruta)))
            continue
        try:
            regex = re.compile(str(patron))
        except re.error as e:
            salida.append(Hallazgo("media", f"{f.id}: comprobacion_prohibido no es una expresión regular válida ({e})", _rel(f.ruta)))
            continue
        globs = [str(g) for g in fm.get("aplica_a") or []] if isinstance(fm.get("aplica_a"), list) else []
        for p in archivos:
            rel = _rel(p)
            if globs and not any(fnmatch.fnmatch(rel, g) for g in globs):
                continue
            texto = _leer(p)
            for m in regex.finditer(texto):
                salida.append(Hallazgo("alta", f"{f.id} prohíbe «{patron}»", f"{rel}:{_linea(texto, m.start())}"))
    return salida


def manuales(a: dict, hoy: date | None = None) -> list[Hallazgo]:
    if not instalado("manuales-operativos"):
        return [Hallazgo("info", "manuales-operativos no está instalado", "—")]
    hoy, dias = hoy or date.today(), int(a.get("dias_manual", 90))
    salida = []
    for f, fm, cuerpo in _con_frontmatter("manuales-operativos", "manual"):
        if fm.get("status") != "vigente":
            continue
        verificado = str(fm.get("ultima_verificacion") or "")
        try:
            edad = (hoy - date.fromisoformat(verificado)).days
        except ValueError:
            edad = None
        if edad is None:
            salida.append(Hallazgo("media", f"{f.id}: vigente sin «ultima_verificacion»", _rel(f.ruta)))
        elif edad > dias:
            salida.append(Hallazgo("baja", f"{f.id}: verificado hace {edad} días (máximo {dias})", _rel(f.ruta)))
        for ruta in {r for r in RUTA_EN_TEXTO.findall(cuerpo) if "/" in r and not re.search(r"[<>*…{}]|^https?:", r)}:
            if not (raiz() / ruta).exists():
                salida.append(Hallazgo("media", f"{f.id}: cita «{ruta}», que no existe", _rel(f.ruta)))
    return salida


def vinculos(a: dict) -> list[Hallazgo]:
    paquetes = raiz() / base.CARPETA_PAQUETES
    existentes = set()
    for p in sorted(paquetes.iterdir()) if paquetes.is_dir() else []:
        if (p / base.MANIFIESTO).is_file() and base.leer_manifiesto(p).get("fichas"):
            existentes |= {f.id for f in fichas.listar(p)}
    salida = []
    for md in sorted((raiz() / base.CARPETA_TRABAJO).rglob("*.md")):
        texto = _leer(md)
        for m in ID.finditer(texto):
            if m.group(0) not in existentes and m.group(0) != md.stem:
                salida.append(Hallazgo("media", f"id colgante: {m.group(0)}", f"{_rel(md)}:{_linea(texto, m.start())}"))
    return salida


def humo(a: dict, ejecutar: bool) -> list[Hallazgo]:
    pruebas = a.get("humo") or []
    if not pruebas:
        return [Hallazgo("info", "sin pruebas de humo en ajustes («humo»: [{nombre, comando}])", "—")]
    if not ejecutar:
        return [Hallazgo("info", f"{len(pruebas)} pruebas de humo sin ejecutar (hace falta --ejecutar)", "—")]
    salida = []
    for prueba in pruebas:
        nombre, comando = prueba.get("nombre", "?"), prueba.get("comando", "")
        try:
            r = subprocess.run(comando, shell=True, cwd=raiz(), capture_output=True, text=True, timeout=int(prueba.get("segundos", 300)))
            if r.returncode != 0:
                cola = (r.stderr or r.stdout).strip().splitlines()[-1:] or ["(sin salida)"]
                salida.append(Hallazgo("alta", f"humo «{nombre}» falla (código {r.returncode}): {cola[0][:160]}", comando))
        except subprocess.TimeoutExpired:
            salida.append(Hallazgo("alta", f"humo «{nombre}» excede el tiempo", comando))
    return salida


REVISIONES = {
    "rutas": rutas,
    "paginas": paginas,
    "anclas": anclas,
    "decisiones": decisiones,
    "manuales": manuales,
    "vinculos": vinculos,
}
