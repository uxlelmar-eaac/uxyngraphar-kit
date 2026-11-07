---
name: listar-reglas-aplicables
description: Muestra las reglas activas que tocan unas rutas o anclas de código (o todas, en una tabla), sin abrir las fichas una a una.
resuelve: [reglas-incumplidas-en-silencio]
---

# Listar reglas aplicables

## Cuándo usarla

- En la fase `consultar-reglas`, antes de escribir código.
- Cuando la persona pregunta qué reglas tiene el proyecto.

## Pasos

1. Con rutas o anclas: `python3 $P/scripts/reglas.py para <ruta|ancla>…`. Acepta anclas con rango de líneas (`src/a.ts:40-80`) y compara con los globs de `aplica_a` (`src/**/*.ts` cubre también `src/a.ts`).
2. Cada regla sale como `- REG-… [nivel] resumen`; las `bloqueante` imprimen además su cuerpo (regla, porqué, ejemplo). Si no hay ninguna: `(ninguna regla del proyecto toca esas rutas)`.
3. Sin rutas todavía: `python3 $P/scripts/reglas.py indice` imprime la tabla `id | nivel | aplica_a | resumen` de las activas, o `(sin reglas del proyecto activas)`.
4. Solo cuentan las reglas `activa` y bien formadas (nivel válido, `aplica_a` no vacío, resumen y regex compilables). Las `propuesta` no obligan.
5. No abras las fichas de `reglas/` una a una salvo que el resumen no baste (límite 7).

## Resultado

- La lista de reglas que debes cumplir en esas rutas, con su nivel.
