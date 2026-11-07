---
fase: seguir-ajustes
resuelve: [paquetes-sin-adaptar-al-proyecto, ajustes-locales-desfasados]
skills: []
---

# Fase: seguir ajustes

## Objetivo

Trabajar con los paquetes activos siguiendo cada ajuste local por encima del texto original del archivo que sustituye.

## Entradas

- Los ajustes activos de `consultar-ajustes`.

## Pasos

1. Cuando un paquete activo te lleve a un archivo con ajuste (`aplica_a`), aplica lo que dice el ajuste en lugar del paso o la regla que sustituye; el resto del archivo sigue valiendo.
2. Si el ajuste está «por revisar», síguelo igualmente y anótalo para avisar al cerrar. Si contradice lo que ahora dice el paquete, detente y pregunta (`LIMITES.md`).
3. Si está «sin paquete», no hay nada que sustituir: sigue el paquete tal cual y anótalo para la persona.
4. Si descubres un paso que no encaja y no tiene ajuste, no lo cambies tú: sigue a `proponer-ajuste`.

## Criterio de salida

- El trabajo de los paquetes activos se hizo respetando cada ajuste activo, y tienes la lista de ajustes «por revisar» o «sin paquete» que comunicar.
