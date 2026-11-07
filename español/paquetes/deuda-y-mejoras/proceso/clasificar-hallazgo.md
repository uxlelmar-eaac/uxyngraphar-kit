---
fase: clasificar-hallazgo
resuelve: [arreglos-fuera-de-alcance, deuda-detectada-sin-registro]
skills: []
---

# Fase: clasificar hallazgo

## Objetivo

Decidir, ante un problema visto durante una tarea, si se resuelve en la tarea, se registra aquí o pertenece a otro paquete; y no tocarlo si no es del pedido.

## Entradas

- El problema observado y la tarea en curso.

## Pasos

1. ¿Forma parte de lo que pidió la persona? Si sí, se resuelve en la tarea y esta fase termina: no es una mejora.
2. ¿Es del propio sistema uxyngraphar (un paquete, una plantilla)? Va a `evolucion-del-sistema`. ¿Necesita investigación antes de poder describirlo? Va a `auditorias-tecnicas`.
3. Si es deuda o un bug del producto fuera del pedido: **no lo arregles**, aunque sea una línea. Sigue en `buscar-duplicados`.
4. Si es `critica` (seguridad, pérdida de datos), avisa a la persona ya, además de registrarlo.

## Criterio de salida

- El problema está clasificado: parte de la tarea, otro paquete, o mejora a registrar.
- Ningún cambio de código fuera del pedido.
