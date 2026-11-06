# Experiencia de usuario

Activado con «usa el paquete experiencia-de-usuario» / «sigue el protocolo optimizacion ux» o por `uxyngraphar/FLUJO.json`. `S=uxyngraphar/paquetes/experiencia-de-usuario/scripts`.

1. Integridad: `python3 $S/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee las **Reglas** (al final de este archivo); según el foco, `docs/heuristicas.md`, `docs/consistencia-ui.md`, `docs/accesibilidad.md` y `docs/metricas.md`.
3. Abre la evaluación: `python3 $S/comun/fichas.py nueva evaluacion --slug <pantalla-o-flujo> --titulo "…"`. Define alcance y tareas del usuario **antes** de evaluar; pásala a `en-curso`.
4. Evalúa: cada problema en la tabla con heurística, severidad 0–4, evidencia y propuesta. Mide las métricas de partida (columna «Antes»).
5. Pasa a `propuesta` y **detente**: la persona revisa y marca `aprobada` (`--humano`).
6. Solo con la evaluación `aprobada`, implementa las propuestas aprobadas; pásala a `implementada` y mide «Después». `validada` la marca una persona.
7. Antes de terminar: `python3 $S/comun/verificar.py` y `python3 $S/verificar-ux.py`.

## Reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel. Valores ajustables en `uxyngraphar/trabajo/experiencia-de-usuario/ajustes.json`.

1. **Evaluar antes de tocar.** Ningún cambio de interfaz sin evaluación con alcance (pantallas o flujos) y tareas del usuario definidas.
2. **Cada problema, con heurística, severidad y evidencia.** Heurística: `H1`–`H10` (Nielsen, ver `docs/heuristicas.md`), `A11Y`, `UI` (consistencia visual) o `RENDIMIENTO`. Severidad 0–4 (0 no es problema · 1 cosmético · 2 menor · 3 mayor · 4 catástrofe). Evidencia: captura, `ruta:línea`, paso reproducible o medición. Sin evidencia es opinión: va a Notas.
3. **Severidad ≥ 3 exige propuesta** concreta (qué cambia, dónde) en la misma fila.
4. **Métricas antes/después.** Toda evaluación registra al menos una métrica con valor «Antes», objetivo y fuente (Lighthouse, analítica, prueba con usuarios, conteo de pasos). `validada` exige «Después» medido en todas.
5. **Aprobación humana.** `aprobada` y `validada` solo las marca una persona. Sin `aprobada` no se implementa nada; se implementan **solo** las filas aprobadas (las demás quedan como propuesta).
6. **Consistencia antes que novedad.** Se reutilizan los componentes y tokens existentes (color, espaciado, tipografía, radios); un componente o token nuevo se justifica en la propuesta.
7. **Estados completos.** Todo componente tocado cubre: normal, hover, foco, activo, deshabilitado, carga, vacío y error.
8. **Accesibilidad mínima WCAG 2.2 AA** en todo lo que se toque (ver `docs/accesibilidad.md`); un cambio que empeore la accesibilidad no se valida aunque mejore otra métrica.
9. **Sin regresiones.** Si una métrica empeora tras implementar, se anota en la ficha y se decide con la persona antes de seguir.
10. **Alcance.** Fuera del alcance de la evaluación no se cambia nada; lo que se detecte fuera va a Notas como posible evaluación futura.
