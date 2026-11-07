# Preguntas de clarificación

Antes de redactar o cambiar nada, el agente pregunta a la persona lo que decide el resultado, con opciones concretas, y deja sus respuestas en una ficha que el trabajo siguiente cita: ninguna decisión que cambie el resultado queda a su criterio.

## Qué resuelve

Un pedido corto («añade un filtro», «exporta a CSV») deja abiertas decisiones que cambian el resultado: qué entra, qué ve el usuario, qué pasa con los datos existentes, quién consume lo que cambia. Si nadie las pregunta, el agente las rellena con su mejor suposición y la persona las descubre cuando el trabajo ya está hecho. Este paquete convierte esas decisiones en pocas preguntas con opciones y una recomendada, registra lo que la persona eligió y su efecto, y deja una síntesis lista para copiar en la instrucción, el plan o el cambio que venga después.

## Problemas que cubre

- `decisiones-supuestas`: decisiones de alcance, comportamiento, datos o compatibilidad que el agente supone en lugar de preguntarlas.

## Fuera de alcance

- Redactar la instrucción con alcance y anclas, esperar su aprobación, implementarla y cerrarla: `instrucciones-aprobadas` (aquí solo se le entrega la síntesis y se enlaza su id).
- Decisiones técnicas caras de revertir (framework, base de datos, patrón transversal): `decisiones-de-arquitectura`; la pregunta puede detectar que hace falta una ADR, pero no la sustituye.
- Investigar el sistema para responder preguntas técnicas con hallazgos y evidencia: `auditorias-tecnicas`.
- Revisar de una vez todas las fichas que esperan una decisión humana: `revision-humana`.

## Cuándo usarlo

- Antes de cualquier pedido que cambie código o documentación del producto y deje abierta alguna decisión que cambie el resultado.
- Junto a `instrucciones-aprobadas`, para que cada instrucción nazca con su «Clarificación» decidida por la persona.
- Cuando la persona quiere constancia de qué decidió y por qué, para retomarlo en otra sesión.

## Cuándo no usarlo

- Cuando el pedido no deja nada abierto o el código ya responde todas las dudas.
- En preguntas de solo lectura que no cambian nada.
- Cuando la persona dice «salta preguntas» o `ajustes.preguntas` es `false`: se deja constancia de la omisión y se sigue.

## Entradas y salidas

- Entradas: el pedido de la persona, lo que el código ya responde sin preguntar y los ajustes de `uxyngraphar/trabajo/preguntas-de-clarificacion/ajustes.json` (`preguntas`, `dias_en_curso`).
- Salidas: fichas `PRE-…` en `uxyngraphar/trabajo/preguntas-de-clarificacion/preguntas/<estado>/` con impacto, tabla de decisiones y síntesis; enlazadas con `instruccion_id` cuando el trabajo siguiente es una instrucción.

## Paquetes complementarios

- `instrucciones-aprobadas`: el destino habitual de la síntesis. Su instrucción cita la pregunta en `preguntas_id` y la pregunta cita la instrucción en `instruccion_id`. Este paquete solo lee `uxyngraphar/trabajo/instrucciones-aprobadas/` si existe (para comprobar que la instrucción enlazada está allí); sin él, la síntesis se entrega en el chat o en el plan que siga.
- `revision-humana`: muestra las preguntas `en-curso` entre las decisiones pendientes de la persona.
- `decisiones-de-arquitectura`: si una respuesta exige una decisión estructural, se registra allí como ADR.
