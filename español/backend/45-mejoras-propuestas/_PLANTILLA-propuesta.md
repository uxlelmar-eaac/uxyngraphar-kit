---
id: MEJ-YYYYMMDD-slug
status: pending
source: ai
tipo: deuda-tecnica
severidad: media
prioridad: despues
proposed_at: YYYY-MM-DD
related_instruction: YYYYMMDD-NNN
areas: []
evidencia: []
motivo: "Breve razón — fuera de alcance de instrucción origen"
---

<!-- Ubicación (R-17): 45-mejoras-propuestas/01-pendientes/YYYY-MM-DD/ (fecha = proposed_at).
     Aprobada → 02-en-progreso/; done → 03-completadas/; rechazada → 05-canceladas/.
     Bug detectado → tipo: bug. -->

# MEJ-YYYYMMDD — Título corto de la mejora

> **No implementar** hasta que el humano cree una instrucción `approved` derivada de esta ficha.

## Contexto detectado

Durante instrucción `related_instruction`: … (1–3 frases).

## Evidencia

- `ruta/archivo.ts:42` — qué se observó
- (opcional) enlace a auditoría si existe

## Problema / deuda

Qué está mal o qué se podría mejorar (sin prosa larga).

## Mejora propuesta

Descripción de la solución **sin implementarla**. El humano puede editar/ampliar esta sección.

## Fuera de alcance porque

Citar explícitamente la instrucción origen (sección Alcance excluido o Pedido).

## Impacto si no se hace

Bajo | medio | alto — una línea.

## Esfuerzo estimado

Bajo | medio | alto.

## Decisión a tomar

<!-- decision-group: MEJ-YYYYMMDD-slug -->
- [ ] <!-- decision:aprobar --> **Aprobar** → crear instrucción desde [_PLANTILLA-revisar-propuesta.md](_PLANTILLA-revisar-propuesta.md); `status: approved` + `02-en-progreso/`
- [ ] <!-- decision:posponer --> **Posponer** — mantener `pending`; añadir notas abajo
- [ ] <!-- decision:rechazar --> **Rechazar** — `status: rejected`; mover a `05-canceladas/`

### Notas del humano

(Espacio libre para contexto, prioridad de negocio, etc.)
