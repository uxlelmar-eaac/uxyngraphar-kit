---
name: ampliar-evidencia
description: Añade evidencia nueva a una ficha MEJ existente del mismo problema en lugar de crear un duplicado, y ajusta severidad o prioridad propuestas si la evidencia lo justifica.
resuelve: [cola-de-mejoras-inmanejable, mejoras-sin-evidencia]
---

# Ampliar evidencia

## Cuándo usarla

- En `buscar-duplicados`, cuando ya existe una ficha `pending` o `approved` del mismo problema o de la misma causa.

## Pasos

1. Abre la ficha: `python3 $P/scripts/comun/fichas.py ver MEJ-…`.
2. Añade en «Evidencia» una línea nueva con la ruta, la salida o los pasos, y la fecha y tarea en que se vio (`2026-11-06, alta de pedidos`).
3. Si la evidencia nueva muestra más alcance o más gravedad, propón subir `severidad` o `prioridad` y dilo a la persona; no cambies el status.
4. No cambies «Mejora propuesta» de una ficha `approved`: lo aprobado es lo que está escrito. Si hace falta otra cosa, menciónalo a la persona.

## Resultado

- Una sola ficha con toda la evidencia del problema; ninguna ficha nueva.
