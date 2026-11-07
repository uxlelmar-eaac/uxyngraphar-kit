---
name: buscar-en-notas
description: Busca un texto en las notas de memoria con notas.py buscar y abre solo las notas que devuelve, descartando las archivadas o caducadas; solo cuando el pedido lo pide.
resuelve: [memoria-leida-sin-pedido, notas-caducadas-tratadas-como-vigentes]
---

# Buscar en notas

## Cuándo usarla

- El pedido pide expresamente consultar la memoria del proyecto.

## Pasos

1. Elige dos o tres términos concretos del pedido (nombre del cliente, del servicio, del incidente).
2. Ejecuta `python3 $P/scripts/notas.py buscar <texto>` por cada término. Cada línea es `memoria/<ruta>:<línea>: <texto>`; sin resultados, no imprime nada.
3. Abre solo los archivos que aparecen en los resultados.
4. Descarta como cierta toda nota con `status: archivada` o con `valida_hasta` ya pasada; menciónala como antecedente.
5. Cita al responder qué nota usaste (`MEM-…`) y su `fuente`.

## Resultado

- Respuesta basada en notas vigentes, con su id y fuente, y la lista de las caducadas que aparecieron.
