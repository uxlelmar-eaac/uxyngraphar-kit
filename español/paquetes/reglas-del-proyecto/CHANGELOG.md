# Cambios

## 2.0.0

- División del paquete: los ajustes locales pasan al paquete nuevo `adaptaciones-de-paquetes`. Este se queda con las reglas y sus excepciones (`convenciones-sin-comprobar`, `reglas-incumplidas-en-silencio`).
- Salen del alcance los problemas `paquetes-sin-adaptar-al-proyecto` y `ajustes-locales-desfasados`; «Fuera de alcance» deriva los ajustes locales a `adaptaciones-de-paquetes`.
- Sale la ficha `ajuste` (`AJL`, carpeta `ajustes-locales/`) y su plantilla: el trabajo pasa a `uxyngraphar/trabajo/adaptaciones-de-paquetes/ajustes-locales/` (moverlo lo hace el motor con respaldo).
- Salen el campo `al_activar_paquete`, los subcomandos `reglas.py ajustes <id>` y `reglas.py aprobar-ajuste <AJL-…> --humano` (ahora `adaptaciones.py` en `adaptaciones-de-paquetes`), la frase de activación «ajustes locales» y las skills `aplicar-ajustes-locales` y `proponer-ajuste-local`.
- `verificar-reglas.py` deja de revisar ajustes. `reglas.py indice|para|comprobar` y `verificar-reglas.py` no cambian.
- La fase `proponer-cambios` usa ahora `proponer-regla` y `proponer-excepcion`.

## 1.1.0

- Reconstruido con el protocolo de piezas: `PAQUETE.md` (alcance y lo que deja fuera), `LIMITES.md`, proceso en cuatro fases (`consultar-reglas`, `implementar`, `verificar`, `proponer-cambios`), seis skills, `COMPONENTES.md` (regla, comprobación, nivel, excepción, ajuste local, huella), `HERRAMIENTAS.md`, ejemplo resuelto y pruebas propias.
- Las reglas del README pasan a `LIMITES.md`, con «Cuándo detenerse y preguntar».
- La skill `proponer-regla` documenta que las regex del frontmatter se escriben con una sola barra invertida.

## 1.0.0

- Primera versión del paquete en uxyngraphar 2.0.
