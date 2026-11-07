---
fase: disenar-modulo
resuelve: [modulos-sin-estructura-uniforme, modulos-acoplados]
skills: [crear-modulo]
---

# Fase: diseñar módulo

Solo si el pedido crea un módulo de negocio nuevo; si no, pasa a `implementar`.

## Objetivo

Que el módulo nazca con las capas del perfil, un nombre claro y sus dependencias con otros módulos ya identificadas.

## Entradas

- El área funcional que pide la persona.
- El perfil del proyecto (`servidor` o `cliente`).

## Pasos

1. Elige el nombre: sustantivo en plural, en inglés y kebab-case si el código está en inglés (`orders`, `payment-methods`).
2. Comprueba que no exista ya un módulo que cubra esa área (`capas.py mapa`). Si existe, el cambio va allí.
3. Lista qué necesita de otros módulos. Cada necesidad será un método en `integrations/<otro-modulo>.integration.<ext>`.
4. Aplica la skill `crear-modulo`.

## Criterio de salida

- El módulo existe con las capas que necesita, sin carpetas vacías.
- Las dependencias con otros módulos están listadas como métodos de `integrations/`.
