---
fase: inventariar
resuelve: [interfaz-inconsistente]
skills: []
---

# Fase: inventariar

## Objetivo

Saber qué tokens y componentes compartidos tiene el proyecto antes de juzgar ninguna pantalla.

## Entradas

- El código del proyecto: tema, variables CSS, archivo de diseño y carpeta de componentes compartidos.
- `uxyngraphar/trabajo/componentes-de-interfaz/INTERFAZ.md`, si existe.

## Pasos

1. Si `INTERFAZ.md` no existe, cópialo desde `$P/plantillas/INTERFAZ.md`.
2. Localiza los tokens y anota en «Tokens» cada escala (color, espaciado, tipografía, radios, sombras) con su archivo y sus valores. Si el inventario ya existe, compruébalo contra el código y actualiza lo que haya cambiado.
3. Localiza los componentes compartidos y anota en «Componentes compartidos» su ruta y su propósito. Si dos sirven para lo mismo, anótalo: será un hallazgo `duplicado`.
4. Si el proyecto no tiene tokens ni componentes compartidos localizables, **detente** y pregunta: sin referencia no hay consistencia que revisar.

## Criterio de salida

- «Inventario» en `INTERFAZ.md` con al menos la escala de color y la de espaciado, y los componentes compartidos con su ruta.
