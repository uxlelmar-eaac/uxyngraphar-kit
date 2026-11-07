# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/notas-de-memoria`.

## `scripts/notas.py`

- `python3 $P/scripts/notas.py buscar <texto>`: busca sin distinguir mayúsculas en los `.md` de `memoria/` e imprime `memoria/<ruta>:<línea>: <texto>`; sin resultados, no imprime nada. Solo cuando el pedido lo pide.

Código 1 y `error: …` si falla.

## `scripts/comun/fichas.py`

Crea y consulta notas `MEM`: `nueva nota --slug <slug> --titulo "…"`, `listar nota`, `ver <id>`, `estado <id> archivada`.

## `scripts/comun/verificar.py`

Verificación genérica: integridad del paquete y status válidos de las notas.
