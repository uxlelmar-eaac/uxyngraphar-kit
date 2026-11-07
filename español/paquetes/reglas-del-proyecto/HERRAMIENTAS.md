# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/reglas-del-proyecto`.

## `scripts/reglas.py`

- `python3 $P/scripts/reglas.py indice`: tabla de las reglas activas (`id | nivel | aplica_a | resumen`). Es lo único que se lee por defecto.
- `python3 $P/scripts/reglas.py para <ruta|ancla>…`: reglas activas que tocan esas rutas; acepta anclas `archivo:inicio-fin`. Las `bloqueante` imprimen también su cuerpo.
- `python3 $P/scripts/reglas.py comprobar [RUTA…] [--git]`: evalúa las reglas activas con comprobación; `--git` limita a lo modificado, preparado o sin seguimiento. Código 1 si hay un bloqueante sin excepción aprobada.

## `scripts/verificar-reglas.py`

Verificación del paquete (está en «verificaciones»). Errores: reglas activas mal formadas, excepciones aprobadas que citan una regla inexistente e incumplimientos bloqueantes sin excusar en todo el código. Avisos: reglas propuestas mal formadas, excepciones aprobadas sin `aprobada_por`, excepciones pendientes que citan una regla inexistente e incumplimientos de nivel `aviso`. Termina con `reglas-del-proyecto: N errores, M avisos`.

## `scripts/reglas_datos.py`

Librería compartida por los dos anteriores: lectura de fichas, globs de `aplica_a` (el `**` puede ser vacío), anclas, excepciones vigentes y archivos a comprobar (`raices`, `excluir` y `max_kb` de los ajustes del paquete, o lo cambiado según git). No se ejecuta directamente.

## `scripts/comun/fichas.py`

Crea fichas y cambia su status: `nueva regla|excepcion --slug <slug>`, `listar`, `ver <id>`, `estado <id> <status> [--humano]`.

## `scripts/comun/verificar.py`

Verificación genérica: integridad del paquete y fichas del trabajo.
