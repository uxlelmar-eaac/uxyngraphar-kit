"""Compuerta «implementado»: ¿el sistema está implementado de verdad o es un esqueleto?

La validación de formato (`especificacion.validar_sistema`) dice si un sistema *cumple el protocolo*; esta compuerta
dice si su contenido es suficiente para que cualquier agente trabaje con él (ESPECIFICACION.md, «Núcleo implementado»).
Se aplica al crear con uxyn, al marcar «listo» y al publicar. Los errores bloquean; los avisos solo se muestran.

`evaluar(carpeta)` → {"implementado": bool, "errores": [...], "avisos": [...], "metricas": {...}}.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import especificacion as esp

base = esp.base

MARCADOR = re.compile(r"\{\{[^}\n]*\}\}|\bTODO\b|\bFIXME\b|\b[Pp]or definir\b|\b[Ll]orem ipsum\b")
REGLA = re.compile(r"^\s*\d+\.\s+\S", re.M)
VINETA = re.compile(r"^\s*(?:[-*]|\d+\.)\s+\S", re.M)
OTRO_SISTEMA = re.compile(r"sistemas-de-gobernanza/([a-z0-9]+(?:-[a-z0-9]+)*)")
MIN_PROBLEMAS, MAX_PROBLEMAS = 1, 5
MIN_FUERA, MIN_ACTIVACION = 2, 2
MIN_REGLAS, MIN_DETENERSE = 5, 3
MIN_RECORDAR, MIN_NO_RECORDAR = 2, 2
MIN_PASOS, AVISO_PASOS = 2, 3
MIN_ROL = 100            # caracteres de la introducción si no hay «## Rol del agente»
MIN_SECCION = 40         # caracteres de contenido de una sección del núcleo
AVISO_NUCLEO_BYTES = 9000
AVISO_FASES, AVISO_SKILLS = 3, 2
# Secciones de SISTEMA.md: (nombre que se muestra, prefijos aceptados ya normalizados).
SECCIONES_SISTEMA = (
    ("Qué resuelve", ("que resuelve",)),
    ("Problemas que cubre", ("problemas",)),
    ("Fuera de alcance", ("fuera de alcance",)),
    ("Cuándo usarlo", ("cuando usarlo",)),
    ("Cuándo no usarlo", ("cuando no usarlo",)),
    ("Entradas y salidas", ("entradas y salidas",)),
    ("Sistemas complementarios", ("sistemas complementarios", "complementarios")),
)
# Donde un marcador sí es un error (plantillas y andamiaje usan sus propias variables a propósito).
CON_MARCADORES = ("proceso/", "skills/", "ejemplos/")
RAIZ_CON_MARCADORES = (*base.NUCLEO, "CHANGELOG.md", "HERRAMIENTAS.md", "COMPONENTES.md")


def normalizar(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", t)).strip()


def secciones(texto: str, nivel: str = "## ") -> dict[str, str]:
    """{título normalizado: contenido} de las secciones de un nivel (el contenido llega hasta la siguiente del mismo nivel o superior)."""
    salida: dict[str, str] = {}
    actual: str | None = None
    lineas: list[str] = []
    for linea in texto.splitlines():
        if linea.startswith("# ") or linea.startswith(nivel) and not linea.startswith(nivel + "#"):
            if actual is not None:
                salida[actual] = "\n".join(lineas).strip()
            actual = normalizar(linea.lstrip("#")) if linea.startswith(nivel) else None
            lineas = []
        elif actual is not None:
            lineas.append(linea)
    if actual is not None:
        salida[actual] = "\n".join(lineas).strip()
    return salida


def _buscar(secs: dict[str, str], prefijos: tuple[str, ...]) -> str | None:
    for titulo, contenido in secs.items():
        if any(titulo.startswith(p) for p in prefijos):
            if prefijos == ("cuando usarlo",) and titulo.startswith("cuando no"):
                continue
            return contenido
    return None


def introduccion(texto: str) -> str:
    """Lo que hay entre el título «# …» y la primera sección «## …»."""
    partes = []
    visto_titulo = False
    for linea in texto.splitlines():
        if linea.startswith("# ") and not visto_titulo:
            visto_titulo = True
            continue
        if linea.startswith("## "):
            break
        if visto_titulo:
            partes.append(linea)
    return "\n".join(partes).strip()


