---
fase: preparar-revision
resuelve: [decisiones-dispersas, status-desfasado, decisiones-aplicadas-a-mano]
skills: [resumir-pendiente, detectar-status-desfasado]
---

# Fase: preparar-revision

## Objetivo

Dejar a la persona una sola hoja con todo lo que decide y, para cada fila, lo justo para decidir sin abrir nada más que la ficha enlazada.

## Entradas

- La lista de `recoger-pendientes`.

## Pasos

1. Ejecuta `python3 $P/scripts/revision.py preparar`. Escribe `uxyngraphar/trabajo/revision-humana/REVISION.md` con una fila por pendiente y la columna «Decisión» vacía.
2. Para cada fila, aplica `detectar-status-desfasado`: si el efecto ya está aplicado, señálalo antes de resumir.
3. Para cada fila, aplica `resumir-pendiente` y entrega los resúmenes en el chat, de lo más antiguo a lo más nuevo. No los escribas en `REVISION.md`: el archivo está protegido y lo regenera el script.
4. Explica cómo se decide: escribir en «Decisión» uno de los status de «Opciones», `posponer` o dejarla vacía, y ejecutar `python3 $P/scripts/revision.py aplicar --humano`.
5. **Detente.** Las decisiones y `aplicar` son de la persona.

## Criterio de salida

- `REVISION.md` existe y refleja todos los pendientes actuales, con «Decisión» vacía.
- La persona tiene un resumen por fila y sabe qué comando ejecutar.
