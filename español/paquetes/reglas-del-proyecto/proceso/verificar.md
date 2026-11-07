---
fase: verificar
resuelve: [reglas-incumplidas-en-silencio, convenciones-sin-comprobar]
skills: [comprobar-incumplimientos]
---

# Fase: verificar

## Objetivo

Demostrar que lo cambiado no incumple ninguna regla activa sin excepción y que las fichas del paquete son coherentes.

## Entradas

- Los archivos cambiados (según git o la lista de la tarea).
- Las excepciones propuestas en `implementar`.

## Pasos

1. Aplica la skill `comprobar-incumplimientos` sobre lo cambiado (`reglas.py comprobar --git`).
2. Todo incumplimiento `bloqueante` en tus archivos se corrige ahora, salvo que tenga una excepción aprobada; los de archivos que no tocaste se mencionan, no se corrigen.
3. Ejecuta las verificaciones del paquete: `python3 $P/scripts/comun/verificar.py` y `python3 $P/scripts/verificar-reglas.py`.
4. Lee sus avisos: una excepción aprobada sin `aprobada_por` o una regla propuesta con regex inválida se comunican a la persona al cerrar.

## Criterio de salida

- `reglas.py comprobar --git` sale con código 0, o los únicos bloqueantes son de archivos que no tocaste.
- `verificar-reglas.py` sin errores atribuibles a tu cambio; avisos comunicados.
