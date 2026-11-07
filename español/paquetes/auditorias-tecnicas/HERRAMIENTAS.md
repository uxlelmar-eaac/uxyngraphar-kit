# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/auditorias-tecnicas`.

## `scripts/verificar-auditorias.py`

Verificación del paquete (está en «verificaciones»): `python3 $P/scripts/verificar-auditorias.py`. Recorre todas las auditorías y comprueba:

- cada fila de «Hallazgos» con severidad de `ajustes.severidades` (error) y evidencia no vacía (error);
- hallazgos escritos como lista (formato 1.x) en lugar de tabla (aviso: pásalos a la tabla);
- `findings_count` igual al número de hallazgos (error en `cerrada`, aviso en el resto);
- en `activa`, días desde `actualizado` (o `fecha`, o la última modificación del archivo) por encima de `dias_sin_cambios` (aviso);
- más de `max_activas` auditorías activas (aviso).

Imprime `aviso:`/`error:` y el resumen `auditorias: N errores, M avisos`. Código 1 si hay errores.

## `scripts/comun/fichas.py`

Fichas de auditoría: `nueva auditoria --slug <s> --titulo "…"` (nace `activa`), `listar auditoria [--status <s>]`, `ver <id>`, `estado <id> <status>` (`pendiente`, `activa`, `cerrada`, `archivada`, `cancelada`, `para-eliminar`).

## `scripts/comun/verificar.py`

Verificación genérica: integridad del paquete y forma de las fichas del trabajo.
