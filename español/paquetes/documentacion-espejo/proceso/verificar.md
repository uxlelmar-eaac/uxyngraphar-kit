---
fase: verificar
resuelve: [espejos-huerfanos, codigo-sin-espejo]
skills: [medir-cobertura]
---

# Fase: verificar

## Objetivo

Demostrar que no quedan espejos huérfanos y que la cobertura cumple el mínimo del proyecto.

## Entradas

- Los espejos creados, movidos o borrados.

## Pasos

1. Ejecuta `python3 $P/scripts/espejo.py huerfanos`: no debe listar nada de lo que tocaste.
2. Ejecuta `python3 $P/scripts/verificar-espejo.py`. `error: espejo huérfano …` se corrige ahora; `error: cobertura X% < mínimo Y%` se corrige si lo causa tu cambio y, si no, se menciona al cerrar.
3. Ejecuta `python3 $P/scripts/comun/verificar.py`.

## Criterio de salida

- `verificar-espejo.py` termina con código 0.
- Todo el código creado en la tarea tiene espejo.
