# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/evolucion-del-sistema`.

## `scripts/evolucion.py`

- `python3 $P/scripts/evolucion.py matriz`: crea `uxyngraphar/trabajo/evolucion-del-sistema/MATRIZ-COBERTURA.md` desde `plantillas/MATRIZ-COBERTURA.md` si falta, y la muestra.
- `python3 $P/scripts/evolucion.py exportar --humano [--todas]`: acción de la persona. Reúne las EVO `approved` (y las `pending` con `--todas`) en `exportaciones/EXPORTACION-<fecha>.md`, sustituye la raíz de la app y la carpeta personal por rutas relativas o `~`, y escribe la fecha en `exportada` de cada EVO incluida. Sin `--humano`, o sin terminal interactiva ni `UXYNGRAPHAR_HUMANO=1`, se niega. Código 1 si no hay EVO que exportar.

Nada sale del equipo: el informe queda en el trabajo del paquete y la persona decide a quién lo envía.

## `scripts/verificar-evolucion.py`

Verificación del paquete (está en «verificaciones»): `python3 $P/scripts/verificar-evolucion.py`. Para cada EVO comprueba:

- `tipo` dentro de `ajustes.tipos` (error);
- en `pending`, «Evidencia» y «Propuesta» rellenas y distintas del texto de la plantilla (aviso);
- `paquete` citado instalado en `uxyngraphar/paquetes/` (aviso).

Imprime `aviso:`/`error:` y el resumen `evolucion-del-sistema: N errores, M avisos`. Código 1 si hay errores.

## `scripts/comun/fichas.py`

Fichas EVO: `nueva evo --slug <s> --titulo "…"`, `listar evo [--status <s>]`, `ver <id>`, `estado <id> <status>`. `approved`, `rejected` y `done` exigen `--humano`.

## `scripts/comun/verificar.py`

Verificación genérica: integridad del paquete y forma de las fichas del trabajo.
