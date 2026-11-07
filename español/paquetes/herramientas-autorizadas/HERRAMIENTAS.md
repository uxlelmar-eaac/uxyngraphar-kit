# Herramientas

Scripts del paquete (Python, solo librería estándar). Se ejecutan desde la raíz de la app; `P=uxyngraphar/paquetes/herramientas-autorizadas`.

## `scripts/verificar-herramientas.py`

Verificación del paquete (está en «verificaciones»). Para cada herramienta `authorized`: error si falta `authorized_by` (o sigue con el texto de la plantilla `<persona o equipo>`), si falta `authorized_at` o si `source` no es `human`; aviso si un ancla no existe. Las `revoked` no se revisan. Código 1 si hay errores.

## `scripts/comun/fichas.py`

Fichas del trabajo:

- `listar autorizada --status authorized`: herramientas vigentes.
- `ver <HER-…>`: ficha completa de una herramienta.
- `nueva propuesta --slug <slug> [--titulo "…"]`: propuesta del agente.
- `estado <PRO-…> en-evaluacion`: propuesta lista para la persona.
- `nueva autorizada --slug <slug> --humano` y `estado <id> promovida|rejected|revoked --humano`: **solo una persona**.

## `scripts/comun/verificar.py`

Verificación genérica: integridad del paquete y fichas del trabajo.
