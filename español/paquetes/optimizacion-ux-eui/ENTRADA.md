# Optimización UX/UI — entrada

Activado con «usa el paquete optimizacion-ux-eui» / «sigue el protocolo optimizacion ux» o por `uxyngraphar-work/FLUJO.json`. `S=uxyngraphar/optimizacion-ux-eui/scripts`.

1. Integridad: `python3 $S/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee `uxyngraphar/optimizacion-ux-eui/REGLAS.md`; según el foco, `guias/heuristicas.md`, `guias/consistencia-ui.md`, `guias/accesibilidad.md` y `guias/metricas.md`.
3. Abre la evaluación: `python3 $S/fichas.py nueva evaluacion --slug <pantalla-o-flujo> --titulo "…"`. Define alcance y tareas del usuario **antes** de evaluar; pásala a `en-curso`.
4. Evalúa: cada problema en la tabla con heurística, severidad 0–4, evidencia y propuesta. Mide las métricas de partida (columna «Antes»).
5. Pasa a `propuesta` y **detente**: la persona revisa y marca `aprobada` (`--humano`).
6. Solo con la evaluación `aprobada`, implementa las propuestas aprobadas; pásala a `implementada` y mide «Después». `validada` la marca una persona.
7. Antes de terminar: `python3 $S/verificar.py` y `python3 $S/verificar-ux.py`.
