---
fase: redactar-pasos
resuelve: [procedimientos-sin-manual, manuales-desfasados, pasos-no-ejecutables, procedimientos-sin-reversion]
skills: [crear-manual, actualizar-manual]
---

# Fase: redactar-pasos

## Objetivo

Que cada manual afectado describa el procedimiento tal como queda tras el cambio, con pasos ejecutables y reversión.

## Entradas

- La lista de `localizar-manual`.
- El código y la configuración tras el cambio.

## Pasos

1. Manual nuevo → skill `crear-manual`. Manual existente → skill `actualizar-manual`.
2. Repasa cada paso: comando exacto, resultado esperado tras `→`, sin valores secretos (solo `<PLACEHOLDER>` y de dónde sale).
3. Si el procedimiento cambia el sistema, «Cómo revertir» está escrito y es ejecutable.
4. Si un procedimiento ya lo describe otro manual, enlázalo en lugar de copiarlo.

## Criterio de salida

- Ningún paso sin comando o sin resultado esperado.
- Ningún valor secreto en el manual.
- «Cómo revertir» presente en todo manual que cambia el sistema.
