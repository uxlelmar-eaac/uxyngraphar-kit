# Cambios

## 2.0.1

- Derivación actualizada tras dividir `memoria-e-historial`: el tema de memoria y archivo histórico de «Fuera de alcance» se separa en dos, notas de memoria → `notas-de-memoria` y archivo histórico de documentos retirados → `documentos-archivados` (manifiesto y `PAQUETE.md`).
- Sin cambios en las fichas, los ajustes ni los scripts.

## 2.0.0

- División del paquete: el problema `decisiones-supuestas` pasa al paquete nuevo `preguntas-de-clarificacion` (1.0.0), que se lleva el tipo de ficha `pregunta` (prefijo `PRE`, carpeta `preguntas/`, mismos status y plantilla `plantillas/pregunta.md`), la fase `preguntar`, la skill `registrar-pregunta`, `referencia/preguntas.md` y el ajuste `preguntas`. Aquí quedan cuatro problemas: `cambios-sin-aprobacion`, `alcance-desbordado`, `contexto-excesivo` y `cierre-sin-rastro`.
- Cambio MAYOR porque cambia la forma del trabajo: las preguntas ya no viven en `uxyngraphar/trabajo/instrucciones-aprobadas/preguntas/` sino en `uxyngraphar/trabajo/preguntas-de-clarificacion/preguntas/`; mover las existentes lo hace el motor, nunca el paquete.
- El proceso empieza en `redactar-instruccion`, que pide preguntar lo que cambia el resultado antes de redactar y, si hay ficha `PRE-…`, la cita en `preguntas_id`. El ciclo funciona igual sin `preguntas-de-clarificacion` instalado.
- `verificar-ciclo.py` avisa si una instrucción activa cita en `preguntas_id` una pregunta que no existe o sigue `en-curso`, solo cuando existe `uxyngraphar/trabajo/preguntas-de-clarificacion/`.
- Sin cambios en el tipo `instruccion` (carpeta `instrucciones/`, status, variantes), en `ESTADO.md` ni en los comandos de `ciclo.py` y `verificar-ciclo.py`.

## 1.1.0

- Reconstruido con el protocolo de piezas: `PAQUETE.md` con cinco problemas y lo que deja fuera, `LIMITES.md`, proceso en seis fases (`preguntar`, `redactar-instruccion`, `esperar-aprobacion`, `cargar-contexto`, `implementar`, `cerrar`), cinco skills, `COMPONENTES.md`, `HERRAMIENTAS.md`, un ejemplo resuelto y pruebas propias.
- Las reglas del README pasan a `LIMITES.md`, con una regla nueva (lo aprobado no se amplía sin nueva aprobación) y «Cuándo detenerse y preguntar».
- `docs/` pasa a `referencia/` (`eficiencia.md`, `preguntas.md`); `preguntas.md` queda como guía de criterio y los pasos pasan a la fase `preguntar`.
- Sin cambios en las fichas, los ajustes ni los scripts.

## 1.0.0

- Primera versión del paquete en uxyngraphar 2.0.
