---
name: escribir-celda
description: Redacta una celda del mosaico con una sola idea: título-beneficio dentro del límite de palabras, mensaje con una prueba concreta, CTA y medio con texto alternativo.
resuelve: [celdas-sobrecargadas]
---

# Escribir celda

## Cuándo usarla

- En `disenar-mosaico`, una vez por celda.
- Cuando `verificar-bento.py` informa de un título o mensaje demasiado largo o de un medio sin texto alternativo.

## Pasos

1. Título: el beneficio, no la función («Cobra en 2 minutos», no «Módulo de pagos»), en ≤ `palabras_titulo` palabras (6).
2. Mensaje: una prueba o detalle concreto (cifra, ejemplo, testimonio corto) en ≤ `palabras_mensaje` palabras (25). Si necesitas dos ideas, son dos celdas.
3. CTA: `primario` (solo una celda en toda la página), `secundario` o `-`.
4. Medio: `-`, `img: <texto alternativo>`, `video: <descripción>` o `icono` si es decorativo. Una imagen sin alt no entra.
5. Si la celda no comunica nada (solo decora), quítala.

## Resultado

- Una fila del mosaico como `| 1 | 2x2 | 1 | Cobra en 2 minutos | Sin contratos ni permanencia | primario | img: panel de cobros en un móvil |`.
