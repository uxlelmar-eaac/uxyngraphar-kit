# Límites

Se cumplen en todo el trabajo del paquete.

1. **Registrar, no implementar.** Una mejora se implementa solo cuando una persona la aprueba (`approved`) y, si se usa `instrucciones-aprobadas`, mediante una instrucción aprobada que la cite.
2. **Máximo `max_por_tarea` (3) fichas nuevas por tarea.** Prioriza; agrupa problemas de la misma causa en una sola ficha.
3. **Evidencia obligatoria:** `ruta:línea`, salida de un comando o pasos para reproducir.
4. **Sin duplicados:** si ya existe, añade evidencia a la ficha existente en lugar de crear otra.
5. **Solo una persona aprueba o rechaza** (`approved`, `rejected`).
6. **Clasifica** cada ficha: `tipo` (`bug`, `deuda-tecnica`, `rendimiento`, `seguridad`, `dx`), `severidad` (`critica`, `alta`, `media`, `baja`) y `prioridad` propuesta (`ahora`, `pronto`, `despues`).
7. **Nada se borra.** Lo que ya no aplica va a `archived`; lo que una persona quiere retirar, a `para-eliminar`.

## Cuándo detenerse y preguntar

- Ya registraste `max_por_tarea` fichas en esta tarea y aparece otro problema.
- El problema es de seguridad o de pérdida de datos (`severidad: critica`): avisa en el momento, no solo con la ficha.
- No está claro si el problema es parte del pedido o está fuera de alcance.
- Una mejora `approved` exige más de lo que dice su ficha (otro módulo, una decisión de arquitectura).
