# Ciclo de instrucciones — reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Sin instrucción aprobada no hay cambios.** Ningún archivo de código o documentación del producto se edita sin una instrucción en `instrucciones/en-progreso/` con `status: approved`.
2. **Solo una persona aprueba.** El agente nunca pone `approved` ni ejecuta `ciclo.py aprobar`; tampoco edita `approved_at`.
3. **Alcance acotado.** Máximo `max_archivos_codigo` archivos de código (5 por defecto) y `max_docs` documentos (8) por instrucción. Si hace falta más:
   - Si no es imprescindible, fracciona en varias instrucciones (`fraccion_de`, `depende_de`).
   - Si lo es, declara `ampliacion_factor` entre 1.5 y `ampliacion_factor_max` con `ampliacion_justificacion` y espera aprobación.
4. **Solo dentro de las anclas.** Implementa únicamente en `anclas_codigo` (`ruta` o `ruta:inicio-fin`). Si descubres que necesitas otro archivo, detente y propón ampliar la instrucción.
5. **Contexto mínimo.** Lee lo que imprime `ciclo.py contexto`; no explores el repo por tu cuenta.
6. **Estado = carpeta.** Cambia de estado con `fichas.py estado` o `ciclo.py`; nunca muevas fichas a mano.
7. **Cierre honesto.** Al cerrar, marca los criterios cumplidos, anota lo que quedó fuera y ejecuta `verificar-ciclo.py`.
8. **Fuera de alcance no se implementa.** Se anota en la instrucción para que la persona decida.
