# Fase de preguntas (antes de la instrucción)

Antes de redactar el contrato en `05-instrucciones/`, el agente aclara el pedido con rondas de preguntas en el **chat**. Las respuestas se guardan en `03-preguntas/` y se **vuelcan** a la instrucción (§ Clarificación).

## Por defecto

En `uxyngraphar.config.json`:

```json
"preguntas": {"activo": true, "rondas": [10, 5, 3]}
```

- `activo: false` — el agente crea la instrucción sin ronda previa.
- `rondas` — enteros ≥ 1; ronda 1 usa el primer número, etc. (máx. 10 rondas, máx. 20 preguntas por ronda).
- En el pedido: «salta preguntas» / «sin fase de preguntas» omite la fase aunque `activo` sea true.

Detalle de config: [configuracion-uxyngraphar.md](configuracion-uxyngraphar.md). Protocolo de fichas: [`03-preguntas/_PROTOCOLO.md`](../03-preguntas/_PROTOCOLO.md).

## Qué hace el agente

1. Comprueba herramienta autorizada → si cubre el pedido, no hay fase ni instrucción nueva.
2. Si aplica la fase → crea ficha en `03-preguntas/01-en-curso/`, pregunta ronda a ronda (adaptando a respuestas previas), actualiza la ficha.
3. Al cerrar → crea instrucción `awaiting_approval` con Clarificación rellena, `preguntas_id`, y mueve la sesión a `03-completadas/`.
4. Espera aprobación humana (panel Pendientes). Sin `approved` no codea (R-03).

## Humano

- Responde en el chat (no hace falta el panel para cada ronda).
- Puedes acortar: «basta, crea la instrucción».
- Apruebas la instrucción resultante como siempre: panel → Proyecto → Pendientes.
