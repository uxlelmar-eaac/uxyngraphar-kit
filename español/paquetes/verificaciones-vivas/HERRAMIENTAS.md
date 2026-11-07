# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/verificaciones-vivas`.

## `scripts/vivas.py`

- `python3 $P/scripts/vivas.py [REVISIÓN…]`: ejecuta las revisiones pedidas (`rutas`, `paginas`, `anclas`, `decisiones`, `manuales`, `vinculos`, `humo`); sin revisiones, todas menos `humo`. Una revisión desconocida es un error de uso.
- `--ejecutar`: ejecuta los comandos de `humo` (sin revisiones, añade `humo` a la lista).
- `--informe`: guarda el resultado como auditoría `AUD-…-vivas-…` de `auditorias-tecnicas` o como `uxyngraphar/trabajo/verificaciones-vivas/INFORME-<fecha>-<revisiones>.md`.

Imprime `[revisión] severidad: hallazgo — evidencia` por línea y `verificaciones-vivas: N hallazgos` (las notas `info` no cuentan). Código 0 = sin hallazgos, 1 = hay hallazgos. No está en «verificaciones»: solo se ejecuta bajo pedido.

## `scripts/vivas_datos.py`

Librería usada por `vivas.py`: una función por revisión, detección de rutas (Nest, Express, Fastify, FastAPI, Flask) y páginas (App Router de Next), normalización de rutas, lectura de las fichas de los paquetes instalados y ejecución del humo con límite de tiempo. No se ejecuta directamente.

## `scripts/comun/verificar.py`

Verificación del paquete (está en «verificaciones»): integridad del paquete y fichas del trabajo.
