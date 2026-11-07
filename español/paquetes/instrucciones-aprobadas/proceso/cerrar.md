---
fase: cerrar
resuelve: [cierre-sin-rastro]
skills: [regenerar-estado]
---

# Fase: cerrar

## Objetivo

Dejar la instrucción cerrada con su fecha, sus criterios marcados y `ESTADO.md` al día, para que la siguiente sesión entre en contexto sin releer el historial.

## Entradas

- La instrucción aprobada, con los criterios marcados durante `implementar`.

## Pasos

1. Revisa la instrucción: criterios cumplidos marcados, los no cumplidos explicados, «Fuera de alcance» con lo detectado. En la variante `solo-docs`, rellena «Resultado (al cerrar)».
2. Ejecuta `python3 $P/scripts/ciclo.py cerrar <id>`: pasa la ficha a `done` en `instrucciones/completadas/`, pone `executed_at` y regenera el bloque de `ESTADO.md`.
3. Ejecuta `python3 $P/scripts/verificar-ciclo.py` y `python3 $P/scripts/comun/verificar.py`. Corrige cualquier error antes de terminar.
4. Informa a la persona: qué se hizo, qué criterios quedaron sin cumplir y qué quedó fuera de alcance.

## Criterio de salida

- La instrucción está en `completadas/` con `status: done` y `executed_at`.
- `verificar-ciclo.py` termina con 0 errores.
- `ESTADO.md` muestra la instrucción como «Última cerrada».
