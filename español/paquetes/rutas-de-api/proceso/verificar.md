---
fase: verificar
resuelve: [rutas-documentadas-dos-veces, fichas-de-ruta-desfasadas]
skills: []
---

# Fase: verificar

## Objetivo

Demostrar que las fichas tienen los campos obligatorios, que no hay endpoints documentados dos veces y que las anclas existen.

## Entradas

- Las fichas creadas o tocadas en `documentar-cambio`.

## Pasos

1. Ejecuta `python3 $P/scripts/verificar-rutas.py`.
2. Cada `error:` se corrige ahora: `faltan campos …` → rellena el frontmatter; `«GET /orders» ya está documentada en …` → une las fichas o pasa la vieja a `retirada`.
3. Cada `aviso: … archivo ancla inexistente …` de una ficha que tocaste se corrige; los de fichas ajenas al pedido se mencionan al cerrar.
4. Ejecuta `python3 $P/scripts/comun/verificar.py` (integridad del paquete y status de las fichas).

## Criterio de salida

- `verificar-rutas.py` termina con código 0 y sin avisos en las fichas tocadas.
- `verificar.py` sin errores.
