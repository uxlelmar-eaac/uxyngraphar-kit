---
fase: redactar-instruccion
resuelve: [cambios-sin-aprobacion, alcance-desbordado, contexto-excesivo]
skills: [fraccionar-instruccion, justificar-ampliacion]
---

# Fase: redactar-instruccion

## Objetivo

Dejar por escrito, para que una persona lo apruebe, qué cambia, qué no, qué archivos se tocan y qué se lee: la instrucción es el contrato de la tarea.

## Entradas

- El pedido de la persona.
- `uxyngraphar/trabajo/instrucciones-aprobadas/ESTADO.md`, si existe (para orientarse; nada más del historial).
- Si existe `uxyngraphar/trabajo/preguntas-de-clarificacion/`, la ficha `PRE-…` de este pedido con su «Síntesis».
- Los ajustes efectivos: `max_archivos_codigo`, `max_docs`, `ampliacion_factor_max`.

## Pasos

1. Si el pedido deja sin decidir algo que cambia el resultado (alcance, comportamiento visible, datos, compatibilidad), no lo supongas: pregúntalo antes de seguir. Si está instalado `preguntas-de-clarificacion`, sigue su proceso y vuelve aquí con su ficha.
2. Elige la variante y crea la ficha:
   - Normal: `python3 $P/scripts/comun/fichas.py nueva instruccion --slug <slug> --titulo "…"`.
   - Cambio pequeño y evidente: `--variante compacta`.
   - Solo documentación, sin código: `--variante solo-docs` (`anclas_codigo` vacío; lo que se escribe va en `documentos`).
   - Primera vez de uxyngraphar en el repo: `--variante adopcion` (fases de escaneo a comprobación).
3. «Clarificación»: si hay ficha `PRE-…`, pon `preguntas_id: <PRE-…>` y copia su síntesis; si no, escribe lo que la persona decidió en el chat o `Omitida (motivo)` y deja `preguntas_id: null`.
4. Rellena «Objetivo» (una frase verificable), «Alcance» (incluye / excluye), «Plan» y «Criterios de aceptación» comprobables.
5. Rellena `anclas_codigo` con rangos siempre que puedas (`src/orders/orders.service.ts:40-88`): sin rango, `contexto` imprime solo las primeras 200 líneas. En `lectura_minima`, solo los documentos imprescindibles.
6. Cuenta los archivos de código de las anclas. Si superan `max_archivos_codigo`, aplica `fraccionar-instruccion`; si de verdad no se puede partir, `justificar-ampliacion`.
7. No toques todavía ningún archivo del producto.

## Criterio de salida

- La instrucción está en `instrucciones/pendientes/` con `status: awaiting_approval`.
- Objetivo, alcance, anclas, criterios y «Clarificación» están rellenos; no queda texto de ejemplo de la plantilla («…»).
- El número de archivos de código está dentro del máximo o la ampliación está justificada.
