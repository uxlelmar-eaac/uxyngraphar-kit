---
fase: buscar-en-memoria
resuelve: [memoria-leida-sin-pedido, notas-caducadas-tratadas-como-vigentes]
skills: [buscar-en-notas]
---

# Fase: buscar-en-memoria

## Objetivo

Solo si el pedido pide expresamente consultar la memoria: encontrar las notas que responden y usarlas sin arrastrar información caducada.

## Entradas

- El pedido, con la petición explícita de buscar en la memoria («¿qué apuntamos sobre…?», «mira en la memoria del proyecto…»).

## Pasos

1. Si el pedido no menciona la memoria, salta esta fase. No abras `memoria/` «por si acaso» (límite 1).
2. Aplica la skill `buscar-en-notas`.
3. Si la respuesta solo puede estar en un documento archivado, no lo busques tú: el archivo histórico es de `documentos-archivados` y solo lo consulta la persona.

## Criterio de salida

- Solo has leído notas devueltas por `notas.py buscar`.
- Las que usas están `vigente` y dentro de su `valida_hasta`; las demás se mencionan como caducadas.
