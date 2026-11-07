---
fase: consultar-ficha
resuelve: [endpoints-sin-ficha, rutas-documentadas-dos-veces]
skills: []
---

# Fase: consultar-ficha

## Objetivo

Saber qué contrato documentado tiene el endpoint antes de tocarlo, o confirmar que aún no tiene ficha.

## Entradas

- El pedido: qué endpoint (método y ruta) se crea, cambia o elimina.
- Las fichas de `uxyngraphar/trabajo/rutas-de-api/`.

## Pasos

1. Lista las fichas: `python3 $P/scripts/comun/fichas.py listar ruta` (filtra con `--status activa` si hay muchas).
2. Busca el endpoint por método y ruta en la lista y ábrelo: `python3 $P/scripts/comun/fichas.py ver <id>`.
3. Si aparecen dos fichas activas para el mismo método y ruta, detente y pregunta cuál describe el comportamiento real (límite 1).
4. Anota lo que el cambio no debe romper: «Entrada», «Salida», `auth` y `roles`.
5. Si no hay ficha, el endpoint se documentará en `documentar-cambio` con la skill `documentar-endpoint`.

## Criterio de salida

- Tienes el id de la ficha del endpoint o sabes que no existe.
- No hay dos fichas activas para el mismo método y ruta.
