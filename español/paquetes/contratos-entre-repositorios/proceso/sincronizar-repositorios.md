---
fase: sincronizar-repositorios
resuelve: [contratos-divergentes-entre-repositorios, consumidor-fusionado-antes-que-proveedor]
skills: [comparar-repositorios]
---

# Fase: sincronizar-repositorios

## Objetivo

Confirmar que el contrato coincide con el del repositorio hermano y que el orden de merge (proveedor primero) se respeta.

## Entradas

- El contrato registrado.
- `otros_repos` en los ajustes, si el repositorio hermano está al lado.

## Pasos

1. Aplica la skill `comparar-repositorios`.
2. En el proveedor: el contrato y su ficha de `rutas-de-api` se fusionan primero; anota en el PR qué consumidores esperan.
3. En el consumidor: comprueba que el cambio del proveedor ya está fusionado. Si no, deja el PR abierto y dilo al cerrar; no lo des por terminado (límite 3).
4. Recorre la lista del PR del consumidor de `$P/referencia/sincronizar.md`.

## Criterio de salida

- `contratos.py comparar` sin divergencias, o el repositorio hermano no está disponible y se dice.
- En el consumidor: el proveedor ya fusionó, o el PR queda explícitamente a la espera.
