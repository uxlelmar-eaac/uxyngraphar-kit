---
fase: diagnosticar
resuelve: [modulos-acoplados, capas-mal-importadas, comun-dependiente-del-negocio]
skills: [revisar-imports]
---

# Fase: diagnosticar

## Objetivo

Saber dónde cae el pedido (qué módulo, qué capas) y cuál es el estado de partida de los imports, para no confundir infracciones heredadas con las propias.

## Entradas

- El pedido de la persona.
- `uxyngraphar/trabajo/arquitectura-monolitica-por-capas/ARQUITECTURA.md`, si existe (lo concreto de este repo).
- Los ajustes efectivos (`perfil`, `nivel`, `modulos`, `comun`).

## Pasos

1. Ejecuta `python3 $P/scripts/capas.py mapa` y localiza el módulo y las capas afectadas.
2. Si existe `ARQUITECTURA.md`, lee sus «Desviaciones aceptadas» y «Restricciones propias».
3. Aplica la skill `revisar-imports` sobre las rutas que vas a tocar y anota las infracciones que ya existían.
4. Decide la fase siguiente: módulo nuevo → `disenar-modulo`; cambio en un módulo existente → `implementar`.

## Criterio de salida

- Sabes qué módulo y qué capas tocas.
- Tienes la lista de infracciones previas en esas rutas (puede estar vacía).
