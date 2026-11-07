# Auditorías técnicas

Convierte «investiga por qué…» en una investigación acotada y repetible: alcance y preguntas antes de empezar, hallazgos con evidencia y severidad, y resultados que se promueven a otros paquetes en lugar de aplicarse sobre la marcha.

## Qué resuelve

Las investigaciones técnicas (rendimiento, una dependencia, un módulo heredado, un incidente) tienden a no tener final, a mezclar hechos con opiniones y a terminar en arreglos que nadie aprobó. Este paquete abre una ficha con alcance, preguntas y método; registra cada hallazgo en una tabla con severidad (`critica`…`info`) y evidencia reproducible; mantiene a raya el número de auditorías activas y avisa de las que se estancan; y obliga a cerrar con conclusiones y promociones propuestas (ADR, instrucción, mejora, documentación) que decide una persona. `verificar-auditorias.py` comprueba la tabla y el contador de hallazgos.

## Problemas que cubre

- `investigaciones-sin-alcance`: investigaciones sin alcance ni preguntas que no terminan nunca.
- `hallazgos-sin-evidencia`: hallazgos sin evidencia reproducible ni severidad.
- `auditorias-que-modifican-codigo`: auditorías que arreglan sobre la marcha sin decisión de una persona.
- `auditorias-abandonadas`: demasiadas activas o activas estancadas durante semanas.
- `conclusiones-sin-seguimiento`: conclusiones que no se convierten en ninguna acción registrada.

## Fuera de alcance

- Implementar las correcciones recomendadas: `instrucciones-aprobadas`.
- Registrar la decisión técnica que surge de una auditoría: `decisiones-de-arquitectura`.
- Anotar deuda o bugs sueltos vistos durante otra tarea: `deuda-y-mejoras`.
- Contrastar automáticamente documentación y código: `verificaciones-vivas` (que puede guardar su resultado como auditoría de este paquete).
- Evaluar la usabilidad de la interfaz: `evaluaciones-de-usabilidad`.
- Revisar la accesibilidad de la interfaz: `pautas-de-accesibilidad`.
- Escanear credenciales y secretos: `secretos-y-credenciales`.

## Cuándo usarlo

- Cuando la persona pide investigar una causa («por qué la API tarda 3 s en el listado»), evaluar una dependencia o revisar un módulo antes de tocarlo.
- Tras un incidente, para reunir hechos antes de decidir.
- Para dar una segunda opinión documentada sobre una parte del sistema.

## Cuándo no usarlo

- Si la causa ya se conoce y solo falta arreglarla.
- Para anotar un problema visto de pasada: `deuda-y-mejoras`.
- Como diario de trabajo o memoria del proyecto.

## Entradas y salidas

- Entradas: la pregunta de la persona, el código, los registros y las mediciones que se puedan obtener, y los ajustes de `uxyngraphar/trabajo/auditorias-tecnicas/ajustes.json`.
- Salidas: una ficha `AUD-…` en `uxyngraphar/trabajo/auditorias-tecnicas/<estado>/` con alcance, preguntas, método, hallazgos, conclusiones, recomendaciones y promociones; y, si la persona acepta alguna, la ficha creada en el paquete destino citando la auditoría.

## Paquetes complementarios

- `decisiones-de-arquitectura`, `instrucciones-aprobadas`, `deuda-y-mejoras`: destinos habituales de las promociones.
- `verificaciones-vivas`: guarda sus resultados como auditorías.
- `documentos-archivados`: archivo histórico de las auditorías retiradas.
