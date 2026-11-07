# Caso: cupones en un servicio de pedidos que pasa del límite

## Pedido

«Añade cupones de descuento al cálculo del total del pedido.» Proyecto TypeScript, `limite_lineas: 350`.

## Recorrido

**diagnosticar.** `revisar-calidad` sobre el archivo que se va a tocar:

```
python3 $P/scripts/calidad.py src/orders/order-service.ts
calidad-de-codigo: 1 archivos revisados, 0 problemas
```

`order-service.ts` tiene 330 líneas: los cupones lo harán pasar. Cerca del cambio hay un `const data = await repo.find()` heredado: se anota, no se renombra (sus usos salen del pedido).

**escribir-codigo.** Primer borrador dentro del mismo archivo, con nombres de `elegir-nombres` (`applyCouponDiscount`, `couponCode`, `discountAmountCents`, no `apply`, `code`, `discount`). `calidad.py` responde:

```
src/orders/order-service.ts: 395 líneas (límite 350); divide por responsabilidad (referencia/limite-lineas.md)
calidad-de-codigo: 1 archivos revisados, 1 problemas
```

**dividir-archivo** (skill). Responsabilidades: cálculo de precios, validación del pedido y orquestación. Se extraen `order-service.pricing.ts` (totales, impuestos y cupones) y `order-service.validation.ts`; `order-service.ts` queda como fachada que compone y reexporta `calculateOrderTotal`, así que sus importadores no cambian. Las pruebas de precios pasan a `order-service.pricing.spec.ts`.

**verificar.**

```
python3 $P/scripts/calidad.py src/orders/order-service.ts src/orders/order-service.pricing.ts src/orders/order-service.validation.ts
calidad-de-codigo: 3 archivos revisados, 0 problemas
```

El `data` heredado se menciona al cerrar (o se registra en `deuda-y-mejoras` si está instalado).

## Resultado

- `src/orders/` con tres archivos por debajo de 350 líneas y los mismos exports que antes.
- Ningún nombre nuevo genérico; el heredado, a la vista y sin tocar.
- Si están instalados, `idiomas-del-codigo` habría decidido el idioma de los nombres (`coupon`, no `cupon`), `mensajes-de-commit` el mensaje del commit y `documentacion-espejo` pediría la ficha de los dos archivos nuevos.
