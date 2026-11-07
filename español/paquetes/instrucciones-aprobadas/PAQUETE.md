# Instrucciones aprobadas

Ningún cambio en el producto sin una instrucción escrita y aprobada por una persona: el agente redacta el alcance con sus anclas de código, lee solo lo aprobado, implementa dentro de esas anclas y cierra dejando rastro.

## Qué resuelve

Un agente con acceso al repositorio tiende a hacer de más: toca archivos que nadie mencionó, arregla de paso lo que ve y lee medio proyecto para un cambio de diez líneas. Este paquete convierte cada pedido en un contrato pequeño y explícito (la instrucción) que una persona aprueba antes de que se edite nada, y que limita qué se lee, qué se toca y cómo se cierra.

## Problemas que cubre

- `cambios-sin-aprobacion`: ediciones de código o documentación sin una instrucción aprobada por una persona.
- `alcance-desbordado`: tareas que crecen en número de archivos o salen de sus anclas.
- `contexto-excesivo`: exploración del repositorio y relecturas que no hacen falta para la tarea.
- `cierre-sin-rastro`: tareas terminadas sin criterios marcados, sin fecha de cierre ni estado para retomar.

## Fuera de alcance

- Preguntar y registrar las decisiones de la persona antes de redactar la instrucción: `preguntas-de-clarificacion` (aquí solo se cita su ficha en `preguntas_id` y se copia la síntesis en «Clarificación»).
- Decisiones técnicas caras de revertir (framework, base de datos, patrón transversal): `decisiones-de-arquitectura`.
- La cola de deuda y bugs detectados fuera de alcance: `deuda-y-mejoras` (aquí solo se anotan en la instrucción).
- Procedimientos repetibles que se ejecutan sin instrucción nueva: `herramientas-autorizadas`.
- Revisar de una vez las decisiones pendientes de todos los paquetes: `revision-humana`.
- Notas de memoria del proyecto más allá de `ESTADO.md`: `notas-de-memoria`.
- Archivo histórico de los documentos retirados: `documentos-archivados`.

## Cuándo usarlo

- En cualquier pedido que cambie código o documentación del producto, como paquete base del proyecto (`trabajar_con` en `FLUJO.json`).
- Al adoptar uxyngraphar en un repositorio (variante `adopcion`).
- Cuando la persona quiere controlar qué toca el agente y cuánto contexto gasta.

## Cuándo no usarlo

- En preguntas de solo lectura que no cambian nada (explicar un módulo, localizar un error sin corregirlo).
- Cuando el pedido encaja en una herramienta autorizada vigente: se usa `herramientas-autorizadas`.
- En prototipos desechables donde la persona prefiere iterar sin aprobaciones.

## Entradas y salidas

- Entradas: el pedido de la persona, los ajustes en `uxyngraphar/trabajo/instrucciones-aprobadas/ajustes.json` (`max_archivos_codigo`, `max_docs`, `ampliacion_factor_max`, `max_tokens_contexto`), para orientarse `ESTADO.md` y, si existe, la ficha `PRE-…` de `uxyngraphar/trabajo/preguntas-de-clarificacion/`.
- Salidas: fichas `INS-…` en `instrucciones/` con su estado según la carpeta, el cambio implementado solo en las anclas aprobadas y `ESTADO.md` regenerado al cerrar.

## Paquetes complementarios

- `preguntas-de-clarificacion`: las decisiones de la persona antes de redactar; la instrucción las cita en `preguntas_id` y `verificar-ciclo.py` avisa si la ficha citada no existe o sigue abierta (solo cuando su carpeta de trabajo existe).
- `revision-humana`: reúne las instrucciones en `awaiting_approval` con el resto de decisiones pendientes y las aprueba con `ciclo.py aprobar`.
- `deuda-y-mejoras`: recibe lo anotado en «Fuera de alcance».
- `herramientas-autorizadas`: atajo para pedidos repetidos que no necesitan instrucción nueva.
- `decisiones-de-arquitectura`: la ADR que una instrucción necesita cuando el cambio es estructural.
