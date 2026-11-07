# Límites

Se cumplen en todo el trabajo del paquete.

1. **El agente prepara, la persona decide.** Nunca escribas en la columna «Decisión» de `REVISION.md` ni ejecutes `revision.py aplicar`.
2. **Estado real:** una ficha que espera decisión afirma que su efecto no está aplicado. Si ya lo está, avisa: el status es incorrecto.
3. **Contexto suficiente, no más:** para cada fila, una o dos líneas con qué se decide y qué pasa si se aprueba; enlaza la ficha en lugar de copiarla.
4. **Lo antiguo primero:** las fichas con más de `dias_aviso` (14) días esperando se señalan; propón decidirlas o cerrarlas.
5. **Las decisiones se aplican con el comando del paquete dueño.** Nunca muevas una ficha de carpeta ni cambies su status a mano para reflejar una decisión: `aplicar` llama al comando que cada paquete declara (por ejemplo, `ciclo.py aprobar`, que comprueba el alcance).
6. **No edites las fichas de otros paquetes** desde este paquete: si una necesita cambios antes de decidirse, dilo en el resumen y que se corrija con su propio paquete.
7. **No recomiendes como si fuera la decisión.** Puedes señalar riesgos o dependencias, pero el resumen no dice qué opción elegir salvo que la persona lo pida.

## Cuándo detenerse y preguntar

- Una ficha parece tener el status incorrecto (su efecto ya está aplicado o la ficha está incompleta).
- Dos fichas pendientes se contradicen (por ejemplo, dos ADR propuestas que eligen opciones incompatibles).
- `aplicar` dejó filas con `FALLÓ` y el motivo exige corregir la ficha en su paquete.
- La persona te pide que escribas tú las decisiones o que ejecutes `aplicar`.
