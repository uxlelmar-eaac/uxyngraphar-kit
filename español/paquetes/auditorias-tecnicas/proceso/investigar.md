---
fase: investigar
resuelve: [hallazgos-sin-evidencia, auditorias-que-modifican-codigo, auditorias-abandonadas]
skills: [registrar-hallazgo]
---

# Fase: investigar

## Objetivo

Responder las preguntas con hechos comprobables, sin cambiar nada del producto.

## Entradas

- La ficha `activa` con alcance, preguntas y método.

## Pasos

1. Investiga solo dentro del alcance: lee código, ejecuta comandos de lectura, mide. No edites código, datos, configuración ni documentación del producto.
2. Registra cada hecho relevante con la skill `registrar-hallazgo` (severidad, evidencia, contador y fecha).
3. Completa «Método» con lo que realmente hiciste, para que otra persona pueda repetirlo.
4. Lo que veas fuera del alcance va a «Notas» (o a `deuda-y-mejoras` si está instalado y es un bug claro).
5. Si encuentras algo `critica`, avisa a la persona en ese momento.
6. Si la investigación se interrumpe, deja `actualizado` con la fecha de hoy y, si va a tardar, propón pasarla a `pendiente`.

## Criterio de salida

- Cada pregunta tiene hallazgos que la responden o una nota de por qué no se pudo responder.
- `findings_count` coincide con la tabla y `actualizado` tiene la fecha del último avance.
- Ningún archivo del producto modificado.
