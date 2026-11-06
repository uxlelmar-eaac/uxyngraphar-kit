# Mejoras pendientes

Activado con «usa el paquete mejoras-pendientes» / «sigue el protocolo mejoras» o por `uxyngraphar/FLUJO.json`. `S=uxyngraphar/paquetes/mejoras-pendientes/scripts`.

1. Integridad: `python3 $S/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee las **Reglas** (al final de este archivo).
3. Si durante una tarea detectas deuda o un bug fuera de alcance: `python3 $S/comun/fichas.py nueva mejora --slug <slug> --titulo "…"` con evidencia. **No lo implementes.**
4. Antes de registrar, revisa duplicados: `python3 $S/comun/fichas.py listar mejora --status pending`.
5. Antes de terminar: `python3 $S/comun/verificar.py`.

## Reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Registrar, no implementar.** Una mejora se implementa solo cuando una persona la aprueba (`approved`) y, si se usa `ciclo-instrucciones`, mediante una instrucción aprobada que la cite.
2. **Máximo `max_por_tarea` (3) fichas nuevas por tarea.** Prioriza; agrupa problemas de la misma causa.
3. **Evidencia obligatoria:** `ruta:línea`, salida de un comando o pasos para reproducir.
4. **Sin duplicados:** si ya existe, añade evidencia a la ficha existente en lugar de crear otra.
5. **Solo una persona aprueba o rechaza** (`approved`, `rejected`).
6. Clasifica: `tipo` (`bug`, `deuda-tecnica`, `rendimiento`, `seguridad`, `dx`), `severidad` y `prioridad` (`ahora`, `pronto`, `despues`).
