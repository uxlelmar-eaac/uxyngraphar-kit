---
fase: comprobar
resuelve: [barreras-de-accesibilidad]
skills: [revisar-accesibilidad]
---

# Fase: comprobar

Solo después de `corregir`.

## Objetivo

Confirmar con la misma herramienta que encontró cada barrera que ya no está y que nada quedó peor.

## Entradas

- La revisión en `ACCESIBILIDAD.md` y las correcciones hechas.

## Pasos

1. Repite, por cada barrera corregida, la comprobación que la encontró (misma herramienta, mismo recorrido con teclado, misma medición de contraste). Si ya no aparece, pasa su estado a `corregida`.
2. Vuelve a pasar la herramienta automática con las mismas condiciones y anota la puntuación «después». Si baja, o aparece una barrera nueva, anótalo y **detente**.
3. Repite la tarea principal solo con teclado de principio a fin.
4. Ejecuta `python3 $P/scripts/comun/verificar.py`.
5. Dile a la persona el resultado: barreras corregidas, pendientes y puntuación antes → después.

## Criterio de salida

- Cada barrera aprobada en `corregida`, comprobada con su misma herramienta; puntuación «después» anotada y no menor que «antes».
- La tarea principal se completa solo con teclado y `verificar.py` no da errores.
