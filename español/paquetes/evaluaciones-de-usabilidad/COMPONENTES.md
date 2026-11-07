# Componentes

Las piezas que define el paquete. Viven en la ficha de evaluación (`plantillas/evaluacion.md`).

## Evaluación

Ficha `UXE-<fecha>-<slug>` en `uxyngraphar/trabajo/evaluaciones-de-usabilidad/<estado>/`. Una por pantalla o flujo. Recorre estos estados:

| Status | Carpeta | Quién lo pone | Significa |
|--------|---------|---------------|-----------|
| `abierta` | `pendientes` | agente | creada, sin alcance cerrado |
| `en-curso` | `en-progreso` | agente | alcance y tareas definidos; evaluando |
| `propuesta` | `en-progreso` | agente | problemas y propuestas listos; espera a la persona |
| `aprobada` | `en-progreso` | persona (`--humano`) | se pueden implementar las filas con «sí» |
| `implementada` | `en-progreso` | agente | filas aprobadas en el código; espera la medición y la validación |
| `validada` | `completadas` | persona (`--humano`) | «Después» medido y aceptado |
| `archivada` / `cancelada` | `archivadas` / `canceladas` | cualquiera | fuera de uso / descartada |

## Tareas del usuario

Lo que el usuario intenta conseguir en las pantallas del alcance («darse de alta», «pagar»). Cada problema y cada métrica se juzgan respecto a ellas.

## Heurística

Código de la causa del problema: `H1`–`H10` (Nielsen), `A11Y` (accesibilidad), `UI` (consistencia visual) o `RENDIMIENTO` (rendimiento percibido). Los admitidos están en el ajuste `heuristicas`. Ver `referencia/heuristicas.md`.

## Severidad

Entero de 0 a `severidad_max` (4): 0 no es problema · 1 cosmético · 2 menor · 3 mayor · 4 catástrofe. Desde `severidad_propuesta_obligatoria` (3) la fila exige propuesta.

## Evidencia

Lo que demuestra el problema: `ruta:línea`, captura, paso reproducible o medición. Sin evidencia es una opinión y va a «Notas».

## Propuesta y aprobación por fila

La propuesta dice qué cambia y dónde. La columna «Aprobada» la rellena la persona con «sí» (o `x`); solo esas filas se implementan.

## Métrica

Fila de «Métricas» con «Antes», «Objetivo», «Después» y «Fuente». «Antes» y «Después» se miden con la misma fuente. Ver `referencia/metricas.md`.
