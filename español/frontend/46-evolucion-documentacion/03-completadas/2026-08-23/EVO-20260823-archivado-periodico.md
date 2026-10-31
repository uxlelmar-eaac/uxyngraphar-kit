---
id: EVO-20260823-archivado-periodico
status: done
source: human
tipo: proceso
impacto: ambos
prioridad: despues
detected_in: revision-humana
areas: []
propuesta_cambio:
  - scripts/decisiones/decisiones.py
proposed_at: 2026-08-23
instruction_derivada: solicitud-humana-20261015
---
# EVO-20260823 — Archivado periódico de secciones acumulativas

## Qué falta hoy

El archivo `03-completadas → 04-archivadas` y la limpieza de `05-canceladas`/`06-listas-para-eliminar` son manuales y trimestrales. Las carpetas crecen mientras tanto.

## Propuesta de cambio

Acción `archivar`/`limpiar` en la CLI `decisiones.py` (o en `metricas`): mueve `done`/`cerrada`/`aceptada` con más de N días a `04-archivadas/` (conservando carpeta de fecha), lista candidatos en `06-listas-para-eliminar` y sugiere borrado tras confirmación humana. Dry-run por defecto.

## Decisión a tomar

<!-- decision-group: EVO-20260823-archivado-periodico -->
- [x] <!-- decision:aprobar --> **Aprobar** → instrucción derivada
- [ ] <!-- decision:posponer --> **Posponer**
- [ ] <!-- decision:rechazar --> **Rechazar** → `05-canceladas/`

### Notas del humano

- [2026-10-15T22:27:26Z] decisiones-pendientes sesión 20261015-222712: aprobar

<!-- revision-pendientes-nota: actualizar matriz-cobertura-proyectos.md fila relacionada con EVO EVO-20260823-archivado-periodico -->
