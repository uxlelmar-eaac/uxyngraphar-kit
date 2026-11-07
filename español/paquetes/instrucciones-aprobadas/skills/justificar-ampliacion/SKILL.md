---
name: justificar-ampliacion
description: Declara en una instrucción un factor de ampliación del máximo de archivos de código, con su justificación, cuando el cambio no se puede fraccionar.
resuelve: [alcance-desbordado]
---

# Justificar ampliación

## Cuándo usarla

- Solo cuando `fraccionar-instruccion` no sirve: el cambio deja el código roto si se entrega a medias (renombrar un tipo usado en 7 archivos, cambiar una firma compartida).

## Pasos

1. Calcula el factor mínimo: archivos de código ÷ `max_archivos_codigo`, redondeado hacia arriba a 1.5 o más (7 archivos con máximo 5 → `1.5`, que permite 7).
2. El factor debe estar entre `1.5` y `ampliacion_factor_max` (2.0 por defecto). Si hace falta más, no se puede ampliar: fracciona.
3. En la instrucción, pon `ampliacion_factor: <factor>` y `ampliacion_justificacion: "<por qué no se puede partir>"` (una frase concreta, no «es necesario»).
4. Menciónalo en el resumen para la persona en `esperar-aprobacion`: aprobar la instrucción es aprobar la ampliación.

## Resultado

- Instrucción con `ampliacion_factor` y `ampliacion_justificacion` que `ciclo.py aprobar` y `verificar-ciclo.py` aceptan.
