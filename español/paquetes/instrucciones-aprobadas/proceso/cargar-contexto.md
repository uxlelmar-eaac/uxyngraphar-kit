---
fase: cargar-contexto
resuelve: [contexto-excesivo, cambios-sin-aprobacion]
skills: []
---

# Fase: cargar-contexto

## Objetivo

Leer exactamente lo que la instrucción aprobada permite y nada más, dentro del presupuesto de tokens.

## Entradas

- La instrucción aprobada.
- `max_tokens_contexto` (12000 por defecto) en los ajustes.

## Pasos

1. Ejecuta `python3 $P/scripts/ciclo.py contexto <id>`. Imprime la ficha, cada documento de `lectura_minima` y cada ancla con su rango y números de línea, y anota `tokens_contexto` en la instrucción.
2. Código 3 (`BLOQUEADO`): la instrucción no está aprobada o incumple el alcance. Vuelve a `esperar-aprobacion`; no leas nada por tu cuenta.
3. Si aparece `OMITIDO (presupuesto): …` y lo omitido es imprescindible, detente y pide a la persona que reduzca anclas o suba el presupuesto (`--max-tokens N` solo si ella lo indica).
4. Un ancla `(NO EXISTE)` es un archivo que se va a crear o un error de la instrucción: si no es lo primero, detente y pregunta.
5. No abras otros archivos ni reabras los ya impresos. Qué leer según el tipo de tarea: `$P/referencia/eficiencia.md`.

## Criterio de salida

- `contexto` terminó con código 0 y tienes en pantalla todo lo necesario para implementar.
- No has leído nada fuera de lo impreso.
