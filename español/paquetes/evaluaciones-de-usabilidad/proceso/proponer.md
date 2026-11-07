---
fase: proponer
resuelve: [cambios-de-interfaz-sin-aprobacion]
skills: []
---

# Fase: proponer

## Objetivo

Dejar en la ficha una propuesta concreta por problema importante y entregar la decisión a la persona.

## Entradas

- La ficha evaluada (problemas y métricas «Antes»).

## Pasos

1. En cada fila con severidad ≥ `severidad_propuesta_obligatoria` (3 por defecto), escribe en «Propuesta» qué cambia y dónde (`componente`, archivo o pantalla). En las de menor severidad, propón si es barato o déjalo en `-`.
2. Cada propuesta reutiliza tokens y componentes existentes; si necesita uno nuevo, justifícalo en la misma celda.
3. Ordena la conversación por severidad: primero los 4 y 3, luego el resto.
4. Pasa la ficha a `propuesta`: `python3 $P/scripts/comun/fichas.py estado UXE-… propuesta`.
5. Ejecuta `python3 $P/scripts/verificar-evaluaciones.py` (exige propuestas en severidad alta y métricas con «Antes»).
6. **Detente.** Resume a la persona los problemas por severidad y dile qué debe decidir: marcar «sí» en la columna «Aprobada» de las filas que quiere y pasar la ficha a `aprobada` con `--humano`.

## Criterio de salida

- Ficha en `propuesta`, con propuesta en todas las filas de severidad alta y `verificar-evaluaciones.py` sin errores.
- La persona tiene el resumen y sabe qué tiene que aprobar.
