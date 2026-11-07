---
fase: ejecutar-revisiones
resuelve: [fichas-desalineadas-del-codigo, referencias-rotas, decisiones-incumplidas, manuales-sin-verificar, flujos-basicos-rotos]
skills: [contrastar-inventario, revisar-referencias, comprobar-decisiones, revisar-manuales, ejecutar-humo]
---

# Fase: ejecutar revisiones

## Objetivo

Obtener la lista completa de hallazgos de las revisiones elegidas, sin modificar nada.

## Entradas

- Las revisiones elegidas en `acotar-revision`.

## Pasos

1. Ejecuta las revisiones de una vez: `python3 $P/scripts/vivas.py <revisión>…` (sin revisiones: todas menos `humo`).
2. Interpreta cada grupo con su skill: `contrastar-inventario` (`rutas`, `paginas`), `revisar-referencias` (`anclas`, `vinculos`), `comprobar-decisiones` (`decisiones`), `revisar-manuales` (`manuales`) y `ejecutar-humo` (`humo`).
3. Separa las notas `info` (no cuentan) de los hallazgos.
4. Si un tipo de hallazgo se repite cientos de veces, para y vuelve a `acotar-revision`: falta un ajuste.
5. No corrijas nada aunque la corrección sea obvia (límite 1).

## Criterio de salida

- Tienes los hallazgos de cada revisión con su severidad y evidencia, y sabes cuáles son ruido de configuración.
