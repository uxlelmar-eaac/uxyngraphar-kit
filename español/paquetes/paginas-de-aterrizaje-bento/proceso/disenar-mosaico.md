---
fase: disenar-mosaico
resuelve: [paginas-sin-objetivo-unico, mosaico-sin-jerarquia, celdas-sobrecargadas, orden-movil-incorrecto]
skills: [componer-mosaico, escribir-celda]
---

# Fase: diseñar mosaico

## Objetivo

Tener en la ficha un mosaico completo y válido (tamaños, prioridades, textos, CTA y medios) y su orden móvil, antes de escribir código.

## Entradas

- La ficha con objetivo y audiencia.
- `referencia/patrones-bento.md` (composiciones probadas y errores frecuentes).
- Los ajustes efectivos (`columnas`, `tamanos`, `celdas_min`, `celdas_max`, `max_2x2`, límites de palabras).

## Pasos

1. Lista los mensajes que la audiencia necesita para decidir y ordénalos por importancia; el primero es la protagonista.
2. Aplica `componer-mosaico` para elegir tamaños que llenen filas completas y den la celda mayor a la prioridad 1.
3. Aplica `escribir-celda` a cada celda: título, mensaje, CTA y medio.
4. Rellena «Orden móvil»: apilado por prioridad 1 → n. Si alguna excepción está justificada (p. ej. la banda `4x1` con el CTA va primero), escríbela con su motivo.
5. Ejecuta `python3 $P/scripts/verificar-bento.py`. En `borrador` los fallos del mosaico salen como avisos: corrígelos todos igualmente.
6. Pasa la ficha a `en-curso`: `python3 $P/scripts/comun/fichas.py estado LAN-… en-curso`. Desde aquí los fallos del mosaico son errores.

## Criterio de salida

- Ficha en `en-curso` con «Mosaico» y «Orden móvil» completos.
- `verificar-bento.py` sin errores ni avisos para esa ficha.
