# Verificaciones vivas

Comprueba, cuando alguien lo pide, que la documentación de los paquetes instalados sigue diciendo la verdad sobre el código: cada diferencia sale como hallazgo con severidad y evidencia, y queda registrada como auditoría o como informe.

## Qué resuelve

La documentación se desfasa sin hacer ruido: se añade un endpoint sin ficha, se borra un servicio que tres fichas citan como ancla, una ADR prohíbe una librería que alguien vuelve a importar, un manual dice «verificado» desde hace un año y la app ya no arranca con el comando del README. Este paquete reúne seis revisiones de solo lectura y una de humo que contrastan lo documentado con lo que hay, y entrega el resultado en un formato que los demás flujos pueden recoger.

## Problemas que cubre

- `fichas-desalineadas-del-codigo`: rutas o páginas sin ficha, o fichas activas sin código (revisiones `rutas` y `paginas`).
- `referencias-rotas`: anclas a archivos que no existen e ids de fichas colgantes (revisiones `anclas` y `vinculos`).
- `decisiones-incumplidas`: ADR aceptadas cuyo patrón prohibido aparece en el código (revisión `decisiones`).
- `manuales-sin-verificar`: manuales vigentes sin verificación reciente o con rutas inexistentes (revisión `manuales`).
- `flujos-basicos-rotos`: la app no arranca o un flujo básico falla (revisión `humo`).

## Fuera de alcance

- Corregir los hallazgos en el código o en las fichas: `instrucciones-aprobadas`.
- Registrar y priorizar los que no se corrigen ahora: `deuda-y-mejoras`.
- Auditorías técnicas con alcance y preguntas propias: `auditorias-tecnicas` (aquí solo se usa como destino del informe).
- Escribir o actualizar fichas de rutas de API: `rutas-de-api`.
- Pruebas automatizadas del proyecto (unitarias, integración, CI): no lo cubre el kit.

## Cuándo usarlo

- Antes de una entrega o una revisión de la documentación.
- Tras una refactorización grande que mueve o borra archivos.
- Cuando la persona sospecha que la documentación ya no refleja el código.
- Para comprobar que la app sigue arrancando con las pruebas de humo configuradas.

## Cuándo no usarlo

- Como verificación automática en cada commit o en CI.
- En un proyecto sin ninguno de los paquetes que documentan (rutas, páginas, decisiones, manuales): solo quedarían `anclas`, `vinculos` y `humo`.

## Entradas y salidas

- Entradas: el código bajo `raices` (con `extensiones`), las fichas de `uxyngraphar/trabajo/` de los paquetes instalados (`rutas-de-api`, `paginas-de-interfaz`, `decisiones-de-arquitectura`, `manuales-operativos`) y los ajustes del paquete.
- Salidas: la lista de hallazgos (`[revisión] severidad: hallazgo — evidencia`) y, con `--informe`, una auditoría `AUD-…-vivas-…` en `auditorias-tecnicas` o un `INFORME-<fecha>-<revisiones>.md` en el trabajo del paquete.

## Paquetes complementarios

- `rutas-de-api` y `paginas-de-interfaz`: las fichas que se contrastan con el código.
- `decisiones-de-arquitectura`: las ADR con `comprobacion_prohibido` que se buscan en el código.
- `manuales-operativos`: los manuales cuya vigencia se revisa.
- `auditorias-tecnicas`: recibe el informe como auditoría y permite promover sus hallazgos.
- `deuda-y-mejoras` e `instrucciones-aprobadas`: los flujos donde se resuelven los hallazgos.
