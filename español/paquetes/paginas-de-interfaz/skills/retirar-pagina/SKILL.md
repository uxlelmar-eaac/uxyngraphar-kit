---
name: retirar-pagina
description: Marca la ficha de una ruta de interfaz eliminada como retirada o la de una en desuso como deprecada con su alternativa, sin borrarla.
resuelve: [rutas-de-interfaz-documentadas-dos-veces]
---

# Retirar página

## Cuándo usarla

- Se elimina una ruta de interfaz.
- Una ruta se sustituye por otra (renombrado, reorganización de la navegación) y la antigua redirige o desaparece.

## Pasos

1. Localiza la ficha: `python3 $P/scripts/comun/fichas.py listar pagina --status activa`.
2. Ruta sustituida que aún redirige: anota en «Acceso» la redirección y la ficha de la nueva; `python3 $P/scripts/comun/fichas.py estado <id> deprecada`.
3. Ruta eliminada: anota en «Qué ve y hace el usuario» en qué cambio desapareció; `python3 $P/scripts/comun/fichas.py estado <id> retirada`.
4. No borres el archivo de la ficha.

## Resultado

- La ficha queda `deprecada` (con alternativa) o `retirada` y no cuenta como duplicada frente a la nueva.
