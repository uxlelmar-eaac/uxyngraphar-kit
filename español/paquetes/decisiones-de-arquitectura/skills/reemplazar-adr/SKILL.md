---
name: reemplazar-adr
description: Archiva una ADR aceptada como reemplazada y la enlaza con la nueva, sin tocar su texto, cuando una persona ya aceptó la ADR que la sustituye.
resuelve: [decisiones-aceptadas-reescritas]
---

# Reemplazar ADR

## Cuándo usarla

- En `registrar-reemplazo`: la ADR nueva tiene `reemplaza: <id>` y ya está `aceptada`.
- Nunca antes de que la persona acepte la nueva: hasta entonces la anterior sigue vigente.

## Pasos

1. En la ADR anterior, cambia solo el campo `reemplazada_por: null` por `reemplazada_por: <ADR-nueva>`. Nada más del archivo cambia.
2. Pásala a reemplazada: `python3 $P/scripts/comun/fichas.py estado <ADR-anterior> reemplazada`. Se mueve a `archivadas/`.
3. Si la anterior quedó sin sentido sin que nadie la sustituya (la tecnología desapareció del proyecto), el status es `obsoleta`, no `reemplazada`, y no lleva `reemplazada_por`.

## Resultado

- La ADR anterior en `archivadas/`, con su decisión original intacta y el enlace a la que la sustituye; la nueva enlaza a la anterior con `reemplaza`.
