---
id: EVO-20261102-fase-preguntas
status: done
source: human
tipo: proceso
impacto: general
prioridad: ahora
detected_in: revision-humana
areas: []
propuesta_cambio:
  - 03-preguntas/
  - AGENTES.md
  - PROTOCOLO.md
  - 05-instrucciones/_PLANTILLA.md
  - 05-instrucciones/_PROTOCOLO.md
  - 00-nucleo/frontmatter/instruccion.md
  - 00-nucleo/frontmatter/preguntas.md
  - 10-guias/fase-preguntas.md
  - 10-guias/organizacion-estados-fechas.md
  - 10-guias/configuracion-uxyngraphar.md
  - scripts/control/uxyngraphar_config.py
  - scripts/nucleo/clasificacion.py
  - scripts/validacion/validar_estructura.py
  - scripts/memoria/almacen.py
proposed_at: 2026-11-02
instruction_derivada: solicitud-humana-20261102-fase-preguntas
---
# EVO-20261102 — Fase de preguntas antes de la instrucción

> Meta-sistema documental (R-18). Aprobada por decisión humana explícita (Uxleleaac, 2026-11-02): incorporar al flujo general una carpeta de preguntas con rondas adaptativas (por defecto 3 rondas: 10 / 5 / 3) en chat, configurables, y volcar preguntas/respuestas en la instrucción final sin plantilla nueva de tipo decisión.

## Qué faltaba

El pedido humano pasaba directo a instrucción `awaiting_approval`. No había fase documentada de clarificación ni lugar para persistir Q&A antes del contrato; la calidad del plan dependía solo del chat efímero.

## Decisión

- Nueva sección `03-preguntas/` (estados reducidos: `01-en-curso`, `03-completadas`, `05-canceladas`) con `_PROTOCOLO.md`; el agente escribe la ficha en chat, sin `decisiones.py new` ni panel por ronda.
- Config `preguntas: { activo: true, rondas: [10, 5, 3] }` (omisión por config o pedido «salta preguntas»).
- Adaptar `_PLANTILLA.md` de instrucción: sección **Clarificación (preguntas y respuestas)** + campos `preguntas_id` / `preguntas_omitidas`.
- Mandato en `AGENTES.md`: fase de preguntas **antes** de `new instruccion` cuando aplica; R-03 intacto (no codear sin instrucción aprobada).
- Taxonomía, validador, clasificación, memoria, paridad y docs humanas/IA alineados. Versión **1.2.3**.
