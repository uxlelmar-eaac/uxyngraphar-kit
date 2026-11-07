---
fase: guardar-nota
resuelve: [conocimiento-del-proyecto-perdido, notas-caducadas-tratadas-como-vigentes]
skills: [registrar-nota, archivar-nota-caducada]
---

# Fase: guardar-nota

## Objetivo

Solo si la persona pide conservar algo o da por caducada una nota: dejarlo como nota breve, fechada, con fuente y validez, en el paquete correcto.

## Entradas

- Lo que la persona quiere recordar y de dónde sale, o la nota que deja de valer.

## Pasos

1. Comprueba que no es una decisión técnica (`decisiones-de-arquitectura`), una regla del código (`reglas-del-proyecto`), un procedimiento (`manuales-operativos`), deuda (`deuda-y-mejoras`) ni un documento entero que se quiere retirar (`documentos-archivados`). Si lo es, propón ese paquete.
2. Aplica la skill `registrar-nota`.
3. Si la nota nueva sustituye a otra, o la persona confirma que una nota ya no vale, aplica `archivar-nota-caducada`.
4. Ejecuta `python3 $P/scripts/comun/verificar.py`.

## Criterio de salida

- Nota `vigente` con `fuente` y `valida_hasta` rellenos (o `null` justificado).
- Ninguna nota anterior contradictoria sigue `vigente`.
