---
fase: informar
resuelve: []
skills: [guardar-informe]
---

# Fase: informar

## Objetivo

Entregar a la persona los hallazgos en una tabla con evidencia y, si lo pidió, dejar constancia en el trabajo.

## Entradas

- Los hallazgos de `ejecutar-revisiones`.

## Pasos

1. Si hay que dejar constancia, aplica la skill `guardar-informe` (vuelve a ejecutar las mismas revisiones con `--informe`).
2. Presenta una tabla `# | severidad | revisión: hallazgo | evidencia`, ordenada de mayor a menor severidad. La prosa va solo en las recomendaciones (límite 4).
3. Añade las notas `info` relevantes (paquetes no instalados, humo sin ejecutar) en una línea aparte.

## Criterio de salida

- La persona tiene la tabla y, si se pidió, la ruta de la auditoría o del informe.
