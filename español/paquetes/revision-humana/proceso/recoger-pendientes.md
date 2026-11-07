---
fase: recoger-pendientes
resuelve: [decisiones-dispersas, pendientes-envejecidos]
skills: [priorizar-pendientes-antiguos]
---

# Fase: recoger-pendientes

## Objetivo

Tener la lista completa de fichas que esperan a una persona en todos los paquetes instalados, ordenada de la más antigua a la más nueva.

## Entradas

- Los paquetes instalados en `uxyngraphar/paquetes/` y sus fichas en `uxyngraphar/trabajo/`.
- `dias_aviso` en los ajustes (14 por defecto).

## Pasos

1. Ejecuta `python3 $P/scripts/revision.py pendientes`. Cada pendiente sale con su id, paquete, status, días esperando, título y el comando que debe ejecutar la persona con las opciones válidas.
2. Si sale `(nada espera una decisión)`, dilo y termina aquí.
3. Aplica la skill `priorizar-pendientes-antiguos` para separar las que superan `dias_aviso`.
4. Si la persona pidió revisar solo un paquete, quédate con sus filas y menciona cuántas quedan del resto.

## Criterio de salida

- Tienes la lista de pendientes (o la certeza de que no hay ninguno) y sabes cuáles superan `dias_aviso`.
