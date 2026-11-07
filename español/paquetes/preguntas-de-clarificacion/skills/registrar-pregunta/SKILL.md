---
name: registrar-pregunta
description: Crea y rellena la ficha PRE con las decisiones que la persona tomó (opciones, elegida, efecto) y su síntesis.
resuelve: [decisiones-supuestas]
---

# Registrar pregunta

## Cuándo usarla

- En la fase `preguntar`, en cuanto la persona ha respondido.
- Cuando la persona añade o corrige una respuesta de una pregunta que sigue `en-curso`.

## Pasos

1. Crea la ficha: `python3 $P/scripts/comun/fichas.py nueva pregunta --slug <slug> --titulo "…"`. Nace en `preguntas/en-curso/`.
2. «Impacto»: qué se decide y por qué importa, en una o dos frases.
3. «Decisiones»: una fila por pregunta con las opciones ofrecidas, la elegida por la persona y su efecto en el trabajo. Nunca rellenes «Elegida» con tu recomendación si la persona no la confirmó.
4. «Síntesis»: las decisiones en viñetas, listas para copiar en «Clarificación» de la instrucción o en el plan.

## Resultado

- Ficha `PRE-<fecha>-<slug>` en `preguntas/en-curso/` con impacto, tabla de decisiones completa y síntesis.
