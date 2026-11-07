# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/rutas-de-api`.

## `scripts/verificar-rutas.py`

Verificación del paquete (está en «verificaciones»): `python3 $P/scripts/verificar-rutas.py`.

- Error si a una ficha le falta un campo de `campos_obligatorios` (por defecto `method`, `path`, `auth`).
- Error si dos fichas no retiradas ni deprecadas comparten la `clave_unica` (por defecto método + ruta; el método se compara en mayúsculas).
- Aviso por cada archivo citado en «Archivos ancla» que no existe en la app.
- Termina con `rutas: N documentadas, E errores, A avisos`; código 1 si hay errores.

## `scripts/comun/fichas.py`

Crea y consulta fichas `RUT`: `nueva ruta --slug <slug> --en <modulo> --titulo "…"`, `listar ruta [--status <status>]`, `ver <id>`, `estado <id> <status>`.

## `scripts/comun/verificar.py`

Verificación genérica: integridad del paquete y status válidos de las fichas.
