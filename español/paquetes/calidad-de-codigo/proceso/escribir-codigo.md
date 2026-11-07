---
fase: escribir-codigo
resuelve: [nombres-poco-explicativos, archivos-demasiado-largos]
skills: [elegir-nombres, dividir-archivo]
---

# Fase: escribir código

## Objetivo

Que todo lo que el pedido añade o cambia cumpla los límites desde el primer borrador, sin dejar la limpieza para después.

## Entradas

- Los problemas heredados de `diagnosticar`.
- Las guías `referencia/nombres.md` y `referencia/limite-lineas.md`.

## Pasos

1. Nombra cada identificador, archivo y carpeta nuevos con la skill `elegir-nombres`: verbo + objeto en funciones, unidad en las magnitudes, sin genéricos y con el casing del lenguaje.
2. Los comentarios explican el porqué (una decisión, una restricción externa), no traducen un mal nombre.
3. Si un archivo que tocas pasa de `limite_lineas`, aplica la skill `dividir-archivo` en esta misma tarea.
4. No renombres nombres genéricos heredados salvo que sea seguro, haya pruebas y todos sus usos estén dentro de lo que pidió la persona.

## Criterio de salida

- Ningún nombre nuevo genérico ni archivo nuevo con espacios en el nombre.
- Ningún archivo que hayas hecho crecer supera el límite.
