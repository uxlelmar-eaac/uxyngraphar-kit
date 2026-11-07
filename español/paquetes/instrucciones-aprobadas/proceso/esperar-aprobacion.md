---
fase: esperar-aprobacion
resuelve: [cambios-sin-aprobacion]
skills: []
---

# Fase: esperar-aprobacion

## Objetivo

Que la persona decida con lo necesario a la vista y que el agente no avance hasta que la instrucción esté aprobada.

## Entradas

- La instrucción en `instrucciones/pendientes/`.

## Pasos

1. Resume a la persona en dos o tres líneas qué cambia, cuántos archivos toca y qué queda fuera; enlaza la ficha en lugar de copiarla.
2. Dale los dos comandos que son suyos (están al final de la ficha, en «Decisión (persona)»):
   - Aprobar: `python3 $P/scripts/ciclo.py aprobar <id> --humano`.
   - Cancelar: `python3 $P/scripts/comun/fichas.py estado <id> cancelled`.
3. **Detente.** No ejecutes `aprobar` aunque la persona te lo pida en el chat: el script exige una terminal interactiva o `UXYNGRAPHAR_HUMANO=1`, que el agente no tiene.
4. Cuando la persona diga que ya decidió, comprueba el estado con `python3 $P/scripts/comun/fichas.py ver <id>`.
5. Si la persona pide cambios, edita la ficha (sigue en `awaiting_approval`) y vuelve al paso 1. Si la instrucción ya estaba aprobada y hay que cambiar su alcance, devuélvela con `fichas.py estado <id> awaiting_approval` antes de editarla.

## Criterio de salida

- La instrucción está en `instrucciones/en-progreso/` con `status: approved` y `approved_at` puesto por `ciclo.py aprobar`, o
- está en `canceladas/` y el trabajo termina aquí.
