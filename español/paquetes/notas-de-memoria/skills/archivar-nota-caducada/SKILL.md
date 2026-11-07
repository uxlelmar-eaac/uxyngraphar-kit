---
name: archivar-nota-caducada
description: Marca como archivada una nota de memoria que una nota nueva sustituye o que ha pasado su validez, para que no se siga usando como cierta.
resuelve: [notas-caducadas-tratadas-como-vigentes]
---

# Archivar nota caducada

## Cuándo usarla

- Una nota nueva contradice o sustituye a otra.
- La persona confirma que una nota ya no vale (o su `valida_hasta` pasó y lo confirma).

## Pasos

1. Añade al final de «Qué hay que recordar» una línea con la causa: «Sustituida por MEM-… el AAAA-MM-DD» o «Dejó de valer el AAAA-MM-DD».
2. Cambia el status: `python3 $P/scripts/comun/fichas.py estado <id> archivada`.
3. No la borres ni la muevas fuera de `memoria/`: archivar una nota es solo cambiar su status. El archivo histórico de documentos es otra cosa (`documentos-archivados`) y lo maneja la persona.

## Resultado

- La nota sigue en `memoria/` con `status: archivada` y la causa escrita.
