# Caso: separar el cálculo de totales del servicio de pedidos

## Pedido

«Saca el cálculo de totales de `src/orders/service.ts` a un archivo propio `src/orders/pricing.ts`, y renombra `src/orders/service.ts` a `src/orders/orders.service.ts`.»

## Recorrido

**leer-espejo.**

```
$ python3 $P/scripts/espejo.py ver src/orders/service.ts
# `service.ts`
> Espejo de: `src/orders/service.ts` · 412 líneas · actualizado 2026-09-02
## Rol
Orquesta la creación de pedidos y calcula su total con impuestos y descuentos.
…
$ python3 $P/scripts/espejo.py ver src/orders/pricing.ts
sin espejo: src/orders/pricing.ts (créalo con «espejo.py nuevo src/orders/pricing.ts»)
```

Lista: mover `service.md` → `orders.service.md`; actualizar su rol; crear `pricing.md`; actualizar la tabla «Contenido» del `README.md` de `src/orders/`.

**actualizar-espejo → mover-espejo** (skill):

```
git mv uxyngraphar/trabajo/documentacion-espejo/src/orders/service.md uxyngraphar/trabajo/documentacion-espejo/src/orders/orders.service.md
```

Cabecera y cambios:

```markdown
> Espejo de: `src/orders/orders.service.ts` · 260 líneas · actualizado 2026-11-06

## Rol
Orquesta la creación de pedidos.

## Interacciones
| Con | Cómo |
|-----|------|
| `src/orders/pricing.ts` | le pide el total del pedido |
```

En el `README.md` de `src/orders/`, la fila de `service.ts` pasa a `orders.service.ts` y se añade `pricing.ts`.

**actualizar-espejo → crear-espejo** (skill):

```
$ python3 $P/scripts/espejo.py nuevo src/orders/pricing.ts
uxyngraphar/trabajo/documentacion-espejo/src/orders/pricing.md
```

«Rol»: «Calcula el total de un pedido: subtotal, descuentos por cupón e IVA por país». «Puntos de extensión»: «reglas de descuento nuevas en `applyDiscounts`». Sin código pegado.

**verificar.**

```
$ python3 $P/scripts/espejo.py huerfanos
$ python3 $P/scripts/verificar-espejo.py
espejo: cobertura 14/31 (45%), 0 errores
```

## Resultado

- El espejo del servicio sigue al archivo renombrado, con su historial y su rol reducido.
- `pricing.ts` nace con espejo; ningún huérfano.
