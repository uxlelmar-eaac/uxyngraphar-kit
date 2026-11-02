# Frontmatter — sesión de preguntas (`03-preguntas/`)

Ruta: `03-preguntas/<estado>/YYYY-MM-DD/<slug>.md`. Estados:
`01-en-curso` (`en-curso`) · `03-completadas` (`completada`) ·
`05-canceladas` (`cancelada`).

| Campo | Tipo | Obligatorio | Notas |
|-------|------|-------------|-------|
| `id` | string | sí | `PRE-YYYYMMDD-NNN-slug` |
| `status` | enum | sí | `en-curso` \| `completada` \| `cancelada` |
| `created` | datetime | sí | ISO UTC; define la carpeta de fecha |
| `pedido` | string | sí | Síntesis del pedido humano |
| `impacto_estimado` | enum | sí | `bajo` \| `medio` \| `alto` |
| `ronda_actual` | number | sí | 1…N mientras `en-curso` |
| `rondas_objetivo` | number[] | sí | Copia de `preguntas.rondas` (topes) al abrir |
| `presupuesto_max` | number | sí | Copia de `preguntas.presupuesto_max` al abrir |
| `preguntas_hechas` | number[] | sí | Conteos reales por ronda (auditoría de uso) |
| `instruccion_id` | string \| null | no | Id de la instrucción al completar; `null` si cancelada |

Cuerpo: rondas con bloques de decisión (contexto + opciones + elección) + síntesis. Canon de flujo: [`03-preguntas/_PROTOCOLO.md`](../../03-preguntas/_PROTOCOLO.md).
