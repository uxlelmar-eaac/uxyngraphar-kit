---
name: medir-metrica
description: Registra o completa una fila de «Métricas» (Antes, Objetivo, Después, Fuente) de forma que la medición se pueda repetir con la misma fuente.
resuelve: [mejoras-sin-medicion]
---

# Medir métrica

## Cuándo usarla

- En `evaluar`, para medir «Antes» y fijar el objetivo.
- En `medir-resultado`, para medir «Después».

## Pasos

1. Elige métricas que respondan a las tareas del usuario (`referencia/metricas.md`): pasos para completar la tarea, LCP, INP, CLS, puntuación de accesibilidad, tasa de éxito, tiempo o errores por tarea.
2. Anota la fuente con detalle suficiente para repetirla: herramienta, dispositivo o emulación, red simulada, muestra («Lighthouse móvil, 4G lenta, 3 ejecuciones, mediana»; «conteo manual del flujo desde /signup»).
3. «Antes»: mide y escribe el valor; «Objetivo»: el umbral de `referencia/metricas.md` o una mejora concreta acordada.
4. «Después»: misma fuente y condiciones que «Antes». Si no es posible, dilo en «Notas» y no compares.
5. Formato de la fila: `| Pasos del alta | 7 | 4 | 4 | conteo manual desde /signup |`.

## Resultado

- Una métrica que `verificar-evaluaciones.py` acepta: «Antes», «Objetivo» y «Fuente» siempre; «Después» antes de `validada`.
