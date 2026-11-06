# Ciclo de instrucciones

Activado con «usa el paquete instrucciones-aprobadas» / «sigue el protocolo uxyngraphar» (frases en el manifiesto) o por `uxyngraphar/FLUJO.json`. Rutas relativas a la raíz de la app. `S=uxyngraphar/paquetes/instrucciones-aprobadas/scripts`.

1. Integridad: `python3 $S/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee las **Reglas** (al final de este archivo). Para orientarte, si existe, `uxyngraphar/trabajo/instrucciones-aprobadas/ESTADO.md` (nada más del historial).
3. **Preguntas** (si `ajustes.preguntas` es true y el pedido no dice «salta preguntas»): decide en el chat con la persona y registra `python3 $S/comun/fichas.py nueva pregunta --slug <slug>`. Guía: `docs/preguntas.md`.
4. **Instrucción**: `python3 $S/comun/fichas.py nueva instruccion --slug <slug> --titulo "…"` (cambio pequeño: `--variante compacta`; sin código: `--variante solo-docs`; primera vez en el repo: `--variante adopcion`); rellena alcance, `anclas_codigo` y criterios. **Espera** a que una persona la apruebe (`python3 $S/ciclo.py aprobar <id> --humano`). Sin `approved` no edites código ni documentación.
5. **Contexto**: `python3 $S/ciclo.py contexto <id>` imprime ficha, lectura mínima y anclas con rango. No abras nada más.
6. **Implementa** solo dentro de `anclas_codigo`. Deuda o bugs fuera de alcance: anótalos en la sección «Fuera de alcance» de la instrucción; no los implementes.
7. **Cierre**: `python3 $S/ciclo.py cerrar <id>` (actualiza `ESTADO.md`) y luego `python3 $S/verificar-ciclo.py`.

Trabajo: `uxyngraphar/trabajo/instrucciones-aprobadas/{instrucciones,preguntas}/<estado>/`. Ajustes (persona): `uxyngraphar/trabajo/instrucciones-aprobadas/ajustes.json`.

## Reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Sin instrucción aprobada no hay cambios.** Ningún archivo de código o documentación del producto se edita sin una instrucción en `instrucciones/en-progreso/` con `status: approved`.
2. **Solo una persona aprueba.** El agente nunca pone `approved` ni ejecuta `ciclo.py aprobar`; tampoco edita `approved_at`.
3. **Alcance acotado.** Máximo `max_archivos_codigo` archivos de código (5 por defecto) y `max_docs` documentos (8) por instrucción. Si hace falta más:
   - Si no es imprescindible, fracciona en varias instrucciones (`fraccion_de`, `depende_de`).
   - Si lo es, declara `ampliacion_factor` entre 1.5 y `ampliacion_factor_max` con `ampliacion_justificacion` y espera aprobación.
4. **Solo dentro de las anclas.** Implementa únicamente en `anclas_codigo` (`ruta` o `ruta:inicio-fin`). Si descubres que necesitas otro archivo, detente y propón ampliar la instrucción.
5. **Contexto mínimo.** Lee lo que imprime `ciclo.py contexto`; no explores el repo por tu cuenta ni reabras lo ya leído. Presupuesto y qué leer por tipo de tarea: `docs/eficiencia.md`.
6. **Estado = carpeta.** Cambia de estado con `fichas.py estado` o `ciclo.py`; nunca muevas fichas a mano.
7. **Cierre honesto.** Al cerrar, marca los criterios cumplidos, anota lo que quedó fuera y ejecuta `verificar-ciclo.py`.
8. **Fuera de alcance no se implementa.** Se anota en la instrucción para que la persona decida.
