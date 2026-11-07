---
name: actualizar-matriz
description: Crea MATRIZ-COBERTURA.md si falta con evolucion.py matriz y propone filas por dimensión del proyecto (servidor, cliente, multi-repositorio) con su estado C, P o F y la EVO que trata cada hueco.
resuelve: [cobertura-desconocida]
---

# Actualizar matriz

## Cuándo usarla

- En la fase `revisar-cobertura`.
- Al cerrar una EVO de tipo `cobertura` o `paquete-nuevo`.

## Pasos

1. Ejecuta `python3 $P/scripts/evolucion.py matriz`: crea `uxyngraphar/trabajo/evolucion-del-sistema/MATRIZ-COBERTURA.md` desde la plantilla si falta y la muestra.
2. Lista los paquetes instalados (`ls uxyngraphar/paquetes/`) y, para cada dimensión que el proyecto necesita (cambios aprobados, reglas propias, arquitectura, contratos, rutas, documentación…), decide si está cubierta en servidor/API, cliente/UI y multi-repositorio: **C** cubierto, **P** parcial, **F** falta.
3. Para cada **P** o **F**, busca la EVO que lo trata (`fichas.py listar evo`) o propón registrarla (fase `registrar-evo`).
4. Presenta a la persona las filas nuevas o cambiadas en el formato de la tabla; no edites la matriz sin su visto bueno.

## Resultado

- Matriz creada y una propuesta de filas que la persona puede copiar o aprobar.
