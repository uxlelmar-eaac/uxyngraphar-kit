# Manuales operativos

Mantiene manuales vivos para operar el sistema —despliegue, incidentes, configuración— con pasos ejecutables, resultado esperado, cómo revertir y sin secretos, que se actualizan en la misma tarea que cambia el procedimiento.

## Qué resuelve

Desplegar, rotar una configuración o responder a un incidente suele depender de la memoria de una persona o de un documento viejo que ya no funciona. Bajo presión, un paso vago o un comando desfasado convierte un incidente pequeño en uno grande, y sin «cómo revertir» no hay salida. Este paquete fija la forma de un manual (requisitos, pasos con resultado esperado, verificación, reversión), lo mantiene al día con cada cambio y deja la validación final a una persona.

## Problemas que cubre

- `procedimientos-sin-manual`: operaciones que solo sabe hacer una persona.
- `manuales-desfasados`: manuales no actualizados tras un cambio o sin fecha de última verificación.
- `pasos-no-ejecutables`: pasos sin comando exacto ni resultado esperado.
- `procedimientos-sin-reversion`: procedimientos que cambian el sistema sin explicar cómo deshacerlos.

## Fuera de alcance

- Detectar manuales sin verificar o desfasados contrastándolos con el código: `verificaciones-vivas`.
- Escanear el repositorio en busca de secretos: `secretos-y-credenciales`.
- Autorizar procedimientos para que el agente los ejecute sin instrucción nueva: `herramientas-autorizadas`.
- Decidir la infraestructura o la estrategia de despliegue: `decisiones-de-arquitectura`.
- Ejecutar el procedimiento en producción: no lo cubre el kit.

## Cuándo usarlo

- Al cambiar cómo se despliega, configura, migra o monitoriza el sistema.
- Al escribir el procedimiento de un incidente tras resolverlo.
- Cuando la persona pide documentar una operación que hoy solo sabe hacer alguien.

## Cuándo no usarlo

- Para documentar código o arquitectura: hay paquetes para eso.
- Para guías de uso del producto dirigidas a usuarios finales.

## Entradas y salidas

- Entradas: el cambio (scripts de despliegue, configuración, CI), lo que la persona sabe del procedimiento y los manuales existentes.
- Salidas: manuales `MAN-…` en `uxyngraphar/trabajo/manuales-operativos/`, en `borrador` hasta que una persona los prueba y los pasa a `vigente`.

## Paquetes complementarios

- `verificaciones-vivas`: avisa de manuales con `ultima_verificacion` antigua.
- `secretos-y-credenciales`: escanea que los manuales no contengan valores reales.
- `herramientas-autorizadas`: un procedimiento repetido y probado puede convertirse en herramienta autorizada.
