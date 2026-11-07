---
name: crear-contrato
description: Crea la ficha CON de un contrato en este repositorio con su id compartido, su rol y la cita a la ficha del proveedor, sin copiar el contrato del otro lado.
resuelve: [ids-compartidos-inconsistentes, fichas-del-proveedor-copiadas]
---

# Crear contrato

## Cuándo usarla

- Este repositorio empieza a consumir una ruta de otro.
- Este repositorio publica una ruta que consumirán otros.
- Un manejador propio del cliente (BFF) intermedia una ruta del proveedor.

## Pasos

1. Crea la ficha: `python3 $P/scripts/comun/fichas.py nueva contrato --slug orders-list --titulo "Listado de pedidos"`. Nace `propuesto`.
2. Frontmatter:
   - `id_compartido`: el mismo que en el repositorio hermano si ya existe; si no, `modulo.recurso.accion` (`orders.list`).
   - `rol`: `proveedor`, `consumidor` o `bff`.
   - `method`, `path`, `version` (`v1` si es nuevo).
   - `proveedor`: nombre de la carpeta del repositorio que sirve la ruta (el que aparece en `otros_repos`).
   - `ficha_proveedor`: en un consumidor, la URL o ruta de la ficha `rutas-de-api` del proveedor. En el proveedor, la ruta de su propia ficha.
   - `consumidores`: en el proveedor, los repositorios que la usan.
3. «Para qué se usa»: la pantalla, servicio o flujo que depende del contrato.
4. «Forma (resumen)»: dos líneas; los detalles están en la ficha del proveedor. Si hay tipos generados desde OpenAPI, dónde quedan.
5. No pegues la ficha ni el OpenAPI del proveedor.

## Resultado

- Un contrato `CON-<fecha>-<slug>.md` en `propuesto`, con id compartido válido y la ficha del proveedor citada. Pasarlo a `vigente` es decisión de la persona.
