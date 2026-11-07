---
fase: redactar-adr
resuelve: [decisiones-sin-registro, opciones-sin-comparar, prohibiciones-no-comprobables]
skills: [redactar-prohibicion-comprobable]
---

# Fase: redactar-adr

## Objetivo

Una ADR concreta del proyecto, con opciones reales comparadas, que una persona pueda aceptar o rechazar sin pedir más contexto.

## Entradas

- El resultado de `consultar-vigentes` (ADR relacionadas y si es un reemplazo).
- El contexto del proyecto: rutas, datos, restricciones que motivan la decisión.

## Pasos

1. Crea la ficha: `python3 $P/scripts/comun/fichas.py nueva adr --slug <slug> --titulo "…"`. Nace en `pendientes/` con `status: propuesta`.
2. Frontmatter: `areas` (las áreas afectadas) y, si reemplaza a otra, `reemplaza: <ADR-…>`.
3. «Contexto»: el problema o la restricción concreta, con rutas, cifras o enlaces. Sin frases que valgan para cualquier proyecto.
4. «Opciones consideradas»: al menos dos opciones que alguien defendería de verdad, con ventajas y desventajas de cada una. «No hacer nada» cuenta si es realista.
5. «Decisión»: la opción elegida y por qué gana a las otras en este contexto.
6. «Consecuencias»: positivas, negativas o riesgos, y qué cambia en el código o en el proceso.
7. «Seguimiento»: cómo se sabrá si fue buena y cuándo revisarla.
8. Si la decisión veta algo detectable en el código, aplica `redactar-prohibicion-comprobable`.

## Criterio de salida

- La ADR tiene contexto concreto, dos o más opciones con pros y contras, decisión, consecuencias negativas y seguimiento.
- No queda texto de ejemplo de la plantilla («Opción A», «…»).
- Si veta algo detectable, `comprobacion_prohibido` es una expresión regular válida.
