---
name: actualizar-ficha-de-ruta
description: Ajusta la ficha RUT de un endpoint que cambia de método, ruta, autenticación, roles, entrada, salida, errores o archivos, en la misma tarea que el código.
resuelve: [fichas-de-ruta-desfasadas, seguridad-de-endpoint-implicita]
---

# Actualizar ficha de ruta

## Cuándo usarla

- El cambio toca el contrato de un endpoint que ya tiene ficha.
- Se mueve o renombra un archivo citado en «Archivos ancla» o en «Pipeline».

## Pasos

1. Abre la ficha: `python3 $P/scripts/comun/fichas.py ver <id>` y edita el archivo en `uxyngraphar/trabajo/rutas-de-api/<modulo>/`.
2. Si cambia el método o la ruta, actualiza `method`/`path` y el título. Si el cambio es incompatible para los clientes (otra ruta, campo obligatorio nuevo), conserva la ficha antigua con la skill `retirar-endpoint` y documenta la nueva con `documentar-endpoint`.
3. Si cambian guardas o middlewares, actualiza `auth` y `roles`.
4. Ajusta «Entrada», «Salida» y los errores: solo lo que ve el cliente, no detalles internos.
5. Actualiza «Pipeline» y «Archivos ancla» con las rutas nuevas.
6. Actualiza `fecha` con la de hoy.

## Resultado

- La ficha describe el endpoint tal como queda tras el cambio y sus anclas existen.
