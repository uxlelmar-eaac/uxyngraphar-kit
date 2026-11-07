---
name: registrar-mejora
description: Crea una ficha MEJ con fichas.py y la rellena con contexto, evidencia, problema, mejora propuesta e impacto, clasificada por tipo, severidad y prioridad.
resuelve: [deuda-detectada-sin-registro, mejoras-sin-evidencia]
---

# Registrar mejora

## Cuándo usarla

- En la fase `registrar`, cuando no hay ficha previa del problema.
- Cuando otro paquete pide registrar algo heredado como deuda.

## Pasos

1. Crea la ficha: `python3 $P/scripts/comun/fichas.py nueva mejora --slug <slug> --titulo "…"`. Nace `pending` en `uxyngraphar/trabajo/deuda-y-mejoras/pendientes/`.
2. Frontmatter: `tipo` (`bug`, `deuda-tecnica`, `rendimiento`, `seguridad`, `dx`), `severidad` (`critica`, `alta`, `media`, `baja`), `prioridad` propuesta (`ahora`, `pronto`, `despues`), `areas` y, si hay una instrucción en curso, `related_instruction`.
3. «Contexto detectado»: durante qué tarea y cómo lo viste, en 1–3 frases.
4. «Evidencia»: una o más líneas `` `ruta:línea` — qué se observó ``, salida de comando o pasos para reproducir.
5. «Problema», «Mejora propuesta» (sin implementarla) e «Impacto si no se hace».
6. Deja la línea «No implementar hasta que una persona la apruebe».

## Resultado

- Ficha `MEJ-<fecha>-<slug>` en `pendientes/`, completa y clasificada.
