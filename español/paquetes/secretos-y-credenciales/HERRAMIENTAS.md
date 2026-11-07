# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/secretos-y-credenciales`.

## `scripts/secretos.py`

Verificación del paquete (está en «verificaciones»).

- `python3 $P/scripts/secretos.py`: escanea las `raices` de los ajustes, salvo `excluir` y `permitir`, y los archivos de más de `max_kb`.
- `python3 $P/scripts/secretos.py <ruta>…`: escanea solo esas rutas (archivos o carpetas).
- `--git`: escanea lo que git versiona, tiene preparado o sin seguimiento no ignorado. Código 2 si no es un repositorio git.
- `--informe`: guarda el resultado en `uxyngraphar/trabajo/secretos-y-credenciales/informes/escaneo-<AAAAMMDD-HHMMSS>.md`.

Imprime `ruta: archivo de secretos (por nombre); no debe versionarse` o `ruta:línea: tipo (muestra enmascarada)` por hallazgo y un resumen; código 0 = limpio, 1 = hallazgos.

## `scripts/secretos_patrones.py`

Librería usada por `secretos.py`: patrones por contenido (claves AWS, llaves privadas, tokens de GitHub, Slack y npm, claves `sk-`, Stripe y Google, JWT, URL con credenciales y asignaciones de `password`/`secret`/`token`), placeholders que se ignoran, la marca `uxyngraphar:permitir-secreto`, los nombres de archivo prohibidos y las plantillas permitidas, y el enmascarado (4 primeros caracteres + longitud). En rutas de prueba no aplica la heurística débil de «credencial asignada». No se ejecuta directamente.

## `scripts/comun/verificar.py`

Verificación genérica: integridad del paquete y fichas del trabajo.
