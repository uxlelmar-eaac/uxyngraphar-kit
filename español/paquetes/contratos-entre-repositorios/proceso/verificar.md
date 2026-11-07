---
fase: verificar
resuelve: [ids-compartidos-inconsistentes, contratos-divergentes-entre-repositorios]
skills: []
---

# Fase: verificar

## Objetivo

Demostrar que los contratos de este repositorio son coherentes entre sí y con los repositorios hermanos presentes.

## Entradas

- Los contratos creados o tocados.

## Pasos

1. Ejecuta `python3 $P/scripts/verificar-contratos.py`.
2. Errores que se corrigen ahora: `id_compartido … debe ser modulo.recurso.accion`, `id_compartido … repetido`, `rol … debe ser proveedor | consumidor | bff`, `vigente sin method o path` y cualquier divergencia con un hermano.
3. `aviso: … consumidor vigente sin ficha_proveedor`: cita la ficha del proveedor.
4. Ejecuta `python3 $P/scripts/comun/verificar.py`.

## Criterio de salida

- `verificar-contratos.py` termina con código 0.
- `verificar.py` sin errores.
