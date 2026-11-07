---
fase: implementar
resuelve: [cambios-de-interfaz-sin-aprobacion]
skills: []
---

# Fase: implementar

Solo si la ficha está en `aprobada` (lo puso una persona). Si sigue en `propuesta`, esta fase no se recorre.

## Objetivo

Aplicar en el código exactamente las filas aprobadas, sin empeorar lo que ya funcionaba.

## Entradas

- La ficha en `aprobada` y las filas con «sí» en «Aprobada».

## Pasos

1. Implementa solo las filas con «sí»; las demás siguen como propuesta aunque parezcan triviales.
2. Usa los componentes y tokens del proyecto que nombra la propuesta. Si `componentes-de-interfaz` o `pautas-de-accesibilidad` están instalados, sus límites rigen sobre lo que toques.
3. Al terminar, repite la tarea del usuario sobre lo tocado, también solo con teclado: nada puede quedar peor que antes.
4. Rellena «Implementación»: filas implementadas y archivos tocados.
5. Lo que encuentres fuera del alcance va a «Notas» (o a `deuda-y-mejoras` si es un bug); no lo arregles.
6. Pasa la ficha a `implementada`: `python3 $P/scripts/comun/fichas.py estado UXE-… implementada`.

## Criterio de salida

- Solo las filas aprobadas están en el código y la tarea del usuario se completa sobre lo tocado.
- Ficha en `implementada` con «Implementación» rellena.
