# Caso: por qué el listado de pedidos tarda 3 segundos

## Pedido

«Usa el paquete auditorias-tecnicas: investiga por qué `GET /orders` tarda unos 3 s con 200 pedidos.» Ajustes por defecto (5 activas como máximo, 14 días sin cambios). Tentación habitual: ver el problema y arreglarlo ya. Aquí no se hace.

## Recorrido

**abrir-auditoria.** `revisar-activas`: `fichas.py listar auditoria --status activa` no devuelve ninguna. Se abre la ficha:

```
python3 $P/scripts/comun/fichas.py nueva auditoria --slug listado-pedidos-lento --titulo "Listado de pedidos lento"
…/trabajo/auditorias-tecnicas/en-progreso/AUD-20261106-listado-pedidos-lento.md
```

Alcance: incluye `src/orders/` y el esquema de la base de datos; excluye el cliente web y la infraestructura. `areas: [orders]`. Preguntas: 1) ¿qué parte del tiempo es base de datos? 2) ¿cuántas consultas hace una petición? 3) ¿falta algún índice en las consultas del listado? Método: log SQL activado en local, `EXPLAIN ANALYZE` de las consultas, lectura de `src/orders/list.ts`.

**investigar.** Con `registrar-hallazgo` quedan tres filas (sin tocar código ni esquema):

```
| 1 | alta  | El listado hace una consulta por pedido     | `src/orders/list.ts:42`; log SQL con 201 consultas |
| 2 | media | orders.customer_id sin índice               | `prisma/schema.prisma:58`; EXPLAIN con Seq Scan     |
| 3 | info  | La tabla orders tiene 2,1 millones de filas | `SELECT count(*) FROM orders`                        |
```

Al olvidar actualizar el contador, la verificación avisa mientras la auditoría está activa:

```
python3 $P/scripts/verificar-auditorias.py
aviso: en-progreso/AUD-20261106-listado-pedidos-lento.md: findings_count=2 pero hay 3 hallazgos
auditorias: 0 errores, 1 avisos
```

Si se cerrara así, sería un error:

```
error: completadas/AUD-20261106-listado-pedidos-lento.md: findings_count=2 pero hay 3 hallazgos
auditorias: 1 errores, 0 avisos
```

Se pone `findings_count: 3` y `actualizado` con la fecha de hoy.

**concluir.** Conclusiones: 1) ~2,7 s de los 3 s son base de datos (#1, #2); 2) 201 consultas por petición (#1); 3) falta el índice de `customer_id` (#2). Recomendaciones y promociones propuestas:

```
- (tipo: instruccion) — instrucciones-aprobadas — cargar los clientes del listado en una sola consulta (#1)
- (tipo: adr) — decisiones-de-arquitectura — política de índices para claves foráneas en tablas de más de 1 millón de filas (#2, #3)
```

`fichas.py estado AUD-20261106-listado-pedidos-lento cerrada`; `verificar.py` y `verificar-auditorias.py` sin errores. El agente se detiene y pregunta qué promociones acepta la persona.

**promover.** La persona acepta solo la instrucción. Con `promover-resultado` se crea la instrucción en `instrucciones-aprobadas` citando `AUD-20261106-listado-pedidos-lento` y la evidencia del hallazgo 1, y se anota en `promociones: [INS-20261106-listado-una-consulta]`. La ADR queda como propuesta en la ficha.

## Resultado

- Ficha `AUD-20261106-listado-pedidos-lento` en `completadas/` con 3 hallazgos con evidencia y dos promociones propuestas, una aceptada.
- Ni una línea de `src/orders/` modificada: el arreglo llegará por la instrucción aprobada.
