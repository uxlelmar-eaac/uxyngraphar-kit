# Deuda y mejoras

Mantiene una cola de deuda técnica y bugs detectados fuera del alcance de cada tarea: se registran con evidencia, sin duplicados y clasificados, y no se tocan hasta que una persona los aprueba.

## Qué resuelve

Al trabajar en una tarea se ven cosas que están mal: una consulta lenta, un bug en otro módulo, código duplicado. Si el agente las arregla, el cambio crece sin control y sin aprobación; si no las anota, se pierden. Este paquete da el punto intermedio: una ficha por problema con evidencia, tipo, severidad y prioridad propuesta, un límite de fichas nuevas por tarea para no inundar la cola, y una regla dura: no se implementa nada que una persona no haya aprobado.

## Problemas que cubre

- `deuda-detectada-sin-registro`: deuda y bugs vistos durante una tarea que se olvidan.
- `arreglos-fuera-de-alcance`: arreglos sobre la marcha que amplían el cambio sin aprobación.
- `mejoras-sin-evidencia`: mejoras anotadas sin evidencia que nadie puede valorar.
- `cola-de-mejoras-inmanejable`: duplicados, fichas sin clasificar o demasiadas fichas por tarea.

## Fuera de alcance

- Mejoras del propio sistema uxyngraphar: `evolucion-del-sistema`.
- Investigar a fondo una causa: `auditorias-tecnicas`.
- Implementar una mejora aprobada con alcance y anclas de código: `instrucciones-aprobadas`.
- Decidir un cambio de arquitectura que una mejora pone sobre la mesa: `decisiones-de-arquitectura`.
- Gestionar el backlog de producto (funcionalidades nuevas, hoja de ruta): no lo cubre el kit.

## Cuándo usarlo

- Durante cualquier tarea, cuando aparece un problema que no es parte del pedido.
- Cuando la persona pide repasar la deuda pendiente o elegir qué aprobar.
- Cuando otro paquete manda registrar lo heredado (por ejemplo, infracciones de capas que ya existían).

## Cuándo no usarlo

- Para lo que sí es parte del pedido: se resuelve en la tarea.
- Para funcionalidades nuevas o peticiones de producto.
- Para lo que falla en un paquete de uxyngraphar: es una EVO de `evolucion-del-sistema`.

## Entradas y salidas

- Entradas: el problema observado y su evidencia (`ruta:línea`, salida de un comando, pasos), las fichas ya registradas y el ajuste `max_por_tarea`.
- Salidas: fichas `MEJ-…` en `uxyngraphar/trabajo/deuda-y-mejoras/<estado>/` (`pendientes/` al nacer) con contexto, evidencia, problema, mejora propuesta e impacto; y, solo con `approved`, la mejora implementada y la ficha en `done`.

## Paquetes complementarios

- `instrucciones-aprobadas`: si el proyecto lo usa, una mejora aprobada se implementa mediante una instrucción que la cite.
- `revision-humana`: recoge las mejoras `pending` que esperan decisión.
- `auditorias-tecnicas`: cuando una mejora necesita investigación antes de decidir, y como origen de mejoras promovidas.
- `arquitectura-monolitica-por-capas`: registra aquí las infracciones heredadas.
