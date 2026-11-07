---
name: resumir-cola
description: Resume para la persona las mejoras pendientes ordenadas por severidad y prioridad propuesta, señalando duplicados y fichas sin clasificar, para que decida qué aprobar o rechazar.
resuelve: [cola-de-mejoras-inmanejable]
---

# Resumir cola

## Cuándo usarla

- Cuando la persona pide repasar la deuda o elegir qué aprobar.
- Antes de planificar una tanda de corrección de deuda.

## Pasos

1. Lista las pendientes: `python3 $P/scripts/comun/fichas.py listar mejora --status pending`.
2. Lee el frontmatter de cada una (`fichas.py ver MEJ-…`) y ordénalas por `severidad` y después por `prioridad`.
3. Señala las fichas sin `tipo`, `severidad` o `prioridad`, sin evidencia, y las que parecen el mismo problema (mismo archivo o misma causa): propón fusionarlas.
4. Presenta una tabla corta: id, título, tipo, severidad, prioridad propuesta, antigüedad.
5. Recuerda a la persona los comandos de decisión: `fichas.py estado MEJ-… approved --humano` o `rejected --humano`.

## Resultado

- Un resumen ordenado de la cola con las anomalías señaladas; ninguna ficha cambiada de status.
