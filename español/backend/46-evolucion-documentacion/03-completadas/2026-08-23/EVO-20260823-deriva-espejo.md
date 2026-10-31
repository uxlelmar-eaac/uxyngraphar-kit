---
id: EVO-20260823-deriva-espejo
status: done
source: human
tipo: proceso
impacto: ambos
prioridad: despues
detected_in: revision-humana
areas: []
propuesta_cambio:
  - scripts/verificar-espejo.py
  - 10-guias/ci-validacion-documentacion.md
proposed_at: 2026-08-23
instruction_derivada: solicitud-humana-20261015
---
# EVO-20260823 — Detección de deriva del espejo 50 vs código

## Qué falta hoy

El espejo 1:1 se actualiza "de palabra": nada verifica que un PR que toca `src/...` haya actualizado el `.md` correspondiente declarado en `espejo_actualizar`.

## Propuesta de cambio

Chequeo en CI (opt-in): compara el diff del PR contra los paths de `espejo_actualizar` de la instrucción del PR; si hay código tocado sin espejo declarado → WARN (fallo con `STRICT_ESPEJO=1`). Documentar en `ci-validacion-documentacion.md`.

## Decisión a tomar

<!-- decision-group: EVO-20260823-deriva-espejo -->
- [x] <!-- decision:aprobar --> **Aprobar** → instrucción derivada
- [ ] <!-- decision:posponer --> **Posponer**
- [ ] <!-- decision:rechazar --> **Rechazar** → `05-canceladas/`

### Notas del humano

- [2026-10-15T22:27:26Z] decisiones-pendientes sesión 20261015-222712: aprobar

<!-- revision-pendientes-nota: actualizar matriz-cobertura-proyectos.md fila relacionada con EVO EVO-20260823-deriva-espejo -->
