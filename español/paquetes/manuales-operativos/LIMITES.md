# Límites

Se cumplen en todo el trabajo del paquete.

1. **Pasos ejecutables:** comandos exactos, en orden, con el resultado esperado de cada uno.
2. **Sin secretos:** variables como `<PLACEHOLDER>` y de dónde se obtienen, nunca valores.
3. **Vivo:** un cambio que altera un procedimiento actualiza su manual en la misma tarea; anota la fecha en «Última verificación».
4. **`vigente` lo decide una persona** tras probarlo; el agente deja `borrador`.
5. **Un procedimiento por manual**; enlaza otros en lugar de copiarlos.
6. Incluye siempre «Cómo revertir» cuando el procedimiento cambia el sistema.
7. **El agente no ejecuta el procedimiento** sobre entornos reales para «probarlo»: lo redacta y lo entrega a la persona.

## Cuándo detenerse y preguntar

- Un paso necesita un valor secreto o un acceso que no conoces: pregunta de dónde se obtiene, no lo inventes.
- No sabes cuál es el resultado esperado de un comando ni puedes deducirlo del código o la configuración.
- El procedimiento no tiene forma conocida de revertirse.
- Tu cambio contradice un manual `vigente` y el pedido no dice cuál manda.
