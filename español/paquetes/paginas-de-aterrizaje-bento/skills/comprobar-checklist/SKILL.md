---
name: comprobar-checklist
description: Comprueba en la página construida cada punto de la checklist de publicación (contraste, foco, alt, movimiento, carga, saltos de diseño, tres tamaños, CTA) y los marca en la ficha solo tras comprobarlos.
resuelve: [publicacion-sin-comprobar, orden-movil-incorrecto]
---

# Comprobar checklist

## Cuándo usarla

- En `revisar-publicacion`, antes de pasar la ficha a `revision`.
- Cuando `verificar-bento.py` informa de «checklist incompleta».

## Pasos

1. Abre la página en el navegador y recorre los puntos de «Checklist de publicación» con el método de `referencia/checklist-publicacion.md`.
2. Contraste (≥ 4.5:1 texto, ≥ 3:1 grande y controles) y puntuación de Lighthouse; foco con Tab siguiendo la prioridad del mosaico.
3. Imágenes: `alt` de la ficha en las informativas, `alt=""` o `aria-hidden` en las decorativas; protagonista con carga prioritaria y el resto diferida; CLS < 0.1.
4. Activa «reducir movimiento» en el sistema y comprueba que no queda paralaje ni animación de desplazamiento.
5. Revisa móvil (~375 px), tableta (~768 px) y escritorio (≥ 1280 px): en móvil la protagonista va primera.
6. Pulsa el CTA primario: llega a su destino y tiene nombre accesible.
7. Marca `- [x]` cada punto comprobado. Si uno no aplica, márcalo y explica por qué en «Notas»; si falla, corrige la página antes de marcarlo.

## Resultado

- Checklist completa en la ficha, con cada punto comprobado de verdad.
