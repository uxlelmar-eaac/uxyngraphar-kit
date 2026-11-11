"""Rellena el núcleo de un sistema recién creado (lo que haría su autor) para que valide en las pruebas."""

from __future__ import annotations

import json
from pathlib import Path

import _rutas  # noqa: F401
import entrada
import especificacion as esp

base = esp.base

ALCANCE = {"problemas": [{"id": "problema-principal", "descripcion": "Un problema concreto que el sistema resuelve."}],
           "fuera_de_alcance": [{"tema": "Todo lo que no es el problema principal", "derivar_a": None}]}

DESCRIPCION = """# {titulo}

Sistema de prueba.

## Qué resuelve

Un problema concreto.

## Problemas que cubre

- `problema-principal`: un problema concreto.

## Fuera de alcance

- Todo lo demás: no lo cubre el kit.

## Cuándo usarlo

- En las pruebas del motor.

## Entradas y salidas

- Entradas: nada.
- Salidas: fichas en uxyngraphar/trabajo/<id>/.
"""

MEMORIAS = """# Memorias

Lo que conviene recordar del proyecto en las pruebas.

## Qué recordar

- Acuerdos de prueba.

## Qué no recordar

- Lo que ya vive en las fichas.
"""


LIMITES = """# Límites

Se cumplen en todo el trabajo del sistema.

1. Solo se escribe en uxyngraphar/trabajo/<id>/.

## Cuándo detenerse y preguntar

- El pedido cae fuera del alcance.
"""

PERMISOS = """# Permisos

Qué hace el agente solo y qué decide una persona en las pruebas.

<!-- uxyngraphar:permisos:inicio -->
<!-- uxyngraphar:permisos:fin -->
"""


def completar(carpeta: Path) -> Path:
    carpeta = Path(carpeta)
    m = base.leer_manifiesto(carpeta)
    m["alcance"] = json.loads(json.dumps(ALCANCE))
    (carpeta / base.MANIFIESTO).write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (carpeta / base.DESCRIPCION).write_text(DESCRIPCION.format(titulo=m["titulo"]), encoding="utf-8")
    (carpeta / base.MEMORIAS).write_text(MEMORIAS, encoding="utf-8")
    (carpeta / base.LIMITES).write_text(LIMITES, encoding="utf-8")
    (carpeta / base.PERMISOS).write_text(PERMISOS, encoding="utf-8")
    entrada.actualizar(carpeta)
    return carpeta


def catalogo_de_prueba(carpeta: Path, *ids: str) -> Path:
    """Un catálogo con un sistema mínimo y válido por id (el kit llega sin sistemas)."""
    import catalogo
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    for pid in ids:
        completar(catalogo.crear(pid, pid.replace("-", " ").capitalize(), "Sistema de prueba", carpeta))
    return carpeta


def con_titulo(carpeta: Path, titulo: str) -> str:
    """README con otro título y el bloque de entrada intacto."""
    texto = (Path(carpeta) / base.ENTRADA).read_text(encoding="utf-8")
    primera, _, resto = texto.partition("\n")
    return f"# {titulo}\n{resto}"
