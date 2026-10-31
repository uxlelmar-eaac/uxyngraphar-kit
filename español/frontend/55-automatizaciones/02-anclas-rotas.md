---
id: auto.02.anclas-rotas
stack: [cliente]
---

# 02: anclas-rotas

## Fuente

`15-rutas/` (archivos ancla por ficha) y `25-areas/*/CONTEXTO.md`
(código ancla por área).

## Valida

Que cada path de código citado en la documentación existe todavía.
Caza referencias muertas tras refactors.

## Procedimiento

1. Extraer todos los paths citados como ancla en fichas y CONTEXTOs.
2. Verificar existencia de cada uno en el árbol del proyecto.

## Aceptación

- [ ] Cero anclas que apunten a archivos inexistentes.
- [ ] Cada ancla movida se reporta con su nueva ubicación sugerida
  (búsqueda por nombre de archivo).

## Salida

Lista: `documento que cita | ancla rota | sugerencia`.
