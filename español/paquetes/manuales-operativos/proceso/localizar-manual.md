---
fase: localizar-manual
resuelve: [procedimientos-sin-manual, manuales-desfasados]
skills: []
---

# Fase: localizar-manual

## Objetivo

Saber qué manuales afecta el cambio o el pedido y si hay que crear uno nuevo.

## Entradas

- El pedido o el cambio (scripts de despliegue, variables de entorno, CI, migraciones, monitorización).
- Los manuales de `uxyngraphar/trabajo/manuales-operativos/`.

## Pasos

1. Lista los manuales: `python3 $P/scripts/comun/fichas.py listar manual` (con `--status vigente` para los que se usan hoy).
2. Abre los que el cambio puede afectar: `python3 $P/scripts/comun/fichas.py ver <id>`. Un cambio afecta a un manual si altera un comando, una variable, un requisito, el resultado esperado o la forma de revertir.
3. Si el procedimiento no tiene manual, se creará en `redactar-pasos` con la skill `crear-manual`.
4. Si el cambio no afecta a ningún procedimiento, dilo y termina el proceso.

## Criterio de salida

- Tienes la lista de manuales a actualizar y de manuales a crear (puede estar vacía, y se dice).
