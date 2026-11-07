# Caso: reembolsos que cierran un ciclo entre pedidos y pagos

## Pedido

«Cuando se cancela un pedido ya cobrado, reembólsalo.» Áreas documentadas: `orders` (`depends_on: [payments, catalog]`) y `payments` (`depends_on: []`).

## Recorrido

**identificar-area.** `fichas.py listar area` muestra `orders`, `payments` y `catalog`. «Posee» de `payments`: cobros, reembolsos, conciliación con la pasarela. El reembolso es de `payments`; el disparador (la cancelación) es de `orders`. Se sigue el mapa de lectura de los dos.

Primera idea del agente: que `payments` consulte el estado del pedido para decidir si reembolsa. Eso añade `orders` a `depends_on` de `payments`.

**actualizar-contexto.** Se edita `payments/ARE-…-payments.md` con `depends_on: [orders]` para probar.

**verificar → revisar-dependencias-entre-areas** (skill):

```
$ python3 $P/scripts/verificar-areas.py
error: ciclo de dependencias: orders → payments → orders
areas: 3 áreas, 1 errores, 0 avisos
```

El ciclo lo introduce la tarea, así que se corrige: `orders` decide (posee el estado del pedido) y llama a `payments` con `refund(orderId, amount)`; `payments` no necesita saber nada de pedidos. Se revierte `depends_on` de `payments` a `[]` y se actualizan sus fronteras:

```markdown
## Fronteras
- Posee: cobros, reembolsos (a petición de otra área), conciliación con la pasarela.
- No posee: el estado de los pedidos ni la decisión de reembolsar (área orders).
```

En `orders`, «Flujos críticos» añade «cancelación de pedido cobrado → reembolso en payments».

```
$ python3 $P/scripts/verificar-areas.py
areas: 3 áreas, 0 errores, 0 avisos
```

## Resultado

- Reembolso en `payments`, decidido por `orders`; el grafo sigue sin ciclos.
- Fronteras de las dos áreas actualizadas para que la decisión quede escrita.
