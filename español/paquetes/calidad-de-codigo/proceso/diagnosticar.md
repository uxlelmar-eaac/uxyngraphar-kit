---
fase: diagnosticar
resuelve: [archivos-demasiado-largos, nombres-poco-explicativos]
skills: [revisar-calidad]
---

# Fase: diagnosticar

## Objetivo

Conocer el estado de partida de los archivos que vas a tocar, para separar los problemas heredados de los que introduzca la tarea.

## Entradas

- El pedido de la persona y los archivos o carpetas que afecta.
- Los ajustes efectivos (`limite_lineas`, `exenciones_lineas`, `excluir`).

## Pasos

1. Aplica la skill `revisar-calidad` sobre los archivos que vas a modificar y anota los que ya exceden el límite o tienen espacios en el nombre.
2. Anota cuántas líneas tiene cada archivo que vas a hacer crecer: si queda cerca del límite, planifica desde ya en qué archivo hermano irá lo nuevo.
3. Anota los nombres genéricos heredados (`data`, `utils.ts`, `handle()`) cerca del cambio: no se renombran de paso si sus usos salen de lo que pidió la persona.

## Criterio de salida

- Tienes la lista de problemas heredados en los archivos afectados (puede estar vacía).
- Sabes qué archivos necesitarán un hermano para no pasar del límite.
