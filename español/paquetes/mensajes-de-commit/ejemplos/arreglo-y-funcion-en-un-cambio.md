# Caso: un cambio con un arreglo y una función nueva

## Pedido

«Añade cupones de descuento al total del pedido; de paso, el redondeo de impuestos está mal. Deja los commits hechos en una rama.» El cambio ya está escrito y verificado; el repositorio usa ámbitos por módulo (`orders`, `auth`).

## Recorrido

**preparar-commit.**

1. Dos intenciones: el redondeo es un `fix` y los cupones un `feat`. `git add -p` separa el arreglo de impuestos de `order-service.pricing.ts`.
2. Rama nueva: `git switch -c feat/order-coupons`.
3. `redactar-commit` para el primero. Un primer borrador falla:

   ```
   python3 $P/scripts/commits.py --mensaje "arreglar redondeo de impuestos"
   mensaje: «arreglar redondeo de impuestos» no cumple Conventional Commits en inglés ASCII (≤72 caracteres)
   ```

   Corregido:

   ```
   python3 $P/scripts/commits.py --mensaje "fix(orders): round tax per line before summing"
   mensajes-de-commit: mensaje válido
   ```

   `git commit -m "fix(orders): round tax per line before summing"`.
4. Segundo commit: `feat(orders): add coupon discount to order total`, comprobado igual antes de hacerlo.
5. `revisar-commits` sobre los dos commits nuevos:

   ```
   python3 $P/scripts/commits.py 2
   mensajes-de-commit: 2 commits revisados, 0 problemas
   ```

Si la persona hubiera hecho antes un commit `WIP` en la rama ya publicada, `commits.py 3` lo listaría; no se reescribe: se menciona al cerrar.

## Resultado

- Rama `feat/order-coupons` con dos commits de una intención cada uno, en Conventional Commits.
- Ningún commit publicado ni ajeno reescrito.
