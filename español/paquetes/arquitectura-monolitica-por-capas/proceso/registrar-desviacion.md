---
fase: registrar-desviacion
resuelve: []
skills: []
---

# Fase: registrar desviación

Solo si cumplir un límite es inviable o claramente peor para el proyecto. Si no, esta fase no se recorre.

## Objetivo

Que ninguna excepción a las capas exista sin una decisión explícita de una persona.

## Entradas

- La restricción que habría que romper y por qué.
- Las alternativas consideradas.

## Pasos

1. No implementes la excepción.
2. Si está instalado `decisiones-de-arquitectura`, redacta la ADR en estado `propuesta` (contexto, opciones, decisión propuesta y consecuencias). Si no, explica el caso a la persona en la respuesta.
3. Di a la persona qué tiene que decidir. Aceptar la ADR es una acción suya.
4. Cuando la ADR esté aceptada, anota la desviación en «Desviaciones aceptadas» de `ARQUITECTURA.md` (créalo con `capas.py iniciar` si falta), citando la ADR, y vuelve a `implementar`.

## Criterio de salida

- La desviación está propuesta y esperando a la persona, o aceptada y anotada en `ARQUITECTURA.md`.
