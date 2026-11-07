---
name: priorizar-pendientes-antiguos
description: Separa las fichas que llevan más de dias_aviso días esperando a una persona y propone, para cada una, decidirla o cerrarla.
resuelve: [pendientes-envejecidos]
---

# Priorizar pendientes antiguos

## Cuándo usarla

- En `recoger-pendientes`, siempre que haya algún pendiente.
- Cuando `verificar-revision.py` imprime avisos `… lleva N días en «status» esperando a una persona`.

## Pasos

1. Ejecuta `python3 $P/scripts/verificar-revision.py`. Imprime un aviso por ficha con más de `dias_aviso` días y un resumen `revision-humana: N pendientes de decisión, M con más de D días`. Nunca falla por antigüedad.
2. Los días salen del campo `actualizado` o `fecha` del frontmatter de la ficha; si no tiene ninguno, de la fecha de modificación del archivo. Si una ficha antigua tiene fecha de modificación reciente, lo que cuenta es el campo.
3. Pon las antiguas al principio del resumen para la persona.
4. Para cada una, propón una salida concreta: decidirla ya, rechazarla o cancelarla si ya no aplica, o `posponer` con un motivo.

## Resultado

- Las fichas antiguas identificadas y encabezando la revisión, cada una con una salida propuesta.
