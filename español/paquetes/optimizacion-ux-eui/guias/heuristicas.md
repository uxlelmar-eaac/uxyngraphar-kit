# Heurísticas (Nielsen) y categorías propias

| Código | Heurística | Pregunta guía |
|--------|------------|---------------|
| H1 | Visibilidad del estado del sistema | ¿El usuario sabe siempre qué pasa (carga, guardado, error)? |
| H2 | Coincidencia con el mundo real | ¿Habla el idioma del usuario, no el del sistema? |
| H3 | Control y libertad | ¿Puede deshacer, cancelar y volver sin perder trabajo? |
| H4 | Consistencia y estándares | ¿Lo mismo se ve y se comporta igual en todas partes? |
| H5 | Prevención de errores | ¿El diseño evita el error antes de tener que avisarlo? |
| H6 | Reconocer antes que recordar | ¿Las opciones están a la vista en lugar de en la memoria? |
| H7 | Flexibilidad y eficiencia | ¿Hay atajos para expertos sin estorbar a novatos? |
| H8 | Diseño estético y minimalista | ¿Cada elemento compite por atención con razón? |
| H9 | Reconocer, diagnosticar y recuperarse de errores | ¿Los errores dicen qué pasó y cómo arreglarlo? |
| H10 | Ayuda y documentación | ¿La ayuda está donde se necesita y es breve? |
| A11Y | Accesibilidad | Ver `accesibilidad.md`. |
| UI | Consistencia visual | Ver `consistencia-ui.md`. |
| RENDIMIENTO | Rendimiento percibido | Ver `metricas.md`. |

## Severidad

| Valor | Significado | Ejemplo |
|-------|-------------|---------|
| 0 | No es un problema de usabilidad | Preferencia estética sin impacto |
| 1 | Cosmético | Alineación irregular de un icono |
| 2 | Menor | Etiqueta ambigua que obliga a dudar |
| 3 | Mayor | El usuario tarda mucho o pide ayuda para completar la tarea |
| 4 | Catástrofe | El usuario no puede completar la tarea o pierde datos |

Pondera frecuencia (¿a cuántos afecta?), impacto (¿cuánto cuesta superarlo?) y persistencia (¿se aprende a evitarlo?).
