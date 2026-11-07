---
fase: leer-espejo
resuelve: [codigo-sin-espejo]
skills: [medir-cobertura]
---

# Fase: leer-espejo

## Objetivo

Entender el código que vas a tocar a partir de su espejo y saber qué espejos tendrás que crear, mover o borrar.

## Entradas

- El pedido y las rutas de código que afecta.

## Pasos

1. Por cada archivo o carpeta afectado: `python3 $P/scripts/espejo.py ver <ruta-del-codigo>`. Lee primero el espejo de la carpeta del módulo y luego el de cada archivo.
2. Si responde `sin espejo: …`, anótalo: se creará en `actualizar-espejo`.
3. Si el pedido abarca un módulo entero o es una adopción, aplica la skill `medir-cobertura` para ver qué falta.
4. Haz la lista de cambios de espejo que implica el pedido: crear (código nuevo o sin espejo), actualizar (cambia responsabilidad o interacciones), mover (código movido o renombrado), borrar (código eliminado).

## Criterio de salida

- Has leído el espejo de todo el código afectado que lo tiene.
- Tienes la lista de espejos a crear, actualizar, mover y borrar.
