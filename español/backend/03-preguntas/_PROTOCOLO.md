# Protocolo — fase de preguntas

Clarificación adaptativa **antes** de redactar la instrucción. Canal: chat con el humano. Persistencia: ficha en esta sección. Destino del contenido: la **instrucción** (sección Clarificación), no un tipo nuevo de decisión.

## Estructura (R-17 reducido)

```
03-preguntas/
├── 01-en-curso/YYYY-MM-DD/<slug>.md     ← en-curso
├── 03-completadas/YYYY-MM-DD/<slug>.md  ← completada (tras crear instrucción)
└── 05-canceladas/YYYY-MM-DD/<slug>.md   ← cancelada
```

- Archivo: `<slug>.md` (kebab, 2–6 palabras); `id`: `PRE-YYYYMMDD-NNN-slug` (fecha UTC).
- Carpeta de fecha = fecha de **creación**; se conserva al mover.
- **Cambio de estado = mover** + actualizar `status` en el mismo acto.
- Sin `02` / `04` / `06`: la sesión no pasa por panel de pendientes.

## Cuándo aplica

1. Pedido nuevo que **no** cubre una herramienta autorizada (`35-herramientas/autorizadas/`).
2. `preguntas.activo` es `true` en `uxyngraphar.config.json` (por defecto sí).
3. El humano **no** pidió omitir («salta preguntas», «sin fase de preguntas»).

Excepciones sin fase ni instrucción: errata de una línea, solo lectura acotada, actualizar instrucción ya aprobada a petición explícita.

## Rondas

- Lista `preguntas.rondas` (por defecto `[10, 5, 3]`): ronda *i* tiene exactamente `rondas[i-1]` preguntas.
- Cada ronda se adapta a las respuestas anteriores (huecos de alcance, restricciones, criterios, riesgos, anclas, prioridades).
- No repetir preguntas ya respondidas.
- El humano puede cerrar anticipado («basta», «crea la instrucción»): se sintetiza con lo respondido.

## Frontmatter mínimo de la ficha

| Campo | Notas |
|-------|--------|
| `id` | `PRE-YYYYMMDD-NNN-slug` |
| `status` | `en-curso` \| `completada` \| `cancelada` |
| `created` | ISO UTC |
| `pedido` | Texto o síntesis del pedido humano |
| `ronda_actual` | Entero 1…N |
| `rondas_objetivo` | Copia de `preguntas.rondas` al abrir |
| `preguntas_por_ronda` | Igual que `rondas_objetivo` (auditoría) |
| `instruccion_id` | Al completar: id de la instrucción creada; si no, `null` |

Cuerpo: por cada ronda, lista pregunta → respuesta; al final, síntesis operativa (3–6 viñetas).

## Flujo

1. Crear ficha en `01-en-curso/YYYY-MM-DD/` con `status: en-curso`.
2. Preguntar en chat ronda a ronda; actualizar la ficha tras cada ronda (o al cerrar).
3. Al terminar (o cierre anticipado): crear instrucción `awaiting_approval` con § Clarificación rellena + `preguntas_id`; mover esta ficha a `03-completadas/` con `status: completada` e `instruccion_id`.
4. Si se abandona sin instrucción: `05-canceladas/` + `status: cancelada`.
5. Si la fase se omite: no crear ficha aquí; en la instrucción `preguntas_omitidas: true` y una línea en Clarificación.

## Límites

- No tocar código ni docs del producto durante la fase (R-03).
- No leer historial de otras sesiones de `03-preguntas/` (solo la ficha de la tarea).
- Tras crear la instrucción, el ejecutor usa solo la instrucción (el Q&A ya está embebido); no reabrir `03-preguntas/` salvo que `lectura_minima` lo cite.