def _contenido(texto: str | None) -> int:
    return len(re.sub(r"\s+", " ", texto or "").strip())


def _leer(ruta: Path) -> str:
    try:
        return ruta.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _textos(carpeta: Path) -> dict[str, str]:
    salida = {}
    for rel in base.archivos_del_sistema(carpeta):
        if rel.startswith(esp.DESTINO_COMUN + "/") or rel == base.INTEGRIDAD:
            continue
        datos = (carpeta / rel).read_bytes()
        if b"\x00" in datos:
            continue
        try:
            salida[rel] = datos.decode("utf-8")
        except UnicodeDecodeError:
            continue
    return salida


def _fases(carpeta: Path, m: dict) -> list[Path]:
    orden = [f for f in (m.get("proceso") or []) if isinstance(f, str)]
    carpeta_p = carpeta / "proceso"
    if not carpeta_p.is_dir():
        return []
    todas = sorted(p for p in carpeta_p.glob("*.md") if p.name.lower() != "readme.md")
    por_nombre = {p.stem: p for p in todas}
    return [por_nombre[f] for f in orden if f in por_nombre] + [p for p in todas if p.stem not in orden]


def evaluar(carpeta: Path) -> dict:
    carpeta = Path(carpeta)
    errores: list[str] = []
    avisos: list[str] = []
    try:
        m = base.leer_manifiesto(carpeta)
    except (OSError, ValueError) as e:
        return {"implementado": False, "errores": [f"{base.MANIFIESTO}: {e}"], "avisos": [], "metricas": {}}
    pid = str(m.get("id") or carpeta.name)
    textos = _textos(carpeta)

    # ── sistema.json ──
    alcance = m.get("alcance") if isinstance(m.get("alcance"), dict) else {}
    problemas = [p for p in (alcance.get("problemas") or []) if isinstance(p, dict)]
    fuera = [f for f in (alcance.get("fuera_de_alcance") or []) if isinstance(f, dict)]
    activacion = [a for a in (m.get("activacion") or []) if isinstance(a, str) and a.strip()]
    if len(problemas) < MIN_PROBLEMAS:
        errores.append("sistema.json: declara al menos un problema en «alcance.problemas»")
    if len(problemas) > MAX_PROBLEMAS:
        avisos.append(f"sistema.json: {len(problemas)} problemas (más de {MAX_PROBLEMAS}); conviene dividirlo en sistemas "
                      "más específicos unidos por un flujo")
    if len(fuera) < MIN_FUERA:
        errores.append(f"sistema.json: «alcance.fuera_de_alcance» necesita al menos {MIN_FUERA} temas, cada uno con «derivar_a» "
                       "(el sistema al que se deriva, o null si no lo cubre nadie)")
    elif any("derivar_a" not in f or not str(f.get("tema") or "").strip() for f in fuera):
        errores.append("sistema.json: cada tema de «fuera_de_alcance» lleva «tema» y «derivar_a»")
    if len(activacion) < MIN_ACTIVACION:
        errores.append(f"sistema.json: «activacion» necesita al menos {MIN_ACTIVACION} frases con las que una persona lo pide")
    if not m.get("verificaciones"):
        errores.append("sistema.json: sin «verificaciones»")

    # ── marcadores (núcleo, proceso, skills, ejemplos, CHANGELOG…) ──
    for rel, contenido in textos.items():
        if rel in RAIZ_CON_MARCADORES or rel.startswith(CON_MARCADORES):
            limpio = contenido
            if rel in (base.ENTRADA, base.PERMISOS):
                limpio = re.sub(r"<!-- uxyngraphar:\w+:inicio -->.*?<!-- uxyngraphar:\w+:fin -->", "", contenido, flags=re.S)
            hallados = sorted({x.group(0) for x in MARCADOR.finditer(limpio)})
            if hallados:
                errores.append(f"{rel}: texto sin rellenar ({', '.join(hallados[:3])})")

    # ── SISTEMA.md ──
    sistema = textos.get(base.DESCRIPCION, "")
    secs = secciones(sistema)
    rol = _buscar(secs, ("rol del agente", "rol", "identidad"))
    if _contenido(rol) < MIN_SECCION and _contenido(introduccion(sistema)) < MIN_ROL:
        errores.append("SISTEMA.md: falta «## Rol del agente» (quién es el agente con este sistema, de qué responde y cómo "
                       "trabaja) o una introducción que lo diga")
    for nombre, prefijos in SECCIONES_SISTEMA:
        seccion = _buscar(secs, prefijos)
        if seccion is None:
            errores.append(f"SISTEMA.md: falta la sección «## {nombre}»")
        elif _contenido(seccion) < (10 if nombre == "Sistemas complementarios" else MIN_SECCION):
            errores.append(f"SISTEMA.md: «## {nombre}» está casi vacía")
    for p in problemas:
        if p.get("id") and f"`{p['id']}`" not in sistema and str(p["id"]) not in sistema:
            errores.append(f"SISTEMA.md: el problema «{p['id']}» no se explica en «Problemas que cubre»")

    # ── LIMITES.md ──
    limites = textos.get(base.LIMITES, "")
    detenerse = _buscar(secciones(limites), ("cuando detenerse", "detente", "cuando parar"))
    reglas_txt = limites.split("## ", 1)[0] if detenerse is not None else limites
    reglas = len(REGLA.findall(reglas_txt))
    n_detenerse = len(VINETA.findall(detenerse or ""))
    if reglas < MIN_REGLAS:
        errores.append(f"LIMITES.md: {reglas} reglas numeradas; hacen falta al menos {MIN_REGLAS} comprobables, cada una con cómo cumplirla")
    if n_detenerse < MIN_DETENERSE:
        errores.append(f"LIMITES.md: «## Cuándo detenerse y preguntar» necesita al menos {MIN_DETENERSE} casos ({n_detenerse})")

    # ── PERMISOS.md ──
    permisos = textos.get(base.PERMISOS, "")
    if "<!-- uxyngraphar:permisos:inicio -->" not in permisos:
        errores.append("PERMISOS.md: falta el bloque generado (uxyngraphar indice-sistema)")
    por_que = _buscar(secciones(permisos), ("por que",))
    if _contenido(por_que) < 20:
        avisos.append("PERMISOS.md: «## Por qué» explica por qué cada acción o ruta queda para la persona")

    # ── MEMORIAS.md ──
    memorias = secciones(textos.get(base.MEMORIAS, ""))
    recordar = len(VINETA.findall(_buscar(memorias, ("que recordar",)) or ""))
    no_recordar = len(VINETA.findall(_buscar(memorias, ("que no recordar",)) or ""))
    if recordar < MIN_RECORDAR:
        errores.append(f"MEMORIAS.md: «## Qué recordar» necesita al menos {MIN_RECORDAR} puntos ({recordar})")
    if no_recordar < MIN_NO_RECORDAR:
        errores.append(f"MEMORIAS.md: «## Qué no recordar» necesita al menos {MIN_NO_RECORDAR} puntos ({no_recordar})")

    # ── README.md: parte del autor ──
    readme = re.sub(r"<!-- uxyngraphar:entrada:inicio -->.*?<!-- uxyngraphar:entrada:fin -->", "",
                    textos.get(base.ENTRADA, ""), flags=re.S)
    if _contenido("\n".join(x for x in readme.splitlines() if not x.startswith("# "))) < MIN_SECCION:
        avisos.append("README.md: añade la parte del autor (qué es, cómo se pide y un ejemplo de instrucción) además del bloque generado")

    # ── mínimo operable ──
    piezas = set(m.get("piezas") or [])
    fases = _fases(carpeta, m) if "proceso" in piezas else []
    if not fases:
        errores.append("proceso: hace falta al menos una fase (proceso/<fase>.md con Objetivo, Pasos y Criterio de salida)")
    cubiertos = set()
    for f in fases:
        rel = f"proceso/{f.name}"
        texto = textos.get(rel, "")
        s = secciones(texto)
        for nombre, prefijo in (("Objetivo", "objetivo"), ("Pasos", "pasos"), ("Criterio de salida", "criterio de salida")):
            if _buscar(s, (prefijo,)) is None:
                errores.append(f"{rel}: falta «## {nombre}»")
        pasos = len(REGLA.findall(_buscar(s, ("pasos",)) or ""))
        if _buscar(s, ("pasos",)) is not None and pasos < MIN_PASOS:
            errores.append(f"{rel}: «## Pasos» tiene {pasos}; hacen falta al menos {MIN_PASOS} verificables")
        elif _buscar(s, ("pasos",)) is not None and pasos < AVISO_PASOS:
            avisos.append(f"{rel}: «## Pasos» tiene {pasos}; lo habitual son {AVISO_PASOS} o más")
        fm, _ = base.leer_frontmatter(texto)
        res = fm.get("resuelve")
        if isinstance(res, list):
            cubiertos |= {str(x) for x in res}
    skills = sorted(p for p in (carpeta / "skills").glob("*/SKILL.md")) if "skills" in piezas else []
    skills = [p for p in skills if _contenido(_leer(p)) >= MIN_SECCION]
    if not skills:
        errores.append("skills: hace falta al menos una skill (skills/<nombre>/SKILL.md)")
    ejemplos = [r for r in textos if r.startswith("ejemplos/") and _contenido(textos[r]) >= MIN_SECCION]
    if "ejemplos" not in piezas or not ejemplos:
        errores.append("ejemplos: hace falta al menos un ejemplo real (ejemplos/<caso>.md)")
    if "cambios" not in piezas or "CHANGELOG.md" not in textos:
        errores.append("cambios: falta CHANGELOG.md (pieza «cambios»)")
    propios = sorted((carpeta / "scripts").glob("*.py")) if (carpeta / "scripts").is_dir() else []
    if propios:
        if "herramientas" not in piezas:
            errores.append("herramientas: tiene scripts propios; HERRAMIENTAS.md dice para qué sirve cada uno")
        if "pruebas" not in piezas or not list((carpeta / "pruebas").glob("test_*.py")):
            errores.append("pruebas: tiene scripts propios; hacen falta pruebas (pruebas/test_<tema>.py)")
    resto = " ".join(textos.get(r, "") for r in textos if r.startswith(("proceso/", "skills/")))
    for p in problemas:
        pid_p = str(p.get("id") or "")
        if pid_p and fases and pid_p not in cubiertos and pid_p not in resto:
            errores.append(f"proceso: ninguna fase ni skill cubre el problema «{pid_p}» (añádelo a «resuelve» de la fase que lo resuelve)")

    # ── desacoplamiento: nada de leer otros sistemas ──
    for rel, texto in textos.items():
        if rel.startswith(("ejemplos/", "referencia/", "plantillas/", "andamiaje/")):
            continue   # ilustran lo que hace una persona; no son instrucciones para el agente
        otros = sorted({x for x in OTRO_SISTEMA.findall(texto) if x not in (pid, "id")})
        if otros:
            errores.append(f"{rel}: cita archivos de otro sistema ({', '.join(otros[:3])}); los sistemas solo se combinan con flujos")

    # ── avisos de calidad (no bloquean) ──
    nucleo_bytes = sum(len(textos.get(n, "").encode("utf-8")) for n in base.NUCLEO)
    if nucleo_bytes < AVISO_NUCLEO_BYTES:
        avisos.append(f"núcleo: {nucleo_bytes} bytes; los sistemas de referencia rondan 9–18 KB (¿falta profundidad?)")
    if fases and len(fases) < AVISO_FASES:
        avisos.append(f"proceso: {len(fases)} fase(s); lo habitual son {AVISO_FASES} o más")
    if skills and len(skills) < AVISO_SKILLS:
        avisos.append(f"skills: {len(skills)} skill; lo habitual son {AVISO_SKILLS} o más")

    metricas = {"nucleo_bytes": nucleo_bytes, "problemas": len(problemas), "fuera_de_alcance": len(fuera),
                "activacion": len(activacion), "reglas": reglas, "detenerse": n_detenerse, "recordar": recordar,
                "no_recordar": no_recordar, "fases": len(fases), "skills": len(skills), "ejemplos": len(ejemplos),
                "archivos": len(textos)}
    return {"implementado": not errores, "errores": errores, "avisos": avisos, "metricas": metricas}


def resumen(r: dict) -> str:
    if r["implementado"]:
        return "Implementado ✓"
    return f"No implementado: {len(r['errores'])} pendiente(s)"


if __name__ == "__main__":   # pragma: no cover - ayuda manual
    import sys
    print(json.dumps(evaluar(Path(sys.argv[1])), ensure_ascii=False, indent=2))
