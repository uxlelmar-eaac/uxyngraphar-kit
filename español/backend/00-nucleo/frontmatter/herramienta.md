# Frontmatter — herramienta (`35-herramientas/`)

| Campo | Tipo | Obligatorio | Notas |
|-------|------|-------------|-------|
| `id` | string | sí | slug corto |
| `status` | enum | sí | Autorizada: `authorized`. Propuesta: `pending` \| `en-evaluacion` \| `rejected` \| `archivada` \| `para-eliminar` |
| `alcance_permitido` | string | sí (autorizada) | Cuándo ejecutar sin instrucción |
| `anclas_codigo` | string[] | no | Código que puede tocar |
| `lectura_minima` | string[] | no | Docs adicionales al ejecutar |

Propuestas en `35-herramientas/propuestas/<estado>/YYYY-MM-DD/`; al
promover, la ficha pasa a `autorizadas/` (registro, sin estados).
