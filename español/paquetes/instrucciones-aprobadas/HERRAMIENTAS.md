# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/instrucciones-aprobadas`.

## `scripts/ciclo.py`

El ciclo de una instrucción. Códigos: 0 bien, 1 error de uso, 2 ficha no encontrada, 3 instrucción sin aprobar o fuera de alcance.

- `python3 $P/scripts/ciclo.py aprobar <id> --humano`: **solo una persona** (terminal interactiva o `UXYNGRAPHAR_HUMANO=1`). Exige `awaiting_approval`, comprueba el alcance (archivos de código, documentos, ampliación), mueve la ficha a `en-progreso/` y pone `approved_at`.
- `python3 $P/scripts/ciclo.py contexto <id> [--max-tokens N]`: imprime la ficha, la `lectura_minima` y las anclas con números de línea, hasta `max_tokens_contexto`; lo que no cabe sale como `OMITIDO (presupuesto)`. Anota `tokens_contexto` en la ficha. Código 3 si no está aprobada o incumple el alcance.
- `python3 $P/scripts/ciclo.py cerrar <id>`: exige `approved`; pasa a `done`, pone `executed_at` y regenera `ESTADO.md`.
- `python3 $P/scripts/ciclo.py pendientes`: instrucciones que esperan aprobación (id y título).
- `python3 $P/scripts/ciclo.py estado`: regenera el bloque de `ESTADO.md`.

## `scripts/verificar-ciclo.py`

Verificación del paquete (está en «verificaciones»). Error si una instrucción activa (`awaiting_approval` o `approved`) incumple el alcance o si una `approved` no tiene `approved_at`. Aviso si un ancla de una instrucción activa no existe, si una `done` no tiene `approved_at` o `executed_at`. Si existe `uxyngraphar/trabajo/preguntas-de-clarificacion/` (paquete `preguntas-de-clarificacion`), avisa también cuando una instrucción activa cita en `preguntas_id` una pregunta que no está allí o que sigue `en-curso`; sin esa carpeta no la consulta.

## `scripts/ciclo_reglas.py`

Librería compartida por los dos anteriores: separa `ruta:inicio-fin`, cuenta los archivos de código de las anclas por extensión, calcula los incumplimientos de alcance con los ajustes y localiza la pregunta citada en `preguntas_id`. No se ejecuta directamente.

## `scripts/comun/fichas.py`

Fichas del trabajo: `nueva instruccion --slug <slug> [--titulo "…"] [--variante compacta|solo-docs|adopcion]`, `listar [<tipo>] [--status <status>]`, `ver <id>`, `estado <id> <status>`. `approved` no se pone con `estado`: lo pone `ciclo.py aprobar`.

## `scripts/comun/verificar.py`

Verificación genérica: integridad del paquete y fichas del trabajo (status, carpeta, frontmatter).
