---
fase: corregir
resuelve: [interfaz-inconsistente]
skills: [revisar-consistencia]
---

# Fase: corregir

Solo si la persona marcó «sí» en algún hallazgo. Si no aprobó ninguno, esta fase no se recorre.

## Objetivo

Aplicar las correcciones aprobadas con los tokens y componentes existentes, sin dejar estados sin cubrir.

## Entradas

- La revisión en `INTERFAZ.md` y sus hallazgos con «sí» en «Aprobada».

## Pasos

1. Corrige solo los hallazgos aprobados: sustituye cada valor suelto por su token y cada componente duplicado por el compartido que nombra la corrección.
2. En cada componente interactivo que toques, cubre los ocho estados (normal, hover, foco visible, activo, deshabilitado, carga, vacío, error).
3. Si una corrección exige crear o cambiar un token o un componente compartido que la persona no aprobó expresamente, **detente** y pregunta.
4. Vuelve a aplicar `revisar-consistencia` sobre lo tocado: los hallazgos corregidos ya no aparecen y no hay hallazgos nuevos. Pasa cada uno a `corregido`.
5. Lo que encuentres fuera de las pantallas del pedido va a «Notas» de la revisión; no lo corrijas.
6. Ejecuta `python3 $P/scripts/comun/verificar.py` y dile a la persona qué quedó corregido y qué sigue pendiente.

## Criterio de salida

- Cada hallazgo aprobado en `corregido`, comprobado con `revisar-consistencia`; ninguno sin aprobar se tocó.
- Los componentes tocados cubren los ocho estados y `verificar.py` no da errores.
