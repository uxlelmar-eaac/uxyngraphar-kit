# Protocolo — fase de preguntas

Clarificación **proporcional** y con **formato de decisión** **antes** de redactar la instrucción. Canal: chat con el humano. Persistencia: ficha en esta sección. Destino del contenido: la **instrucción** (§ Clarificación = síntesis de decisiones), no un tipo nuevo de decisión.

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

## Presupuesto e impacto (no cuota fija)

Config `preguntas` (por defecto):

```json
"preguntas": {"activo": true, "rondas": [6, 4, 2], "presupuesto_max": 12}
```

- `rondas` — **tope máximo** de preguntas por ronda (no hay que rellenar el cupo).
- `presupuesto_max` — techo de la sesión completa.
- Al abrir la ficha, el agente estima `impacto_estimado` y elige un presupuesto efectivo ≤ `presupuesto_max`:

| Impacto | Preguntas sugeridas | Rondas típicas |
|---------|---------------------|----------------|
| `bajo`  | 1–3                 | 1              |
| `medio` | 3–6                 | 1–2            |
| `alto`  | 6–12                | 2–3            |

- Impacto bajo **acorta**; no omite la fase (salvo config o «salta preguntas»).
- Cierre anticipado: «basta», «crea la instrucción», o cuando hay **suficiencia** (alcance, restricciones, criterio de hecho y riesgos abiertos resueltos o asumidos).
- No repetir decisiones ya tomadas.

## Capas de decisión (orden)

Preguntar solo las capas que falten, en este orden:

1. **Alcance** — qué entra / qué queda fuera.
2. **Enfoque** — camino técnico o de UX.
3. **Restricciones** — compatibilidad, no romper X, tiempo.
4. **Criterio de hecho** — cómo se verifica.
5. **Riesgos / borde** — solo si el impacto lo pide.

## Formato obligatorio de cada pregunta

Una pregunta = **una decisión**. 2 opciones si el espacio es binario; 3 si hay caminos reales. Nunca rellenar con puntos sueltos sin contexto.

```markdown
### P1. [Decisión en una línea]

**Contexto:** por qué esto importa ahora (pedido + restricción del repo / área).
**Qué desbloquea:** qué parte de la instrucción queda clara al responder.

| Opción | Consideraciones | Efecto en código/docs |
|--------|-----------------|------------------------|
| A — … | pros/contras cortos | archivos/áreas/acto probable |
| B — … | … | … |
| C — … | … | … |   <!-- omitir C si binario -->

**Recomendación:** A — porque …
**Tu elección:** _
```

Reglas: opciones excluyentes y reales; el efecto nombra tipo de cambio (qué tocaría), no el plan completo.

## Frontmatter mínimo de la ficha

| Campo | Notas |
|-------|--------|
| `id` | `PRE-YYYYMMDD-NNN-slug` |
| `status` | `en-curso` \| `completada` \| `cancelada` |
| `created` | ISO UTC |
| `pedido` | Texto o síntesis del pedido humano |
| `impacto_estimado` | `bajo` \| `medio` \| `alto` |
| `ronda_actual` | Entero 1…N |
| `rondas_objetivo` | Copia de `preguntas.rondas` (topes) al abrir |
| `presupuesto_max` | Copia de `preguntas.presupuesto_max` al abrir |
| `preguntas_hechas` | Conteos reales por ronda (p. ej. `[3, 1]`) |
| `instruccion_id` | Al completar: id de la instrucción; si no, `null` |

Cuerpo: por cada ronda, bloques de decisión con elección; al final, síntesis operativa (3–6 viñetas) lista para volcar a Clarificación.

## Flujo

1. Crear ficha en `01-en-curso/YYYY-MM-DD/` con `status: en-curso`, impacto y topes.
2. Declarar en chat: impacto estimado + nº de preguntas de esta ronda + por qué.
3. Preguntar en el formato de decisión; actualizar la ficha tras cada ronda (o al cerrar); llevar `preguntas_hechas`.
4. Al terminar (o cierre anticipado): crear instrucción `awaiting_approval` con § Clarificación = **decisiones** (opción elegida + efecto) + síntesis; `preguntas_id`; mover esta ficha a `03-completadas/` con `status: completada` e `instruccion_id`.
5. Si se abandona sin instrucción: `05-canceladas/` + `status: cancelada`.
6. Si la fase se omite: no crear ficha aquí; en la instrucción `preguntas_omitidas: true` y una línea en Clarificación.

## Límites

- No tocar código ni docs del producto durante la fase (R-03).
- No leer historial de otras sesiones de `03-preguntas/` (solo la ficha de la tarea).
- Tras crear la instrucción, el ejecutor usa solo la instrucción (las decisiones ya están embebidas); no reabrir `03-preguntas/` salvo que `lectura_minima` lo cite.
