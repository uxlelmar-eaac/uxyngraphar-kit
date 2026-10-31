---
id: modulo.accion.nombre
method: POST
path: /ejemplo
auth: bearer | public | cookie
roles: []
module: ejemplo
status: activa
---

# METHOD /path — Título corto

## Hace

…

## Entrada

- Cabeceras: …
- Cuerpo / query: …

## Salida

- 200: …
- Errores relevantes: …

## Conectado con

- Caso de uso: …
- Integraciones: …
- Externos: …
- Modelos BD: …

## Pipeline

1. capa de entrada: `…controller.ts`
2. aplicación: `…use-case.ts` / servicio
3. dominio / infraestructura / integraciones: …

## Archivos ancla

- `src/modules/…`
