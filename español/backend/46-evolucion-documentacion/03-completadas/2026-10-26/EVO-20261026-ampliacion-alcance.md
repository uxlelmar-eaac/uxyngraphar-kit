---
id: EVO-20261026-ampliacion-alcance
status: done
source: human
tipo: proceso
impacto: general
prioridad: ahora
detected_in: revision-humana
areas: []
propuesta_cambio:
  - PROTOCOLO.md
  - REGLAS.md
  - AGENTES.md
  - 00-nucleo/ampliacion-alcance.md
  - 00-nucleo/agentes-detalle.md
  - 00-nucleo/eficiencia-ia.md
  - 00-nucleo/frontmatter/instruccion.md
  - 05-instrucciones/_PLANTILLA.md
  - 05-instrucciones/_PLANTILLA-compacta.md
  - scripts/decisiones/alcance.py
proposed_at: 2026-10-26
instruction_derivada: solicitud-humana-20261026-alcance
---
# EVO-20261026 — Ampliación del alcance de archivos de código (R-21)

> Meta-sistema documental (R-18). Aprobada y aplicada por decisión humana explícita en la versión **1.0.0** (completada el 2026-10-28 en el pack cliente y con `alcance.py`).

## Qué faltaba

Los agentes pedían con frecuencia ampliar el alcance de código (p. ej. de 5 a 7 archivos para cubrir dos módulos nuevos) sin un criterio común: a veces se aprobaba por comodidad lo que podía entregarse en partes, y nada impedía tocar más archivos de los declarados.

## Cambio aplicado

Regla **R-21**, con dos frentes obligatorios tras evaluar si la ampliación es *sumamente necesaria* (¿hay un subconjunto de ≤5 archivos entregable solo, compilando y sin contratos rotos?):

1. **Necesidad crítica** → `ampliacion_factor` 1.5–2 (tope `floor(5 × factor)`: 7–10), `ampliacion_justificacion` y **aprobación humana explícita antes de proceder** (`ampliacion_aprobada_at`).
2. **Sin necesidad crítica** → fraccionar en instrucciones de ≤5 archivos (`fraccion_de`, `depende_de`), cada una entregable sola, sin exceder el estándar.

La justificación se escribe siempre en `## Alcance`. Guía: `00-nucleo/ampliacion-alcance.md`.

Tooling (fuente única `scripts/decisiones/alcance.py`): `decisiones.py apply` rechaza aprobar alcances inválidos y registra la aprobación de la ampliación; el escaneo marca con `+` las que la piden; `contexto.py` / `presupuesto.py` bloquean sin aprobación; el validador da error en colas activas; `controlar.py` avisa o bloquea si el cambio supera el tope; `decisiones.py cerrar` no cierra sin aprobación registrada.

## Verificación

`test_alcance.py` (rango del factor, tope, justificación, fracciones, aprobación) y pruebas R-21 en `test_validar.py` y `test_espejo.py`; suite completa en verde en ambos packs.
