# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/documentacion-espejo`.

## `scripts/espejo.py`

- `python3 $P/scripts/espejo.py mapa [--faltantes]`: cada carpeta y archivo de código bajo `raices` con `✓` (tiene espejo) o `·` (no tiene), y `cobertura: N/M`. Con `--faltantes`, solo los que no tienen.
- `python3 $P/scripts/espejo.py ver <ruta-del-codigo>`: imprime el espejo, o `sin espejo: …` con el comando para crearlo.
- `python3 $P/scripts/espejo.py nuevo <ruta-del-codigo>`: crea el espejo desde `plantillas/archivo.md` o `plantillas/carpeta.md` con nombre, ruta, líneas y fecha. Falla si el código no existe, si está fuera de la app o si el espejo ya existe.
- `python3 $P/scripts/espejo.py huerfanos`: espejos cuyo código ya no existe.

## `scripts/verificar-espejo.py`

Verificación del paquete (está en «verificaciones»). Error por cada espejo huérfano y si la cobertura queda bajo `cobertura_minima`. Termina con `espejo: cobertura N/M (P%), E errores`; código 1 si hay errores.

## `scripts/espejo_mapa.py`

Librería compartida por los dos anteriores: recorrido del código según `raices`, `extensiones` y `excluir`, cálculo de la ruta espejo y detección de huérfanos. No se ejecuta directamente.

## `scripts/comun/verificar.py`

Verificación genérica: integridad del paquete.
