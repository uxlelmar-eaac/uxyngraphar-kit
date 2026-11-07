---
name: medir-cobertura
description: Muestra qué archivos y carpetas del código tienen espejo y cuáles no, con el porcentaje de cobertura, para decidir qué espejar primero.
resuelve: [codigo-sin-espejo]
---

# Medir cobertura

## Cuándo usarla

- Al empezar un pedido que abarca un módulo entero.
- Al adoptar el paquete en un proyecto existente.
- Cuando `verificar-espejo.py` falla por cobertura.

## Pasos

1. Ejecuta `python3 $P/scripts/espejo.py mapa --faltantes`: lista con `·` lo que no tiene espejo (las carpetas terminan en `/`) y al final `cobertura: N/M`.
2. Sin `--faltantes` muestra también lo cubierto (`✓`).
3. Prioriza: primero las carpetas de módulo, luego los archivos que el pedido toca, luego los puntos de entrada (controladores, casos de uso, páginas).
4. Si faltan muchos y el pedido no es espejarlos, resume por carpeta y propón tandas a la persona.

## Resultado

- La cobertura actual y la lista priorizada de lo que falta.
