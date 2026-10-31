---
id: auto.04.decisiones-vinculantes
stack: [cliente]
---

# 04: decisiones-vinculantes

## Fuente

`00-nucleo/ciclo-vinculante.md` y `20-decisiones/` (estados
`02-en-progreso` y `03-completadas`).

## Valida

Que el código respeta las decisiones activas, incluidas las prohibiciones
explícitas (lo vetado no aparece).

## Procedimiento

1. Extraer de cada decisión activa su regla verificable y su
   prohibición (patrón de código, dependencia, ruta, práctica).
2. Buscar cada patrón/prohibición en el árbol de código.

## Aceptación

- [ ] Cero apariciones de patrones prohibidos por decisiones activas.
- [ ] Cada decisión activa tiene al menos una evidencia de cumplimiento
  o queda marcada como `sin-evidencia`.

## Salida

Lista: `decisión (id) | cumple / viola / sin-evidencia | evidencia`.


> **Implementación (desde 1.0.0):** la verificación de que el núcleo no se edita sin EVO aprobada la realiza `scripts/verificar-nucleo.py`.
