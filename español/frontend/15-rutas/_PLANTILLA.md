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

1. manejador de ruta: `app/api/.../route.ts`
2. `api/` + `reception/` + `hooks/` según aplique

## Archivos ancla

- `src/app/api/…`
- `src/modules/…`
