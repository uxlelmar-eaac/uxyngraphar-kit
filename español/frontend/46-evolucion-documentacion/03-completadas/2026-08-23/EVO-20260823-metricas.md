---
id: EVO-20260823-metricas
status: done
source: human
tipo: herramienta-pack
impacto: ambos
prioridad: despues
detected_in: revision-humana
areas: []
propuesta_cambio:
  - scripts/decisiones/decisiones.py
proposed_at: 2026-08-23
instruction_derivada: solicitud-humana-20261015
---
# EVO-20260823 — Métricas del propio sistema documental

## Qué falta hoy

El sistema ahorra tokens y organiza el trabajo, pero no lo mide: no hay datos de instrucciones/semana, antigüedad media de decisiones, presupuestos excedidos ni tamaño de colas.

## Propuesta de cambio

Comando `metricas` en `decisiones.py`: instrucciones por semana (por carpeta de fecha), antigüedad media de pendientes, recuento por cola y estado, WARN de presupuesto históricos. Salida en tabla + opción JSON para dashboards.

## Decisión a tomar

<!-- decision-group: EVO-20260823-metricas -->
- [x] <!-- decision:aprobar --> **Aprobar** → instrucción derivada
- [ ] <!-- decision:posponer --> **Posponer**
- [ ] <!-- decision:rechazar --> **Rechazar** → `05-canceladas/`

### Notas del humano

- [2026-10-15T22:27:26Z] decisiones-pendientes sesión 20261015-222712: aprobar

<!-- revision-pendientes-nota: actualizar matriz-cobertura-proyectos.md fila relacionada con EVO EVO-20260823-metricas -->
