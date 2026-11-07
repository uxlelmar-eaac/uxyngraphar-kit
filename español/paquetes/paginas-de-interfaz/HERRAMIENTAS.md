# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/paginas-de-interfaz`.

## `scripts/verificar-paginas.py`

Verificación del paquete (está en «verificaciones»): `python3 $P/scripts/verificar-paginas.py`.

- Error si a una ficha le falta un campo de `campos_obligatorios` (por defecto `path`, `tipo`, `auth`).
- Error si dos fichas no retiradas ni deprecadas comparten la `clave_unica` (por defecto `path`).
- Aviso por cada archivo citado en «Archivos ancla» que no existe en la app.
- Termina con `rutas: N documentadas, E errores, A avisos` (cuenta rutas de interfaz); código 1 si hay errores.

## `scripts/comun/fichas.py`

Crea y consulta fichas `PAG`: `nueva pagina --slug <slug> --en <modulo> --titulo "…"`, `listar pagina [--status <status>]`, `ver <id>`, `estado <id> <status>`.

## `scripts/comun/verificar.py`

Verificación genérica: integridad del paquete y status válidos de las fichas.
