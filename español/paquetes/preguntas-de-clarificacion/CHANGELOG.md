# Cambios

## 1.0.0

- Primera versión, nacida de la división de `instrucciones-aprobadas` 1.1.0 (que pasa a 2.0.0): se lleva el problema `decisiones-supuestas`, el tipo de ficha `pregunta` (prefijo `PRE`, carpeta `preguntas/`, status `en-curso`, `completada` y `cancelada`, plantilla `plantillas/pregunta.md` sin cambios), la fase `preguntar`, la skill `registrar-pregunta`, `referencia/preguntas.md` y el ajuste `preguntas`.
- El trabajo pasa de `uxyngraphar/trabajo/instrucciones-aprobadas/preguntas/` a `uxyngraphar/trabajo/preguntas-de-clarificacion/preguntas/`.
- Nuevo: fase `cerrar-pregunta`, skill `enlazar-pregunta`, `LIMITES.md`, `COMPONENTES.md`, `HERRAMIENTAS.md`, un ejemplo resuelto, el ajuste `dias_en_curso` y `verificar-preguntas.py` (decisiones sin elegir o síntesis vacía en las completadas; preguntas estancadas; instrucción enlazada inexistente, solo si existe el trabajo de `instrucciones-aprobadas`), con pruebas propias.
- No depende de `instrucciones-aprobadas`: funciona solo y colabora con él leyendo su carpeta de trabajo si existe.
