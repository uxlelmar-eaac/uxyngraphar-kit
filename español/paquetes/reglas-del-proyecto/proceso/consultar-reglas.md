---
fase: consultar-reglas
resuelve: [reglas-incumplidas-en-silencio]
skills: [listar-reglas-aplicables]
---

# Fase: consultar reglas

## Objetivo

Saber, antes de escribir nada, qué reglas del proyecto tocan las rutas del pedido.

## Entradas

- El pedido y las rutas o anclas que afecta (las de la instrucción, si la hay).

## Pasos

1. Aplica la skill `listar-reglas-aplicables` con las rutas o anclas del pedido. Si el pedido no da rutas aún, usa `reglas.py indice` y vuelve a esta fase cuando las sepas.
2. Si el pedido es crear, retirar o cambiar una regla o una excepción, salta a `proponer-cambios`.

## Criterio de salida

- Tienes la lista de reglas aplicables (puede estar vacía) con su nivel.
