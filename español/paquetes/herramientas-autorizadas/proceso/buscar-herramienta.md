---
fase: buscar-herramienta
resuelve: [procedimientos-repetidos-sin-atajo, herramientas-usadas-fuera-de-alcance]
skills: [comprobar-encaje-de-pedido]
---

# Fase: buscar-herramienta

## Objetivo

Saber si una herramienta autorizada y vigente cubre el pedido tal como está, o si el pedido sigue el proceso normal.

## Entradas

- El pedido de la persona.
- Las fichas de `uxyngraphar/trabajo/herramientas-autorizadas/autorizadas/`.

## Pasos

1. Lista las vigentes: `python3 $P/scripts/comun/fichas.py listar autorizada --status authorized`. Las `revoked` no cuentan.
2. Por el título, elige las candidatas y aplica `comprobar-encaje-de-pedido` a cada una.
3. Si ninguna encaja, el pedido sigue el proceso normal (con `instrucciones-aprobadas`, si está instalado). Si es un procedimiento que se repite, pasa además por `proponer-herramienta`.
4. Si una encaja, pasa a `ejecutar-herramienta`.

## Criterio de salida

- Hay una herramienta vigente cuyo «Alcance permitido» cubre el pedido entero, o la certeza de que no la hay.
