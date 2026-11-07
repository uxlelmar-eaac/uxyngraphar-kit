# Reglas del proyecto

Da al equipo un sitio para las reglas que solo valen en su proyecto: se escriben como fichas, se comprueban sin IA con expresiones regulares y sus excepciones las aprueba una persona.

## Qué resuelve

Cada equipo tiene convenciones que ningún paquete del catálogo conoce («nada de `console.log` en `src/`», «todo controlador lleva `@ApiTags`») y que hoy dependen de que alguien las recuerde en la revisión. Este paquete convierte esas convenciones en reglas comprobables y obliga a que cada incumplimiento pase por una excepción aprobada por una persona, en lugar de colarse en silencio.

## Problemas que cubre

- `convenciones-sin-comprobar`: convenciones del equipo que no están escritas ni se comprueban.
- `reglas-incumplidas-en-silencio`: código que rompe una regla activa sin excepción aprobada.

## Fuera de alcance

- Límite de líneas y nombres del código: `calidad-de-codigo`.
- Idioma del código y glosario de dominio: `idiomas-del-codigo`.
- Formato de los mensajes de commit y nombres de rama: `mensajes-de-commit`.
- Qué capa o módulo puede importar a cuál: `arquitectura-monolitica-por-capas`.
- Decisiones de arquitectura con contexto y alternativas: `decisiones-de-arquitectura`.
- Adaptar a este proyecto un paso o una regla de otro paquete instalado sin editarlo (ajustes locales `AJL-…`): `adaptaciones-de-paquetes`.
- Cambiar un paquete del catálogo para todos los proyectos: `evolucion-del-sistema`.
- Análisis estático que no cabe en una expresión regular (tipos, flujo de datos): no lo cubre el kit.

## Cuándo usarlo

- Antes de tocar código en un proyecto con reglas activas (`reglas.py para <rutas>`).
- Cuando la persona quiere fijar una convención nueva o retirar una.
- Cuando una regla impide cumplir un pedido y hace falta una excepción.

## Cuándo no usarlo

- Para reglas que valen para cualquier proyecto: van al catálogo, como paquete o como mejora de uno.
- Para registrar decisiones con alternativas y consecuencias: eso es una ADR.
- Para cambiar cómo trabaja otro paquete en este proyecto: eso es un ajuste local de `adaptaciones-de-paquetes`.

## Entradas y salidas

- Entradas: las fichas de `uxyngraphar/trabajo/reglas-del-proyecto/{reglas,excepciones}/` y el código bajo `raices` (o lo cambiado según git).
- Salidas: fichas nuevas en estado `propuesta` o `pendiente`; el informe de `reglas.py comprobar` (`archivo: regla [nivel] motivo`); la lista de reglas que tocan unas rutas (`reglas.py para`).

## Paquetes complementarios

- `calidad-de-codigo`, `idiomas-del-codigo` y `mensajes-de-commit`: las convenciones generales que no hace falta reescribir como reglas.
- `adaptaciones-de-paquetes`: los ajustes locales de otros paquetes; al activar un paquete, su `adaptaciones.py ajustes` recuerda cuántas reglas de este paquete están activas.
- `decisiones-de-arquitectura`: la ADR cuando una regla nace de una decisión de arquitectura.
- `instrucciones-aprobadas`: las anclas de cada instrucción son las rutas que se pasan a `reglas.py para`.
