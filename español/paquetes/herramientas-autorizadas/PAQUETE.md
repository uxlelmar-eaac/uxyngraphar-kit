# Herramientas autorizadas

Procedimientos que una persona autorizó para ejecutarse sin instrucción nueva cuando el pedido encaja exactamente en su alcance; el agente solo los usa tal como están escritos y, si ve uno nuevo que convendría, lo propone.

## Qué resuelve

Algunas tareas se repiten con la misma forma (regenerar el cliente de la API, actualizar una traducción, crear una migración vacía) y redactar y aprobar una instrucción completa cada vez es burocracia. Pero un atajo sin control acaba usándose para lo que no era. Este paquete deja que una persona autorice cada procedimiento por escrito, con su alcance cerrado, sus anclas y quién lo autorizó; el agente comprueba el encaje antes de usarlo y nunca convierte en herramienta lo que solo propuso.

## Problemas que cubre

- `procedimientos-repetidos-sin-atajo`: tareas repetitivas que exigen una instrucción completa cada vez.
- `herramientas-usadas-fuera-de-alcance`: herramientas aplicadas a pedidos que no encajan en su alcance, o ya revocadas.
- `autorizaciones-sin-responsable`: herramientas sin constancia de quién y cuándo las autorizó, o creadas por el agente.
- `propuestas-ejecutadas`: procedimientos que el agente ejecuta como herramienta antes de que una persona los promueva.

## Fuera de alcance

- Pedidos que no encajan en ninguna herramienta, incluido escribir o cambiar el script de una herramienta: `instrucciones-aprobadas`.
- Reglas propias del equipo para su código: `reglas-del-proyecto`.
- Mejoras de los paquetes y procesos de uxyngraphar: `evolucion-del-sistema`.
- Credenciales que una herramienta necesite: `secretos-y-credenciales`.
- Ejecución programada o automática fuera de una sesión (cron, CI): no lo cubre el kit.

## Cuándo usarlo

- Al recibir un pedido que podría ser uno de los procedimientos autorizados del proyecto.
- Cuando la persona pide «usa la herramienta …».
- Cuando el agente detecta un procedimiento que se repite y merece proponerse.

## Cuándo no usarlo

- Para tareas únicas o que cambian cada vez: no hay nada que autorizar.
- Para saltarse una instrucción en un cambio de producto que no es un procedimiento fijo.

## Entradas y salidas

- Entradas: el pedido y las fichas `HER-…` vigentes en `uxyngraphar/trabajo/herramientas-autorizadas/autorizadas/`.
- Salidas: los cambios que la herramienta autoriza (solo en sus anclas) o, si se propone una nueva, una ficha `PRO-…` en `propuestas/`.

## Paquetes complementarios

- `instrucciones-aprobadas`: el proceso normal cuando ninguna herramienta encaja; una herramienta autorizada es la excepción a su regla de instrucción previa.
- `revision-humana`: reúne las propuestas `pending` y `en-evaluacion` con el resto de decisiones pendientes.
- `secretos-y-credenciales`: si una herramienta usa credenciales, solo como variables de entorno o placeholders.
