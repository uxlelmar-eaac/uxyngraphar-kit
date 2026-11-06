---
id: {{id}}
status: {{status}}
source: human
created: {{fecha}}
approved_at: null
executed_at: null
preguntas_id: null
ampliacion_factor: null
ampliacion_justificacion: null
fraccion_de: null
depende_de: []
lectura_minima: []
anclas_codigo: []
---

# {{titulo}}

## Clarificación
Decisiones tomadas con la persona (opción elegida + efecto), o «Omitida (motivo)».

## Objetivo
Una frase: qué quedará verdadero al terminar.

## Alcance
- Incluye: …
- Excluye: …
- Archivos de código: N (máximo 5; si son más, fracciona o justifica la ampliación).

## Plan
1. …

## Criterios de aceptación
- [ ] …

## Fuera de alcance
- (deuda o bugs detectados que no se implementan aquí)

## Decisión (persona)
- Aprobar: `python3 uxyngraphar/paquetes/instrucciones-aprobadas/scripts/ciclo.py aprobar {{id}} --humano`
- Cancelar: `python3 uxyngraphar/paquetes/instrucciones-aprobadas/scripts/comun/fichas.py estado {{id}} cancelled`
