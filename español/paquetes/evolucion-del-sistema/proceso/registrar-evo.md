---
fase: registrar-evo
resuelve: [carencias-del-sistema-sin-registro]
skills: [redactar-evo]
---

# Fase: registrar EVO

## Objetivo

Dejar la carencia como una EVO única, con evidencia y propuesta, dentro del límite por tarea.

## Entradas

- La carencia y su evidencia.
- Las EVO pendientes (solo para evitar duplicados).

## Pasos

1. Busca duplicados: `python3 $P/scripts/comun/fichas.py listar evo --status pending`. Si ya existe una EVO de lo mismo, añade allí la evidencia nueva y termina.
2. Si ya registraste `max_por_tarea` EVO en esta tarea, no crees otra: menciónalo a la persona.
3. Aplica `redactar-evo`.
4. Ejecuta las verificaciones: `python3 $P/scripts/comun/verificar.py` y `python3 $P/scripts/verificar-evolucion.py`.
5. Al cerrar la tarea, menciona la EVO creada (id y una línea).

## Criterio de salida

- EVO `pending` con tipo válido, evidencia y propuesta; `verificar-evolucion.py` sin errores ni avisos sobre ella.
