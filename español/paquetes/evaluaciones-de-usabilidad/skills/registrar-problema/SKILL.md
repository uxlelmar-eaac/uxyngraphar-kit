---
name: registrar-problema
description: Añade un problema de interfaz a la tabla «Problemas» de la evaluación con heurística, severidad 0–4, evidencia y, si la severidad es alta, propuesta.
resuelve: [problemas-de-usabilidad-sin-evidencia]
---

# Registrar problema

## Cuándo usarla

- En la fase `evaluar`, por cada problema encontrado.
- Cuando la persona señala un problema concreto y hay que dejarlo en la evaluación.

## Pasos

1. Elige el código en `referencia/heuristicas.md`: `H1`–`H10`, `A11Y`, `UI` o `RENDIMIENTO` (los admitidos están en `heuristicas` de los ajustes). Si encajan dos, el que describa la causa.
2. Pon la severidad 0–4 ponderando frecuencia, impacto y persistencia (tabla de `referencia/heuristicas.md`). En duda entre dos valores, el menor, y explica la duda en «Notas».
3. Escribe el problema como lo vive el usuario («el error no dice qué campo falla»), no como solución.
4. Escribe la evidencia: `ruta:línea` entre comillas invertidas, nombre de captura, paso reproducible («paso 3 del alta, enviar vacío») o medición. Sin evidencia, el problema no entra en la tabla: va a «Notas».
5. Con severidad ≥ 3, rellena «Propuesta» ya (qué cambia y dónde). Deja «Aprobada» vacía: la marca la persona.
6. Formato de la fila:

   ```
   | 3 | H9 | 3 | El error no dice qué campo falla | `src/signup/form.tsx:88` | Mensaje bajo el campo, anunciado con aria-live | |
   ```

## Resultado

- Una fila nueva en «Problemas» que `verificar-evaluaciones.py` acepta.
