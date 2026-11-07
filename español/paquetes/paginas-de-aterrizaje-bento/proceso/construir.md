---
fase: construir
resuelve: [orden-movil-incorrecto, celdas-sobrecargadas]
skills: []
---

# Fase: construir

## Objetivo

Que la página en el código sea exactamente el mosaico de la ficha, con su orden móvil, su accesibilidad y su carga de medios.

## Entradas

- La ficha en `en-curso`.
- Los componentes y tokens del proyecto.

## Pasos

1. Construye la rejilla con `columnas` columnas; cada celda ocupa su `ancho x alto` (p. ej. `grid-column: span 2; grid-row: span 2` para `2x2`).
2. Escribe las celdas en el DOM **en orden de prioridad** y colócalas en la rejilla con CSS: así el apilado móvil y el orden de tabulación siguen la prioridad sin trucos.
3. Una celda clicable entera lleva un único enlace con nombre accesible; el CTA primario es un botón o enlace real, no un `div`.
4. Medios: `img` con el `alt` de la ficha, `width`/`height` o `aspect-ratio` reservados; la imagen de la protagonista con carga prioritaria y el resto con `loading="lazy"`; iconos decorativos con `aria-hidden`.
5. Animaciones dentro de `@media (prefers-reduced-motion: no-preference)`.
6. Si al construir una celda cambia (texto, tamaño, medio), cambia primero la ficha y vuelve a pasar `verificar-bento.py`.
7. Anota en `archivos` del frontmatter los archivos de la página.

## Criterio de salida

- La página en el código coincide celda a celda con la ficha.
- `archivos` del frontmatter lista los archivos tocados.
