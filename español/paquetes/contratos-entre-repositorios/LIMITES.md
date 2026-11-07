# Límites

Se cumplen en todo el trabajo del paquete.

1. **Un id compartido, el mismo en todos los repos** (`modulo.recurso.accion`). Se cita en áreas, espejo e instrucciones; no se renombra (contrato nuevo y retirada del anterior).
2. **No duplicar:** el consumidor cita la ficha del proveedor; nunca copia su ficha ni su OpenAPI.
3. **Proveedor primero:** no cierres un cambio del consumidor que depende de un contrato que el proveedor aún no fusionó.
4. **Cambios incompatibles** con nueva `version` y convivencia; la anterior pasa a `deprecado`.
5. **Repo aislado:** no abras el otro repo salvo para `comparar` o si el pedido lo pide.
6. **Solo una persona** marca `vigente` o `retirado`.
7. **No edites `REGISTRO.md` a mano:** lo regenera `contratos.py registro`.

## Cuándo detenerse y preguntar

- `contratos.py comparar` muestra divergencias y no está claro qué repositorio tiene la versión correcta.
- El cambio del consumidor depende de un contrato que el proveedor aún no ha fusionado.
- El cambio rompe a consumidores y el pedido no habla de versión ni de convivencia.
- El repositorio hermano no está al lado (`otros_repos`) y el pedido exige comparar.
