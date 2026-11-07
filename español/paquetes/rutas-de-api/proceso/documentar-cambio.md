---
fase: documentar-cambio
resuelve: [endpoints-sin-ficha, fichas-de-ruta-desfasadas, seguridad-de-endpoint-implicita, endpoints-retirados-sin-rastro]
skills: [documentar-endpoint, actualizar-ficha-de-ruta, retirar-endpoint]
---

# Fase: documentar-cambio

## Objetivo

Que la ficha refleje el endpoint tal como queda al terminar la tarea, en la misma tarea que cambia el código.

## Entradas

- El resultado de `consultar-ficha` (id de la ficha o su ausencia).
- El código del endpoint tal como queda tras el cambio.

## Pasos

1. Elige la skill según el cambio:
   - endpoint nuevo o sin ficha → `documentar-endpoint`;
   - cambia método, ruta, autenticación, roles, entrada, salida, errores o archivos → `actualizar-ficha-de-ruta`;
   - el endpoint se elimina o deja de recomendarse → `retirar-endpoint`.
2. Comprueba `auth` y `roles` contra el código (guardas, middlewares, decoradores). Si es público, la razón va en «Hace».
3. Revisa que cada archivo de «Archivos ancla» exista con esa ruta exacta.

## Criterio de salida

- La ficha tiene `method`, `path`, `auth`, `roles` y `module` acordes al código.
- «Entrada» y «Salida» describen lo que ve el cliente, con los errores relevantes.
- El status es el correcto: `activa`, `planificada`, `deprecada` o `retirada`.
