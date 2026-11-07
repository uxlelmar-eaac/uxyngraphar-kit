---
name: redactar-commit
description: Redacta un mensaje de commit en Conventional Commits, en inglés ASCII, en imperativo y de 72 caracteres como máximo, y lo comprueba con commits.py --mensaje antes de hacer el commit.
resuelve: [commits-sin-convencion]
---

# Redactar commit

## Cuándo usarla

- En la fase `preparar-commit`, para cada commit del cambio.
- Cuando `commits.py` informa de un commit tuyo que aún no se publicó.

## Pasos

1. Elige un tipo (tabla de `referencia/commits.md`): `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore` o `revert`. Si necesitas dos, son dos commits.
2. Ámbito opcional en minúsculas (letras, dígitos, `.`, `_`, `/`, `-`): el módulo o carpeta afectada (`feat(orders): …`). `!` tras el ámbito marca un cambio incompatible.
3. Resumen en inglés, en imperativo y sin punto final: `add coupon discount to order total`, no `added coupons` ni `añadir cupones`.
4. Comprueba el asunto antes del commit: `python3 $P/scripts/commits.py --mensaje "feat(orders): add coupon discount to order total"` debe responder `mensajes-de-commit: mensaje válido` (todo ASCII y 72 caracteres como máximo en total).
5. Detalle opcional en el cuerpo, separado por una línea en blanco, también en inglés: el porqué del cambio, no el qué.
6. Tras el commit: `python3 $P/scripts/commits.py 1` no debe listarlo.

## Resultado

- Una línea de asunto válida, por ejemplo `feat(orders): add coupon discount to order total`.
