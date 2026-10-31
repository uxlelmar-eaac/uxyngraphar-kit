"""Control `reglas_proyecto` de la puerta: hace cumplir las reglas del proyecto (96-reglas-proyecto/) sin IA.

  · Una regla activa con `comprobacion_*` que falla en un archivo de código del cambio: bloquea si es de nivel
    bloqueante (o avisa si es de nivel aviso), salvo excepción declarada en una instrucción aprobada del cambio.
  · Una excepción declarada en una instrucción sin aprobar, o con `excepciones: prohibidas`, bloquea.
  · Cambiar archivos de 96-reglas-proyecto/ exige una instrucción aprobada del cambio que los tenga en sus anclas
    (con `cambios_reglas: solo_humano` el agente no puede tocarlos: reglas deny; la puerta no lo exige a la persona).
"""

from __future__ import annotations

import sys
from pathlib import Path

_AQUI = Path(__file__).resolve().parent
for p in (_AQUI.parent / "reglas", _AQUI.parent / "decisiones"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import reglas_proyecto as rp  # noqa: E402
from common_frontmatter import split_frontmatter  # noqa: E402


def _instrucciones(repo: Path, cambiados: list[str], docs: str) -> list[tuple[str, dict]]:
    """(ruta, frontmatter) de las instrucciones tocadas por el cambio, en cualquier estado."""
    salida = []
    for rel in cambiados:
        nombre = rel.rpartition("/")[2]
        if rel.startswith(f"{docs}/05-instrucciones/") and rel.endswith(".md") and not nombre.startswith("_") and nombre not in ("README.md", "INDICE.md"):
            f = repo / rel
            if f.is_file():
                fm, _c, _r = split_frontmatter(f.read_text(encoding="utf-8", errors="replace"))
                salida.append((rel, fm))
    return salida


def evaluar(repo: Path, cambiados: list[str], cfg: dict, docs: str, es_codigo) -> list[tuple[str, str]]:
    """Hallazgos como (nivel, mensaje)."""
    nivel_cfg = cfg["niveles"].get("reglas_proyecto", "bloqueante")
    if nivel_cfg == "apagado":
        return []
    modo_exc, modo_cambio = rp.config(cfg)
    hallazgos: list[tuple[str, str]] = []
    aprobadas: dict[str, dict[str, str]] = {}   # id instrucción → {regla: motivo}
    anclas_aprobadas: set[str] = set()
    for rel, fm in _instrucciones(repo, cambiados, docs):
        ident = str(fm.get("id") or Path(rel).stem)
        exc, problemas = rp.excepciones(fm)
        hallazgos += [(nivel_cfg, f"{ident}: {p}") for p in problemas]
        aprobada = str(fm.get("status", "")) in rp.ESTADOS_INSTRUCCION_APROBADA
        if exc and modo_exc == "prohibidas":
            hallazgos.append((nivel_cfg, f"{ident}: declara excepciones a reglas del proyecto ({', '.join(exc)}) y la configuración las prohíbe."))
        elif exc and not aprobada:
            hallazgos.append((nivel_cfg, f"{ident}: declara excepciones ({', '.join(exc)}) sin estar aprobada: una persona debe aprobar la instrucción."))
        elif exc:
            aprobadas[ident] = exc
        if aprobada:
            anclas = fm.get("anclas_codigo") or []
            anclas_aprobadas |= {rp.ruta_de_ancla(str(a)).replace("\\", "/").rstrip("/") for a in (anclas if isinstance(anclas, list) else [anclas])}

    docs_path = repo / docs
    fichas_ok = rp.fichas_excepcion_aprobadas(docs_path) if modo_exc == "ficha_aparte" else set()

    def exceptuada(regla: str) -> bool:
        if modo_exc == "prohibidas":
            return False
        for ident, exc in aprobadas.items():
            if regla in exc and (modo_exc == "en_instruccion" or (regla, ident) in fichas_ok):
                return True
        return False

    reglas = rp.activas(docs_path)
    for ruta in [c for c in cambiados if es_codigo(c)]:
        aplicables = [r for r in reglas if (r.prohibido or r.obligatorio) and rp.coincide(ruta, r.aplica_a)]
        if not aplicables:
            continue
        try:
            texto = (repo / ruta).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for r in aplicables:
            motivo = rp.incumplimiento(r, texto)
            if not motivo or exceptuada(r.id):
                continue
            nivel = nivel_cfg if r.nivel == "bloqueante" else "aviso"
            hallazgos.append((nivel, f"{ruta}: incumple {r.id} ({r.resumen}): {motivo}. Corrígelo o declara la excepción en la instrucción y que una persona la apruebe."))

    if modo_cambio == "instruccion_aprobada":
        prefijo = f"{docs}/{rp.CARPETA}/"
        # Solo las reglas y fichas de excepción: INDICE.md es derivado (lo vigila el doctor) y _PLANTILLA/_PROTOCOLO son núcleo.
        tocados = [c for c in cambiados if c.startswith(prefijo) and c.rpartition("/")[2].startswith(("RP-", "EX-"))]
        carpeta = {prefijo.rstrip("/"), prefijo[len(docs) + 1:].rstrip("/")}
        sin_ancla = [c for c in tocados if c not in anclas_aprobadas and c[len(docs) + 1:] not in anclas_aprobadas
                     and not (anclas_aprobadas & carpeta)]
        if sin_ancla:
            hallazgos.append((nivel_cfg, f"Reglas del proyecto cambiadas sin una instrucción aprobada que las ancle: {', '.join(sin_ancla[:5])}. "
                                         "Crear, editar o retirar reglas exige aprobación humana explícita."))
    return hallazgos
