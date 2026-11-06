---
id: {{id}}
status: {{status}}
method: GET
path: /ejemplo
auth: bearer
roles: []
module: ejemplo
fecha: {{fecha}}
---

# {{titulo}}

## Hace
…

## Entrada
- Cabeceras: …
- Parámetros / query: …
- Cuerpo: …

## Salida
- 200: …
- Errores relevantes: 400 …, 401 …, 404 …

## Conectado con
- Caso de uso: …
- Integraciones / externos: …
- Modelos de datos: …

## Pipeline
1. Entrada: `…controller.ts`
2. Aplicación: `…use-case.ts`
3. Dominio / infraestructura: …

## Archivos ancla
- `src/modules/…`
