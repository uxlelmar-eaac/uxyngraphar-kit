---
fase: actualizar-espejo
resuelve: [codigo-sin-espejo, espejos-desfasados, espejos-huerfanos, espejos-que-copian-codigo]
skills: [crear-espejo, mover-espejo]
---

# Fase: actualizar-espejo

## Objetivo

Que los espejos del código tocado describan cómo queda al terminar la tarea.

## Entradas

- La lista de `leer-espejo`.
- El código tal como queda tras el cambio.

## Pasos

1. Código nuevo o sin espejo → skill `crear-espejo`.
2. Código movido o renombrado → skill `mover-espejo`.
3. Código borrado → borra su espejo (`espejo.py huerfanos` lo confirma).
4. Cambio de responsabilidad o de interacciones → edita «Rol», «Responsabilidades» o «Interacciones» y actualiza la fecha y las líneas de la cabecera (`> Espejo de: … · N líneas · actualizado AAAA-MM-DD`).
5. Relee cada espejo tocado: si contiene bloques de código o enumera funciones línea a línea, reescríbelo como papel en el sistema (límite 3).

## Criterio de salida

- Cada elemento de la lista está hecho.
- Ningún espejo tocado contiene código pegado.
