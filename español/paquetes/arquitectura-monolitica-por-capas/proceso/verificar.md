---
fase: verificar
resuelve: [capas-mal-importadas, modulos-acoplados, comun-dependiente-del-negocio]
skills: [revisar-imports]
---

# Fase: verificar

## Objetivo

Demostrar que el cambio no introdujo infracciones y dejar registradas las heredadas que se vieron.

## Entradas

- Las rutas tocadas.
- La lista de infracciones previas de `diagnosticar`.

## Pasos

1. Aplica la skill `revisar-imports` sobre las rutas tocadas.
2. Compara con la lista previa: toda infracción nueva se corrige ahora (vuelve a `implementar`).
3. Las heredadas que no pidió la persona no se tocan: si está instalado `deuda-y-mejoras`, regístralas allí; si no, menciónalas al cerrar.
4. Ejecuta las verificaciones del paquete: `python3 $P/scripts/comun/verificar.py` y `python3 $P/scripts/verificar-capas.py`.

## Criterio de salida

- Cero infracciones nuevas en las rutas tocadas.
- Verificaciones sin errores (con `nivel: aviso`, los avisos heredados no cuentan como error).
