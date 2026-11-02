# Fase de preguntas (antes de la instrucción)

Antes de redactar el contrato en `05-instrucciones/`, el agente aclara el pedido con **decisiones** en el **chat** (contexto + opciones + efecto). Las respuestas se guardan en `03-preguntas/` y se **vuelcan** a la instrucción (§ Clarificación) como síntesis de decisiones, no como transcript crudo.

## Por defecto

En `uxyngraphar.config.json`:

```json
"preguntas": {"activo": true, "rondas": [6, 4, 2], "presupuesto_max": 12}
```

- `activo: false` — el agente crea la instrucción sin ronda previa.
- `rondas` — **tope** de preguntas por ronda (máx. 10 rondas, máx. 20 por ronda); no es cuota obligatoria.
- `presupuesto_max` — techo de la sesión (1–40; por defecto 12).
- En el pedido: «salta preguntas» / «sin fase de preguntas» omite la fase aunque `activo` sea true.

### Proporcional al impacto

| Impacto del pedido | Preguntas sugeridas |
|--------------------|---------------------|
| Bajo (ajuste local, copy) | 1–3 |
| Medio (feature acotada) | 3–6 |
| Alto / transversal | 6–12 |

El agente declara al inicio el impacto estimado y cuántas preguntas usará. Puede cerrar antes si ya hay suficiencia, o si dices «basta, crea la instrucción».

Detalle de config: [configuracion-uxyngraphar.md](configuracion-uxyngraphar.md). Protocolo de fichas: [`03-preguntas/_PROTOCOLO.md`](../03-preguntas/_PROTOCOLO.md).

## Formato de cada pregunta (ejemplo)

```markdown
### P1. ¿Dónde vive el nuevo endpoint?

**Contexto:** el pedido pide listar proyectos; hoy la API está bajo `/api/v1` y el espejo documenta rutas en `15-rutas/`.
**Qué desbloquea:** alcance de archivos y si hace falta actualizar espejo.

| Opción | Consideraciones | Efecto en código/docs |
|--------|-----------------|------------------------|
| A — `/api/v1/projects` | Consistente con el resto; más boilerplate | Nuevo handler + ficha en `15-rutas/` |
| B — extender `/api/v1/orgs/:id/...` | Menos rutas nuevas; acopla a org | Menos archivos; cambia contrato existente |

**Recomendación:** A — porque …
**Tu elección:** _
```

## Qué hace el agente

1. Comprueba herramienta autorizada → si cubre el pedido, no hay fase ni instrucción nueva.
2. Si aplica la fase → crea ficha en `03-preguntas/01-en-curso/`, estima impacto, pregunta por rondas (hasta el tope, sin rellenar), actualiza la ficha.
3. Al cerrar → crea instrucción `awaiting_approval` con Clarificación = decisiones + síntesis, `preguntas_id`, y mueve la sesión a `03-completadas/`.
4. Espera aprobación humana (panel Pendientes). Sin `approved` no codea (R-03).

## Humano

- Responde en el chat (no hace falta el panel para cada ronda).
- Puedes acortar: «basta, crea la instrucción».
- Apruebas la instrucción resultante como siempre: panel → Proyecto → Pendientes.
