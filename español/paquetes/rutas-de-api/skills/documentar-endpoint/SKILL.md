---
name: documentar-endpoint
description: Crea la ficha RUT de un endpoint HTTP nuevo o sin documentar, con su contrato visto desde el cliente, su seguridad y sus archivos ancla.
resuelve: [endpoints-sin-ficha, seguridad-de-endpoint-implicita]
---

# Documentar endpoint

## Cuándo usarla

- Se crea un endpoint nuevo (también si aún no está implementado: status `planificada`).
- Se toca un endpoint existente que no tiene ficha.

## Pasos

1. Elige el slug a partir del método y la ruta, sin barras ni llaves: `GET /orders/:id` → `get-orders-id`.
2. Crea la ficha en la carpeta del módulo:
   `python3 $P/scripts/comun/fichas.py nueva ruta --slug get-orders-id --en orders --titulo "GET /orders/:id"`
3. Abre el archivo que imprime y rellena el frontmatter: `method`, `path` (con la sintaxis de parámetros del framework), `auth`, `roles`, `module`.
4. Rellena las secciones leyendo el código, no imaginándolo:
   - «Hace»: una o dos frases; si `auth: public`, por qué.
   - «Entrada»: cabeceras, parámetros, query y cuerpo con sus validaciones.
   - «Salida»: el código de éxito con la forma de la respuesta y los errores que el cliente debe tratar (400, 401, 403, 404, 409…).
   - «Pipeline»: controlador → caso de uso → dominio o infraestructura, con rutas reales.
   - «Archivos ancla»: un archivo por línea, entre comillas invertidas, con ruta desde la raíz de la app.
5. Si el endpoint aún no existe en el código, pon el status a `planificada`: `python3 $P/scripts/comun/fichas.py estado <id> planificada`.

## Resultado

- Una ficha `RUT-<fecha>-<slug>.md` en `uxyngraphar/trabajo/rutas-de-api/<modulo>/` con los campos obligatorios y anclas existentes.
