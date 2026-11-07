# Límites

Se cumplen en todo el trabajo del paquete. Valores ajustables en `uxyngraphar/trabajo/evaluaciones-de-usabilidad/ajustes.json`.

1. **Evaluar antes de tocar.** Ningún cambio de interfaz sin evaluación con alcance (pantallas o flujos) y tareas del usuario definidas.
2. **Cada problema, con heurística, severidad y evidencia.** Heurística: `H1`–`H10` (Nielsen, ver `referencia/heuristicas.md`), `A11Y` (accesibilidad), `UI` (consistencia visual) o `RENDIMIENTO`. Severidad 0–4 (0 no es problema · 1 cosmético · 2 menor · 3 mayor · 4 catástrofe). Evidencia: captura, `ruta:línea`, paso reproducible o medición. Sin evidencia es opinión: va a «Notas».
3. **Severidad ≥ 3 exige propuesta** concreta (qué cambia, dónde) en la misma fila (`severidad_propuesta_obligatoria`).
4. **Métricas antes/después.** Toda evaluación registra al menos una métrica con valor «Antes», objetivo y fuente (Lighthouse, analítica, prueba con usuarios, conteo de pasos). `validada` exige «Después» medido en todas, con la misma fuente que «Antes».
5. **Aprobación humana.** `aprobada` y `validada` solo las marca una persona, igual que la columna «Aprobada». Sin `aprobada` no se implementa nada; se implementan **solo** las filas aprobadas (las demás quedan como propuesta).
6. **Reutilizar lo existente.** Las propuestas usan los componentes y tokens del proyecto; uno nuevo se justifica en la propia propuesta.
7. **Sin regresiones ocultas.** Si una métrica empeora tras implementar, o la puntuación de accesibilidad baja, se anota en la ficha y se decide con la persona antes de seguir; una mejora que empeore la accesibilidad no se valida.
8. **Alcance.** Fuera del alcance de la evaluación no se cambia nada; lo que se detecte fuera va a «Notas» como posible evaluación futura (o a `deuda-y-mejoras` si es un bug).

## Cuándo detenerse y preguntar

- Al pasar la evaluación a `propuesta`: siempre. La persona aprueba antes de implementar.
- Las tareas del usuario no están claras o el pedido no dice qué pantallas entran.
- La única propuesta posible exige un token o componente nuevo, o cambiar el sistema de diseño global.
- Una métrica empeora tras implementar, o una mejora de una métrica empeora la accesibilidad.
- No hay forma de medir «Antes» con una fuente que luego se pueda repetir.
- El pedido es en realidad una revisión completa de accesibilidad o de consistencia visual: propón `pautas-de-accesibilidad` o `componentes-de-interfaz`.
