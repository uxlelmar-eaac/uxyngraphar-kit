# Pruebas (cliente)

- Preferir tests de mappers/esquemas en la capa de adaptación y utilidades puras.
- Flujos críticos de auth o pagos: verificar reintentos, sesión y códigos de error habituales.
- Tras cambios de contrato: regenerar tipos y alinear capas `types/` + `reception/`.
