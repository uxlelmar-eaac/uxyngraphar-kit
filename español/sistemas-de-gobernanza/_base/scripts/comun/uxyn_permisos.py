"""Límites y permisos de un sistema: qué hace el agente solo, qué decide una persona y qué rutas del trabajo no toca.

Parte del propio sistema (`scripts/comun/`). La fuente es «permisos» en `sistema.json`; `PERMISOS.md` lleva un bloque
generado a partir de él (entre marcas) y `LIMITES.md` las reglas duras. Los scripts propios llaman a `exigir` antes de
una acción que solo decide una persona.
"""

from __future__ import annotations

import re
from pathlib import Path

import uxyn_base as base

INICIO = "<!-- uxyngraphar:permisos:inicio -->"
FIN = "<!-- uxyngraphar:permisos:fin -->"
MEMORIAS_AGENTE = ("scripts/comun/memorias.py listar", "scripts/comun/memorias.py ver", "scripts/comun/memorias.py nueva")
MEMORIAS_PERSONA = ("scripts/comun/memorias.py aprobar", "scripts/comun/memorias.py archivar")
SIEMPRE_PROTEGIDAS = ("ajustes.json",)
EXIGE = re.compile(r"\b(?:exigir|exigir_humano)\(")


def _normal(accion: str) -> str:
    return " ".join(accion.split())


def solo_persona(m: dict) -> list[str]:
    """Acciones que solo decide una persona: las declaradas y las de memorias (aprobar y archivar)."""
    return [*MEMORIAS_PERSONA, *(a for a in base.acciones_permiso(m, "solo_persona") if a not in MEMORIAS_PERSONA)]


def del_agente(m: dict) -> list[str]:
    """Acciones que el agente hace solo: las declaradas y las de memorias (listar, ver y proponer)."""
    return [*MEMORIAS_AGENTE, *(a for a in base.acciones_permiso(m, "agente") if a not in MEMORIAS_AGENTE)]


def estados_solo_persona(m: dict) -> dict[str, list[str]]:
    """{tipo de ficha: status que solo pone una persona} («fichas.<tipo>.solo_humano»)."""
    return {tipo: list(d.get("solo_humano") or []) for tipo, d in (m.get("fichas") or {}).items()
            if isinstance(d, dict) and d.get("solo_humano")}


def es_solo_persona(m: dict, accion: str) -> bool:
    """La acción (o el script entero, si se declara sin subcomando) es solo de una persona."""
    accion = _normal(accion)
    return any(accion == a or accion.startswith(a + " ") for a in solo_persona(m))


def exigir(sistema: Path, accion: str) -> None:
    """Para los scripts propios: si `accion` es solo de una persona y no la ejecuta una persona, PermissionError."""
    if es_solo_persona(base.leer_manifiesto(sistema), accion):
        base.exigir_humano(f"«{_normal(accion)}»")


def _codigo(lista) -> str:
    return ", ".join(f"`{x}`" for x in lista) if lista else "ninguna"


def bloque(m: dict) -> str:
    pid = m["id"]
    agente = [f"Leer y escribir en `{base.CARPETA_TRABAJO}/{pid}/`, salvo las rutas de «Rutas»."]
    agente += [f"`{a}`" + (" (las memorias nacen «propuesta»)" if a.endswith(" nueva") and "memorias.py" in a else "")
               for a in del_agente(m)]
    if m.get("fichas"):
        agente.append("`scripts/comun/fichas.py nueva` y `estado`, salvo los status de «Solo una persona».")
    persona = [f"`{a}`" for a in solo_persona(m)]
    persona += [f"Fichas «{tipo}»: poner {', '.join(f'«{s}»' for s in estados)}"
                + (" (también crearlas, porque nacen así)" if m["fichas"][tipo].get("inicial") in estados else "") + "."
                for tipo, estados in estados_solo_persona(m).items()]
    protegidas = [*SIEMPRE_PROTEGIDAS, *(r for r in base.rutas_permiso(m, "protegidas") if r not in SIEMPRE_PROTEGIDAS)]
    lineas = [INICIO,
              "## El agente puede", "", *(f"- {x}" for x in agente), "",
              "## Solo una persona", "",
              "Si el trabajo necesita una de estas acciones, el agente se detiene y se la pide a la persona.", "",
              *(f"- {x}" for x in persona), "",
              "## Rutas", "",
              f"Relativas a `{base.CARPETA_TRABAJO}/{pid}/`.", "",
              f"- Protegidas (el agente no las escribe): {_codigo(protegidas)}.",
              f"- Fuera de la IA (el agente no las lee): {_codigo(base.rutas_permiso(m, 'fuera_de_ia'))}.",
              FIN]
    return "\n".join(lineas)


