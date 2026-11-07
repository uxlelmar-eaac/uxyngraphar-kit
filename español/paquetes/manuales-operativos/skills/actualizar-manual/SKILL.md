---
name: actualizar-manual
description: Ajusta un manual existente cuando un cambio altera sus comandos, variables, requisitos, resultado esperado o reversión, y lo devuelve a borrador para que una persona lo pruebe.
resuelve: [manuales-desfasados, pasos-no-ejecutables, procedimientos-sin-reversion]
---

# Actualizar manual

## Cuándo usarla

- El cambio de la tarea altera un procedimiento que ya tiene manual.
- Un manual tiene pasos vagos o le falta «Cómo revertir».

## Pasos

1. Abre el manual: `python3 $P/scripts/comun/fichas.py ver <id>`.
2. Cambia solo los pasos afectados y su resultado esperado; si cambia el orden, renumera.
3. Variables nuevas o renombradas → «Requisitos», como `<NOMBRE>` y su origen.
4. Si el cambio afecta a la reversión, actualiza «Cómo revertir».
5. Si el procedimiento deja de aplicar (por ejemplo, se cambió de proveedor), pasa el manual a `obsoleto` con una línea en «Cuándo usarlo» que diga cuál lo sustituye: `python3 $P/scripts/comun/fichas.py estado <id> obsoleto`.
6. Si estaba `vigente`, vuelve a `borrador` (fase `entregar-para-verificacion`): la persona debe probar la versión nueva.

## Resultado

- El manual describe el procedimiento tal como queda, en `borrador` (u `obsoleto` con su sustituto).
