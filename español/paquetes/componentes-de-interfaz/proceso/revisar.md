---
fase: revisar
resuelve: [interfaz-inconsistente]
skills: [revisar-consistencia]
---

# Fase: revisar

## Objetivo

Encontrar en las pantallas del pedido los valores sueltos, los componentes duplicados, los estados sin cubrir y los problemas de jerarquía, y entregar a la persona la decisión de qué se corrige.

## Entradas

- El inventario de `INTERFAZ.md` y las pantallas del pedido.
- `referencia/consistencia-ui.md`.

## Pasos

1. Si ya hay una revisión de esas pantallas con hallazgos `pendiente`, continúa esa. Si no, añade arriba de las revisiones una sección `## Revisión <AAAA-MM-DD> — <pantallas>`.
2. Aplica la skill `revisar-consistencia` sobre los archivos de esas pantallas y anota cada hallazgo con «Aprobada» vacía y estado `pendiente`.
3. **Detente.** Resume a la persona los hallazgos por tipo y dile qué debe decidir: marcar «sí» en «Aprobada» de los que se corrigen, o pedir que alguno quede `aceptado`.

## Criterio de salida

- Revisión con cada hallazgo con tipo, evidencia `ruta:línea` o captura y la corrección con el token o componente existente; o la constancia en «Notas» de que las pantallas son consistentes.
- La persona tiene el resumen y sabe qué tiene que aprobar.
