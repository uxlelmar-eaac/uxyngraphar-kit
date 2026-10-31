# Restricciones (cliente)

Personaliza esta lista por proyecto.

1. **Separar transporte de adaptación** — capa de red vs capa que adapta respuestas (p. ej. `api/` vs `reception/`).
2. **Sin acoplar dominios** — no importar UI/estado ajenos; usar integraciones solo hacia APIs externas al dominio.
3. **Estilos acotados** a la funcionalidad; globales en la carpeta común del proyecto.
4. **Secretos** — no exponer claves de servidor en el cliente; solo variables públicas validadas según el stack.
5. **Instrucción antes de código** — salvo excepciones en `PROTOCOLO.md`.
6. **No duplicar** el catálogo HTTP del servidor en `15-rutas/` del cliente.
7. **Despliegue** — seguir el runbook del proyecto.
8. **Límite 350 líneas por archivo (R-19)** — ningún archivo de código supera 350 líneas físicas (`wc -l`); proyecto nuevo = bloqueante; proyecto existente = inventario en `40-auditorias/` + fichas `MEJ-*` en 45 y ajuste progresivo; toda división con nomenclatura relacional (`<raiz>.<relacion>.<ext>`). Detalle: [limite-350-lineas.md](limite-350-lineas.md).
