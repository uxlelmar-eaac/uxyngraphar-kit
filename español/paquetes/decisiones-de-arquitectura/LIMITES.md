# Límites

Se cumplen en todo el trabajo del paquete.

1. **Cuándo hace falta una ADR:** elegir o cambiar framework, base de datos, protocolo, patrón transversal, proveedor externo, modelo de seguridad o cualquier decisión cara de revertir.
2. **Una decisión por ADR**, con al menos dos opciones reales y sus consecuencias (positivas y negativas).
3. **Solo una persona acepta o rechaza** (`aceptada`, `rechazada`). El agente propone y deja en `en-evaluacion`.
4. **Las ADR aceptadas son vinculantes.** Si el trabajo contradice una, detente y propón una ADR nueva que la reemplace (`reemplaza: <id>`); nunca edites la aceptada.
5. **Reemplazo:** al aceptarse la nueva, la anterior pasa a `reemplazada` con `reemplazada_por: <id>`. Es el único cambio permitido en una ADR aceptada.
6. **Sin prosa genérica:** contexto concreto del proyecto, con rutas o enlaces cuando existan.
7. **Prohibiciones comprobables:** si la decisión veta algo detectable en el código, escríbelo como expresión regular en `comprobacion_prohibido` (y, si aplica, los archivos en `aplica_a`, p. ej. `["src/**/*.ts"]`); `verificaciones-vivas` lo busca.
8. **Una ADR no cambia código.** Implementar lo decidido es otro trabajo (una instrucción aprobada, si el proyecto usa `instrucciones-aprobadas`).

## Cuándo detenerse y preguntar

- El pedido contradice una ADR aceptada: no sigas; propón el reemplazo y espera a la persona.
- Solo encuentras una opción realista: pregunta qué alternativas se descartaron y por qué antes de redactar.
- Dos ADR aceptadas se contradicen entre sí.
- No está claro si la decisión es lo bastante cara de revertir como para merecer una ADR.
