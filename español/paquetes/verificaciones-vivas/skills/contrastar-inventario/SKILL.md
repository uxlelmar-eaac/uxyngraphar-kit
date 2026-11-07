---
name: contrastar-inventario
description: Compara las rutas de API y las páginas del código con sus fichas y lista las que faltan en un lado o en el otro.
resuelve: [fichas-desalineadas-del-codigo]
---

# Contrastar inventario

## Cuándo usarla

- La persona pregunta si las fichas de rutas o páginas están al día.
- Tras añadir, mover o borrar controladores o páginas.

## Pasos

1. Ejecuta `python3 $P/scripts/vivas.py rutas paginas`.
2. `rutas` detecta `@Controller` + `@Get/@Post/…` (Nest), `app|router|server|fastify.get(…)` (Express, Fastify) y `@<x>.get(…)` (FastAPI, Flask), y compara método + ruta normalizada con `method` + `path` de las fichas `ruta` de `rutas-de-api`.
3. `paginas` toma las carpetas con `page.*` bajo `app/` (sin grupos `(…)`, rutas paralelas `@…` ni privadas `_…`) y las compara con `path` de las fichas `pagina` de `paginas-de-interfaz`.
4. Lee los hallazgos:
   - `alta: ficha activa sin ruta en el código: DELETE /orders/{}` → la ficha describe algo que ya no existe.
   - `media: ruta sin ficha: POST /orders — src/orders/orders.controller.ts:5` → falta documentar.
   - `info: … no está instalado` o `no se detectaron rutas…` → no cuenta.
5. Si casi todas las rutas salen «sin ficha», comprueba `prefijo_global` antes de informar.

## Resultado

- Las rutas y páginas sin ficha y las fichas activas sin código, con su evidencia.
