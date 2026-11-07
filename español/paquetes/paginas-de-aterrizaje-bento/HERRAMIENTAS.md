# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/paginas-de-aterrizaje-bento`.

## `scripts/verificar-bento.py`

Verificación del paquete (está en «verificaciones»): `python3 $P/scripts/verificar-bento.py`. Lee la tabla «Mosaico» de cada ficha no archivada ni cancelada y comprueba con los ajustes efectivos:

- número de celdas entre `celdas_min` y `celdas_max`, tamaños de `tamanos` que caben en `columnas` y como mucho `max_2x2` celdas `2x2`;
- prioridades 1..n sin repetir y la prioridad 1 en la celda de mayor área;
- suma de áreas múltiplo de `columnas` (sin huecos);
- título no vacío y dentro de `palabras_titulo`, mensaje dentro de `palabras_mensaje`;
- CTA `primario`, `secundario` o `-`, con exactamente un `primario`;
- medios `img:`/`video:` con texto alternativo;
- en `revision` y `publicada`, ninguna casilla `- [ ]` en «Checklist de publicación».

En `borrador` los fallos del mosaico son avisos; desde `en-curso`, errores. Imprime `aviso:`/`error:` y el resumen `bento: N errores, M avisos`. Código 1 si hay errores.

## `scripts/comun/fichas.py`

Fichas de página: `nueva landing --slug <s> --titulo "…"`, `listar landing`, `ver <id>`, `estado <id> <status>`. `publicada` exige `--humano`.

## `scripts/comun/verificar.py`

Verificación genérica: integridad del paquete y forma de las fichas del trabajo.
