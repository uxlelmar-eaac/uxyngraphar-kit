# Caso: endpoint para cancelar un pedido y retirada del antiguo

## Pedido

«Añade `POST /orders/:id/cancel` para que el cliente cancele su pedido. El antiguo `DELETE /orders/:id` deja de existir.» Módulo `orders`.

## Recorrido

**consultar-ficha.** `fichas.py listar ruta --status activa` muestra `RUT-20260310-delete-orders-id` (`DELETE /orders/:id`, `auth: bearer`, `roles: [customer]`) y ninguna ficha para `POST /orders/:id/cancel`.

**documentar-cambio → documentar-endpoint** (skill):

```
python3 $P/scripts/comun/fichas.py nueva ruta --slug post-orders-id-cancel --en orders --titulo "POST /orders/:id/cancel"
```

Frontmatter: `method: POST`, `path: /orders/:id/cancel`, `auth: bearer`, `roles: [customer]`, `module: orders`. Secciones, leídas del código:

```markdown
## Hace
Cancela un pedido del cliente autenticado si aún no se ha enviado.

## Entrada
- Parámetros: `id` (uuid del pedido).
- Cuerpo: `{ "reason": string }` opcional, máximo 200 caracteres.

## Salida
- 200: `{ "id", "status": "cancelled", "cancelledAt" }`.
- Errores relevantes: 401 sin sesión, 403 el pedido es de otro cliente, 404 no existe, 409 ya enviado.

## Archivos ancla
- `src/modules/orders/presentation/orders.controller.ts`
- `src/modules/orders/application/cancel-order.usecase.ts`
```

**documentar-cambio → retirar-endpoint** (skill): en la ficha antigua, «Hace» añade «Eliminado al introducir `POST /orders/:id/cancel` (RUT-20261106-post-orders-id-cancel)».

```
python3 $P/scripts/comun/fichas.py estado RUT-20260310-delete-orders-id retirada
```

**verificar.**

```
$ python3 $P/scripts/verificar-rutas.py
aviso: orders/RUT-20260310-delete-orders-id.md: archivo ancla inexistente src/modules/orders/application/delete-order.usecase.ts
rutas: 2 documentadas, 0 errores, 1 avisos
```

El aviso es de la ficha retirada (su caso de uso se borró): se menciona y no se corrige. `verificar.py` sin errores.

## Resultado

- Ficha nueva `activa` para `POST /orders/:id/cancel` con errores 401/403/404/409.
- Ficha de `DELETE /orders/:id` conservada como `retirada`, con el enlace a su sustituta.
