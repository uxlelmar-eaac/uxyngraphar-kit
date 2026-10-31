# Pruebas (servidor)

- Preferir tests de caso de uso / dominio cerca del código.
- No mockear de más: probar reglas de dominio sin levantar el framework cuando sea posible.
- Webhooks o colas: cubrir firma, idempotencia y reintentos en specs del dominio.
- Tras cambios de esquema de datos: pruebas + migración en el mismo cambio cuando aplique.
