---
name: comprobar-decisiones
description: Busca en el código el patrón prohibido de cada ADR aceptada y lista cada aparición con archivo y línea.
resuelve: [decisiones-incumplidas]
---

# Comprobar decisiones

## Cuándo usarla

- La persona quiere saber si el código respeta las decisiones de arquitectura aceptadas.
- Tras aceptar una ADR que prohíbe algo que el código ya usaba.

## Pasos

1. Ejecuta `python3 $P/scripts/vivas.py decisiones` (necesita `decisiones-de-arquitectura`).
2. Solo cuentan las ADR `aceptada` con `comprobacion_prohibido`; `aplica_a` (lista de globs) limita los archivos. Las aceptadas sin patrón salen como `info`: no hay evidencia automática.
3. Cada aparición sale como `alta: ADR-… prohíbe «<patrón>» — src/…:línea`.
4. Un patrón que no compila sale como `media: ADR-…: comprobacion_prohibido no es una expresión regular válida`.
5. No decidas si sobra el código o la ADR: preséntalo y deriva (fase `derivar-hallazgos`).

## Resultado

- Cada incumplimiento de una decisión aceptada, con archivo y línea.
