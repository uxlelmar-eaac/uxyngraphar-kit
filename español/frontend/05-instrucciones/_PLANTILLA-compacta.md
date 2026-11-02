---
id: YYYYMMDD-NNN
status: awaiting_approval
source: human
created: YYYY-MM-DDTHH:MM:SSZ
approved_at: null
executed_at: null
areas: []
acto: crear
lectura_minima: []
anclas_codigo: []
espejo_actualizar: []
vinculos_salida: []
preguntas_id: null
preguntas_omitidas: false
---

# YYYYMMDD-NNN — Título corto

> **Contrato IA:** hasta **Decisión a tomar**. Compacta. Opcionales: [instruccion.md](../00-nucleo/frontmatter/instruccion.md).

## Clarificación (decisiones)
Impacto; por cada decisión: opción elegida + efecto; síntesis 3–6 viñetas. O `Omitida (config|pedido)`. [fase-preguntas.md](../10-guias/fase-preguntas.md).

## Objetivo
Una frase: qué quedará verdadero al terminar.

## Alcance
- Incluye / excluye: …
- Código: N (≤5). ¿Más? No → fracciona (`fraccion_de`); sí → `ampliacion_factor` 1.5–2 + justificación ([R-21](../00-nucleo/ampliacion-alcance.md)).

## Plan
1. … 2. Código según `anclas_codigo`. 3. `espejo_actualizar` + `decisiones.py cerrar`.

## Criterios de aceptación
- [ ] Código/pruebas en inglés ASCII; i18n; nombres claros ([R-22](../00-nucleo/politica-idioma.md), [R-23](../00-nucleo/nombres-autoexplicativos.md))
- [ ] Espejo y `96-reglas-proyecto/` OK; excepciones en `excepciones_reglas`

## Decisión a tomar
<!-- decision-group: YYYYMMDD-NNN -->
- [ ] <!-- decision:aprobar --> **Aprobar** → `approved` + `02-en-progreso/`
- [ ] <!-- decision:cancelar --> **Cancelar** → `cancelled` + `05-canceladas/`

## Costo en tokens
<!-- tokens:inicio -->
Al cerrar (`decisiones.py cerrar`); fases con `costo-tokens.py fase <id> <fase>`.
<!-- tokens:fin -->
