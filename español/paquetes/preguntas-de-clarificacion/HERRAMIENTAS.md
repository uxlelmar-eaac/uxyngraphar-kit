# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/preguntas-de-clarificacion`.

## `scripts/verificar-preguntas.py`

Verificación del paquete (está en «verificaciones»): `python3 $P/scripts/verificar-preguntas.py`. Códigos: 0 sin errores, 1 con errores.

- Error si una pregunta `completada` no tiene filas en «Decisiones», tiene una fila sin «Pregunta» o sin «Elegida», o su «Síntesis» está vacía.
- Aviso si una pregunta lleva `en-curso` más de `dias_en_curso` días (según `created`).
- Aviso si `instruccion_id` cita una instrucción que no está en `uxyngraphar/trabajo/instrucciones-aprobadas/`. Solo se comprueba si esa carpeta existe; sin ella no se consulta.

## `scripts/preguntas_reglas.py`

Librería de `verificar-preguntas.py`: separa las secciones de la ficha, lee la tabla de decisiones, calcula lo que impide cerrar una pregunta, su antigüedad y si la instrucción enlazada existe. No se ejecuta directamente.

## `scripts/comun/fichas.py`

Fichas del trabajo: `nueva pregunta --slug <slug> [--titulo "…"]`, `listar [pregunta] [--status <status>]`, `ver <id>`, `estado <id> en-curso|completada|cancelada`.

## `scripts/comun/verificar.py`

Verificación genérica: integridad del paquete y fichas del trabajo (status, carpeta, frontmatter).
