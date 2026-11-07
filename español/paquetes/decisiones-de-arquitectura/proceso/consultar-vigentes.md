---
fase: consultar-vigentes
resuelve: [decisiones-contradichas, decisiones-sin-registro]
skills: [buscar-adr-vigentes]
---

# Fase: consultar-vigentes

## Objetivo

Saber, antes de decidir o cambiar algo estructural, qué ADR aceptadas lo condicionan y si el pedido necesita una ADR nueva.

## Entradas

- El pedido de la persona o el cambio que se está preparando.
- Las ADR del trabajo en `uxyngraphar/trabajo/decisiones-de-arquitectura/`.

## Pasos

1. Aplica la skill `buscar-adr-vigentes` con los términos del pedido (tecnología, área, patrón).
2. Si una ADR aceptada cubre el pedido y el pedido la cumple, cítala y termina: no hace falta una ADR nueva.
3. Si el pedido la contradice, detente: lo que sigue es una ADR que la reemplace (`redactar-adr` con `reemplaza: <id>`).
4. Si ninguna lo cubre, decide con el límite 1 si la decisión es cara de revertir. Si lo es, pasa a `redactar-adr`; si no, dilo y termina.
5. Mira también las ADR en `propuesta` o `en-evaluacion` del mismo tema: no abras una segunda sobre lo mismo.

## Criterio de salida

- Sabes qué ADR aceptadas aplican (puede no haber ninguna) y si hace falta una nueva, un reemplazo o nada.
