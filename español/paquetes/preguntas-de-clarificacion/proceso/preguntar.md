---
fase: preguntar
resuelve: [decisiones-supuestas]
skills: [registrar-pregunta]
---

# Fase: preguntar

Solo si `ajustes.preguntas` es `true` (por defecto) y el pedido no dice «salta preguntas». Si se omite, dilo a la persona y anota `Omitida (pedido)` u `Omitida (config)` donde se use la síntesis (en `instrucciones-aprobadas`, en «Clarificación»).

## Objetivo

Que el trabajo siguiente nazca con las decisiones ya tomadas por la persona: nada de lo que cambia el resultado queda a criterio del agente.

## Entradas

- El pedido de la persona.
- Lo que el código ya responde sin preguntar (no se pregunta lo que se puede leer).
- Las preguntas `en-curso` de este paquete (`python3 $P/scripts/comun/fichas.py listar pregunta --status en-curso`): si ya hay una del mismo pedido, continúa esa.

## Pasos

1. Identifica lo que cambia el resultado: alcance, comportamiento visible, datos, compatibilidad y riesgos. Criterio y ejemplos: `$P/referencia/preguntas.md`.
2. Pregunta en el chat solo eso, con opciones concretas y una recomendada. Cambio pequeño: de 1 a 3 preguntas.
3. Con las respuestas, aplica la skill `registrar-pregunta`: ficha `pregunta` con impacto, tabla de decisiones y síntesis.
4. Si la persona abandona el pedido, cancela la pregunta (`fichas.py estado <id> cancelada`) y termina aquí.

## Criterio de salida

- Existe una ficha `PRE-…` en `preguntas/en-curso/` con la tabla de decisiones completa (cada fila con su «Elegida») y su «Síntesis», o la omisión está justificada.
- Ninguna decisión que cambie el resultado queda sin respuesta de la persona.
