---
fase: proponer-cambios
resuelve: [convenciones-sin-comprobar, reglas-incumplidas-en-silencio]
skills: [proponer-regla, proponer-excepcion]
---

# Fase: proponer cambios

Solo si el pedido es fijar, cambiar o retirar una regla, o pedir una excepción fuera de una implementación. Si no, esta fase no se recorre.

## Objetivo

Dejar la propuesta escrita y lista para que una persona la active, sin que el agente active nada.

## Entradas

- Lo que la persona quiere fijar, con un ejemplo correcto y uno incorrecto.
- Para una excepción: la regla, los archivos y el plazo.

## Pasos

1. Convención del código → skill `proponer-regla`. Si sustituye a una regla activa, la nueva lleva `reemplaza: REG-…`.
2. Excepción a una regla activa → skill `proponer-excepcion`.
3. Regla que ya no hace falta → propón a la persona retirarla (`fichas.py estado REG-… retirada --humano`).
4. Si lo que no encaja es un paso de otro paquete instalado, no es una regla: deriva a `adaptaciones-de-paquetes`.
5. Ejecuta `python3 $P/scripts/verificar-reglas.py`: una regla propuesta con regex inválida sale como aviso; corrígela antes de entregar.
6. Di a la persona exactamente qué comando la activa (sección «Lo que decide la persona» del README).

## Criterio de salida

- La ficha existe en estado `propuesta` o `pendiente`, sin avisos de `verificar-reglas.py`, y la persona sabe qué tiene que decidir.
