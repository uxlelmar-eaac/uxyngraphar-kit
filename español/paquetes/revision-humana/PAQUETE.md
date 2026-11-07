# Revisión humana

Una sola hoja con todo lo que espera una decisión de una persona en los paquetes instalados, de lo más antiguo a lo más nuevo, y una sola orden de la persona para aplicar lo que decida con las comprobaciones de cada paquete.

## Qué resuelve

Cada paquete que pide una decisión humana (aprobar una instrucción, aceptar una ADR, promover una herramienta, activar una regla) la deja en su propia carpeta. Con varios paquetes instalados, las decisiones se pierden: unas envejecen sin que nadie las vea, otras se aplican a mano saltándose las comprobaciones y otras siguen «pendientes» cuando su efecto ya está en el código. Este paquete las reúne, las ordena por antigüedad, resume cada una y aplica las decisiones con el comando de su paquete.

## Problemas que cubre

- `decisiones-dispersas`: las fichas que esperan a una persona están repartidas y nadie ve el conjunto.
- `pendientes-envejecidos`: fichas que llevan semanas esperando sin decidirse ni cerrarse.
- `status-desfasado`: fichas que dicen esperar una decisión cuando su efecto ya está aplicado.
- `decisiones-aplicadas-a-mano`: decisiones aplicadas moviendo fichas o editando su status, sin las comprobaciones del paquete dueño.

## Fuera de alcance

- Redactar o corregir una instrucción antes de aprobarla: `instrucciones-aprobadas`.
- Preguntar a la persona lo que decide el resultado antes de redactar o cambiar nada: `preguntas-de-clarificacion`.
- Redactar una ADR o decidir entre sus opciones: `decisiones-de-arquitectura`.
- Priorizar y planificar la cola de deuda y mejoras: `deuda-y-mejoras`.
- Fichas de paquetes no instalados o de otros repositorios: no lo cubre el kit.
- Avisos fuera del repositorio (correo, chat, calendario): no lo cubre el kit.

## Cuándo usarlo

- En una revisión periódica (semanal, antes de una planificación) de lo que espera a la persona.
- Cuando la persona pregunta «¿qué tengo pendiente de decidir?».
- Cuando `verificar-revision.py` avisa de fichas antiguas.

## Cuándo no usarlo

- Para decidir una sola ficha que la persona ya tiene delante: basta el comando de su paquete.
- Con un único paquete instalado que pide decisiones: su propio listado (`fichas.py listar`) es suficiente.

## Entradas y salidas

- Entradas: los manifiestos de los paquetes instalados (`fichas`, `solo_humano`, `espera_humano`, `comandos`), sus fichas en `uxyngraphar/trabajo/` y `dias_aviso` en `uxyngraphar/trabajo/revision-humana/ajustes.json`.
- Salidas: `uxyngraphar/trabajo/revision-humana/REVISION.md`, un resumen por pendiente en el chat y, tras `aplicar` de la persona, las fichas movidas por los comandos de sus paquetes.

## Paquetes complementarios

- `instrucciones-aprobadas`: su `awaiting_approval` es el pendiente más habitual; se aprueba con `ciclo.py aprobar`.
- `decisiones-de-arquitectura`: ADR en `propuesta` y `en-evaluacion`.
- `herramientas-autorizadas`: propuestas de herramienta por promover.
- `reglas-del-proyecto` y `evolucion-del-sistema`: reglas, excepciones y mejoras del sistema que esperan a la persona.
- `adaptaciones-de-paquetes`: ajustes locales `AJL-…` en `propuesto`; se activan con `adaptaciones.py aprobar-ajuste`.
- `evaluaciones-de-usabilidad`: evaluaciones `UXE-…` en `propuesta` o `implementada`.
