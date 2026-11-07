---
fase: implementar-aprobada
resuelve: [arreglos-fuera-de-alcance]
skills: []
---

# Fase: implementar aprobada

Solo si la persona pide implementar una mejora que está en `approved`. Si está en `pending`, esta fase no se recorre.

## Objetivo

Implementar exactamente lo que la ficha aprobada describe y cerrarla.

## Entradas

- La ficha `MEJ-…` en `approved` (en `en-progreso/`).
- Si el proyecto usa `instrucciones-aprobadas`, la instrucción aprobada que la cita.

## Pasos

1. Comprueba el status: `python3 $P/scripts/comun/fichas.py ver MEJ-…`. Sin `approved` no hay implementación.
2. Si está instalado `instrucciones-aprobadas`, trabaja a través de su instrucción aprobada; si no existe, propónla allí y espera.
3. Implementa la «Mejora propuesta» de la ficha, sin ampliarla. Si exige más de lo descrito, detente y pregunta.
4. Pasa la ficha a `done`: `python3 $P/scripts/comun/fichas.py estado MEJ-… done`.
5. Ejecuta `python3 $P/scripts/comun/verificar.py`.

## Criterio de salida

- La mejora aprobada está en el código, sin cambios extra, y la ficha en `done` (`completadas/`).
