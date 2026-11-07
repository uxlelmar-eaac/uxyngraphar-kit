---
fase: proponer-herramienta
resuelve: [procedimientos-repetidos-sin-atajo, propuestas-ejecutadas]
skills: [redactar-propuesta]
---

# Fase: proponer-herramienta

Solo si ves un procedimiento que se repite (la persona lo ha pedido varias veces, o es un paso fijo de otros trabajos) y ninguna herramienta lo cubre.

## Objetivo

Dejar a la persona una propuesta concreta de herramienta para que decida si la autoriza, sin ejecutarla como tal.

## Entradas

- El procedimiento observado y cuántas veces se ha repetido.

## Pasos

1. Comprueba que no hay ya una propuesta igual: `python3 $P/scripts/comun/fichas.py listar propuesta`.
2. Aplica `redactar-propuesta`.
3. Cuando esté completa, pásala a evaluación: `python3 $P/scripts/comun/fichas.py estado <PRO-…> en-evaluacion`.
4. Dile a la persona que la tiene y cómo se autoriza (ver «Lo que decide la persona» en el README).
5. El pedido de hoy sigue el proceso normal: la propuesta no autoriza nada todavía.
6. Ejecuta `python3 $P/scripts/comun/verificar.py` y `python3 $P/scripts/verificar-herramientas.py`.

## Criterio de salida

- Hay una propuesta `PRO-…` completa en `en-evaluacion` y el procedimiento no se ejecutó como herramienta.
- Las verificaciones terminan sin errores.
