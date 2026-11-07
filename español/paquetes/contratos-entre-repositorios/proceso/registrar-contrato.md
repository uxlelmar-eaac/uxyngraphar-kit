---
fase: registrar-contrato
resuelve: [ids-compartidos-inconsistentes, fichas-del-proveedor-copiadas, cambios-incompatibles-sin-version]
skills: [crear-contrato, versionar-contrato]
---

# Fase: registrar-contrato

## Objetivo

Que este repositorio tenga su contrato al día, citando la ficha del proveedor, y que el registro lo refleje.

## Entradas

- El `id_compartido`, el rol y la compatibilidad del cambio (de `identificar-contrato`).

## Pasos

1. Contrato nuevo en este repositorio → skill `crear-contrato`.
2. Cambio incompatible → skill `versionar-contrato`.
3. Cambio compatible de un contrato existente → edita su «Forma (resumen)» y, si cambia, `consumidores`; `method`, `path` y `version` no cambian (si cambiaran, el cambio es incompatible).
4. En el consumidor, aplica el lado técnico de `$P/referencia/contratos-api.md`: tipos generados si hay OpenAPI, una sola capa de adaptación, errores por código.
5. Regenera el registro: `python3 $P/scripts/contratos.py registro`.

## Criterio de salida

- El contrato tiene `id_compartido`, `rol`, `method`, `path`, `version`, `proveedor` y, en un consumidor, `ficha_proveedor`.
- Ninguna ficha ni OpenAPI del proveedor copiada en este repositorio.
- `REGISTRO.md` regenerado.
