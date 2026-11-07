---
name: detectar-status-desfasado
description: Comprueba si el efecto de una ficha pendiente ya está aplicado (el cambio ya está en el código, la regla ya se cumple) y, si es así, lo señala como status incorrecto.
resuelve: [status-desfasado]
---

# Detectar status desfasado

## Cuándo usarla

- En `preparar-revision`, para cada fila cuyo efecto se pueda comprobar con poco: una instrucción con anclas, una ADR con `comprobacion_prohibido`, una herramienta propuesta que ya se usa.

## Pasos

1. Lee en la ficha qué cambiaría al aprobarla (anclas, decisión, regla, procedimiento).
2. Comprueba solo eso, con lo mínimo: la existencia del archivo o del cambio en las anclas, una búsqueda de la expresión prohibida.
3. Si el efecto ya está aplicado, escribe en el resumen de la fila: «Status desfasado: <evidencia con ruta>; aprobarla solo regularizaría lo hecho». No cambies el status.
4. Si alguien implementó sin aprobación (por ejemplo, una instrucción en `awaiting_approval` cuyo cambio ya está en el código), dilo expresamente: es un incumplimiento del paquete dueño, no solo un dato desfasado.

## Resultado

- Las filas con status desfasado señaladas con su evidencia, para que la persona decida cómo regularizarlas.
