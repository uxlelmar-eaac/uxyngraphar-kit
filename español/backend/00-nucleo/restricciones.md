# Restricciones (servidor)

Reglas que la IA **no debe violar** sin ADR + aprobación. Personaliza esta lista por proyecto.

1. **Cruces de módulo solo por integraciones** — la capa de aplicación no acopla módulos ajenos directamente.
2. **Dominio puro** — sin dependencias de framework ni de ORM en la capa de dominio.
3. **Código común no importa módulos de negocio**.
4. **Webhooks firmados** — si aplica: cuerpo en bruto + verificación de firma antes de parsear JSON.
5. **Secretos** — no documentar ni commitear credenciales reales.
6. **Instrucción antes de código** — salvo excepciones en `PROTOCOLO.md`.
7. **Despliegue** — seguir el runbook del proyecto; no asumir scripts o entornos no documentados aquí.
8. **Límite 350 líneas por archivo (R-19)** — ningún archivo de código supera 350 líneas físicas (`wc -l`); proyecto nuevo = bloqueante; proyecto existente = inventario en `40-auditorias/` + fichas `MEJ-*` en 45 y ajuste progresivo; toda división con nomenclatura relacional (`<raiz>.<relacion>.<ext>`). Detalle: [limite-350-lineas.md](limite-350-lineas.md).
