---
name: comprobar-incumplimientos
description: Evalúa sin IA las reglas activas con comprobación (regex prohibida u obligatoria) sobre lo cambiado o unas rutas, y separa lo bloqueante de lo excusado por una excepción aprobada.
resuelve: [reglas-incumplidas-en-silencio, convenciones-sin-comprobar]
---

# Comprobar incumplimientos

## Cuándo usarla

- En la fase `verificar`, sobre lo que cambiaste.
- Cuando la persona activa una regla nueva y quiere saber cuánto código la incumple.

## Pasos

1. Lo cambiado según git (modificado, preparado y sin seguimiento): `python3 $P/scripts/reglas.py comprobar --git`. Unas rutas: `python3 $P/scripts/reglas.py comprobar <ruta>…`. Sin argumentos: todas las `raices` salvo `excluir` y los archivos de más de `max_kb`.
2. Cada línea es `archivo: REG-… [nivel] motivo`, con `[excepción aprobada]` en lugar del nivel si una excepción vigente lo excusa. El motivo es `línea N contiene lo prohibido (…)` o `falta lo obligatorio (…)`.
3. La última línea resume: `reglas del proyecto: N incumplimientos, M bloqueantes`. Código 1 si hay algún bloqueante sin excusar.
4. Bloqueante en tu archivo → corrige el código o, si no se puede, `proponer-excepcion`. Aviso → menciónalo al cerrar.
5. Una excepción con `hasta` vencido deja de excusar: el incumplimiento vuelve a contar.

## Resultado

- Lista de incumplimientos de lo revisado, separados en bloqueantes, avisos y excusados.
