# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/contratos-entre-repositorios`.

## `scripts/contratos.py`

- `python3 $P/scripts/contratos.py registro`: regenera `uxyngraphar/trabajo/contratos-entre-repositorios/REGISTRO.md` con una fila por contrato de este repositorio, ordenada por `id_compartido`.
- `python3 $P/scripts/contratos.py comparar [RUTA…]`: compara los contratos vigentes de consumidor con los repositorios hermanos (por defecto `otros_repos`; rutas relativas a la raíz de esta app). Busca el `id_compartido` en sus contratos y, si no está, el método y la ruta en sus fichas de `rutas-de-api`. Código 1 si hay divergencias. Solo lee el otro repositorio.

## `scripts/verificar-contratos.py`

Verificación del paquete (está en «verificaciones»). Errores: `id_compartido` mal formado o repetido, `rol` inválido, contrato `vigente` sin `method` o `path`, y las divergencias de `comparar`. Aviso: consumidor vigente sin `ficha_proveedor`. Termina con `contratos-entre-repositorios: E errores, A avisos`.

## `scripts/contratos_datos.py`

Librería compartida por los dos anteriores: lectura de los contratos propios, lectura de los repositorios hermanos y reglas de validación. No se ejecuta directamente.

## `scripts/comun/fichas.py`

Crea y consulta contratos `CON`: `nueva contrato --slug <slug> --titulo "…"`, `listar contrato`, `ver <id>`, `estado <id> <status>` (`vigente` y `retirado` exigen `--humano`).

## `scripts/comun/verificar.py`

Verificación genérica: integridad del paquete y status válidos de las fichas.
