# Contratos API en el lado consumidor

- **Fuente automática:** si el proveedor publica OpenAPI, los tipos del consumidor se **generan** (script del proyecto), no se escriben a mano. Anota en el contrato dónde quedan.
- **Fuente humana:** la ficha de la ruta en el repo proveedor (`rutas-de-api`). El consumidor la cita en `ficha_proveedor`; nunca la duplica.
- **Capa de adaptación:** el JSON del proveedor se transforma a la forma de vista en una sola capa (por ejemplo `reception/` o un mapper). Al cambiar el contrato, se ajustan los tipos y esa capa en el mismo cambio.
- **Variables públicas:** en clientes web, solo variables pensadas para exponerse (p. ej. `NEXT_PUBLIC_*`) y validadas al arrancar; nunca secretos del servidor.
- **Errores:** los códigos de error de la API se tratan por código, no por texto.
