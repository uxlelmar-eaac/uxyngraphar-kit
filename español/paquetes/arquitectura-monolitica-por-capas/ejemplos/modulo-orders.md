# Caso: módulo de pedidos que cobra a través de pagos

## Pedido

«Crea el módulo de pedidos (`orders`) en el servidor. Al confirmar un pedido hay que cobrarlo con el módulo de pagos que ya existe.» Perfil `servidor`, `nivel: aviso`.

## Recorrido

**diagnosticar.** `capas.py mapa` muestra `payments: application, domain, infrastructure, integrations` y ningún `orders`. `capas.py revisar src/modules/payments` da 0 infracciones: punto de partida limpio.

**disenar-modulo.** Nombre `orders`. Necesidad de otro módulo: cobrar un importe → método `chargeOrder(orderId, amount)` en `orders/integrations/payments.integration.ts`.

**crear-modulo** (skill):

```
python3 $P/scripts/comun/andamiar.py modulo-servidor --nombre orders
python3 $P/scripts/comun/andamiar.py modulo-servidor --nombre orders --aplicar
```

Crea `domain/orders.entity.ts`, `contracts/orders.dto.ts`, `infrastructure/orders.repository.ts`, `application/orders.usecase.ts` y `presentation/orders.controller.ts`, ya con imports permitidos. El framework pide `orders.module.ts` en la raíz del módulo; se añade a mano.

**implementar.** El caso de uso `confirm-order` necesita cobrar. Primer intento:

```ts
// application/confirm-order.usecase.ts
import { ChargeService } from '../../payments/application/charge.service';
```

`capas.py revisar src/modules/orders` responde:

```
src/modules/orders/application/confirm-order.usecase.ts:1: cruce de módulo orders → payments fuera de «integrations/» (importa src/modules/payments/application/charge.service.ts)
```

**corregir-dependencia-de-capa** (skill): caso «cruce de módulo». Se crea la integración y el caso de uso la usa:

```ts
// integrations/payments.integration.ts
import { ChargeService } from '../../payments/application/charge.service';
export class PaymentsIntegration {
  constructor(private readonly charges: ChargeService) {}
  chargeOrder(orderId: string, amount: number) { return this.charges.charge({ reference: orderId, amount }); }
}

// application/confirm-order.usecase.ts
import { PaymentsIntegration } from '../integrations/payments.integration';
```

**verificar.** `capas.py revisar src/modules/orders` → `capas: 0 imports fuera de las reglas`. `verificar.py` y `verificar-capas.py` sin errores.

## Resultado

- `src/modules/orders/` con cinco capas y una integración hacia `payments`.
- Ningún import nuevo fuera del perfil; ninguna desviación necesaria.
- Si están instalados: área `orders` en `mapa-de-modulos` y sus endpoints en `rutas-de-api`.
