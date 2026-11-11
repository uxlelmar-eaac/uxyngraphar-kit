"""Contratos del protocolo de sistemas v3 (ESPECIFICACION.md) del lado del motor: sistema (fuente o construido) y FLUJO.json.

El manifiesto y la integridad se validan con la copia de `scripts/comun/uxyn_base.py` de `sistemas-de-gobernanza/_base/`, la base de
la que nacen los sistemas nuevos (no es un sistema: no se lista, no se construye ni se instala). Las piezas estándar las
valida `piezas.py`; el bloque de entrada del README lo genera `entrada.py`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

MOTOR = Path(__file__).resolve().parent
KIT = MOTOR.parent
CATALOGO = KIT / "sistemas-de-gobernanza"
PLANTILLA = CATALOGO / "_base"
DESTINO_COMUN = "scripts/comun"
COMUN = PLANTILLA / DESTINO_COMUN
sys.path.insert(0, str(COMUN))

import uxyn_base as base  # noqa: E402

VERSION_MOTOR = (MOTOR / "VERSION").read_text(encoding="utf-8").strip()
FLUJO = "FLUJO.json"
INDICE = "INDICE.md"
FORMATO_FLUJO = 1
MODOS = ("manual", "leer_por_defecto", "trabajar_con", "secuencia")
CONFLICTOS = ("preguntar",)
OBLIGATORIOS = (base.ENTRADA, base.DESCRIPCION, base.MEMORIAS, base.LIMITES, base.PERMISOS)
FLUJO_INICIAL = {"formato": FORMATO_FLUJO, "modo": "manual", "leer_por_defecto": [], "trabajar_con": None,
                 "secuencia": [], "conflictos": "preguntar"}


def version_tupla(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split("."))


# Versión del motor desde la que existe cada pieza y cada campo opcional del manifiesto. Un sistema que los usa debe
# pedir al menos esa versión en «motor». Al añadir una pieza o un campo nuevo, se añade aquí con la versión que lo trae.
PIEZA_DESDE = {pieza: (1, 0) for pieza in base.PIEZAS}
CAMPO_DESDE = {"fichas": (1, 0), "ajustes": (1, 0), "al_activar_sistema": (1, 0),
               "proceso": (1, 0), "andamiaje": (1, 0), "extensiones": (1, 0), "piezas": (1, 0),
               "editor": (1, 0), "idioma": (1, 0), "licencia": (1, 0), "etiquetas": (1, 0), "repositorio": (1, 0),
               "permisos": (1, 0)}


def rango_motor(requisito: str) -> tuple[tuple[int, ...], tuple[int, ...] | None]:
    """(mínimo, techo exclusivo o None) de un requisito «>=X.Y» o «>=X.Y,<Z»."""
    minimo, _, techo = requisito[2:].partition(",<")
    return version_tupla(minimo), (version_tupla(techo) if techo else None)


def motor_compatible(requisito: str, version: str = VERSION_MOTOR) -> bool:
    minimo, techo = rango_motor(requisito)
    actual = version_tupla(version)
    if actual[: len(minimo)] < minimo:
        return False
    return techo is None or actual[: len(techo)] < techo


def minimo_necesario(m: dict) -> tuple[int, ...]:
    """La versión del motor más baja que entiende todo lo que usa el manifiesto."""
    usados = [PIEZA_DESDE.get(p, (1, 0)) for p in m.get("piezas") or []]
    usados += [v for campo, v in CAMPO_DESDE.items() if campo in m]
    return max(usados, default=(1, 0))


def validar_sistema(carpeta: Path, construido: bool = False) -> list[str]:
    """Errores de un sistema del catálogo (`construido=False`) o ya construido/instalado (`True`)."""
    carpeta = Path(carpeta)
    try:
        m = base.leer_manifiesto(carpeta)
    except (OSError, ValueError) as e:
        return [f"{base.MANIFIESTO}: {e}"]
    errores = base.validar_manifiesto(m)
    if errores:
        return errores
    if carpeta.name != m["id"]:
        errores.append(f"la carpeta se llama «{carpeta.name}» pero el id es «{m['id']}»")
    for campo in ("titulo", "descripcion"):
        if str(m.get(campo, "")).strip().lower() == "plantilla":
            errores.append(f"{campo}: «{m[campo]}» es el texto de la base; escribe el del sistema")
    if not motor_compatible(m["motor"]):
        errores.append(f"motor: requiere {m['motor']}, este motor es {VERSION_MOTOR}")
    minimo, techo = rango_motor(m["motor"])
    necesario = minimo_necesario(m)
    if minimo < necesario:
        errores.append(f"motor: «{m['motor']}» admite motores que no entienden lo que usa (hace falta >={'.'.join(map(str, necesario))})")
    if techo is None:
        errores.append(f"motor: «{m['motor']}» sin techo; declara también la siguiente versión mayor («{m['motor']},<{minimo[0] + 1}»)")
    for nombre in OBLIGATORIOS:
        if not (carpeta / nombre).is_file():
            errores.append(f"falta {nombre}")
    for v in m["verificaciones"]:
        de_la_base = not construido and v.startswith(DESTINO_COMUN + "/") and (COMUN / v[len(DESTINO_COMUN) + 1:]).is_file()
        if not (carpeta / v).is_file() and not de_la_base:
            errores.append(f"verificación inexistente: {v}")
    for tipo, d in m.get("fichas", {}).items():
        for donde, plantilla in [("plantilla", d["plantilla"]), *((f"variantes.{k}", v) for k, v in d.get("variantes", {}).items())]:
            if not (carpeta / plantilla).is_file():
                errores.append(f"fichas.{tipo}.{donde} inexistente: {plantilla}")
    for rel in base.archivos_del_sistema(carpeta):
        if not rel.isascii() or " " in rel:
            errores.append(f"nombre de archivo no ASCII o con espacios: {rel}")
    import entrada
    import piezas
    errores += piezas.nucleo(carpeta, m)
    errores += piezas.validar(carpeta, m)[0]
    if (carpeta / base.ENTRADA).is_file() and not entrada.al_dia(carpeta):
        errores.append(f"{base.ENTRADA}: el bloque de entrada no corresponde al manifiesto; ejecuta «uxyngraphar indice-sistema {m['id']}»")
    if construido:
        informe = base.comprobar_integridad(carpeta)
        if not base.integro(informe):
            errores.append(f"integridad: {json.dumps(informe, ensure_ascii=False)}")
    elif (carpeta / base.INTEGRIDAD).exists():
        errores.append(f"{base.INTEGRIDAD} no va en el catálogo: lo genera la construcción")
    return errores


def avisos_sistema(carpeta: Path) -> list[str]:
    """Avisos (no impiden validar): especialización, completitud, marcadores en piezas opcionales y scripts de
    copias locales de `scripts/comun/` que difieren de `sistemas-de-gobernanza/_base/`."""
    import piezas
    avisos = []
    try:
        m = base.leer_manifiesto(carpeta)
        if not base.validar_manifiesto(m):
            import uxyn_permisos as permisos
            avisos += piezas.validar(Path(carpeta), m)[1]
            avisos += [f"permisos: {s} tiene acciones «solo_persona» y nunca llama a exigir(); un agente podría ejecutarlas"
                       for s in permisos.sin_exigir(Path(carpeta), m)]
    except (OSError, ValueError):
        pass
    propios = [s for s in (Path(carpeta) / "scripts").glob("*.py")] if (Path(carpeta) / "scripts").is_dir() else []
    if propios and not list((Path(carpeta) / "pruebas").glob("test_*.py")):
        avisos.append("tiene scripts propios y no tiene pieza «pruebas» (pruebas/test_<tema>.py); será un error en la "
                      "próxima versión mayor del protocolo")
    for script in sorted(COMUN.glob("*.py")):   # la copia local (no versionada) solo sirve para trabajar desde la fuente
        propio = Path(carpeta) / DESTINO_COMUN / script.name
        if propio.is_file() and base.sha256(propio) != base.sha256(script):
            avisos.append(f"{DESTINO_COMUN}/{script.name}: difiere de sistemas-de-gobernanza/_base (construir usa la de _base; "
                          "«uxyngraphar sincronizar-comun» pone al día la copia local)")
    return avisos


def validar_flujo(flujo, instalados: set[str] | None = None) -> list[str]:
    """Errores de FLUJO.json. Con `instalados`, también comprueba que los sistemas citados existan."""
    if not isinstance(flujo, dict):
        return ["FLUJO.json debe ser un objeto JSON"]
    errores = []
    if flujo.get("formato") != FORMATO_FLUJO:
        errores.append(f"formato: debe ser {FORMATO_FLUJO}")
    modo = flujo.get("modo")
    if modo not in MODOS:
        errores.append(f"modo: uno de {', '.join(MODOS)}")
    if flujo.get("conflictos") not in CONFLICTOS:
        errores.append("conflictos: debe ser «preguntar»")
    citados: list[str] = []
    for campo in ("leer_por_defecto", "secuencia"):
        valor = flujo.get(campo)
        if not isinstance(valor, list) or not all(isinstance(x, str) and base.ID_VALIDO.match(x) for x in valor):
            errores.append(f"{campo}: lista de ids de sistema")
        else:
            citados += valor
            if len(set(valor)) != len(valor):
                errores.append(f"{campo}: ids repetidos")
    trabajar = flujo.get("trabajar_con")
    if trabajar is not None and (not isinstance(trabajar, str) or not base.ID_VALIDO.match(trabajar)):
        errores.append("trabajar_con: id de sistema o null")
    elif trabajar:
        citados.append(trabajar)
    if modo == "leer_por_defecto" and not flujo.get("leer_por_defecto"):
        errores.append("modo leer_por_defecto: «leer_por_defecto» no puede estar vacío")
    if modo == "trabajar_con" and not trabajar:
        errores.append("modo trabajar_con: falta «trabajar_con»")
    if modo == "secuencia" and not flujo.get("secuencia"):
        errores.append("modo secuencia: «secuencia» no puede estar vacía")
    if instalados is not None:
        for pid in sorted(set(citados) - instalados):
            errores.append(f"sistema no instalado: {pid}")
    return errores
