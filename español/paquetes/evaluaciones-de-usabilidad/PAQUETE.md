# Evaluaciones de usabilidad

Convierte las mejoras de interfaz en un ciclo comprobable: se evalúa con heurísticas y evidencia, una persona aprueba qué se cambia, se implementa solo eso y se mide si mejoró.

## Qué resuelve

Las discusiones sobre interfaz suelen ser opiniones («este botón no se ve bien») y los cambios se hacen sin saber si mejoraron algo. Este paquete obliga a acotar pantallas y tareas del usuario, a registrar cada problema con una heurística (Nielsen `H1`–`H10`, `A11Y`, `UI`, `RENDIMIENTO`), una severidad 0–4 y una evidencia, a proponer antes de tocar, a esperar la aprobación de una persona y a medir antes y después con la misma fuente. Todo queda en una ficha de evaluación que `verificar-evaluaciones.py` comprueba.

## Problemas que cubre

- `problemas-de-usabilidad-sin-evidencia`: problemas discutidos como opiniones, sin heurística, severidad ni evidencia.
- `cambios-de-interfaz-sin-aprobacion`: cambios de interfaz hechos sin evaluación ni propuesta aprobada, o más allá de lo aprobado.
- `mejoras-sin-medicion`: mejoras sin métrica antes/después, o con regresiones que nadie ve.

## Fuera de alcance

- Revisar a fondo una interfaz contra WCAG 2.2 AA: `pautas-de-accesibilidad`. Aquí un problema de accesibilidad evidente se registra con `A11Y`, sin auditoría completa.
- Revisar que las pantallas reutilicen tokens y componentes y cubran todos sus estados: `componentes-de-interfaz`. Aquí una inconsistencia que estorba la tarea se registra con `UI`.
- Diseñar y construir páginas de aterrizaje con mosaico bento: `paginas-de-aterrizaje-bento`.
- La ficha viva de cada página o ruta de la interfaz: `paginas-de-interfaz`.
- Bugs y deuda detectados fuera del alcance de la evaluación: `deuda-y-mejoras`.
- Investigar a fondo el rendimiento del servidor, la base de datos o la infraestructura: `auditorias-tecnicas`.
- Investigación con usuarios (reclutamiento, entrevistas, pruebas moderadas): no lo cubre el kit; sus resultados sí pueden ser evidencia y fuente de métricas.

## Cuándo usarlo

- Cuando la persona pide «mejorar la UX» de una pantalla o un flujo concreto.
- Antes de rediseñar un formulario, un proceso de compra, un alta o cualquier flujo con una tarea clara del usuario.
- Para comprobar con datos si una mejora ya implementada funcionó.

## Cuándo no usarlo

- Para un bug visual puntual con causa clara (un margen roto): basta corregirlo con el flujo habitual del proyecto.
- Para crear una pantalla nueva desde cero sin versión anterior que evaluar.
- Para decisiones de marca o de estilo sin tarea del usuario detrás.
- Para una revisión solo de accesibilidad o solo de consistencia visual: `pautas-de-accesibilidad` o `componentes-de-interfaz`.

## Entradas y salidas

- Entradas: las pantallas o flujos del pedido (código, capturas o la app en marcha), las tareas del usuario y los ajustes de `uxyngraphar/trabajo/evaluaciones-de-usabilidad/ajustes.json`.
- Salidas: una ficha `UXE-…` en `uxyngraphar/trabajo/evaluaciones-de-usabilidad/<estado>/` con alcance, tareas, problemas, propuestas, métricas antes/después y lo implementado; y, tras la aprobación, los cambios de interfaz aprobados en el código.

## Paquetes complementarios

- `pautas-de-accesibilidad`: si está instalado, sus hallazgos sobre las pantallas evaluadas se registran aquí como filas `A11Y`.
- `componentes-de-interfaz`: si está instalado, sus hallazgos se registran aquí como filas `UI`, y la implementación sigue sus límites de tokens y estados.
- `paginas-de-interfaz`: la ficha de cada página que la evaluación toca se actualiza allí.
- `deuda-y-mejoras`: lo que se detecta fuera del alcance de la evaluación.
- `revision-humana`: recoge las evaluaciones en `propuesta` e `implementada` que esperan a una persona.
- `instrucciones-aprobadas`: si el proyecto exige instrucción aprobada para tocar código, la implementación cita la evaluación aprobada.
