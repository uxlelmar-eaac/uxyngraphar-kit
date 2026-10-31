---
id: EVO-20260823-validador-python
status: done
source: human
tipo: herramienta-pack
impacto: ambos
prioridad: ahora
detected_in: revision-humana
areas: []
propuesta_cambio:
  - scripts/validar-documentacion.py
  - scripts/validar-documentacion.sh
proposed_at: 2026-08-23
instruction_derivada: solicitud-humana-20261015
---
# EVO-20260823 — Validador unificado en Python

## Qué falta hoy

`validar-documentacion.sh` parsea YAML con awk/heurísticas (listas en línea `[a, b]` no soportadas, frontmatter multilínea frágil) y requiere bash (limitante en Windows/CI sin Git Bash).

## Propuesta de cambio

`validar-documentacion.py` (stdlib, misma que usa `decisiones`): estructura de estados, enums contra convenciones, vínculos colgantes (`vinculos_entrada/salida`, `mejoras_propuestas` → archivos existentes), ids duplicados entre colas, secretos con allowlist centralizada, presupuestos. El `.sh` queda como wrapper delgado con las mismas variables `STRICT_*`.

## Decisión a tomar

<!-- decision-group: EVO-20260823-validador-python -->
- [x] <!-- decision:aprobar --> **Aprobar** → instrucción derivada
- [ ] <!-- decision:posponer --> **Posponer**
- [ ] <!-- decision:rechazar --> **Rechazar** → `05-canceladas/`

### Notas del humano

- [2026-10-15T22:27:26Z] decisiones-pendientes sesión 20261015-222712: aprobar

<!-- revision-pendientes-nota: actualizar matriz-cobertura-proyectos.md fila relacionada con EVO EVO-20260823-validador-python -->
