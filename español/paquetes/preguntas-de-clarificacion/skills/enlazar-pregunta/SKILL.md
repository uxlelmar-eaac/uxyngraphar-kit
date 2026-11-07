---
name: enlazar-pregunta
description: Enlaza la ficha PRE con la instrucción que usa su síntesis (instruccion_id) y la cierra como completada, o la cancela si el pedido se abandona.
resuelve: [decisiones-supuestas]
---

# Enlazar pregunta

## Cuándo usarla

- En la fase `cerrar-pregunta`, cuando ya existe el trabajo que usa la síntesis.
- Cuando el pedido se abandona y la pregunta queda sin uso.

## Pasos

1. Si la síntesis va a una instrucción de `instrucciones-aprobadas`, pon `instruccion_id: <INS-…>` en el frontmatter de la pregunta. El `preguntas_id` de la instrucción lo pone el proceso de ese paquete: no edites su trabajo desde aquí.
2. Si no hay instrucción (el paquete no está instalado o la síntesis va a un plan), deja `instruccion_id: null`.
3. Cierra la pregunta: `python3 $P/scripts/comun/fichas.py estado <PRE-…> completada`.
4. Si el pedido se abandona: `python3 $P/scripts/comun/fichas.py estado <PRE-…> cancelada`.
5. Ejecuta `python3 $P/scripts/verificar-preguntas.py`: falla si una pregunta `completada` tiene decisiones sin elegir o síntesis vacía, y avisa si la instrucción enlazada no está en `uxyngraphar/trabajo/instrucciones-aprobadas/` (solo si esa carpeta existe).

## Resultado

- Ficha `PRE-<fecha>-<slug>` en `preguntas/completadas/` (o `canceladas/`), enlazada con su instrucción cuando la hay (`instruccion_id` ↔ `preguntas_id`).
