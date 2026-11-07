---
name: registrar-hallazgo
description: Añade un hallazgo a la tabla «Hallazgos» de la auditoría con severidad válida y evidencia reproducible, y mantiene findings_count y actualizado al día.
resuelve: [hallazgos-sin-evidencia]
---

# Registrar hallazgo

## Cuándo usarla

- En la fase `investigar`, por cada hecho que responde a una pregunta.
- Cuando `verificar-auditorias.py` informa de un hallazgo sin severidad, sin evidencia o de un `findings_count` desfasado.

## Pasos

1. Escribe el hallazgo como un hecho («el listado hace una consulta por pedido: 201 consultas para 200 filas»), no como solución.
2. Elige la severidad de `ajustes.severidades`: `critica` (seguridad, pérdida de datos, caída), `alta`, `media`, `baja` o `info` (dato útil sin problema).
3. Escribe la evidencia: `ruta:línea`, el comando exacto que lo reproduce o la medición con su fuente. Sin evidencia va a «Notas».
4. Añade la fila:

   ```
   | 3 | alta | El listado hace una consulta por pedido | `src/orders/list.ts:42`; log SQL con 201 consultas |
   ```
5. Actualiza `findings_count` con el número de filas de la tabla y `actualizado` con la fecha de hoy.

## Resultado

- Una fila nueva que `verificar-auditorias.py` acepta y el frontmatter al día.
