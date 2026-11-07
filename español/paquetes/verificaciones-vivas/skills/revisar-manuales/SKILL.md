---
name: revisar-manuales
description: Revisa los manuales vigentes, avisa de los que no tienen verificación o la tienen caducada según dias_manual, y de las rutas citadas que no existen.
resuelve: [manuales-sin-verificar]
---

# Revisar manuales

## Cuándo usarla

- La persona pregunta si los manuales operativos siguen valiendo.
- Antes de una guardia, un despliegue o una entrega donde se van a seguir manuales.

## Pasos

1. Ejecuta `python3 $P/scripts/vivas.py manuales` (necesita `manuales-operativos`).
2. Solo se revisan los manuales `vigente`:
   - Sin `ultima_verificacion` válida (`AAAA-MM-DD`) → `media: MAN-…: vigente sin «ultima_verificacion»`.
   - Verificados hace más de `dias_manual` (90 por defecto) → `baja: MAN-…: verificado hace N días (máximo 90)`.
   - Cada ruta citada entre comillas invertidas (con `/`) que no existe → `media: MAN-…: cita «ruta», que no existe`.
3. Verificar un manual de nuevo es trabajo de `manuales-operativos`; aquí solo se informa.

## Resultado

- Los manuales vigentes que necesitan reverificación y las rutas que citan sin existir.
