---
fase: someter-a-evaluacion
resuelve: [decisiones-sin-registro]
skills: []
---

# Fase: someter-a-evaluacion

## Objetivo

Dejar la ADR en manos de la persona, lista para decidir, sin que el agente la acepte ni la rechace.

## Entradas

- La ADR redactada en `pendientes/`.

## Pasos

1. Pásala a evaluación: `python3 $P/scripts/comun/fichas.py estado <ADR-…> en-evaluacion`. Se mueve a `en-progreso/`.
2. Resume a la persona en dos o tres líneas: qué se decide, la opción propuesta, su principal consecuencia negativa y, si es un reemplazo, qué ADR deja de valer.
3. Dale sus comandos: aceptar `python3 $P/scripts/comun/fichas.py estado <ADR-…> aceptada --humano`; rechazar, lo mismo con `rechazada`. (Con `revision-humana` instalado, también desde su hoja de revisión.)
4. **Detente.** Mientras la ADR no esté aceptada, el trabajo que dependa de ella no empieza.
5. Ejecuta `python3 $P/scripts/comun/verificar.py`.

## Criterio de salida

- La ADR está en `en-progreso/` con `status: en-evaluacion` y la persona tiene el resumen y los comandos.
- La verificación termina sin errores.