def con_bloque(texto: str, m: dict) -> str:
    """PERMISOS.md con el bloque actualizado: reemplaza el que hay entre marcas o lo coloca tras el primer párrafo."""
    nuevo = bloque(m)
    if INICIO in texto and FIN in texto:
        antes, _, resto = texto.partition(INICIO)
        _, _, despues = resto.partition(FIN)
        return antes + nuevo + despues
    titulo, _, resto = texto.partition("\n")
    return f"{titulo}\n\n{nuevo}\n" + (f"\n{resto.lstrip(chr(10))}" if resto.strip() else "")


def actualizar(sistema: Path) -> bool:
    """Regenera el bloque de PERMISOS.md; devuelve True si cambió."""
    ruta = Path(sistema) / base.PERMISOS
    actual = ruta.read_text(encoding="utf-8")
    nuevo = con_bloque(actual, base.leer_manifiesto(sistema))
    if nuevo != actual:
        ruta.write_text(nuevo, encoding="utf-8")
    return nuevo != actual


def al_dia(sistema: Path) -> bool:
    texto = (Path(sistema) / base.PERMISOS).read_text(encoding="utf-8")
    return INICIO in texto and con_bloque(texto, base.leer_manifiesto(sistema)) == texto


def scripts_que_faltan(sistema: Path, m: dict, comun: Path | None = None) -> list[str]:
    """Scripts citados en «permisos.acciones» que no existen (los de `scripts/comun/` también valen en `comun`)."""
    faltan = []
    for clave in base.CLAVES_ACCIONES:
        for a in base.acciones_permiso(m, clave):
            script = base.script_de_accion(a)
            en_comun = comun is not None and script.startswith("scripts/comun/") and (comun / script[len("scripts/comun/"):]).is_file()
            if not (Path(sistema) / script).is_file() and not en_comun and script not in faltan:
                faltan.append(script)
    return faltan


def sin_exigir(sistema: Path, m: dict) -> list[str]:
    """Scripts propios con acciones «solo_persona» que nunca llaman a `exigir` ni a `exigir_humano`."""
    salida = []
    for a in base.acciones_permiso(m, "solo_persona"):
        script = base.script_de_accion(a)
        ruta = Path(sistema) / script
        if script.startswith("scripts/comun/") or not ruta.is_file() or script in salida:
            continue
        if not EXIGE.search(ruta.read_text(encoding="utf-8", errors="replace")):
            salida.append(script)
    return salida


def validar(sistema: Path) -> tuple[list[str], list[str]]:
    """(errores, avisos) de límites y permisos de un sistema instalado."""
    sistema = Path(sistema)
    m = base.leer_manifiesto(sistema)
    errores, avisos = [], []
    for nombre in (base.LIMITES, base.PERMISOS):
        if not (sistema / nombre).is_file():
            errores.append(f"falta {nombre} (núcleo)")
    if (sistema / base.PERMISOS).is_file() and not al_dia(sistema):
        errores.append(f"{base.PERMISOS}: el bloque de permisos no corresponde a «permisos» del manifiesto")
    errores += [f"permisos.acciones: no existe {s}" for s in scripts_que_faltan(sistema, m)]
    avisos += [f"permisos: {s} tiene acciones «solo_persona» y nunca llama a exigir(); un agente podría ejecutarlas"
               for s in sin_exigir(sistema, m)]
    return errores, avisos
