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
---

# YYYYMMDD-NNN — Título corto

> **Contrato IA:** frontmatter + secciones hasta **Decisión a tomar**; no leer más. Plantilla **compacta** (bajo costo de tokens). Añade al frontmatter solo los campos que necesites (`vinculos_entrada`, `excepciones_reglas`, `espejo_leer`, `mejoras_propuestas`, `evolucion_documentacion`, `presupuesto_max_docs`…); ver [instruccion.md](../00-nucleo/frontmatter/instruccion.md).

## Objetivo

Una frase: qué quedará verdadero al terminar.

## Alcance

- Incluye: …
- Excluye: …
- Archivos de código: N (≤5). ¿Más? Justifica aquí si es sumamente necesario: no → fracciona (`fraccion_de`, `depende_de`); sí → `ampliacion_factor` 1.5–2 + `ampliacion_justificacion` y espera aprobación ([R-21](../00-nucleo/ampliacion-alcance.md)).

## Plan

1. …
2. Implementar según `anclas_codigo` (con rango `ruta:inicio-fin`).
3. Escribir `espejo_actualizar` y cerrar con `decisiones.py cerrar`.

## Criterios de aceptación

- [ ] Código y pruebas según alcance, en inglés y ASCII; términos locales en el glosario; texto para el usuario en i18n ([R-22](../00-nucleo/politica-idioma.md)); nombres que se entienden sin comentario ([R-23](../00-nucleo/nombres-autoexplicativos.md))
- [ ] Espejo alineado (`espejo_actualizar`) y reglas del proyecto revisadas (`96-reglas-proyecto/INDICE.md`; excepción solo en `excepciones_reglas`, «RP-NNN: motivo»)

## Decisión a tomar

<!-- decision-group: YYYYMMDD-NNN -->
- [ ] <!-- decision:aprobar --> **Aprobar** — cambiar a `status: approved`, fijar `approved_at` y mover a `02-en-progreso/`
- [ ] <!-- decision:cancelar --> **Cancelar** — cambiar a `status: cancelled` y mover a `05-canceladas/`

## Costo en tokens
<!-- tokens:inicio -->
Se mide al cerrar (`decisiones.py cerrar`). Marca `verificacion` y `cierre` con `costo-tokens.py fase <id> <fase>`.
<!-- tokens:fin -->
