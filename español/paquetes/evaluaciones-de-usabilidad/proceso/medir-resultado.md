---
fase: medir-resultado
resuelve: [mejoras-sin-medicion]
skills: [medir-metrica]
---

# Fase: medir resultado

Solo después de `implementar`.

## Objetivo

Saber, con la misma fuente que «Antes», si la mejora cumplió su objetivo y si empeoró algo.

## Entradas

- La ficha en `implementada` y su tabla «Métricas».

## Pasos

1. Mide «Después» de cada métrica con la skill `medir-metrica`, con la misma herramienta, dispositivo y condiciones que «Antes».
2. Si alguna métrica empeora, o la puntuación de accesibilidad baja, anótalo en «Notas» y **detente**: la persona decide si seguir, revertir o aceptarlo.
3. Ejecuta las verificaciones: `python3 $P/scripts/comun/verificar.py` y `python3 $P/scripts/verificar-evaluaciones.py`.
4. Dile a la persona el resultado (antes → después frente al objetivo). Pasar la ficha a `validada` es una acción suya (`--humano`).

## Criterio de salida

- Todas las métricas con «Después» medido y la fuente anotada.
- Verificaciones sin errores y la persona informada; la ficha queda en `implementada` hasta que la persona la valide.
