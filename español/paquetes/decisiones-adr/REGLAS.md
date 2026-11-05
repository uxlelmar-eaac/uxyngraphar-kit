# Decisiones de arquitectura — reglas

Paquete inmutable: ni la IA ni la persona lo editan dentro del repo. Cambios: catálogo del panel.

1. **Cuándo hace falta una ADR:** elegir o cambiar framework, base de datos, protocolo, patrón transversal, proveedor externo, modelo de seguridad o cualquier decisión cara de revertir.
2. **Una decisión por ADR**, con al menos dos opciones reales y sus consecuencias (positivas y negativas).
3. **Solo una persona acepta o rechaza** (`aceptada`, `rechazada`). El agente propone y deja en `en-evaluacion`.
4. **Las ADR aceptadas son vinculantes.** Si el trabajo contradice una, detente y propón una ADR nueva que la reemplace (`reemplaza: <id>`); nunca edites la aceptada.
5. **Reemplazo:** al aceptarse la nueva, la anterior pasa a `reemplazada` con `reemplazada_por: <id>`.
6. **Sin prosa genérica:** contexto concreto del proyecto, con rutas o enlaces cuando existan.
