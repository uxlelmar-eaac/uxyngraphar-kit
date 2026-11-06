# Fase de preguntas

Objetivo: que la instrucción nazca con las decisiones ya tomadas por la persona, sin suposiciones del agente.

1. Antes de redactar la instrucción, identifica lo que cambia el resultado: alcance, comportamiento visible, datos, compatibilidad, riesgos.
2. Pregunta solo eso, con opciones concretas y una recomendada. Cambios pequeños: 1–3 preguntas. No preguntes lo que el código ya responde.
3. Registra la ficha `pregunta` con impacto, tabla de decisiones y síntesis.
4. Al crear la instrucción, pon `preguntas_id: <id de la pregunta>` y copia la síntesis en «Clarificación».
5. Cierra la pregunta: `fichas.py estado <id> completada`; si se abandona, `cancelada`.
6. Si el pedido dice «salta preguntas» o `ajustes.preguntas` es false, escribe en «Clarificación»: `Omitida (pedido)` u `Omitida (config)`.
