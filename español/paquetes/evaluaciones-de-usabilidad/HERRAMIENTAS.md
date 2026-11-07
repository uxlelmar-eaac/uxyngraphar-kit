# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/evaluaciones-de-usabilidad`.

## `scripts/verificar-evaluaciones.py`

Verificación del paquete (está en «verificaciones»): `python3 $P/scripts/verificar-evaluaciones.py`. Recorre las evaluaciones no archivadas ni canceladas y comprueba:

- heurística admitida por el ajuste `heuristicas` y severidad entre 0 y `severidad_max`;
- evidencia en cada problema y propuesta en los de severidad ≥ `severidad_propuesta_obligatoria`;
- ninguna fila marcada como aprobada mientras la ficha está en `abierta`, `en-curso` o `propuesta`;
- desde `propuesta`, al menos una métrica con «Antes», «Objetivo» y «Fuente»; en `validada`, «Después» en todas;
- en `implementada` o `validada`, al menos una fila con «Aprobada» = sí.

Imprime `aviso:` y `error:` por línea y un resumen `evaluaciones: N errores, M avisos`. Código 1 si hay errores.

## `scripts/comun/fichas.py`

Fichas de evaluación: `nueva evaluacion --slug <s> --titulo "…"`, `listar evaluacion [--status <s>]`, `ver <id>`, `estado <id> <status>`. `aprobada` y `validada` exigen `--humano` (solo una persona).

## `scripts/comun/verificar.py`

Verificación genérica: integridad del paquete y forma de las fichas del trabajo.
