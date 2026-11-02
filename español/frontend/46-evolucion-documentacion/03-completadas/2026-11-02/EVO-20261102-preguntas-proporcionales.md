---
id: EVO-20261102-preguntas-proporcionales
status: done
source: human
tipo: proceso
impacto: general
prioridad: ahora
detected_in: revision-humana
areas: []
propuesta_cambio:
  - 03-preguntas/_PROTOCOLO.md
  - 00-nucleo/frontmatter/preguntas.md
  - 10-guias/fase-preguntas.md
  - 10-guias/configuracion-uxyngraphar.md
  - 05-instrucciones/_PLANTILLA.md
  - 05-instrucciones/_PROTOCOLO.md
  - AGENTES.md
  - scripts/control/uxyngraphar_config.py
  - instalador (panel / api / sistema)
proposed_at: 2026-11-02
instruction_derivada: solicitud-humana-20261102-preguntas-proporcionales
---
# EVO-20261102 — Preguntas proporcionales + formato de decisión

> Meta-sistema documental (R-18). Aprobada por decisión humana explícita (Uxleleaac, 2026-11-02): reformar la fase de preguntas para que no exija cuota fija 10/5/3, use topes y presupuesto según impacto, e imponga preguntas de decisión (contexto + opciones + efecto en código) con Clarificación = síntesis de decisiones.

## Qué faltaba

La fase 1.2.3 exigía exactamente N preguntas por ronda y no fijaba formato: el agente rellenaba cupo con puntos sueltos sin contexto, poco útiles para decidir. Pedidos de bajo impacto pagaban el mismo ritual.

## Decisión

- `preguntas.rondas` = **tope** por ronda (default `[6, 4, 2]`); nuevo `presupuesto_max` (default `12`).
- Impacto `bajo` | `medio` | `alto` → presupuesto efectivo 1–3 / 3–6 / 6–12; bajo acorta, no omite.
- Formato obligatorio: contexto + 2–3 opciones con consideraciones y efecto + recomendación + elección.
- Frontmatter: `impacto_estimado`, `presupuesto_max`, `preguntas_hechas` (reemplaza la copia redundante `preguntas_por_ronda`).
- § Clarificación de la instrucción = decisiones tomadas; detalle en `03-preguntas/`.
- Proyectos con `rondas: [10,5,3]` siguen válidos (tope alto). Sin migración de fichas antiguas. Versión **1.2.4**.
