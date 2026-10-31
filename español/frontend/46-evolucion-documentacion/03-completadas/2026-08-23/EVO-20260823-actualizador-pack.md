---
id: EVO-20260823-actualizador-pack
status: done
source: human
tipo: proceso
impacto: ambos
prioridad: despues
detected_in: revision-humana
areas: []
propuesta_cambio:
  - scripts/actualizar-pack.py
proposed_at: 2026-08-23
instruction_derivada: solicitud-humana-20261015
---
# EVO-20260823 — Actualización de packs adoptados desde la plantilla

## Qué falta hoy

Los repos que adoptaron el pack comparan su versión contra el CHANGELOG de la plantilla **a mano**. Al salir cada versión nueva, migrar los cambios a cada repo es propenso a error.

## Propuesta de cambio

`scripts/actualizar-pack.py`: compara la versión registrada en `00-nucleo/configuracion-proyecto.md` contra el CHANGELOG de la plantilla más reciente; produce un diff por carpeta (respetando R-14/R-17) y genera automáticamente una ficha `EVO-*` de adopción de cambios en `01-pendientes/` con los paths afectados.

## Decisión a tomar

<!-- decision-group: EVO-20260823-actualizador-pack -->
- [x] <!-- decision:aprobar --> **Aprobar** → instrucción derivada
- [ ] <!-- decision:posponer --> **Posponer**
- [ ] <!-- decision:rechazar --> **Rechazar** → `05-canceladas/`

### Notas del humano

- [2026-10-15T22:27:26Z] decisiones-pendientes sesión 20261015-222712: aprobar

<!-- revision-pendientes-nota: actualizar matriz-cobertura-proyectos.md fila relacionada con EVO EVO-20260823-actualizador-pack -->
