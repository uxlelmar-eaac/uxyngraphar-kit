---
fase: detectar-carencia
resuelve: [paquetes-editados-en-el-proyecto, carencias-del-sistema-sin-registro]
skills: []
---

# Fase: detectar carencia

## Objetivo

Reconocer que lo que falla es el sistema (un paquete, una plantilla, un proceso) y no el producto, y no resolverlo editando el paquete.

## Entradas

- La tarea en curso y el paquete cuyo proceso, plantilla o verificación no encaja.

## Pasos

1. Comprueba que el hueco es del sistema: «el paquete X no prevé el caso Y», «la plantilla Z no tiene la sección que este proyecto necesita», «no hay paquete para W». Si es del código del producto, va a `deuda-y-mejoras` y esta fase termina.
2. No edites el paquete instalado (`uxyngraphar/paquetes/<id>/`) ni su copia del catálogo, aunque el cambio parezca trivial: la verificación de integridad lo detectaría y la próxima actualización lo borraría.
3. Si la tarea no puede seguir sin el cambio, díselo a la persona y propón un ajuste local en `adaptaciones-de-paquetes` que cite la EVO; no lo actives tú.
4. Anota la evidencia mientras la tienes delante: tarea, archivo del paquete (`proceso/…`, `plantillas/…`) y qué pasó.

## Criterio de salida

- La carencia está identificada como del sistema, con evidencia anotada.
- Ningún archivo de `uxyngraphar/paquetes/` modificado.
