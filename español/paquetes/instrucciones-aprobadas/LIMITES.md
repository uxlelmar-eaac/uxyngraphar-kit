# Límites

Se cumplen en todo el trabajo del paquete. Cambiar un límite o un ajuste lo decide una persona.

1. **Sin instrucción aprobada no hay cambios.** Ningún archivo de código o documentación del producto se edita sin una instrucción en `instrucciones/en-progreso/` con `status: approved`.
2. **Solo una persona aprueba.** El agente nunca pone `approved` ni ejecuta `ciclo.py aprobar`; tampoco edita `approved_at`.
3. **Alcance acotado.** Máximo `max_archivos_codigo` archivos de código (5 por defecto) y `max_docs` documentos (8) por instrucción. Si hace falta más:
   - Si no es imprescindible, fracciona en varias instrucciones (`fraccion_de`, `depende_de`).
   - Si lo es, declara `ampliacion_factor` entre 1.5 y `ampliacion_factor_max` con `ampliacion_justificacion` y espera aprobación.
4. **Solo dentro de las anclas.** Implementa únicamente en `anclas_codigo` (`ruta` o `ruta:inicio-fin`). Si descubres que necesitas otro archivo, detente y propón ampliar la instrucción.
5. **Contexto mínimo.** Lee lo que imprime `ciclo.py contexto`; no explores el repo por tu cuenta ni reabras lo ya leído. Presupuesto y qué leer por tipo de tarea: `referencia/eficiencia.md`.
6. **Estado = carpeta.** Cambia de estado con `fichas.py estado` o `ciclo.py`; nunca muevas fichas a mano.
7. **Cierre honesto.** Al cerrar, marca los criterios cumplidos, anota lo que quedó fuera y ejecuta `verificar-ciclo.py`.
8. **Fuera de alcance no se implementa.** Se anota en la instrucción para que la persona decida.
9. **Lo aprobado no se amplía en silencio.** Cambiar el alcance, las anclas o la `lectura_minima` de una instrucción aprobada exige una nueva aprobación de la persona: detente y pídela.

## Cuándo detenerse y preguntar

- El pedido es ambiguo en algo que cambia el resultado (alcance, comportamiento visible, datos, compatibilidad) y la persona no lo ha decidido: pregúntalo antes de redactar (con `preguntas-de-clarificacion`, si está instalado); nunca lo supongas en la instrucción.
- Durante la implementación aparece un archivo necesario que no está en `anclas_codigo`.
- `ciclo.py contexto` responde `BLOQUEADO` (instrucción sin aprobar o alcance incumplido).
- El contexto impreso marca algo como `OMITIDO (presupuesto)` y sin eso no puedes implementar con seguridad.
- La instrucción contradice una ADR aceptada o una regla de otro paquete activo.
