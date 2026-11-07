---
fase: promover
resuelve: [conclusiones-sin-seguimiento]
skills: [promover-resultado]
---

# Fase: promover

Solo si la persona acepta alguna promoción. Si no, esta fase no se recorre.

## Objetivo

Que cada promoción aceptada exista como ficha en su paquete destino y que la auditoría lo refleje.

## Entradas

- La ficha `cerrada` y las promociones que la persona aceptó.

## Pasos

1. Para cada promoción aceptada, aplica `promover-resultado`.
2. Las promociones no aceptadas se quedan en la ficha como propuesta; no se insiste.
3. Ejecuta `python3 $P/scripts/verificar-auditorias.py`.

## Criterio de salida

- Cada promoción aceptada tiene su ficha en el paquete destino (o, si ese paquete no está instalado, la persona sabe qué crear) y figura en `promociones` del frontmatter.
