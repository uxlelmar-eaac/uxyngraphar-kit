# Documentos archivados

Guarda un archivo histórico inmutable de los documentos que se retiran: copias fechadas que crea y consulta solo la persona, y que el agente no lee ni edita nunca.

## Qué resuelve

Cuando un documento deja de usarse, borrarlo pierde el histórico, mientras que dejarlo a la vista confunde al agente, que lo toma como vigente. Y un histórico que el agente puede editar, borrar o leer deja de ser fiable. Este paquete da un sitio único para lo retirado: una copia fechada por documento, que solo crece, fuera del alcance de la IA y que solo maneja la persona.

## Problemas que cubre

- `archivo-historico-alterado`: documentos del archivo editados, borrados o leídos por el agente.
- `documentos-retirados-sin-archivar`: documentos retirados que se borran sin copia fechada.

## Fuera de alcance

- Notas breves con lo que la persona quiere recordar, incluido lo que vuelve a importar de un documento archivado: `notas-de-memoria`.
- Decisiones técnicas sustituidas o rechazadas (se quedan en su ADR con su status): `decisiones-de-arquitectura`.
- Copias de seguridad del repositorio o de la base de datos: no lo cubre el kit.

## Cuándo usarlo

- La persona quiere retirar un documento (un informe viejo, una especificación sustituida) sin perderlo.
- La persona quiere consultar algo del archivo histórico (lo hace ella).

## Cuándo no usarlo

- Para conservar un dato suelto: eso es una nota de `notas-de-memoria`.
- Para que el agente consulte el histórico: el agente no lee el archivo nunca.

## Entradas y salidas

- Entradas: la ruta de un documento a archivar (la da la persona).
- Salidas: el comando exacto para la persona y, cuando lo ejecuta, la copia en `uxyngraphar/trabajo/documentos-archivados/archivo/<AAAA-MM-DD>/<nombre>`.

## Paquetes complementarios

- `notas-de-memoria`: si algo de un documento debe seguir a mano, se guarda allí como nota antes de archivarlo; y si algo del archivo vuelve a importar, la persona lo trae allí.
- `secretos-y-credenciales`: escanea que lo archivado no contenga credenciales.
