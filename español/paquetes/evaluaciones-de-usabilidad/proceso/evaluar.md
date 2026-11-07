---
fase: evaluar
resuelve: [problemas-de-usabilidad-sin-evidencia, mejoras-sin-medicion]
skills: [registrar-problema, medir-metrica]
---

# Fase: evaluar

## Objetivo

Encontrar los problemas reales de las pantallas acotadas, cada uno con su evidencia, y medir el punto de partida.

## Entradas

- La ficha en `en-curso` con alcance y tareas.
- `referencia/heuristicas.md` (códigos y severidad) y `referencia/metricas.md`.
- Los componentes del proyecto que aparecen en las pantallas del alcance.

## Pasos

1. Recorre cada tarea del usuario paso a paso en las pantallas del alcance y pregúntate cada heurística de `referencia/heuristicas.md`.
2. Lo que impida o entorpezca la tarea por accesibilidad (`A11Y`), por inconsistencia visual (`UI`) o por lentitud percibida (`RENDIMIENTO`) también se registra, con su evidencia. Si existen `uxyngraphar/trabajo/pautas-de-accesibilidad/ACCESIBILIDAD.md` o `uxyngraphar/trabajo/componentes-de-interfaz/INTERFAZ.md`, léelos: sus hallazgos sobre estas pantallas sirven de evidencia (cita el documento y el número de hallazgo).
3. Registra cada problema con la skill `registrar-problema`. Lo que no tenga evidencia va a «Notas»; lo que esté fuera del alcance, también.
4. Elige al menos una métrica ligada a las tareas y mide «Antes» con la skill `medir-metrica`.
5. Ejecuta `python3 $P/scripts/verificar-evaluaciones.py` y corrige lo que señale en la ficha.

## Criterio de salida

- Tabla «Problemas» con heurística válida, severidad 0–4 y evidencia en cada fila; la columna «Aprobada» vacía.
- Al menos una métrica con «Antes», «Objetivo» y «Fuente».
- `verificar-evaluaciones.py` sin errores.
