"""Mover la carpeta del pack de un proyecto (p. ej. `docs/` → `uxyngraphar/`). Solo cuando una persona lo pide: nunca al actualizar.

Todo o nada (transaccion.py): se guarda la copia de cada archivo de la raíz que se va a cambiar, la carpeta se mueve con
`git mv` si git la sigue, y si algo falla o el proceso se corta, todo vuelve a como estaba (también la carpeta).
Lo que se pone al día con la ruta nueva es solo lo que escribió uxyngraphar:
  · el lock (`docs`), los ganchos de git (`DOCS_LIST`), las reglas deny de `.claude/settings.json` bajo la carpeta,
    el bloque de uxyngraphar en `.cursorignore`/`.geminiignore`/`.aiexclude` y en `.github/CODEOWNERS`,
    y sus líneas de `.gitignore`/`.gitattributes`;
  · `CLAUDE.md` y el workflow de CI, solo si siguen como los dejó uxyngraphar (si no, se avisa qué línea cambiar).
Lo demás del proyecto (enlaces propios a la carpeta en el README o en el código) se lista para que una persona lo revise.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ganchos"))

import ci  # noqa: E402
import clasificacion as cl  # noqa: E402
import lock  # noqa: E402
import proteccion  # noqa: E402
import transaccion  # noqa: E402

MAX_REVISAR = 30


class ErrorMover(RuntimeError):
    pass


@dataclass
class Plan:
    repo: Path
    desde: str
    hacia: str
    git: bool = False
    cambios: list[str] = field(default_factory=list)    # qué se hará, en frases cortas
    revisar: list[str] = field(default_factory=list)    # «ruta:línea: texto» que menciona la carpeta vieja y no es de uxyngraphar
    avisos: list[str] = field(default_factory=list)
    _textos: dict[str, str] = field(default_factory=dict, repr=False)   # rel → contenido nuevo de los archivos de la raíz

    def a_dict(self) -> dict:
        return {"repo": str(self.repo), "desde": self.desde, "hacia": self.hacia, "git": self.git,
                "cambios": self.cambios, "revisar": self.revisar, "avisos": self.avisos}


def _git(repo: Path, *a: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace")


def _es_git(repo: Path) -> bool:
    try:
        return _git(repo, "rev-parse", "--git-dir").returncode == 0
    except OSError:
        return False


def destino_de(desde: str, nombre: str) -> str:
    padre = cl.padre(desde)
    return f"{padre}/{nombre}" if padre else nombre


def _cambiar_ruta(texto: str, desde: str, hacia: str) -> str:
    """Cambia la carpeta en rutas («docs/…», «/docs/…», «(docs/…», «docs/**»), sin tocar palabras que solo la contienen."""
    return re.sub(rf"(?<![\w.\-]){re.escape(desde)}(?=/)", hacia, texto)


def _bloque(texto: str, ini: str, fin: str, desde: str, hacia: str) -> str:
    if ini not in texto or fin not in texto:
        return texto
    antes, resto = texto.split(ini, 1)
    dentro, despues = resto.split(fin, 1)
    return antes + ini + _cambiar_ruta(dentro, desde, hacia) + fin + despues


def _leer(repo: Path, rel: str) -> str | None:
    f = repo / rel
    return f.read_text(encoding="utf-8") if f.is_file() else None


def _ganchos(repo: Path) -> list[str]:
    """Ganchos de uxyngraphar dentro del repo (rutas relativas)."""
    try:
        import instalar_ganchos
        carpeta = instalar_ganchos.dir_ganchos(repo)
        salida = []
        for n in ("pre-commit", "commit-msg", "pre-push"):
            f = carpeta / n
            if f.is_file() and instalar_ganchos.es_nuestro(f):
                salida.append(f.resolve().relative_to(repo.resolve()).as_posix())
        return salida
    except (ImportError, ValueError, OSError):
        return []


def _claude_md(desde: str, hacia: str, texto: str) -> str | None:
    """El CLAUDE.md nuevo si es el de uxyngraphar sin tocar; None si la persona lo cambió."""
    import flujo
    if texto in (*flujo.CLAUDE_MD_ANTERIORES, flujo.texto_claude_md(desde)):
        return flujo.texto_claude_md(hacia)
    return None


def _ci_de(docs: str) -> str:
    slug = ci.nombre_archivo(docs)[:-4]
    return ci.PLANTILLA.format(nombre="uxyngraphar" + (f" ({cl.padre(docs)})" if cl.padre(docs) else ""), job=slug.replace("-", "_"), grupo=slug, docs=docs)


def planificar(repo: Path, desde: str, nombre: str = cl.CARPETA) -> Plan:
    """Qué haría mover `desde` a la carpeta `nombre` (junto a ella). No escribe nada; lanza ErrorMover si no se puede."""
    repo, desde = repo.resolve(), desde.strip("/")
    if nombre not in cl.carpeta_pack.CARPETAS:
        raise ErrorMover(f"la carpeta debe llamarse {' o '.join(cl.carpeta_pack.CARPETAS)}; recibido: {nombre}")
    hacia = destino_de(desde, nombre)
    if hacia == desde:
        raise ErrorMover(f"el pack ya está en {desde}/: no hay nada que mover")
    if not lock.ruta_lock(repo, desde).is_file():
        raise ErrorMover(f"no hay un pack de uxyngraphar en {desde}/ (falta {lock.LOCK_NOMBRE})")
    if not (repo / desde / "scripts" / "carpeta_pack.py").is_file():
        raise ErrorMover("las herramientas de este proyecto son anteriores a la 1.1.0 y no entienden otra carpeta: actualízalo primero (uxyngraphar actualizar)")
    if (repo / hacia).exists():
        raise ErrorMover(f"ya existe {hacia}/ en el proyecto: muévela o bórrala tú antes (no se mezcla nada)")
    if transaccion.interrumpidas(repo):
        raise ErrorMover("hay una actualización a medias: ejecuta antes doctor.py --fix (la deshace)")
    p = Plan(repo, desde, hacia, git=_es_git(repo))
    if p.git:
        sucio = [l for l in _git(repo, "status", "--porcelain", "--", desde).stdout.splitlines() if l.strip()]
        if sucio:
            raise ErrorMover(f"{desde}/ tiene {len(sucio)} cambio(s) sin commit: haz commit antes, así el movimiento queda limpio en git")
        p.git = bool(_git(repo, "ls-files", "--", desde).stdout.strip())
    p.cambios.append(f"Mover {desde}/ → {hacia}/" + (" (git mv: git lo verá como un renombrado)" if p.git else ""))
    p.cambios.append(f"Lock: la carpeta del pack pasa a «{hacia}»")
    for rel in _ganchos(repo):
        texto = _leer(repo, rel) or ""
        nuevo = re.sub(r'^(DOCS_LIST=")([^"]*)(")', lambda m: m[1] + " ".join(hacia if d == desde else d for d in m[2].split()) + m[3], texto, flags=re.M)
        if nuevo != texto:
            p._textos[rel] = nuevo
            p.cambios.append(f"Gancho de git {Path(rel).name}: usa {hacia}/")
    ajustes = _leer(repo, ".claude/settings.json")
    if ajustes:
        try:
            cfg = json.loads(ajustes)
        except ValueError:
            p.avisos.append(".claude/settings.json no es JSON válido: no se toca; revisa sus reglas deny a mano")
            cfg = None
        deny = ((cfg or {}).get("permissions") or {}).get("deny")
        if isinstance(deny, list) and any(isinstance(r, str) and f"({desde}/" in r for r in deny):
            cfg["permissions"]["deny"] = [r.replace(f"({desde}/", f"({hacia}/") if isinstance(r, str) else r for r in deny]
            p._textos[".claude/settings.json"] = json.dumps(cfg, indent=2, ensure_ascii=False) + "\n"
            p.cambios.append(f".claude/settings.json: las reglas deny de uxyngraphar apuntan a {hacia}/")
    for nombre_exc in proteccion.EXCLUSIONES:
        texto = _leer(repo, nombre_exc)
        if texto is not None and (nuevo := _bloque(texto, proteccion.EXC_INI, proteccion.EXC_FIN, desde, hacia)) != texto:
            p._textos[nombre_exc] = nuevo
            p.cambios.append(f"{nombre_exc}: bloque de uxyngraphar con {hacia}/")
    texto = _leer(repo, ".github/CODEOWNERS")
    if texto is not None:
        ini, fin = proteccion.marcas_codeowners(desde)
        n_ini, n_fin = proteccion.marcas_codeowners(hacia)
        nuevo = _bloque(texto, ini, fin, desde, hacia).replace(ini, n_ini, 1).replace(fin, n_fin, 1) if ini in texto and fin in texto else texto
        if nuevo != texto:
            p._textos[".github/CODEOWNERS"] = nuevo
            p.cambios.append(f".github/CODEOWNERS: revisores del núcleo en {hacia}/")
    for rel, viejas in ((".gitignore", [f"{desde}/.depuracion/respaldo/"]), (".gitattributes", [f"{desde}/** text eol=lf"])):
        texto = _leer(repo, rel)
        if texto is None:
            continue
        lineas = texto.split("\n")
        nuevas = [_cambiar_ruta(l, desde, hacia) if l.strip() in viejas else l for l in lineas]
        if nuevas != lineas:
            p._textos[rel] = "\n".join(nuevas)
            p.cambios.append(f"{rel}: líneas de uxyngraphar con {hacia}/")
    rel_claude = f"{cl.padre(desde)}/CLAUDE.md" if cl.padre(desde) else "CLAUDE.md"   # junto a AGENTES.md
    texto = _leer(repo, rel_claude)
    if texto is not None and f"{Path(desde).name}/" in texto:
        nuevo = _claude_md(desde, hacia, texto)
        if nuevo is not None:
            p._textos[rel_claude] = nuevo
            p.cambios.append(f"{rel_claude}: el de uxyngraphar, con {hacia}/")
        else:
            p.avisos.append(f"{rel_claude} lo cambiaste tú: no lo toco. Cambia a mano «{Path(desde).name}/» por «{Path(hacia).name}/» donde hable del pack")
    rel_ci = f".github/workflows/{ci.nombre_archivo(desde)}"
    texto = _leer(repo, rel_ci)
    if texto is not None and f"{desde}/" in texto:
        if texto == _ci_de(desde):
            p._textos[rel_ci] = _ci_de(hacia)
            p.cambios.append(f"{rel_ci}: el workflow de uxyngraphar, con {hacia}/")
        else:
            p.avisos.append(f"{rel_ci} lo cambiaste tú: no lo toco. Cambia «{desde}/» por «{hacia}/» en sus pasos (si no, el CI fallará)")
    p.revisar = _menciones(repo, desde, hacia, set(p._textos) | {rel_claude, rel_ci})
    return p


def _menciones(repo: Path, desde: str, hacia: str, hechos: set[str]) -> list[str]:
    """Líneas del proyecto (seguidas por git) que nombran la carpeta vieja y que uxyngraphar no pone al día."""
    if not _es_git(repo):
        return []
    r = _git(repo, "grep", "-n", "-I", "-F", f"{desde}/", "--", ".", f":(exclude){desde}/**", ":(exclude).uxyngraphar-respaldo/**")
    salida = []
    for linea in r.stdout.splitlines():
        rel = linea.split(":", 1)[0]
        if rel in hechos or rel in (cl.destino("AGENTES.md", desde), cl.destino("AGENTS.md", desde)):
            continue
        salida.append(linea if len(linea) <= 160 else linea[:157] + "…")
        if len(salida) >= MAX_REVISAR:
            salida.append("… (hay más: git grep -n " + f"'{desde}/')")
            break
    return salida


def aplicar(plan: Plan) -> Path:
    """Ejecuta el plan como una transacción. Devuelve la carpeta de respaldo. Si algo falla, todo vuelve a como estaba."""
    repo = plan.repo
    tx = transaccion.Transaccion(repo, plan.desde, accion=f"mover la carpeta del pack: {plan.desde}/ → {plan.hacia}/")
    try:
        for rel in plan._textos:
            tx.preparar(rel)
        tx.mover(plan.desde, plan.hacia, plan.git)
        tx.preparar(lock.ruta_lock(repo, plan.hacia).relative_to(repo).as_posix())
        datos = lock.leer(repo, plan.hacia)
        if not datos or datos.get("danado"):
            raise ErrorMover("no pude leer el lock en la carpeta nueva")
        datos["docs"] = plan.hacia
        lock.escribir(repo, plan.hacia, datos)
        for rel, texto in plan._textos.items():
            tx.escribir(rel, texto.encode("utf-8"))
        if plan.git:   # que el commit recoja juntos el renombrado y lo que se puso al día (lo ignorado por git se queda fuera)
            for rel in [lock.ruta_lock(repo, plan.hacia).relative_to(repo).as_posix(), *plan._textos]:
                if not rel.startswith(".git/"):
                    _git(repo, "add", "--", rel)
    except BaseException as exc:   # también Ctrl+C: nada queda a medias
        tx.deshacer(f"{type(exc).__name__}: {exc}"[:300])
        raise
    return tx.confirmar(motivo=f"mover la carpeta del pack: {plan.desde}/ → {plan.hacia}/")


def formatear(plan: Plan) -> str:
    l = [f"Mover la carpeta del pack: {plan.desde}/ → {plan.hacia}/", ""]
    l += [f"  · {c}" for c in plan.cambios]
    if plan.avisos:
        l += ["", "Para revisar tú (no lo toco):"] + [f"  ! {a}" for a in plan.avisos]
    if plan.revisar:
        l += ["", f"Tu proyecto menciona «{plan.desde}/» en estos sitios (enlaces propios; cámbialos si apuntan al pack):"] + [f"    {r}" for r in plan.revisar]
    return "\n".join(l)
