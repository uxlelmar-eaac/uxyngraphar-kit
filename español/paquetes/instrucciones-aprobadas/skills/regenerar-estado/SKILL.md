---
name: regenerar-estado
description: Regenera el bloque de ESTADO.md (última instrucción cerrada, las que están en curso, las que esperan aprobación y el coste de contexto) sin tocar las notas de la persona.
resuelve: [cierre-sin-rastro, contexto-excesivo]
---

# Regenerar estado

## Cuándo usarla

- Al entrar en una sesión, si `ESTADO.md` no existe o parece desfasado.
- Tras mover fichas con `fichas.py estado` (cancelar, archivar), que no regenera el estado; `ciclo.py cerrar` ya lo hace solo.

## Pasos

1. Ejecuta `python3 $P/scripts/ciclo.py estado`. Escribe `uxyngraphar/trabajo/instrucciones-aprobadas/ESTADO.md` y reemplaza solo lo que hay entre `<!-- uxyngraphar:estado -->` y `<!-- /uxyngraphar:estado -->`.
2. Lee la tabla: «Última cerrada», «En curso (approved)», «Esperando aprobación» y las tres últimas cerradas con sus `tokens_contexto`.
3. Si los tokens de las últimas cerradas crecen mucho, la próxima instrucción debe ser más pequeña: anótalo al redactarla.
4. No edites el bloque a mano; lo que la persona escriba debajo de «## Notas» se conserva.

## Resultado

- `ESTADO.md` al día, la única lectura de orientación permitida al empezar.
