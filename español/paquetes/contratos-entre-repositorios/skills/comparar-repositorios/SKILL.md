---
name: comparar-repositorios
description: Compara los contratos vigentes de consumidor de este repositorio con los del repositorio proveedor que está al lado e interpreta cada divergencia.
resuelve: [contratos-divergentes-entre-repositorios]
---

# Comparar repositorios

## Cuándo usarla

- Antes de cerrar un cambio de consumidor (fase `sincronizar-repositorios`).
- Cuando la persona pide comprobar que los repositorios están alineados.

## Pasos

1. Ejecuta `python3 $P/scripts/contratos.py comparar` (usa `otros_repos`) o `python3 $P/scripts/contratos.py comparar ../mi-api` para una ruta concreta.
2. Solo se comparan contratos `vigente` con `rol: consumidor` cuyo `proveedor` coincide con el nombre de la carpeta de un hermano.
3. Interpreta cada línea:
   - `aviso: <ruta>: no está o no tiene uxyngraphar/trabajo/`: el hermano no está disponible; dilo al cerrar.
   - `divergencia: CON-…: mi-api no documenta «orders.list» ni GET /orders`: el proveedor no tiene ni el contrato ni la ficha de ruta; el cambio del proveedor falta o no se ha fusionado.
   - `divergencia: CON-…: version «v1» aquí, «v2» en mi-api`: alinea con el proveedor o detente si no está claro cuál es el bueno.
   - `aviso: CON-…: el proveedor lo marca «deprecado»`: planifica la migración a la versión nueva.
4. Código 1 si hay divergencias.

## Resultado

- Lista de divergencias y avisos con la acción para cada una, o confirmación de que los repositorios están alineados.
