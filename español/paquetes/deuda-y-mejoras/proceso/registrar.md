---
fase: registrar
resuelve: [deuda-detectada-sin-registro, mejoras-sin-evidencia, cola-de-mejoras-inmanejable]
skills: [registrar-mejora]
---

# Fase: registrar

## Objetivo

Dejar el problema en la cola con evidencia y clasificación, dentro del límite de fichas por tarea.

## Entradas

- El problema sin ficha previa y su evidencia.
- El número de fichas ya creadas en esta tarea y `max_por_tarea`.

## Pasos

1. Si ya creaste `max_por_tarea` fichas en esta tarea, no crees otra: agrupa con una de la misma causa o menciónalo a la persona al cerrar.
2. Aplica `registrar-mejora`.
3. Ejecuta `python3 $P/scripts/comun/verificar.py`.
4. Al cerrar la tarea, menciona a la persona las fichas creadas (id y una línea cada una).

## Criterio de salida

- Ficha `MEJ-…` en `pending` con evidencia y `tipo`, `severidad` y `prioridad` rellenos.
- `verificar.py` sin errores y la persona informada.
