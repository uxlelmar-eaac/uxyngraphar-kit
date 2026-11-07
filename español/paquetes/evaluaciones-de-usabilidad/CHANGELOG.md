# Cambios

## 1.0.0

- Nace de dividir `experiencia-de-usuario` (1.1.0) en tres paquetes: este se queda con la evaluación de usabilidad (`problemas-de-usabilidad-sin-evidencia`, `cambios-de-interfaz-sin-aprobacion`, `mejoras-sin-medicion`); `barreras-de-accesibilidad` pasa a `pautas-de-accesibilidad` e `interfaz-inconsistente` a `componentes-de-interfaz`.
- Conserva la ficha de evaluación (`UXE`, carpeta `.`, mismos estados, plantilla y status), los ajustes (`heuristicas`, `severidad_max`, `severidad_propuesta_obligatoria`), las cinco fases, las skills `registrar-problema` y `medir-metrica` y las referencias `heuristicas.md` y `metricas.md`.
- `scripts/verificar-ux.py` pasa a `scripts/verificar-evaluaciones.py`, con las mismas comprobaciones; el resumen pasa a `evaluaciones: N errores, M avisos`.
- Las fases dejan la revisión de accesibilidad y de consistencia (skills `revisar-accesibilidad` y `revisar-consistencia`) a sus paquetes; los límites de estados completos y WCAG pasan con ellos.
