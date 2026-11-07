---
fase: revisar
resuelve: [barreras-de-accesibilidad]
skills: [revisar-accesibilidad]
---

# Fase: revisar

## Objetivo

Encontrar las barreras de accesibilidad de las pantallas del pedido, cada una con criterio y evidencia, y entregar a la persona la decisión de qué se corrige.

## Entradas

- Las pantallas del pedido y la tarea principal que el usuario hace en ellas.
- `referencia/accesibilidad.md`.
- `uxyngraphar/trabajo/pautas-de-accesibilidad/ACCESIBILIDAD.md`, si existe (revisiones anteriores de esas pantallas).

## Pasos

1. Si `ACCESIBILIDAD.md` no existe, cópialo desde `$P/plantillas/ACCESIBILIDAD.md`. Si ya hay una revisión de esas pantallas con barreras `pendiente`, continúa esa en lugar de abrir otra.
2. Añade arriba una sección `## Revisión <AAAA-MM-DD> — <pantallas>` con pantallas, tarea principal y herramientas. Si el pedido no permite fijarlas, pregunta antes de seguir.
3. Aplica la skill `revisar-accesibilidad` sobre cada pantalla y anota cada barrera en «Barreras» con «Aprobada» vacía y estado `pendiente`.
4. **Detente.** Resume a la persona las barreras por gravedad (primero las bloqueantes) y dile qué debe decidir: marcar «sí» en «Aprobada» de las que se corrigen, o pedir que alguna quede `aceptada`.

## Criterio de salida

- Revisión con pantallas, tarea, herramientas, puntuación automática «antes» y cada barrera con criterio, evidencia, gravedad y corrección propuesta.
- La persona tiene el resumen y sabe qué tiene que aprobar.
