# Límites

Se cumplen en todo el trabajo del paquete. Cambiar un límite o un ajuste lo decide una persona.

1. **Nada que cambie el resultado se supone.** Alcance, comportamiento visible, datos, compatibilidad y riesgos se preguntan antes de redactar o cambiar nada; no después de implementar.
2. **«Elegida» es de la persona.** En la tabla de decisiones solo va lo que la persona respondió; nunca tu recomendación si ella no la confirmó.
3. **Preguntas cerradas y proporcionales.** Cada pregunta trae opciones concretas, una recomendada y su efecto. Cambio pequeño: de 1 a 3 preguntas. No se pregunta lo que el código o la documentación ya responden.
4. **Sin cambios en el producto.** Este paquete no edita código ni documentación del producto: solo escribe fichas en `uxyngraphar/trabajo/preguntas-de-clarificacion/`. La instrucción o el cambio que sigue es de otro paquete.
5. **Estado = carpeta.** Cambia de estado con `fichas.py estado`; nunca muevas fichas a mano.
6. **Omisión explícita.** Si el pedido dice «salta preguntas» o `ajustes.preguntas` es `false`, no se crea ficha y la omisión se anota donde se use la síntesis (`Omitida (pedido)` u `Omitida (config)`).
7. **No escribas en el trabajo de otro paquete.** El enlace inverso (`preguntas_id` en la instrucción) lo pone el paquete dueño de la instrucción; aquí solo se pone `instruccion_id`.

## Cuándo detenerse y preguntar

- La persona responde de forma ambigua o con una opción que no estaba: repregunta antes de rellenar «Elegida».
- Salen más de 5 preguntas para un solo pedido: probablemente es demasiado grande; propón partirlo.
- Una respuesta contradice una ADR aceptada o una regla de otro paquete activo.
- La respuesta exige una decisión técnica cara de revertir: propón registrarla en `decisiones-de-arquitectura`.
