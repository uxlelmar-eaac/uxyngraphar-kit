# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/documentos-archivados`.

## `scripts/archivo.py`

- `python3 $P/scripts/archivo.py archivar <ruta> --humano`: copia el archivo a `archivo/<AAAA-MM-DD>/<nombre>` conservando fechas, sin borrar el original, e imprime la ruta de la copia. Rechaza archivos de `uxyngraphar/paquetes/` y nombres ya archivados ese día. Solo la persona.
- `python3 $P/scripts/archivo.py buscar <texto> --humano`: busca sin distinguir mayúsculas en los `.md` de `archivo/` e imprime `archivo/<fecha>/<nombre>:<línea>: <texto>`. Solo la persona.

Sin `--humano`, o sin terminal interactiva ni `UXYNGRAPHAR_HUMANO=1`, ambos fallan. Código 1 y `error: …` si falla.

## `scripts/comun/verificar.py`

Verificación genérica: integridad del paquete.
