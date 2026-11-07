# Límites

Se cumplen en todo el trabajo del paquete.

1. **Mínimo WCAG 2.2 AA** en todo lo que se revise o se toque (`referencia/accesibilidad.md`).
2. **Automático y manual.** Una revisión no se da por hecha solo con Lighthouse o axe: incluye el recorrido de la tarea principal solo con teclado.
3. **Cada barrera, con criterio y evidencia.** Criterio: el punto de `referencia/accesibilidad.md` que incumple. Evidencia: `ruta:línea`, captura, paso reproducible («Tab desde el campo correo salta el botón») o medición (contraste 3.1:1). Sin evidencia no entra en la tabla.
4. **Lo que impide completar la tarea es «bloqueante».** Se corrige antes que cualquier otra barrera.
5. **Corrección aprobada por una persona.** Se corrigen solo las barreras con «sí» en «Aprobada»; esa columna la rellena la persona, nunca el agente. También vale una fila `A11Y` con «sí» de una evaluación `UXE-…` en `aprobada` de `uxyngraphar/trabajo/evaluaciones-de-usabilidad/`, si existe.
6. **Corregir en el origen.** Si la barrera viene de un componente o token compartido, la corrección va al componente o al token, no a una copia en la pantalla.
7. **Comprobar con la misma herramienta.** Una barrera pasa a `corregida` solo tras repetir la comprobación que la encontró; la puntuación automática no puede bajar.
8. **Alcance.** Solo las pantallas del pedido. Lo que se vea fuera se anota en «Notas» de la revisión.

## Cuándo detenerse y preguntar

- Al terminar `revisar`: siempre. La persona decide qué barreras se corrigen.
- La corrección exige cambiar un token de color, el diseño de un componente compartido o el sistema de diseño global.
- No hay forma de comprobar con teclado o con una herramienta automática (la app no arranca, falta acceso).
- Corregir una barrera rompe otra cosa (un flujo, otra pantalla o una métrica que la persona sigue).
