---
fase: cerrar-pregunta
resuelve: [decisiones-supuestas]
skills: [enlazar-pregunta]
---

# Fase: cerrar-pregunta

## Objetivo

Entregar la síntesis al trabajo que sigue, dejar la pregunta enlazada con él y cerrada, de modo que las decisiones de la persona sigan localizables en otra sesión.

## Entradas

- La ficha `PRE-…` en `preguntas/en-curso/` de la fase anterior.
- El trabajo que usa la síntesis: una instrucción de `instrucciones-aprobadas` (si existe `uxyngraphar/trabajo/instrucciones-aprobadas/`) o el plan o cambio que la persona haya pedido.

## Pasos

1. Entrega la «Síntesis»: con `instrucciones-aprobadas`, el agente la copia en «Clarificación» de la instrucción y pone allí `preguntas_id: <PRE-…>` siguiendo el proceso de ese paquete; sin él, la cita en el chat o en el plan.
2. Aplica `enlazar-pregunta`: pon `instruccion_id` si hay instrucción y cierra la pregunta con `completada`.
3. Ejecuta `python3 $P/scripts/verificar-preguntas.py` y `python3 $P/scripts/comun/verificar.py`. Corrige cualquier error antes de terminar.

## Criterio de salida

- La pregunta está en `preguntas/completadas/` con todas sus decisiones respondidas y su síntesis, o en `canceladas/` si el pedido se abandonó.
- `verificar-preguntas.py` termina con 0 errores.
