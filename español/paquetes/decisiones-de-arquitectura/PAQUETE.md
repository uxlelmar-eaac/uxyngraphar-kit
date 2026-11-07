# Decisiones de arquitectura

Cada decisión técnica cara de revertir queda registrada en una ADR con su contexto, opciones comparadas y consecuencias; la acepta o la rechaza una persona, y una vez aceptada solo se cambia reemplazándola.

## Qué resuelve

Las decisiones que más condicionan un sistema (base de datos, framework, protocolo, modelo de seguridad) suelen tomarse en una conversación o directamente en el código. Meses después nadie sabe por qué se eligió así, qué se descartó ni si sigue valiendo, y un agente puede deshacerlas sin darse cuenta. Este paquete las registra con un formato fijo, separa quién propone de quién decide, impide reescribir lo aceptado y expresa las prohibiciones de forma que una herramienta pueda comprobarlas.

## Problemas que cubre

- `decisiones-sin-registro`: decisiones caras de revertir tomadas sin dejar contexto, opciones ni consecuencias.
- `opciones-sin-comparar`: ADR con una sola opción real o sin consecuencias negativas.
- `decisiones-contradichas`: cambios que contradicen una ADR aceptada sin decisión de reemplazarla.
- `decisiones-aceptadas-reescritas`: ADR aceptadas editadas en lugar de reemplazadas.
- `prohibiciones-no-comprobables`: vetos detectables en el código sin expresión que los busque.

## Fuera de alcance

- Buscar en el código las prohibiciones de las ADR aceptadas: `verificaciones-vivas`.
- Reglas propias del equipo comprobables con expresiones regulares y sus excepciones: `reglas-del-proyecto`.
- Mantener las capas y los cruces entre módulos de un monolito: `arquitectura-monolitica-por-capas`.
- Investigar con evidencia un problema antes de decidir: `auditorias-tecnicas`.
- Implementar lo decidido: `instrucciones-aprobadas`.

## Cuándo usarlo

- Al elegir o cambiar framework, base de datos, protocolo, patrón transversal, proveedor externo o modelo de seguridad.
- Cuando un pedido parece contradecir una decisión anterior.
- Al adoptar uxyngraphar en un repo con decisiones ya tomadas que conviene dejar por escrito.
- Cuando `arquitectura-monolitica-por-capas` necesita autorizar una desviación.

## Cuándo no usarlo

- Para decisiones baratas de revertir (nombre de una variable, orden de un menú, una librería de utilidades interna).
- Para normas de estilo o de código del equipo: van en `reglas-del-proyecto`.

## Entradas y salidas

- Entradas: el pedido o el cambio que obliga a decidir, las ADR existentes en `uxyngraphar/trabajo/decisiones-de-arquitectura/` y el contexto concreto del proyecto (rutas, datos, restricciones).
- Salidas: fichas `ADR-…` en la carpeta de su estado; con prohibición, `comprobacion_prohibido` y `aplica_a` listos para `verificaciones-vivas`; con reemplazo, la ADR anterior archivada y enlazada.

## Paquetes complementarios

- `verificaciones-vivas`: comprueba en el código las prohibiciones de las ADR aceptadas.
- `revision-humana`: reúne las ADR en `propuesta` y `en-evaluacion` con el resto de decisiones pendientes.
- `arquitectura-monolitica-por-capas`: cada desviación aceptada de las capas se apoya en una ADR.
- `auditorias-tecnicas`: la evidencia que alimenta el contexto de una ADR.
