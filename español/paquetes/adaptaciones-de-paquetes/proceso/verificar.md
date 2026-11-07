---
fase: verificar
resuelve: [ajustes-locales-desfasados]
skills: [revisar-ajustes-desfasados]
---

# Fase: verificar

## Objetivo

Demostrar que los ajustes locales son coherentes con los paquetes instalados y comunicar los que necesitan a una persona.

## Entradas

- Las fichas de `ajustes-locales/` y los avisos anotados en las fases anteriores.

## Pasos

1. Ejecuta las verificaciones del paquete: `python3 $P/scripts/comun/verificar.py` y `python3 $P/scripts/verificar-adaptaciones.py`.
2. Cada aviso «cambió desde que se aprobó» o «no está instalado» se trata con la skill `revisar-ajustes-desfasados`: el agente no lo resuelve, lo lleva a la persona.
3. Al cerrar, enumera los ajustes que seguiste «por revisar» y lo que la persona tiene que decidir.

## Criterio de salida

- `verificar-adaptaciones.py` sale con código 0 y cada aviso está comunicado a la persona con su comando.
