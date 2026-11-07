---
name: resumir-pendiente
description: Escribe para una fila de REVISION.md una o dos líneas con qué se decide y qué pasa con cada opción, enlazando la ficha en lugar de copiarla.
resuelve: [decisiones-dispersas]
---

# Resumir pendiente

## Cuándo usarla

- En `preparar-revision`, una vez por fila.

## Pasos

1. Abre solo la ficha (`python3 uxyngraphar/paquetes/<paquete>/scripts/comun/fichas.py ver <id>`); no recorras el código ni el historial.
2. Escribe una línea con qué se decide, en términos de efecto: «Aprobar permite tocar 2 archivos de `src/orders/` para filtrar por estado».
3. Si las «Opciones» tienen efectos distintos, una segunda línea con lo que pasa con cada una (`aceptada` vincula al equipo; `rechazada` la cierra).
4. Añade la ruta de la ficha para que la persona la abra si quiere más detalle.
5. Señala lo que la persona debe saber antes de decidir (una ampliación de alcance, una ADR que se reemplaza), sin recomendar una opción salvo que lo pida.

## Resultado

- Un resumen de una o dos líneas por fila, con el enlace a la ficha.
