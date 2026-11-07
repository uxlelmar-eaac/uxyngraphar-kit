# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/revision-humana`.

## `scripts/revision.py`

- `python3 $P/scripts/revision.py pendientes`: lista los pendientes de todos los paquetes instalados, del más antiguo al más nuevo, con el comando que debe ejecutar la persona y sus opciones. Sin pendientes: `(nada espera una decisión)`.
- `python3 $P/scripts/revision.py preparar`: escribe `uxyngraphar/trabajo/revision-humana/REVISION.md` con una fila por pendiente y «Decisión» vacía.
- `python3 $P/scripts/revision.py aplicar --humano`: **solo una persona** (terminal interactiva o `UXYNGRAPHAR_HUMANO=1`). Lee las decisiones de `REVISION.md`, ejecuta el comando de cada una en el paquete dueño, imprime `<id> → <decisión>: hecho|FALLÓ …` y regenera la hoja. Código 1 si alguna falla o no es una opción válida.

## `scripts/verificar-revision.py`

Verificación del paquete (está en «verificaciones»). Avisa de cada ficha con más de `dias_aviso` días esperando y resume cuántos pendientes hay. Nunca falla por antigüedad.

## `scripts/pendientes.py`

Librería compartida por los dos anteriores: localiza los paquetes instalados, recoge las fichas cuyo status espera a una persona, calcula su antigüedad y construye el comando de cada decisión. No se ejecuta directamente.

## `scripts/comun/verificar.py`

Verificación genérica: integridad del paquete.
