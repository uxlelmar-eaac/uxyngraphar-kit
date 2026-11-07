# Guía de preguntas

Objetivo: que el trabajo nazca con las decisiones ya tomadas por la persona, sin suposiciones del agente. Los pasos están en `proceso/preguntar.md` y `proceso/cerrar-pregunta.md`, y la ficha en las skills `registrar-pregunta` y `enlazar-pregunta`; aquí, el criterio.

## Qué se pregunta

1. Antes de redactar la instrucción o el plan, identifica lo que cambia el resultado: alcance, comportamiento visible, datos, compatibilidad, riesgos.
2. Pregunta solo eso, con opciones concretas y una recomendada. Cambios pequeños: 1–3 preguntas. No preguntes lo que el código ya responde.
3. Registra la ficha `pregunta` con impacto, tabla de decisiones y síntesis.
4. Con `instrucciones-aprobadas`, la instrucción pone `preguntas_id: <id de la pregunta>` y copia la síntesis en «Clarificación»; la pregunta pone `instruccion_id`.
5. Cierra la pregunta: `fichas.py estado <id> completada`; si se abandona, `cancelada`.
6. Si el pedido dice «salta preguntas» o `ajustes.preguntas` es false, anota donde se use la síntesis: `Omitida (pedido)` u `Omitida (config)`.

## Buenas y malas preguntas

| Mala | Por qué | Buena |
|------|---------|-------|
| «¿Cómo quieres que lo haga?» | abierta; traslada el diseño a la persona | «¿El filtro se guarda en la URL (recomendado: se puede compartir) o solo en memoria?» |
| «¿Uso TypeScript?» | el repo ya lo responde | (no se pregunta: se lee `package.json`) |
| «¿Añado tests?» | sin opciones ni efecto | «¿Cubro solo el caso feliz (1 archivo de test) o también los errores de red (2)?» |
| «¿Está bien así?» después de implementar | llega tarde | se pregunta antes de redactar la instrucción |

## Qué cambia el resultado

- **Alcance:** qué entra y qué no (¿también la pantalla de edición o solo la de alta?).
- **Comportamiento visible:** textos, orden, valores por defecto, qué ve el usuario ante un error.
- **Datos:** migraciones, campos nuevos, qué pasa con los registros existentes.
- **Compatibilidad:** clientes o repos que consumen lo que cambia, versiones soportadas.
- **Riesgos:** borrados, permisos, operaciones irreversibles.

Una pregunta cuya respuesta no cambia ninguna de estas cosas sobra.
