"""Flujos de alto nivel (instalar / actualizar / diagnosticar) con resultados estructurados y mensajes en lenguaje llano.

Los usan el asistente visual de la raíz de uxyngraphar y los scripts de línea de comandos, para que ambos expliquen lo mismo.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

AQUI = Path(__file__).resolve().parent
for sub in (AQUI, AQUI.parent / "ganchos", AQUI.parent / "control", AQUI.parent / "decisiones", AQUI.parent / "tokens"):
    if str(sub) not in sys.path:
        sys.path.insert(0, str(sub))

import actualizar as act  # noqa: E402
import ci  # noqa: E402
import clasificacion as cl  # noqa: E402
import doctor  # noqa: E402
import instalar as ins  # noqa: E402
import lock  # noqa: E402
import proteccion  # noqa: E402
import uxyngraphar_config as cfgmod  # noqa: E402

CLAUDE_MD = ("# CLAUDE.md\n\nEste proyecto usa uxyngraphar. Lee **solo** [AGENTES.md](AGENTES.md) al empezar y sigue su flujo "
             "(instrucción aprobada → `python3 docs/scripts/contexto.py <id>`). No edites el núcleo (R-20).\n")


@dataclass
class Paso:
    texto: str
    estado: str = "ok"   # ok · aviso · error
    detalle: str = ""


@dataclass
class Resultado:
    pasos: list[Paso] = field(default_factory=list)
    ok: bool = True

    def add(self, texto: str, estado: str = "ok", detalle: str = "") -> None:
        self.pasos.append(Paso(texto, estado, detalle))
        if estado == "error":
            self.ok = False


def ficha_destino(repo: Path, docs: str) -> dict:
    """Qué hay ya en esa ubicación (para decidir entre instalar, adoptar o actualizar)."""
    repo, docs = cfgmod.normalizar(repo, docs)
    datos = lock.leer(repo, docs)
    carpeta = repo / docs
    return {
        "docs": docs,
        "instalado": bool(datos),
        "version": (datos or {}).get("version", ""),
        "pack": (datos or {}).get("pack", ""),
        "docs_existe": carpeta.is_dir() and any(carpeta.iterdir()),
        "agentes": (repo / cl.destino("AGENTES.md", docs)).is_file(),
    }


def plan_instalacion(pack: Path, repo: Path, docs: str, adoptar: bool = False, perfil: str = "completo") -> dict:
    """Simulación: cuántos archivos se crearían y cuáles chocarían con lo existente (no escribe nada)."""
    repo, docs = cfgmod.normalizar(repo, docs)
    r = ins.instalar(pack, repo, docs, perfil, adoptar, True, False)
    return {"version": r.version, "nuevos": len(r.nuevos), "iguales": len(r.iguales), "conflictos": list(r.conflictos),
            "ejemplos": [cl.destino(x, docs) for x in r.nuevos[:6]]}


def instalar_completo(pack: Path, repo: Path, docs: str, *, adoptar: bool = False, proteger: bool = True, propietario: str = "",
                      estricto: bool = False, claude_md: bool = True, ganchos: bool = True, perfil: str = "completo", fuente: str = "",
                      exigir_git: bool = True) -> Resultado:
    repo, docs = cfgmod.normalizar(repo, docs)
    res = Resultado()
    try:
        r = ins.instalar(pack, repo, docs, perfil, adoptar, False, exigir_git, fuente=fuente or str(pack), estricto=estricto)
    except ins.ErrorInstalacion as exc:
        res.add("No se pudo instalar", "error", str(exc))
        return res
    res.add(f"Pack {r.version} copiado a {docs}/ ({len(r.nuevos)} archivos nuevos)")
    res.add(f"{cl.destino('AGENTES.md', docs)} creado: es lo único que lee tu agente al empezar" if (repo / cl.destino("AGENTES.md", docs)).is_file() else "AGENTES.md no se creó", "ok" if (repo / cl.destino("AGENTES.md", docs)).is_file() else "aviso")
    for c in r.conflictos:
        res.add(f"{c} ya existía y es distinto: se conservó el tuyo", "aviso", f"La versión de uxyngraphar quedó como {c}.uxyngraphar-nuevo para que la compares")
    res.add(f"Configuración de tu proyecto generada: {docs}/uxyngraphar.config.json (pila detectada y límites)")
    if claude_md:
        f = repo / cl.padre(docs) / "CLAUDE.md"
        if not f.exists():
            f.write_text(CLAUDE_MD, encoding="utf-8", newline="\n")
            res.add("CLAUDE.md creado: apunta a AGENTES.md")
    if proteger:
        proteccion.reglas_agente(repo, docs)
        proteccion.exclusiones_agentes(repo, docs)
        res.add("Protección para agentes activada: no podrán editar el núcleo ni leer .env, llaves ni la memoria del sistema",
                detalle=".claude/settings.json · .cursorignore · .geminiignore · .aiexclude")
        proteccion.codeowners(repo, docs, propietario or "@CAMBIAR-PROPIETARIO")
        wf, creado = ci.workflow(repo, docs)
        res.add(f"Verificación en el servidor: {wf.relative_to(repo).as_posix()} " + ("creado" if creado else "ya existía"), "ok",
                "Hazlo obligatorio en GitHub: Settings → Branches → «Require status checks»; sin eso el gancho local se puede saltar con --no-verify" if creado else "")
        res.add("Revisores del núcleo definidos en .github/CODEOWNERS" + ("" if propietario else " (cambia @CAMBIAR-PROPIETARIO por tu usuario)"), "ok" if propietario else "aviso")
    if ganchos:
        try:
            import instalar_ganchos
            instalar_ganchos.instalar(repo, docs)
            res.add("Verificación automática en cada commit instalada (secretos, núcleo, límite de líneas)")
        except FileExistsError as exc:
            res.add("No se instaló la verificación automática: ya tienes un gancho pre-commit propio", "aviso", str(exc))
        except Exception as exc:  # noqa: BLE001 - un fallo de git no debe ocultar lo ya instalado
            res.add("No se pudo instalar la verificación automática", "aviso", str(exc))
    return res


def plan_actualizacion(pack: Path, repo: Path, docs: str) -> dict:
    repo, docs = cfgmod.normalizar(repo, docs)
    p = act.planificar(pack, repo, docs)
    return {"actual": p.adoptada, "nueva": p.nueva, "nuevos": len(p.de("añadir")), "reemplazar": len(p.de("reemplazar", "restaurar", "zona")),
            "conflictos": [a.rel for a in p.de("conflicto")], "modificados": [a.rel for a in p.de("modificado-local")],
            "degradacion": not p.sin_lock and lock.es_degradacion(p.adoptada, p.nueva),
            "mayor": lock.mayor(p.nueva) != lock.mayor(p.adoptada) and not p.sin_lock,
            "avisos": list(p.avisos), "migraciones": list(p.migraciones),
            "al_dia": not p.acciones and p.adoptada == p.nueva and not p.migraciones}


def actualizar_completo(pack: Path, repo: Path, docs: str, migracion: str = "") -> Resultado:
    repo, docs = cfgmod.normalizar(repo, docs)
    res = Resultado()
    try:
        p = act.planificar(pack, repo, docs)
        respaldo = act.aplicar(pack, repo, docs, p, migracion, probar=True)
    except (act.ErrorActualizacion, ValueError, OSError) as exc:
        res.add("No se pudo actualizar; tu proyecto quedó exactamente como estaba", "error", str(exc))
        return res
    for aviso in p.avisos:
        res.add(aviso, "aviso")
    res.add(f"Núcleo actualizado de {p.adoptada} a {p.nueva}: {len(p.de('añadir'))} archivos nuevos, {len(p.de('reemplazar', 'restaurar'))} reemplazados")
    if respaldo:
        res.add("Copia de seguridad del estado anterior (se puede deshacer)",
                detalle=f"{respaldo} · deshacer: python3 {docs}/scripts/respaldos.py restaurar actualizacion/{respaldo.name} --docs {docs} --aplicar")
    for ident, hecho in p.hechas:
        res.add(f"Migración {ident} aplicada", detalle="; ".join(hecho) or "no había nada que cambiar")
    if respaldo:
        res.add("Herramientas del proyecto probadas tras actualizar: arrancan bien (ganchos, CI y comandos)")
    for a in p.de("conflicto"):
        res.add(f"{a.rel}: editaste este archivo y también cambió en uxyngraphar", "aviso", f"Compara con {a.rel}.uxyngraphar-nuevo y decide a mano")
    for h in reparar(repo, docs):
        res.add(h)
    return res


def reparar(repo: Path, docs: str) -> list[str]:
    """Protecciones que versiones nuevas añaden y un proyecto ya instalado no tiene (CI, deny, .gitignore…). Idempotente; no toca contenido."""
    return [f"Protección al día: {h}" for h in doctor.arreglar(repo, docs)]


NIVEL_TEXTO = {"OK": "ok", "INFO": "ok", "WARN": "aviso", "ERROR": "error"}


def diagnostico(repo: Path, docs: str) -> Resultado:
    """El doctor en lenguaje llano: un paso por chequeo, con el arreglo cuando falla."""
    repo, docs = cfgmod.normalizar(repo, docs)
    res = Resultado()
    for c in doctor.diagnosticar(repo, docs):
        res.add(c.mensaje, NIVEL_TEXTO.get(c.nivel, "aviso"), c.arreglo)
    return res
