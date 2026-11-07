---
fase: registrar-reemplazo
resuelve: [decisiones-aceptadas-reescritas, decisiones-contradichas]
skills: [reemplazar-adr]
---

# Fase: registrar-reemplazo

Solo si una persona aceptó una ADR con `reemplaza: <id>`. Si no, el trabajo terminó en `someter-a-evaluacion`.

## Objetivo

Que la ADR anterior quede archivada y enlazada con la que la sustituye, sin reescribir lo que decidió.

## Entradas

- La ADR nueva, ya `aceptada` en `completadas/`.
- La ADR que nombra en `reemplaza`.

## Pasos

1. Comprueba que la nueva está aceptada: `python3 $P/scripts/comun/fichas.py ver <ADR-nueva>`.
2. Aplica la skill `reemplazar-adr` sobre la anterior.
3. Ejecuta `python3 $P/scripts/comun/verificar.py`.

## Criterio de salida

- La ADR anterior está en `archivadas/` con `status: reemplazada` y `reemplazada_por: <ADR-nueva>`; su texto no cambió.
- `fichas.py listar adr --status aceptada` ya no la muestra.
