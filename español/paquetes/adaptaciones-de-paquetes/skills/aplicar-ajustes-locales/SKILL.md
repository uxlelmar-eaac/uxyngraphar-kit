---
name: aplicar-ajustes-locales
description: Imprime los ajustes locales activos de un paquete al activarlo, avisa de los que están por revisar porque el paquete cambió y recuerda si hay reglas del proyecto activas.
resuelve: [paquetes-sin-adaptar-al-proyecto, ajustes-locales-desfasados]
---

# Aplicar ajustes locales

## Cuándo usarla

- Al activar cualquier paquete instalado (el motor lo pide con `al_activar_paquete`).
- En la fase `consultar-ajustes`, para cada paquete activo en la tarea.

## Pasos

1. Ejecuta `python3 $P/scripts/adaptaciones.py ajustes <id-del-paquete>`.
2. Cada ajuste activo sale como `## AJL-… → manda sobre <id>/<archivo>` seguido de su cuerpo. Lo que dice manda sobre ese archivo del paquete, solo en lo que dice.
3. Si la cabecera termina en `(POR REVISAR: por revisar; síguelo y avisa a la persona)`, el archivo del paquete cambió desde la aprobación: síguelo igualmente y avisa al cerrar. Con `(POR REVISAR: sin paquete; …)`, ese archivo ya no existe en el paquete: no hay nada que sustituir, avisa a la persona.
4. La última línea dice cuántos ajustes activos hay (`<id>: N ajustes locales activos`) y, si `reglas-del-proyecto` está instalado con reglas activas, recuerda ejecutar su `reglas.py para <rutas>` antes de tocar código.

## Resultado

- Sabes qué partes del paquete activado sustituye este proyecto y cuáles necesitan revisión de una persona.
