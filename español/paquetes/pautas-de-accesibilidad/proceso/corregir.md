---
fase: corregir
resuelve: [barreras-de-accesibilidad]
skills: []
---

# Fase: corregir

Solo si la persona marcó «sí» en alguna barrera. Si no aprobó ninguna, esta fase y la siguiente no se recorren.

## Objetivo

Aplicar en el código las correcciones aprobadas, en el origen de cada barrera.

## Entradas

- La revisión en `ACCESIBILIDAD.md` y sus barreras con «sí» en «Aprobada».

## Pasos

1. Corrige solo las barreras aprobadas, empezando por las bloqueantes.
2. Si la barrera viene de un componente o token compartido, corrige el componente o el token. Si eso cambia su aspecto en otras pantallas o exige un token nuevo, **detente** y pregunta.
3. Prefiere elementos nativos (`button`, `a`, `label`) a ARIA; añade ARIA solo cuando no hay nativo.
4. Lo que encuentres fuera de las pantallas del pedido va a «Notas» de la revisión; no lo corrijas.

## Criterio de salida

- Todas las barreras aprobadas tienen su corrección en el código; ninguna sin aprobar se tocó.
