# Conventional Commits en este paquete

## Forma del asunto

```
tipo(ámbito)!: resumen
```

- `tipo`: uno de la tabla de abajo.
- `(ámbito)`: opcional; minúsculas, dígitos, `.`, `_`, `/`, `-`. El módulo o carpeta afectada (`orders`, `api/payments`).
- `!`: opcional; cambio incompatible. Explica la incompatibilidad en el cuerpo (`BREAKING CHANGE: …`).
- `resumen`: inglés, ASCII, imperativo («add», no «added» ni «adds»), sin punto final.
- Todo el asunto: 72 caracteres como máximo.

## Tipos

| Tipo | Cuándo | Ejemplo |
|------|--------|---------|
| `feat` | Una capacidad nueva para el usuario o para otro sistema | `feat(orders): add coupon discount to order total` |
| `fix` | Corrige un comportamiento erróneo | `fix(auth): reject expired refresh tokens` |
| `docs` | Solo documentación | `docs(api): describe pagination parameters` |
| `style` | Formato sin cambio de comportamiento (espacios, punto y coma) | `style: apply formatter to checkout module` |
| `refactor` | Cambia la estructura sin cambiar el comportamiento | `refactor(orders): split pricing out of order service` |
| `perf` | Mejora el rendimiento sin cambiar el comportamiento | `perf(search): cache category lookups` |
| `test` | Añade o corrige pruebas | `test(orders): cover coupon expiry` |
| `build` | Sistema de construcción o dependencias | `build: bump typescript to 5.6` |
| `ci` | Configuración de integración continua | `ci: run unit tests on pull requests` |
| `chore` | Mantenimiento que no encaja en los anteriores | `chore: remove unused env sample` |
| `revert` | Deshace un commit anterior | `revert: feat(orders): add coupon discount` |

## Cuerpo

Separado del asunto por una línea en blanco, en inglés, con líneas de 72 caracteres. Explica el porqué y las consecuencias; el qué ya lo dice el diff. Referencias a tickets al final (`Refs: ORD-142`).

## Ramas

`tipo/descripcion-corta`, en inglés ASCII y kebab-case, con los mismos tipos: `feat/checkout-coupons`, `fix/expired-refresh-tokens`.

## Errores frecuentes

| Asunto | Problema | Corregido |
|--------|----------|-----------|
| `añadir cupones al pedido` | Sin tipo y en español | `feat(orders): add coupons to order` |
| `Fix: login` | Tipo en mayúscula y resumen vago | `fix(auth): accept emails with plus sign` |
| `feat(Orders): added coupons.` | Ámbito en mayúscula, pasado y punto final | `feat(orders): add coupons` |
| `fix stuff and add coupons` | Sin tipo y dos intenciones | dos commits: `fix(...)` y `feat(...)` |
