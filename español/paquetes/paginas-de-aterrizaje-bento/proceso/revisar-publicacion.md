---
fase: revisar-publicacion
resuelve: [publicacion-sin-comprobar]
skills: [comprobar-checklist]
---

# Fase: revisar publicación

## Objetivo

Dejar la página lista para que una persona decida publicarla, con cada punto de la checklist comprobado de verdad.

## Entradas

- La página construida y su ficha en `en-curso`.
- `referencia/checklist-publicacion.md` (cómo se comprueba cada punto).

## Pasos

1. Aplica `comprobar-checklist`: marca cada casilla solo después de comprobarla.
2. Pasa la ficha a `revision`: `python3 $P/scripts/comun/fichas.py estado LAN-… revision`.
3. Ejecuta las verificaciones: `python3 $P/scripts/comun/verificar.py` y `python3 $P/scripts/verificar-bento.py`. En `revision` una casilla sin marcar es un error.
4. **Detente.** Dile a la persona dónde ver la página y que publicar es una acción suya (`estado LAN-… publicada --humano`).

## Criterio de salida

- Ficha en `revision` con la checklist completa y las verificaciones sin errores.
- La persona sabe que tiene que revisar y publicar.
