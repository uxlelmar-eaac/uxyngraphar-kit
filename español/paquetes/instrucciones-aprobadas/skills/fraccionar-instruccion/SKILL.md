---
name: fraccionar-instruccion
description: Parte un pedido que supera el máximo de archivos de código o documentos en varias instrucciones encadenadas, cada una aprobable por separado.
resuelve: [alcance-desbordado]
---

# Fraccionar instrucción

## Cuándo usarla

- Las anclas suman más de `max_archivos_codigo` archivos de código (5 por defecto) o `lectura_minima` supera `max_docs` (8).
- `ciclo.py aprobar` respondió `no se puede aprobar: N archivos de código en anclas (máximo M)`.
- En la variante `adopcion`, cuando una fase no cabe en el alcance de una instrucción.

## Pasos

1. Agrupa las anclas por unidad que se pueda entregar sola (un caso de uso, una pantalla, una migración y su uso).
2. La primera fracción es la instrucción actual: déjale solo las anclas de su grupo.
3. Crea cada fracción: `python3 $P/scripts/comun/fichas.py nueva instruccion --slug <slug>-parte-2 --titulo "…"`.
4. En cada fracción pon `fraccion_de: <INS-original>` y, si necesita que otra esté cerrada antes, `depende_de: [<INS-…>]`.
5. Cada fracción lleva sus propios criterios de aceptación; no repitas anclas entre fracciones.
6. Comprueba que cada una cabe: la persona verá el mismo error al aprobar si no.

## Resultado

- Varias instrucciones en `pendientes/`, cada una dentro del máximo, enlazadas con `fraccion_de` y `depende_de`.
