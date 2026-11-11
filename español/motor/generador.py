"""Generador de sistemas del catálogo, para personas y para agentes de IA (método: GENERADOR.md y GUIA-PARA-AGENTES.md).

Dos modos sobre la misma base que `catalogo.crear`:
  - completo: `desde_spec` escribe el sistema entero a partir de una especificación JSON (`plantilla_spec` da una de
    partida). Se genera en una carpeta oculta del catálogo y solo pasa al catálogo si valida sin errores.
  - guiado: `catalogo.crear` deja el esqueleto con marcadores {{…}} y `pendientes` dice qué falta, dónde y qué hacer después.

Todas las funciones devuelven datos (listas y diccionarios); la CLI y el panel deciden cómo mostrarlos.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import catalogo
import entrada
import especificacion as esp
import nomenclatura
import piezas

base = esp.base
FORMATO_SPEC = 1
OCULTA = ".generando-"
TEXTOS_OBLIGATORIOS = ("id", "titulo", "descripcion", "familia", "resumen", "que_resuelve", "entradas", "salidas")
GENERADAS = ("proceso", "skills", "plantillas", "ejemplos", "cambios")
NUCLEO = base.NUCLEO
LIMITES_POR_DEFECTO = {
    "reglas": ["Solo se escribe en `uxyngraphar/trabajo/<id>/` y en el código que el pedido pida."],
    "detenerse": ["El pedido cae fuera del alcance del sistema o pide una acción de «Solo una persona» (PERMISOS.md)."],
}
PERMISOS_VACIOS = {"rutas": {"protegidas": [], "fuera_de_ia": []}, "acciones": {"agente": [], "solo_persona": []}}
MEMORIAS_POR_DEFECTO = {
    "recordar": ["Acuerdos con la persona sobre cómo aplicar este sistema en el proyecto que no están escritos en otra parte.",
                 "Particularidades del proyecto que cambian la forma de trabajar del sistema (rutas, nombres, excepciones aceptadas)."],
    "no_recordar": ["Lo que ya vive en fichas, en el código o en otro sistema: se enlaza, no se copia.",
                    "Datos que caducan enseguida (estado de una tarea, ramas, fechas sueltas) y secretos o credenciales."],
}
SIN_MARCADORES = ("plantillas/",)   # las plantillas de fichas llevan {{id}}, {{status}}… a propósito

AYUDA = {
    "formato": f"versión del formato de especificación (hoy {FORMATO_SPEC})",
    "id": "2 a 5 palabras kebab-case; empieza por el objeto gobernado (NOMENCLATURA.md)",
    "titulo": "las palabras del id, en orden, con tildes y mayúscula inicial",
    "descripcion": "una frase (máx. 300 caracteres) para el catálogo",
    "familia": " | ".join(nomenclatura.NORMA["familias"]),
    "activacion": "frases extra para activarlo (el id y el id con espacios se añaden solos)",
    "resumen": "una o dos frases: qué garantiza el sistema (abre SISTEMA.md)",
    "que_resuelve": "el problema de fondo en lenguaje llano: qué sale mal sin el sistema",
    "problemas": "[{id: síntoma en kebab-case, descripcion}] — idealmente 1 a 5",
    "fuera_de_alcance": "[{tema, derivar_a: id de un sistema del catálogo o null}] — al menos uno",
    "cuando_usarlo / cuando_no_usarlo": "listas de situaciones concretas",
    "entradas / salidas": "qué necesita del proyecto o de la persona / qué deja",
    "complementarios": "[{id, motivo}] sistemas del catálogo que se combinan con este",
    "decide_la_persona": "lo que solo decide una persona (va al README)",
    "limites": "{reglas: [reglas duras y comprobables], detenerse: [cuándo parar y preguntar]} → LIMITES.md (núcleo; si falta, texto genérico)",
    "permisos": "{rutas: {protegidas, fuera_de_ia}, acciones: {agente, solo_persona}} → «permisos» del manifiesto y PERMISOS.md (núcleo)",
    "proceso": "[{fase, titulo?, condicion?, objetivo, entradas?, pasos, criterio_salida, resuelve, skills?}] en orden",
    "skills": "[{nombre, titulo?, descripcion, resuelve, cuando, pasos, resultado?}] una acción por skill",
    "fichas": "{tipo: {prefijo?, inicial, estados: {status: carpeta} o status_validos, solo_humano?, espera_humano?, secciones?}}",
    "ajustes": "valores por defecto que cada proyecto puede cambiar en su ajustes.json",
    "ejemplos": "[{nombre, titulo, pedido, recorrido, resultado}] casos resueltos",
    "memorias": "{recordar: [qué conviene memorizar del proyecto], no_recordar: [qué no]} → MEMORIAS.md (núcleo; si falta, texto genérico)",
    "piezas_extra": f"piezas que se añaden con marcadores para completar a mano: {', '.join(p for p in base.PIEZAS if p not in GENERADAS)}",
}


# ---------- especificación ----------

def plantilla_spec(pid: str = "contratos-de-pago", familia: str = "proceso") -> dict:
    """Especificación de partida, válida en forma: se cambian los textos y se borra lo que no haga falta."""
    titulo = pid.replace("-", " ").capitalize()
    return {
        "_ayuda": AYUDA,
        "formato": FORMATO_SPEC,
        "id": pid,
        "titulo": titulo,
        "descripcion": f"Qué hace {titulo.lower()}, en una frase.",
        "familia": familia,
        "activacion": [],
        "resumen": "Qué garantiza el sistema y en qué trabajo se usa.",
        "que_resuelve": "Qué sale mal hoy sin este sistema.",
        "problemas": [{"id": "sintoma-principal", "descripcion": "El síntoma concreto que se ve en el proyecto."}],
        "fuera_de_alcance": [{"tema": "Lo que este sistema no resuelve", "derivar_a": None}],
        "cuando_usarlo": ["Situación concreta en la que se activa."],
        "cuando_no_usarlo": ["Situación en la que no aplica."],
        "entradas": "Qué necesita del proyecto o de la persona.",
        "salidas": f"Qué deja (fichas en uxyngraphar/trabajo/{pid}/, código, informes).",
        "complementarios": [],
        "decide_la_persona": ["Qué aprueba o rechaza solo una persona."],
        "limites": {"reglas": ["Regla dura y comprobable."], "detenerse": ["Cuándo el agente no sigue solo."]},
        "permisos": json.loads(json.dumps(PERMISOS_VACIOS)),
        "proceso": [{"fase": "preparar", "objetivo": "Qué queda claro antes de tocar nada.", "entradas": ["Qué se lee."],
                     "pasos": ["Paso concreto, con el comando o archivo exacto."], "criterio_salida": ["Cómo se sabe que terminó."],
                     "resuelve": ["sintoma-principal"], "skills": ["accion-principal"]}],
        "skills": [{"nombre": "accion-principal", "descripcion": "Qué hace la skill y cuándo usarla, en una frase.",
                    "resuelve": ["sintoma-principal"], "cuando": ["Situación que la dispara."],
                    "pasos": ["Paso concreto, con el comando o archivo exacto."], "resultado": ["Qué deja hecho."]}],
        "ajustes": {},
        "ejemplos": [],
        "memorias": {"recordar": ["Qué dato del proyecto necesita este sistema y se pierde entre conversaciones."],
                     "no_recordar": ["Lo que ya vive en fichas, código u otros sistemas."]},
        "piezas_extra": [],
    }


def _texto(v) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _textos(v, minimo: int = 0) -> bool:
    return isinstance(v, list) and len(v) >= minimo and all(_texto(x) for x in v)


def _marcadores(valor, donde: str = "") -> list[str]:
    if isinstance(valor, str):
        return [f"{donde or 'spec'}: contiene el marcador {piezas.MARCADOR.search(valor).group()}"] if piezas.MARCADOR.search(valor) else []
    if isinstance(valor, dict):
        return [e for k, v in valor.items() if k != "_ayuda" for e in _marcadores(v, f"{donde}.{k}" if donde else k)]
    if isinstance(valor, list):
        return [e for i, v in enumerate(valor) for e in _marcadores(v, f"{donde}[{i}]")]
    return []


def _frontmatter_seguro(v: str) -> bool:
    return "\n" not in v and " #" not in v


def piezas_de(spec: dict) -> list[str]:
    """Piezas del sistema que saldrá de la especificación, en el orden del protocolo."""
    elegidas = {"cambios", *(spec.get("piezas_extra") or [])}
    for clave in ("proceso", "skills", "ejemplos"):
        if spec.get(clave):
            elegidas.add(clave)
    if spec.get("fichas"):
        elegidas.add("plantillas")
    return [p for p in base.PIEZAS if p in elegidas]


def validar_spec(spec, raiz: Path | None = None) -> dict:
    """{"errores": […], "avisos": […]} de la especificación, sin escribir nada. Errores = no se puede generar."""
    if not isinstance(spec, dict):
        return {"errores": ["la especificación debe ser un objeto JSON"], "avisos": []}
    errores: list[str] = []
    avisos: list[str] = []
    if spec.get("formato", FORMATO_SPEC) != FORMATO_SPEC:
        errores.append(f"formato: este motor genera el formato {FORMATO_SPEC}")
    for campo in TEXTOS_OBLIGATORIOS:
        if not _texto(spec.get(campo)):
            errores.append(f"{campo}: obligatorio (texto)")
    if errores:
        return {"errores": errores, "avisos": avisos}
    pid = spec["id"]
    errores += nomenclatura.problemas_id(pid) + nomenclatura.problemas_titulo(pid, spec["titulo"])
    if spec["familia"] not in nomenclatura.NORMA["familias"]:
        errores.append(f"familia «{spec['familia']}»: una de {', '.join(nomenclatura.NORMA['familias'])}")
    if len(spec["descripcion"]) > nomenclatura.MAX_DESCRIPCION:
        errores.append(f"descripcion: máximo {nomenclatura.MAX_DESCRIPCION} caracteres")
    sistemas = catalogo._sistemas(raiz)
    if pid in sistemas:
        errores.append(f"id «{pid}»: ya existe en el catálogo")
    errores += [f"id «{pid}»: choca con «{otro}» (uno es prefijo del otro)" for otro in sistemas
                if otro != pid and (otro.startswith(pid + "-") or pid.startswith(otro + "-"))]
    activacion = spec.get("activacion", [])
    if not _textos(activacion):
        errores.append("activacion: lista de frases")
    else:
        errores += [f"activacion «{f}»: minúsculas ASCII sin tildes ni signos" for f in activacion if not nomenclatura.FRASE.match(f)]

    problemas = spec.get("problemas")
    ids: set[str] = set()
    if not isinstance(problemas, list) or not problemas:
        errores.append("problemas: al menos uno {id, descripcion}")
    else:
        for i, p in enumerate(problemas):
            if not isinstance(p, dict) or not isinstance(p.get("id"), str) or not base.ID_VALIDO.match(p["id"]) or not _texto(p.get("descripcion")):
                errores.append(f"problemas[{i}]: {{id: kebab-case, descripcion: texto}}")
            elif p["id"] in ids:
                errores.append(f"problemas: id repetido «{p['id']}»")
            else:
                ids.add(p["id"])
        if len(problemas) > piezas.MAX_PROBLEMAS:
            avisos.append(f"problemas: {len(problemas)} (más de {piezas.MAX_PROBLEMAS}); posible sistema generalista, valora dividirlo")

    fuera = spec.get("fuera_de_alcance")
    if not isinstance(fuera, list) or not fuera:
        errores.append("fuera_de_alcance: al menos una entrada {tema, derivar_a}")
    else:
        for i, f in enumerate(fuera):
            derivar = f.get("derivar_a") if isinstance(f, dict) else None
            if not isinstance(f, dict) or not _texto(f.get("tema")):
                errores.append(f"fuera_de_alcance[{i}]: {{tema: texto, derivar_a: id o null}}")
            elif derivar is not None and derivar not in sistemas:
                errores.append(f"fuera_de_alcance[{i}].derivar_a «{derivar}»: no es un sistema del catálogo (o null)")
    if not _textos(spec.get("cuando_usarlo"), 1):
        errores.append("cuando_usarlo: al menos una situación")
    for campo in ("cuando_no_usarlo", "decide_la_persona"):
        if campo in spec and not _textos(spec[campo]):
            errores.append(f"{campo}: lista de textos")
    for i, c in enumerate(spec.get("complementarios") or []):
        if not isinstance(c, dict) or c.get("id") not in sistemas or not _texto(c.get("motivo")):
            errores.append(f"complementarios[{i}]: {{id: sistema del catálogo, motivo: texto}}")

    limites = spec.get("limites")
    if limites is not None and (not isinstance(limites, dict) or not _textos(limites.get("reglas"), 1)
                                or not _textos(limites.get("detenerse"), 1)):
        errores.append("limites: {reglas: al menos una, detenerse: al menos una}")
    elif limites is None:
        avisos.append("limites: sin «limites»; LIMITES.md saldrá con reglas genéricas")
    if "permisos" in spec:
        errores += base.validar_permisos(spec["permisos"])

    nombres_skills: set[str] = set()
    for i, s in enumerate(spec.get("skills") or []):
        donde = f"skills[{i}]"
        if not isinstance(s, dict) or not isinstance(s.get("nombre"), str) or not base.ID_VALIDO.match(s["nombre"]):
            errores.append(f"{donde}.nombre: kebab-case")
            continue
        if s["nombre"] in nombres_skills:
            errores.append(f"{donde}: skill repetida «{s['nombre']}»")
        nombres_skills.add(s["nombre"])
        if not _texto(s.get("descripcion")) or not _frontmatter_seguro(s["descripcion"]):
            errores.append(f"{donde}.descripcion: una línea, sin « #»")
        for campo, minimo in (("cuando", 1), ("pasos", 1), ("resultado", 0)):
            if not _textos(s.get(campo, []), minimo):
                errores.append(f"{donde}.{campo}: lista de textos" + (" (al menos uno)" if minimo else ""))
        errores += _resuelve(donde, s.get("resuelve"), ids)
        if not s.get("resuelve"):
            avisos.append(f"{donde}: sin «resuelve» (¿qué problema atiende?)")

    fases: set[str] = set()
    for i, f in enumerate(spec.get("proceso") or []):
        donde = f"proceso[{i}]"
        if not isinstance(f, dict) or not isinstance(f.get("fase"), str) or not base.ID_VALIDO.match(f["fase"]):
            errores.append(f"{donde}.fase: kebab-case")
            continue
        if f["fase"] in fases:
            errores.append(f"{donde}: fase repetida «{f['fase']}»")
        fases.add(f["fase"])
        if not _texto(f.get("objetivo")):
            errores.append(f"{donde}.objetivo: obligatorio (texto)")
        for campo, minimo in (("pasos", 1), ("criterio_salida", 1), ("entradas", 0)):
            if not _textos(f.get(campo, []), minimo):
                errores.append(f"{donde}.{campo}: lista de textos" + (" (al menos uno)" if minimo else ""))
        errores += _resuelve(donde, f.get("resuelve"), ids)
        citadas = f.get("skills") or []
        if not _textos(citadas):
            errores.append(f"{donde}.skills: lista de nombres de skills")
        else:
            errores += [f"{donde}.skills: cita «{s}», que no está en «skills»" for s in citadas if s not in nombres_skills]

    usados = _prefijos_usados(sistemas)
    fichas = spec.get("fichas") or {}
    if not isinstance(fichas, dict):
        errores.append("fichas: objeto {tipo: definición}")
        fichas = {}
    for tipo, d in fichas.items():
        donde = f"fichas.{tipo}"
        if not base.ID_VALIDO.match(tipo) or not isinstance(d, dict):
            errores.append(f"{donde}: tipo kebab-case con una definición (objeto)")
            continue
        prefijo = d.get("prefijo")
        if prefijo is not None and (not nomenclatura.PREFIJO.match(str(prefijo)) or prefijo in nomenclatura.NORMA["prefijos_reservados"]):
            errores.append(f"{donde}.prefijo «{prefijo}»: 3 letras mayúsculas, no reservadas")
        elif prefijo in usados:
            errores.append(f"{donde}.prefijo «{prefijo}»: ya lo usa {usados[prefijo]}")
        if "secciones" in d and not _textos(d["secciones"]):
            errores.append(f"{donde}.secciones: lista de títulos de sección")
    if "ajustes" in spec and not isinstance(spec["ajustes"], dict):
        errores.append("ajustes: objeto con valores por defecto")
    memorias = spec.get("memorias")
    if memorias is not None and (not isinstance(memorias, dict) or not _textos(memorias.get("recordar"), 1)
                                 or not _textos(memorias.get("no_recordar"), 1)):
        errores.append("memorias: {recordar: al menos uno, no_recordar: al menos uno}")
    elif memorias is None:
        avisos.append("memorias: sin «memorias»; MEMORIAS.md saldrá con un texto genérico")
    for i, e in enumerate(spec.get("ejemplos") or []):
        if not isinstance(e, dict) or not isinstance(e.get("nombre"), str) or not base.ID_VALIDO.match(e["nombre"]) \
                or not all(_texto(e.get(k)) for k in ("titulo", "pedido", "recorrido", "resultado")):
            errores.append(f"ejemplos[{i}]: {{nombre: kebab-case, titulo, pedido, recorrido, resultado}}")
    extra = spec.get("piezas_extra") or []
    if not _textos(extra):
        errores.append("piezas_extra: lista de piezas")
    else:
        errores += [f"piezas_extra «{p}»: una de {', '.join(x for x in base.PIEZAS if x not in GENERADAS)}"
                    for p in extra if p not in base.PIEZAS or p in GENERADAS]
    errores += _marcadores(spec)

    if not errores:
        cubiertos = {r for x in (*(spec.get("proceso") or []), *(spec.get("skills") or [])) for r in x.get("resuelve") or []}
        if spec.get("proceso") or spec.get("skills"):
            avisos += [f"problemas: «{p}» no lo cubre ninguna fase ni skill" for p in sorted(ids - cubiertos)]
        else:
            avisos.append("sin «proceso» ni «skills»: el agente no tendrá pasos que seguir")
        elegidas = piezas_de(spec)
        faltan = [p for p in piezas.RECOMENDADAS.get(spec["familia"], ()) if p not in elegidas]
        if faltan:
            avisos.append(f"piezas recomendadas para «{spec['familia']}» que faltan: {', '.join(faltan)}")
    return {"errores": errores, "avisos": avisos}


def _resuelve(donde: str, valores, ids: set[str]) -> list[str]:
    if valores is None:
        return []
    if not _textos(valores):
        return [f"{donde}.resuelve: lista de ids de «problemas»"]
    return [f"{donde}.resuelve: cita «{v}», que no está en «problemas»" for v in valores if v not in ids]


def _prefijos_usados(sistemas: dict[str, tuple[Path, dict]]) -> dict[str, str]:
    return {d.get("prefijo"): f"{pid}.{tipo}" for pid, (_, m) in sistemas.items() for tipo, d in m.get("fichas", {}).items()}


# ---------- escritura ----------

def _vinetas(items) -> str:
    return "\n".join(f"- {x}" for x in items)


def _numeradas(items) -> str:
    return "\n".join(f"{i}. {x}" for i, x in enumerate(items, 1))


def _lista_fm(items) -> str:
    return "[" + ", ".join(items or []) + "]"


def _sistema_md(spec: dict) -> str:
    fuera = [f"{f['tema']}: " + (f"`{f['derivar_a']}`" if f.get("derivar_a") else "no lo cubre el kit") + "."
             for f in spec["fuera_de_alcance"]]
    partes = [f"# {spec['titulo']}", spec["resumen"],
              "## Qué resuelve", spec["que_resuelve"],
              "## Problemas que cubre", _vinetas(f"`{p['id']}`: {p['descripcion']}" for p in spec["problemas"]),
              "## Fuera de alcance", _vinetas(fuera),
              "## Cuándo usarlo", _vinetas(spec["cuando_usarlo"])]
    if spec.get("cuando_no_usarlo"):
        partes += ["## Cuándo no usarlo", _vinetas(spec["cuando_no_usarlo"])]
    partes += ["## Entradas y salidas", _vinetas([f"Entradas: {spec['entradas']}", f"Salidas: {spec['salidas']}"])]
    if spec.get("complementarios"):
        partes += ["## Sistemas complementarios", _vinetas(f"`{c['id']}`: {c['motivo']}" for c in spec["complementarios"])]
    return "\n\n".join(partes) + "\n"


def _memorias_md(spec: dict) -> str:
    memorias = spec.get("memorias") or MEMORIAS_POR_DEFECTO
    pid = spec["id"]
    return (f"# Memorias\n\nLo que el agente y la persona acuerdan recordar de este proyecto al trabajar con {spec['titulo'].lower()}.\n\n"
            f"Viven en `uxyngraphar/trabajo/{pid}/memorias/` y se gestionan con "
            f"`python3 uxyngraphar/sistemas-de-gobernanza/{pid}/scripts/comun/memorias.py`. El agente las lee al activar el "
            "sistema, aplica las vigentes y propone nuevas (quedan «propuesta»); solo una persona las aprueba o archiva (`--humano`).\n\n"
            f"## Qué recordar\n\n{_vinetas(memorias['recordar'])}\n\n## Qué no recordar\n\n{_vinetas(memorias['no_recordar'])}\n")


def _readme(spec: dict) -> str:
    texto = f"# {spec['titulo']}\n\n{entrada.INICIO}\n{entrada.FIN}\n"
    if spec.get("decide_la_persona"):
        texto += "\n## Lo que decide la persona\n\n" + _vinetas(spec["decide_la_persona"]) + "\n"
    return texto


def _limites_md(spec: dict) -> str:
    limites = spec.get("limites") or LIMITES_POR_DEFECTO
    reglas = [r.replace("<id>", spec["id"]) for r in limites["reglas"]]
    return ("# Límites\n\nSe cumplen en todo el trabajo del sistema. Romper uno lo decide una persona.\n\n" + _numeradas(reglas)
            + "\n\n## Cuándo detenerse y preguntar\n\n" + _vinetas(limites["detenerse"]) + "\n")


def _permisos_md(spec: dict) -> str:
    import uxyn_permisos as permisos
    texto = (f"# Permisos\n\nQué hace el agente solo y qué decide una persona al trabajar con {spec['titulo'].lower()}. "
             "El bloque siguiente se genera a partir de «permisos» en `sistema.json`; lo demás es del autor.\n\n"
             f"{permisos.INICIO}\n{permisos.FIN}\n")
    if spec.get("decide_la_persona"):
        texto += "\n## Por qué\n\n" + _vinetas(spec["decide_la_persona"]) + "\n"
    return texto


def _fase_md(f: dict) -> str:
    partes = [f"---\nfase: {f['fase']}\nresuelve: {_lista_fm(f.get('resuelve'))}\nskills: {_lista_fm(f.get('skills'))}\n---",
              f"# Fase: {f.get('titulo') or f['fase'].replace('-', ' ')}"]
    if _texto(f.get("condicion")):
        partes.append(f["condicion"])
    partes += ["## Objetivo", f["objetivo"]]
    if f.get("entradas"):
        partes += ["## Entradas", _vinetas(f["entradas"])]
    partes += ["## Pasos", _numeradas(f["pasos"]), "## Criterio de salida", _vinetas(f["criterio_salida"])]
    return "\n\n".join(partes) + "\n"


def _skill_md(s: dict) -> str:
    partes = [f"---\nname: {s['nombre']}\ndescription: {s['descripcion']}\nresuelve: {_lista_fm(s.get('resuelve'))}\n---",
              f"# {s.get('titulo') or s['nombre'].replace('-', ' ').capitalize()}",
              "## Cuándo usarla", _vinetas(s["cuando"]), "## Pasos", _numeradas(s["pasos"])]
    if s.get("resultado"):
        partes += ["## Resultado", _vinetas(s["resultado"])]
    return "\n\n".join(partes) + "\n"


def _ficha_md(d: dict) -> str:
    semilla = (catalogo.SEMILLAS / "plantillas" / "plantillas" / "ficha.md").read_text(encoding="utf-8")
    secciones = d.get("secciones") or []
    if not secciones:
        return semilla
    return semilla.replace("…\n", "".join(f"## {s}\n\n…\n\n" for s in secciones).rstrip("\n") + "\n")


def _ejemplo_md(e: dict) -> str:
    return (f"# Caso: {e['titulo']}\n\n## Pedido\n\n{e['pedido']}\n\n## Recorrido\n\n{e['recorrido']}\n\n"
            f"## Resultado\n\n{e['resultado']}\n")


def _definicion_ficha(tipo: str, d: dict, prefijo: str, unico: bool) -> dict:
    salida = {"carpeta": d.get("carpeta", "." if unico else tipo), "prefijo": prefijo, "plantilla": f"plantillas/{tipo}.md", "inicial": d.get("inicial")}
    for clave in ("estados", "status_validos", "solo_humano", "espera_humano", "comandos", "variantes"):
        if clave in d:
            salida[clave] = d[clave]
    return salida


def _escribir(c: Path, spec: dict, usados: dict[str, str]) -> None:
    pid = spec["id"]
    escribir = lambda rel, texto: ((c / rel).parent.mkdir(parents=True, exist_ok=True), (c / rel).write_text(texto, encoding="utf-8"))  # noqa: E731
    m = base.leer_manifiesto(c)
    frases = [pid, pid.replace("-", " "), *(spec.get("activacion") or [])]
    m["activacion"] = list(dict.fromkeys(frases))
    m["descripcion"] = spec["descripcion"]
    m["alcance"] = {"problemas": [{"id": p["id"], "descripcion": p["descripcion"]} for p in spec["problemas"]],
                    "fuera_de_alcance": [{"tema": f["tema"], "derivar_a": f.get("derivar_a")} for f in spec["fuera_de_alcance"]]}
    m["piezas"] = sorted({*piezas_de(spec), *(["pruebas"] if (c / "pruebas").is_dir() else [])}, key=list(base.PIEZAS).index)
    if spec.get("ajustes"):
        m["ajustes"] = spec["ajustes"]
    m["permisos"] = json.loads(json.dumps(spec.get("permisos") or PERMISOS_VACIOS))
    escribir(base.LIMITES, _limites_md(spec))
    escribir(base.PERMISOS, _permisos_md(spec))
    if spec.get("proceso"):
        m["proceso"] = [f["fase"] for f in spec["proceso"]]
        for f in spec["proceso"]:
            escribir(f"proceso/{f['fase']}.md", _fase_md(f))
    for s in spec.get("skills") or []:
        escribir(f"skills/{s['nombre']}/SKILL.md", _skill_md(s))
    if spec.get("fichas"):
        libres = dict(usados)
        m["fichas"] = {}
        for tipo, d in spec["fichas"].items():
            prefijo = d.get("prefijo") or nomenclatura.proponer_prefijo(pid if len(spec["fichas"]) == 1 else f"{tipo}-{pid}", set(libres))
            libres[prefijo] = f"{pid}.{tipo}"
            m["fichas"][tipo] = _definicion_ficha(tipo, d, prefijo, len(spec["fichas"]) == 1)
            escribir(f"plantillas/{tipo}.md", _ficha_md(d))
    for e in spec.get("ejemplos") or []:
        escribir(f"ejemplos/{e['nombre']}.md", _ejemplo_md(e))
    escribir("CHANGELOG.md", f"# Cambios\n\n## {m['version']}\n\n- Primera versión, generada desde una especificación.\n")
    escribir(base.DESCRIPCION, _sistema_md(spec))
    escribir(base.MEMORIAS, _memorias_md(spec))
    escribir(base.ENTRADA, _readme(spec))
    (c / base.MANIFIESTO).write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    entrada.actualizar(c)


def _errores_finales(c: Path, raiz: Path | None) -> list[str]:
    sistemas = catalogo._sistemas(raiz)
    sistemas[c.name] = (c, base.leer_manifiesto(c))
    nombres = nomenclatura.revisar_catalogo(sistemas)[c.name][0]
    return esp.validar_sistema(c) + [f"nomenclatura: {e}" for e in nombres]


def desde_spec(spec: dict, aplicar: bool = False, raiz: Path | None = None) -> dict:
    """Genera el sistema completo. Sin `aplicar` solo simula; con `aplicar` lo deja en el catálogo si valida sin errores.

    Devuelve {"id", "ruta", "aplicado", "archivos", "errores", "avisos"}. Nunca deja un sistema a medias en el catálogo.
    """
    r = validar_spec(spec, raiz)
    pid = spec.get("id") if isinstance(spec, dict) else None
    salida = {"id": pid, "ruta": None, "aplicado": False, "archivos": [], **r}
    if r["errores"]:
        return salida
    destino = catalogo.catalogo(raiz) / pid
    temporal = Path(tempfile.mkdtemp(prefix=OCULTA, dir=catalogo.catalogo(raiz)))
    try:
        extra = [p for p in piezas_de(spec) if p not in GENERADAS and p != "pruebas"] + ["pruebas", "cambios"]   # pruebas de serie (M-07)
        c = catalogo.crear(pid, spec["titulo"], spec["descripcion"], raiz=temporal, familia=spec["familia"], piezas=extra)
        _escribir(c, spec, _prefijos_usados(catalogo._sistemas(raiz)))
        salida["errores"] = _errores_finales(c, raiz)
        salida["avisos"] = r["avisos"] + esp.avisos_sistema(c)
        salida["archivos"] = base.archivos_del_sistema(c)
        if aplicar and not salida["errores"]:
            if destino.exists():
                raise FileExistsError(f"ya existe {destino}")
            c.rename(destino)
            salida.update(ruta=str(destino), aplicado=True)
    finally:
        shutil.rmtree(temporal, ignore_errors=True)
    return salida


# ---------- modo guiado ----------

def marcadores(c: Path) -> list[dict]:
    """Marcadores {{…}} por rellenar, con archivo y línea (las plantillas de fichas los llevan a propósito)."""
    salida = []
    # El orden del sistema de archivos cambia entre Windows y Linux; «siguiente» debe ser el mismo en todos.
    for rel in sorted(base.archivos_del_sistema(c), key=lambda r: (r not in NUCLEO, r != base.DESCRIPCION, r)):
        if not rel.endswith((".md", ".json")) or rel.startswith(SIN_MARCADORES):
            continue
        for n, linea in enumerate((c / rel).read_text(encoding="utf-8").splitlines(), 1):
            for marca in piezas.MARCADOR.findall(linea):
                salida.append({"archivo": rel, "linea": n, "marcador": marca, "texto": linea.strip()})
    return salida


def pendientes(pid: str, raiz: Path | None = None) -> dict:
    """Lo que le falta a un sistema del catálogo, por prioridad, y la siguiente acción concreta («siguiente»)."""
    c = catalogo.carpeta(pid, raiz)
    m = base.leer_manifiesto(c)
    errores = _errores_finales(c, raiz)
    marcas = marcadores(c)
    completitud = piezas.completitud(c, m)
    avisos = [a for a in esp.avisos_sistema(c) if "marcadores sin rellenar" not in a]
    reales = [e for e in errores if "marcadores sin rellenar" not in e]
    en_nucleo = [x for x in marcas if x["archivo"] in NUCLEO]
    if en_nucleo:
        x = en_nucleo[0]
        siguiente = f"Rellena {x['marcador']} en {x['archivo']}:{x['linea']} (el núcleo no valida con marcadores)"
    elif reales:
        siguiente = f"Corrige: {reales[0]}"
    elif marcas:
        x = marcas[0]
        siguiente = f"Rellena {x['marcador']} en {x['archivo']}:{x['linea']}"
    elif completitud["faltan_recomendadas"]:
        p = completitud["faltan_recomendadas"][0]
        siguiente = f"Valora la pieza recomendada «{p}»: uxyngraphar pieza {pid} agregar {p}"
    elif avisos:
        siguiente = f"Revisa el aviso: {avisos[0]}"
    else:
        siguiente = (f"Listo: anota el cambio en CHANGELOG.md, sube la versión si procede (uxyngraphar version {pid} …) "
                     f"y ejecuta las pruebas del sistema")
    return {"id": pid, "listo": not errores and not marcas, "errores": errores, "marcadores": marcas,
            "faltan_recomendadas": completitud["faltan_recomendadas"], "avisos": avisos, "siguiente": siguiente}
