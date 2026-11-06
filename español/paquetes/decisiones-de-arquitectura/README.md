# Decisiones de arquitectura (ADR)

Activado con «usa el paquete decisiones-de-arquitectura» / «sigue el protocolo adr» o por `uxyngraphar/FLUJO.json`. `S=uxyngraphar/paquetes/decisiones-de-arquitectura/scripts`.

1. Integridad: `python3 $S/comun/verificar-integridad.py`. Si falla, **detente y avisa**.
2. Lee las **Reglas** (al final de este archivo).
3. Antes de decidir algo estructural, consulta las ADR vigentes: `python3 $S/comun/fichas.py listar adr --status aceptada`.
4. Nueva decisión: `python3 $S/comun/fichas.py nueva adr --slug <slug> --titulo "…"`; complétala y pásala a `en-evaluacion` cuando esté lista para la persona.
5. Antes de terminar: `python3 $S/comun/verificar.py`.

Trabajo: `uxyngraphar/trabajo/decisiones-de-arquitectura/<estado>/`.

## Reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Cuándo hace falta una ADR:** elegir o cambiar framework, base de datos, protocolo, patrón transversal, proveedor externo, modelo de seguridad o cualquier decisión cara de revertir.
2. **Una decisión por ADR**, con al menos dos opciones reales y sus consecuencias (positivas y negativas).
3. **Solo una persona acepta o rechaza** (`aceptada`, `rechazada`). El agente propone y deja en `en-evaluacion`.
4. **Las ADR aceptadas son vinculantes.** Si el trabajo contradice una, detente y propón una ADR nueva que la reemplace (`reemplaza: <id>`); nunca edites la aceptada.
5. **Reemplazo:** al aceptarse la nueva, la anterior pasa a `reemplazada` con `reemplazada_por: <id>`.
6. **Sin prosa genérica:** contexto concreto del proyecto, con rutas o enlaces cuando existan.
7. **Prohibiciones comprobables:** si la decisión veta algo detectable en el código, escríbelo como expresión regular en `comprobacion_prohibido` (y, si aplica, los archivos en `aplica_a`, p. ej. `["src/**/*.ts"]`); `verificaciones-vivas` lo busca.
