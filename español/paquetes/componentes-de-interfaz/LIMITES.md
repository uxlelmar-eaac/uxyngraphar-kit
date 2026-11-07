# Límites

Se cumplen en todo el trabajo del paquete.

1. **Tokens antes que valores sueltos.** Color, espaciado, tipografía, radios y sombras salen de los tokens del proyecto; un valor escrito a mano en un componente es un hallazgo.
2. **Un propósito, un componente.** Antes de crear un componente se busca en `INTERFAZ.md` y en la carpeta de componentes compartidos; si existe pero no encaja, se propone extenderlo.
3. **Ocho estados.** Todo componente interactivo que se revise o se toque cubre: normal, hover, foco visible, activo, deshabilitado, carga, vacío y error.
4. **Una acción primaria por vista**; las secundarias, visualmente subordinadas.
5. **Cada hallazgo, con evidencia y solución existente.** Evidencia: `ruta:línea` o captura. La corrección nombra el token o componente existente que lo resuelve; uno nuevo se justifica en la misma celda.
6. **Corrección aprobada por una persona.** Se corrigen solo los hallazgos con «sí» en «Aprobada»; esa columna la rellena la persona, nunca el agente. También vale una fila `UI` con «sí» de una evaluación `UXE-…` en `aprobada` de `uxyngraphar/trabajo/evaluaciones-de-usabilidad/`, si existe.
7. **No se cambia el sistema de diseño.** No se crean ni modifican tokens ni componentes compartidos sin aprobación expresa; cambiar uno afecta a todas las pantallas que lo usan.
8. **Alcance.** Solo las pantallas del pedido. Lo que se vea fuera se anota en «Notas» de la revisión.

## Cuándo detenerse y preguntar

- Al terminar `revisar`: siempre. La persona decide qué hallazgos se corrigen.
- El proyecto no tiene tokens o componentes compartidos localizables.
- La única corrección posible exige un token o componente nuevo, o cambiar uno compartido.
- Dos componentes compartidos sirven para lo mismo y hay que elegir cuál queda.
