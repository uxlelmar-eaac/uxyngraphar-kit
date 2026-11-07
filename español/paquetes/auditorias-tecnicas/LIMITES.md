# Límites

Se cumplen en todo el trabajo del paquete. Valores ajustables en `uxyngraphar/trabajo/auditorias-tecnicas/ajustes.json`.

1. **Auditar no es arreglar.** Una auditoría no modifica código ni documentación del producto; solo produce la ficha. Medir o ejecutar comandos de lectura sí; cambiar, no.
2. **Alcance y preguntas primero.** Sin ellos no se investiga.
3. **Evidencia o no es hallazgo.** Cada hallazgo cita `ruta:línea`, un comando reproducible o una medición. Las opiniones van en «Notas».
4. **Severidad obligatoria** por hallazgo: `critica`, `alta`, `media`, `baja` o `info` (según `ajustes.severidades`).
5. **`findings_count`** coincide con el número de hallazgos de la tabla.
6. **Promociones, no acciones.** Lo que haya que cambiar se propone como ADR, instrucción, mejora o actualización de documentación; lo decide una persona.
7. **Pocas activas y vivas.** Como mucho `max_activas` (5) a la vez; una activa sin cambios en `dias_sin_cambios` (14) días se propone cerrar o pasar a `pendiente`. Cada avance actualiza `actualizado`.
8. **Nada se borra.** Una auditoría descartada va a `cancelada`; lo que una persona quiere retirar va a `para-eliminar` y de ahí al archivo histórico.

## Cuándo detenerse y preguntar

- El pedido no permite fijar alcance o preguntas («revisa todo el backend»).
- Ya hay `max_activas` auditorías activas: ¿cuál se cierra o se pospone?
- Responder una pregunta exige cambiar código, datos o configuración (aunque sea para medir).
- Un hallazgo `critica` (seguridad, pérdida de datos): avisa en cuanto lo tengas, sin esperar a cerrar.
- Al cerrar: la persona decide qué promociones se aceptan.
