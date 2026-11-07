---
name: revisar-dependencias-entre-areas
description: Ejecuta verificar-areas.py e interpreta sus ciclos y dependencias hacia áreas sin documentar, proponiendo cómo romper cada ciclo sin decidirlo por la persona.
resuelve: [dependencias-entre-areas-circulares, dependencias-hacia-areas-sin-documentar]
---

# Revisar dependencias entre áreas

## Cuándo usarla

- Al terminar un cambio que toca `depends_on` (fase `verificar`).
- Cuando la persona pide revisar el mapa de áreas.

## Pasos

1. Ejecuta `python3 $P/scripts/verificar-areas.py`.
2. `error: ciclo de dependencias: orders → payments → orders`: el ciclo es un error. Si lo introdujo la tarea, quita la dependencia nueva o mueve la responsabilidad que la causa (y actualiza «Posee»/«No posee» de las dos áreas). Si mover responsabilidades cambia el diseño, detente y propónlo.
3. `aviso: orders: depende de «shipping», que aún no está documentada`: documenta `shipping` con la skill `documentar-area` o, si no es parte del pedido, menciónalo al cerrar.
4. La última línea resume: `areas: N áreas, E errores, A avisos`.

## Resultado

- Sin ciclos, o con el ciclo heredado explicado y una propuesta para romperlo.
- Lista de áreas citadas que faltan por documentar.
