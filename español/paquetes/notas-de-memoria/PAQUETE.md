# Notas de memoria

Conserva el conocimiento del proyecto que la persona quiere guardar en notas breves, fechadas y con fuente, sin que el agente las cargue en su contexto salvo que el pedido lo pida.

## Qué resuelve

Entre conversaciones se pierden acuerdos informales, lecciones de incidentes y matices que no son decisiones ni reglas. Guardarlo todo en documentos que el agente lee siempre es peor: llena el contexto de información vieja y el agente trabaja con datos caducados. Este paquete guarda ese conocimiento como notas que se buscan solo cuando se piden, con su fuente y hasta cuándo valen, y marca como archivadas las que dejan de valer.

## Problemas que cubre

- `conocimiento-del-proyecto-perdido`: lo que la persona quiere conservar se pierde entre conversaciones.
- `memoria-leida-sin-pedido`: el agente carga notas antiguas en su contexto sin que el pedido lo pida.
- `notas-caducadas-tratadas-como-vigentes`: notas sin fuente ni validez que se siguen tomando como ciertas.

## Fuera de alcance

- Archivo histórico de documentos retirados (copias fechadas que solo toca la persona): `documentos-archivados`.
- Decisiones técnicas que condicionan el sistema: `decisiones-de-arquitectura`.
- Reglas del equipo que el código debe cumplir: `reglas-del-proyecto`.
- Procedimientos para operar el sistema: `manuales-operativos`.
- Deuda técnica y bugs detectados fuera de alcance: `deuda-y-mejoras`.

## Cuándo usarlo

- La persona dice «recuerda que…», «apunta esto para la próxima vez» o similar.
- El pedido pide expresamente buscar en la memoria del proyecto.
- Una nota deja de valer o la sustituye otra.

## Cuándo no usarlo

- Para lo que tiene un paquete propio (decisiones, reglas, manuales, deuda): la nota duplicaría y se desfasaría.
- Como contexto por defecto del agente: la memoria no se lee en cada pedido.
- Para retirar un documento sin perderlo: eso es `documentos-archivados`.

## Entradas y salidas

- Entradas: lo que la persona pide conservar o buscar, y de dónde sale.
- Salidas: notas `MEM-…` en `uxyngraphar/trabajo/notas-de-memoria/memoria/` y resultados de `notas.py buscar`.

## Paquetes complementarios

- `documentos-archivados`: archivo histórico de documentos retirados. Si algo del archivo vuelve a importar, la persona lo trae aquí como nota.
- `decisiones-de-arquitectura`, `reglas-del-proyecto`, `manuales-operativos`: destino de lo que parece una nota pero es una decisión, una regla o un procedimiento.
- `secretos-y-credenciales`: escanea que las notas no contengan credenciales.
