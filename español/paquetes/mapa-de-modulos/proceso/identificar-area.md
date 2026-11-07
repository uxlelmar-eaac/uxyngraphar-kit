---
fase: identificar-area
resuelve: [cambios-sin-area-identificada]
skills: []
---

# Fase: identificar-area

## Objetivo

Saber en qué área cae el pedido y haber leído lo mínimo para cambiarla.

## Entradas

- El pedido de la persona.
- Los contextos de `uxyngraphar/trabajo/mapa-de-modulos/`.

## Pasos

1. Lista las áreas: `python3 $P/scripts/comun/fichas.py listar area`.
2. Elige el área por sus fronteras («Posee»), no por el nombre de la carpeta del código. Ábrela: `python3 $P/scripts/comun/fichas.py ver <id>`.
3. Sigue su «Mapa de lectura» en orden.
4. Si el cambio toca varias áreas, lee el contexto de cada una y anota qué dependencia nueva aparece.
5. Si no encaja en ninguna, detente y pregunta si es un área nueva (límites, «Cuándo detenerse»).

## Criterio de salida

- Sabes qué área o áreas toca el pedido y has seguido su mapa de lectura.
- Sabes si el cambio altera fronteras, dependencias o código ancla (si no, el proceso termina en `verificar`).
