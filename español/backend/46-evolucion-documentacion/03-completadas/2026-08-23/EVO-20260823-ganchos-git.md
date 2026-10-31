---
id: EVO-20260823-ganchos-git
status: done
source: human
tipo: proceso
impacto: ambos
prioridad: despues
detected_in: revision-humana
areas: []
propuesta_cambio:
  - scripts/instalar-ganchos.py
  - 10-guias/ci-validacion-documentacion.md
proposed_at: 2026-08-23
instruction_derivada: solicitud-humana-20261015
---
# EVO-20260823 — Ganchos git para el ciclo vinculante

## Qué falta hoy

El ciclo vinculante (R-03, R-15) depende de que la IA cumpla las reglas; no hay enforcement mecánico. Un PR puede llegar sin instrucción `approved` ni `espejo_actualizar` y solo lo detecta la revisión humana.

## Propuesta de cambio

Hook `pre-commit`/`pre-push` (opcional, opt-in en adopción) que: avise si el diff toca código sin instrucción `approved` en el PR; avise si instrucción `done` sin `vinculos_salida`/`espejo_actualizar`; y doc en `ci-validacion-documentacion.md` para GitHub Actions (revisa diff del PR vs `espejo_actualizar` declarado).

## Decisión a tomar

<!-- decision-group: EVO-20260823-ganchos-git -->
- [x] <!-- decision:aprobar --> **Aprobar** → instrucción derivada
- [ ] <!-- decision:posponer --> **Posponer**
- [ ] <!-- decision:rechazar --> **Rechazar** → `05-canceladas/`

### Notas del humano

- [2026-10-15T22:27:26Z] decisiones-pendientes sesión 20261015-222712: aprobar

<!-- revision-pendientes-nota: actualizar matriz-cobertura-proyectos.md fila relacionada con EVO EVO-20260823-ganchos-git -->
