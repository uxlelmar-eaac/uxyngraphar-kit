---
fase: buscar-duplicados
resuelve: [cola-de-mejoras-inmanejable]
skills: [ampliar-evidencia]
---

# Fase: buscar duplicados

## Objetivo

No crear una ficha para algo que ya está en la cola.

## Entradas

- El problema clasificado como mejora.
- Las fichas existentes.

## Pasos

1. Lista las pendientes: `python3 $P/scripts/comun/fichas.py listar mejora --status pending`; y, si sospechas que ya se trató, también `approved`, `done` y `rejected`.
2. Busca por archivo y por síntoma (por ejemplo, `rg -l "src/orders/list.ts" uxyngraphar/trabajo/deuda-y-mejoras/`).
3. Si existe una ficha `pending` o `approved` del mismo problema o de la misma causa, aplica `ampliar-evidencia` y termina aquí.
4. Si existe una `rejected`, no la reabras por tu cuenta: menciónala a la persona con la evidencia nueva.

## Criterio de salida

- Sabes que no hay ficha del problema, o la evidencia nueva quedó en la ficha existente.
