# Caso: fichas de pedidos desfasadas tras una refactorización

## Pedido

«Hemos rehecho el módulo de pedidos. ¿Siguen al día las fichas de rutas? Déjalo por escrito.» Proyecto Nest con `rutas-de-api` instalado; sin `auditorias-tecnicas`, `paginas-de-interfaz`, `decisiones-de-arquitectura` ni `manuales-operativos`.

## Recorrido

**acotar-revision.** El pedido habla de rutas y de dejar constancia: revisiones `rutas` y `anclas` (las fichas de rutas citan archivos ancla), con `--informe`. El servidor no usa prefijo global, así que `prefijo_global` vacío es correcto. No se pide humo.

**ejecutar-revisiones.** Primero todas, para ver el panorama:

```
python3 $P/scripts/vivas.py
[rutas] alta: ficha activa sin ruta en el código: DELETE /orders/{} — uxyngraphar/trabajo/rutas-de-api/RUT-20261106-borrar-pedido.md
[rutas] media: ruta sin ficha: POST /orders — src/orders/orders.controller.ts:5
[paginas] info: paginas-de-interfaz no está instalado — —
[anclas] media: ancla rota: src/orders/orders.service.ts — uxyngraphar/trabajo/rutas-de-api/RUT-20261106-ver-pedido.md
[decisiones] info: decisiones-de-arquitectura no está instalado — —
[manuales] info: manuales-operativos no está instalado — —
[vinculos] media: id colgante: RUT-20260101-pedidos-viejos — uxyngraphar/trabajo/rutas-de-api/RUT-20261106-ver-pedido.md:43
verificaciones-vivas: 4 hallazgos
```

`contrastar-inventario`: el controlador ya no tiene `@Delete(':id')` y el nuevo `@Post()` no tiene ficha. `revisar-referencias`: la ficha `ver-pedido` cita un servicio borrado y una ficha que ya no existe.

**informar.** `guardar-informe` con las revisiones acordadas:

```
python3 $P/scripts/vivas.py rutas anclas --informe
…
verificaciones-vivas: 3 hallazgos
informe: uxyngraphar/trabajo/verificaciones-vivas/INFORME-20261106-rutas-anclas.md
```

| # | Severidad | Hallazgo | Evidencia |
|---|-----------|----------|-----------|
| 1 | alta | rutas: ficha activa sin ruta en el código: DELETE /orders/{} | `uxyngraphar/trabajo/rutas-de-api/RUT-20261106-borrar-pedido.md` |
| 2 | media | rutas: ruta sin ficha: POST /orders | `src/orders/orders.controller.ts:5` |
| 3 | media | anclas: ancla rota: src/orders/orders.service.ts | `uxyngraphar/trabajo/rutas-de-api/RUT-20261106-ver-pedido.md` |

Nota aparte: el id colgante `RUT-20260101-pedidos-viejos` (revisión `vinculos`, fuera del informe acordado).

**derivar-hallazgos.** Propuesta a la persona: retirar `RUT-20261106-borrar-pedido` (o restaurar el endpoint si su borrado fue un error), crear la ficha de `POST /orders` con `rutas-de-api` y actualizar las anclas y el vínculo de `RUT-20261106-ver-pedido`. Ninguna se hace sin su visto bueno. `verificar.py` sin errores.

## Resultado

- Un informe con tres hallazgos reproducible con `vivas.py rutas anclas`.
- Ningún archivo de código ni ficha modificados por el agente.
- Cada hallazgo con su flujo propuesto, a la espera de la persona.
