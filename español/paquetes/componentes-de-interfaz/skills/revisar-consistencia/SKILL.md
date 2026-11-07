---
name: revisar-consistencia
description: Revisa los componentes de unas pantallas contra los tokens y componentes compartidos del inventario y los ocho estados interactivos, y anota cada hallazgo en INTERFAZ.md.
resuelve: [interfaz-inconsistente]
---

# Revisar consistencia

## Cuándo usarla

- En `revisar`, sobre los archivos de las pantallas del pedido.
- En `corregir`, sobre lo que acabas de cambiar, antes de dar el hallazgo por corregido.

## Pasos

1. Ten a mano el inventario de `INTERFAZ.md` (tokens y componentes compartidos).
2. Busca valores sueltos en los archivos de las pantallas: colores hex o `rgb(`, tamaños en `px` fuera de la escala de espaciado, familias tipográficas, radios y sombras escritos a mano. Cada uno es un hallazgo `valor-suelto` con su `ruta:línea`.
3. Busca componentes propios de la pantalla que repitan uno compartido (dos botones primarios distintos, tres modales): hallazgo `duplicado`.
4. En cada componente interactivo, comprueba los estados de `referencia/consistencia-ui.md`: normal, hover, foco visible, activo, deshabilitado, carga, vacío y error. Cada uno que falte es un hallazgo `estado-sin-cubrir`.
5. Comprueba la jerarquía: una sola acción primaria por vista y las secundarias subordinadas (`jerarquia`).
6. Anota cada hallazgo; la corrección nombra el token o componente existente que lo resuelve. Formato:

   ```
   | 1 | /signup | valor-suelto | Azul del botón escrito a mano | `src/signup/form.module.css:12` (`#3b82f6`) | Token `--color-primario` | | pendiente |
   ```

## Resultado

- Hallazgos con tipo, evidencia y corrección, o la constancia en «Notas» de que las pantallas usan tokens y componentes de forma consistente.
