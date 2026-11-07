---
fase: revisar-cobertura
resuelve: [cobertura-desconocida]
skills: [actualizar-matriz]
---

# Fase: revisar cobertura

Solo si la persona lo pide, al adoptar uxyngraphar o al registrar una EVO de tipo `cobertura` o `paquete-nuevo`. Si no, esta fase no se recorre.

## Objetivo

Que `MATRIZ-COBERTURA.md` diga qué dimensiones del proyecto cubren los paquetes instalados y qué EVO trata cada hueco.

## Entradas

- Los paquetes instalados (`uxyngraphar/paquetes/`).
- `uxyngraphar/trabajo/evolucion-del-sistema/MATRIZ-COBERTURA.md`, si existe.

## Pasos

1. Aplica `actualizar-matriz`.
2. Presenta a la persona las filas que cambiarían; la matriz la edita ella o una instrucción aprobada.

## Criterio de salida

- La matriz existe y la persona tiene la propuesta de filas con su estado (C, P, F) y la EVO de cada hueco.
