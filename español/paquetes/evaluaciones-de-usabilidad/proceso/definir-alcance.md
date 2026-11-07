---
fase: definir-alcance
resuelve: [cambios-de-interfaz-sin-aprobacion]
skills: []
---

# Fase: definir alcance

## Objetivo

Abrir la evaluación y fijar qué pantallas o flujos entran y qué tareas intenta completar el usuario, antes de mirar un solo problema.

## Entradas

- El pedido de la persona (qué pantalla, flujo o queja concreta).
- Evaluaciones anteriores de las mismas pantallas: `python3 $P/scripts/comun/fichas.py listar evaluacion`.

## Pasos

1. Si ya hay una evaluación abierta o en curso de esas pantallas, continúa esa en lugar de abrir otra.
2. Abre la ficha: `python3 $P/scripts/comun/fichas.py nueva evaluacion --slug <pantalla-o-flujo> --titulo "…"`. Nace `abierta` en `uxyngraphar/trabajo/evaluaciones-de-usabilidad/pendientes/`.
3. Rellena «Alcance»: pantallas o flujos que entran (con su ruta en la app o su archivo) y lo que se excluye expresamente. Anota las pantallas también en `pantallas` del frontmatter.
4. Rellena «Tareas del usuario»: de una a tres tareas con verbo y objetivo («darse de alta con correo», «pagar un pedido guardado»). Son la vara de medir de todo lo demás.
5. Si el pedido no permite fijar pantallas o tareas, pregunta a la persona antes de seguir.
6. Pasa la ficha a `en-curso`: `python3 $P/scripts/comun/fichas.py estado UXE-… en-curso`.

## Criterio de salida

- Ficha `UXE-…` en `en-curso` con «Alcance» (incluye y excluye) y al menos una tarea del usuario.
