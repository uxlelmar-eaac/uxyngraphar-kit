# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/mapa-de-modulos`.

## `scripts/verificar-areas.py`

Verificación del paquete (está en «verificaciones»): `python3 $P/scripts/verificar-areas.py`.

- Construye el grafo de áreas: el nombre de cada área es su carpeta bajo el trabajo (o el `id` de la ficha si está en la raíz) y sus aristas, `depends_on`.
- Error por cada ciclo de dependencias (`orders → payments → orders`).
- Aviso por cada dependencia hacia un área sin contexto.
- Termina con `areas: N áreas, E errores, A avisos`; código 1 si hay ciclos.
- No comprueba que el «Código ancla» exista.

## `scripts/comun/fichas.py`

Crea y consulta contextos `ARE`: `nueva area --slug <area> --en <area> --titulo "Área: …"`, `listar area`, `ver <id>`, `estado <id> <status>`.

## `scripts/comun/verificar.py`

Verificación genérica: integridad del paquete y status válidos de las fichas.
