---
name: revisar-imports
description: Lista los imports que rompen las capas, los cruces entre módulos o la independencia de lo común en unas rutas, y separa los nuevos de los heredados.
resuelve: [capas-mal-importadas, modulos-acoplados, comun-dependiente-del-negocio]
---

# Revisar imports

## Cuándo usarla

- Al empezar (fase `diagnosticar`) y al terminar (fase `verificar`) un cambio.
- Cuando la persona pide una revisión de arquitectura de una parte del código.

## Pasos

1. Ejecuta `python3 $P/scripts/capas.py revisar <rutas>` (sin rutas revisa todo el código de `raices`).
2. Cada línea es `archivo:línea: motivo (importa destino)`. Agrúpalas por motivo: capa no permitida, cruce de módulo o común que importa negocio.
3. Si es la revisión final, compara con la inicial: las nuevas son tuyas y se corrigen; las heredadas se registran como deuda.
4. Si hay muchas infracciones en un proyecto que adopta el perfil, no las corrijas todas: resume por módulo y propón tandas.

## Resultado

- Lista de infracciones de las rutas revisadas, separadas en nuevas y heredadas.
