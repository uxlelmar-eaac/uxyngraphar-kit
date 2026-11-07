---
fase: redactar-brief
resuelve: [paginas-sin-objetivo-unico]
skills: []
---

# Fase: redactar brief

## Objetivo

Fijar, antes de diseñar, qué debe hacer el visitante al terminar la página y para quién se escribe.

## Entradas

- El pedido de la persona (producto, campaña, acción esperada).
- Páginas anteriores del mismo tema: `python3 $P/scripts/comun/fichas.py listar landing`.

## Pasos

1. Si ya existe una ficha de esa página en `borrador` o `en-curso`, continúa esa.
2. Abre la ficha: `python3 $P/scripts/comun/fichas.py nueva landing --slug <slug> --titulo "…"`. Nace `borrador` en `uxyngraphar/trabajo/paginas-de-aterrizaje-bento/pendientes/`.
3. Escribe «Objetivo» en una frase con la acción del CTA primario («crear una cuenta gratis»). Si el pedido trae dos acciones principales, pregunta cuál manda.
4. Escribe «Audiencia»: quién llega, desde dónde (anuncio, correo, buscador) y qué necesita saber para decidir.
5. Anota en `ruta_pagina` del frontmatter la ruta donde vivirá la página (`/precios`, `/lanzamiento`).

## Criterio de salida

- Ficha `LAN-…` con «Objetivo» de una sola acción y «Audiencia» rellenos.
