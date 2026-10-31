# Protocolo de áreas

## Qué es

Un área ≈ un módulo de negocio. Directorio = id = carpeta en `15-rutas/<id>/` y `src/modules/<id>/` cuando exista.

## Qué es CONTEXTO.md

Mapa de capacitación (**60–120 líneas**): fronteras, mapa de lectura, índice local de endpoints, anclas de código, invariantes. **No** es un tratado ni copia del código. Objetivo: mínimo tokens para orientar a la IA.

## RESUMEN.md (lectura primero)

Cada área tiene un `RESUMEN.md` de **máximo 10 líneas** (ver
[_PLANTILLA-RESUMEN-area.md](_PLANTILLA-RESUMEN-area.md)). El agente lo lee
antes que el CONTEXTO y solo abre el CONTEXTO si el resumen no basta. Se
regenera cuando cambia el área, en el mismo cierre.

## Sincronización

1. Módulo nuevo → `CONTEXTO.md` + fila en INDICE + `15-rutas/<id>/`.
2. Ruta nueva → actualizar índice del CONTEXTO + ficha.
3. Cambio de frontera → actualizar CONTEXTO en el mismo cambio.
4. Hallazgos de audit → **no** se acumulan aquí; se promocionan a invariantes/ADR/ficha.
