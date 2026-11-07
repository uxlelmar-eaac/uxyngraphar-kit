---
fase: comprobar-decisiones
resuelve: [decisiones-aplicadas-a-mano, pendientes-envejecidos]
skills: []
---

# Fase: comprobar-decisiones

Solo si la persona ya ejecutó `revision.py aplicar --humano` y pide que se compruebe el resultado.

## Objetivo

Confirmar que cada decisión quedó aplicada por el comando de su paquete y explicar las que fallaron.

## Entradas

- La salida de `aplicar` que comparta la persona: una línea `<id> → <decisión>: hecho|FALLÓ <motivo>` por decisión.
- `REVISION.md`, que `aplicar` regenera al terminar con lo que sigue pendiente.

## Pasos

1. Ejecuta `python3 $P/scripts/revision.py pendientes`: las fichas decididas ya no deben aparecer; las pospuestas sí.
2. Para cada `FALLÓ`, explica el motivo que dio el comando del paquete (por ejemplo, `no se puede aprobar: 7 archivos de código en anclas`) y qué paquete debe corregir la ficha. Una decisión que no está entre las «Opciones» sale como «no es una opción».
3. Una fila que salió como `ya no espera decisión (se omite)` cambió de status entre `preparar` y `aplicar`: comprueba que fue intencionado.
4. Ejecuta `python3 $P/scripts/comun/verificar.py` y `python3 $P/scripts/verificar-revision.py`.

## Criterio de salida

- Ninguna ficha decidida sigue como pendiente; los fallos están explicados con el paquete que debe corregirlos.
- Las verificaciones terminan sin errores.
